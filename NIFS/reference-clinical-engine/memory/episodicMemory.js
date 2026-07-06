/* ======================================================================
   episodicMemory.js — Episodic Memory Engine (Nurse-PaLM Layer 2)
   Clinical Engine V9 — NIFS v5.0

   Stores and retrieves clinical episodes (admission → intervention →
   outcome) using vector similarity for case-based reasoning.

   Schema: ni_memory.episodes, .observations, .actions, .outcomes, .learnings
   Dependency: pgvector (similarity_embedding VECTOR(1536))

   API:
     const mem = new EpisodicMemory(supabaseClient);
     await mem.storeEpisode(episode);        // persists full episode
     await mem.recallSimilar(query, k);      // top-k similar past episodes
     await mem.extractLearnings(episodeId);  // derives learnings from outcome
   ====================================================================== */
(function (global) {
  "use strict";

  const EPISODE_TYPES = [
    "admission", "intervention", "crisis", "recovery", "discharge", "longitudinal"
  ];

  const OUTCOME_TYPES = [
    "improved", "unchanged", "deteriorated", "resolved", "adverse"
  ];

  const LEARNING_TYPES = [
    "effective_intervention", "ineffective_intervention",
    "adverse_reaction", "time_pattern", "context_pattern"
  ];

  class EpisodicMemory {
    constructor(supabaseClient) {
      this.db = supabaseClient;
      this.schema = "ni_memory";
    }

    /**
     * Store a complete clinical episode with its observations,
     * actions, and outcomes. Returns the episode UUID.
     */
    async storeEpisode(episode) {
      if (!episode || !episode.patient_identifier || !episode.episode_type) {
        throw new Error("storeEpisode: patient_identifier and episode_type required");
      }
      if (EPISODE_TYPES.indexOf(episode.episode_type) === -1) {
        throw new Error("storeEpisode: invalid episode_type: " + episode.episode_type);
      }

      // 1. Insert episode record
      const epRow = {
        patient_identifier: episode.patient_identifier,
        case_id: episode.case_id || null,
        episode_type: episode.episode_type,
        started_at: episode.started_at || new Date().toISOString(),
        ended_at: episode.ended_at || null,
        outcome_summary: episode.outcome_summary || null,
        success_score: episode.success_score != null
          ? Math.max(0, Math.min(1, episode.success_score))
          : null,
        similarity_embedding: episode.embedding || null,
        created_by: episode.created_by || null
      };

      const { data: ep, error: epErr } = await this.db
        .from("episodes")
        .insert(epRow)
        .select("episode_id")
        .single();

      if (epErr) throw new Error("storeEpisode: " + epErr.message);
      const episodeId = ep.episode_id;

      // 2. Insert observations
      if (episode.observations && episode.observations.length) {
        const obsRows = episode.observations.map(o => ({
          episode_id: episodeId,
          observed_at: o.observed_at || new Date().toISOString(),
          observation_type: o.observation_type,
          observation_value: o.observation_value,
          attention_score: o.attention_score || null,
          node_id: o.node_id || null,
          created_by: episode.created_by || null
        }));
        const { error: obsErr } = await this.db.from("observations").insert(obsRows);
        if (obsErr) console.error("[episodicMemory] observations insert:", obsErr.message);
      }

      // 3. Insert actions
      if (episode.actions && episode.actions.length) {
        const actRows = episode.actions.map(a => ({
          episode_id: episodeId,
          action_type: a.action_type,
          nic_code: a.nic_code || null,
          protocol_id: a.protocol_id || null,
          action_data: a.action_data || null,
          reasoning_session_id: a.reasoning_session_id || null,
          created_by: episode.created_by || null
        }));
        const { error: actErr } = await this.db.from("actions").insert(actRows);
        if (actErr) console.error("[episodicMemory] actions insert:", actErr.message);
      }

      // 4. Insert outcomes
      if (episode.outcomes && episode.outcomes.length) {
        const outRows = episode.outcomes.map(o => ({
          episode_id: episodeId,
          action_id: o.action_id || null,
          noc_code: o.noc_code || null,
          outcome_type: o.outcome_type,
          outcome_value: o.outcome_value != null ? o.outcome_value : null,
          expected_value: o.expected_value != null ? o.expected_value : null,
          surprise_score: this._computeSurprise(o),
          measured_at: o.measured_at || new Date().toISOString(),
          created_by: episode.created_by || null
        }));
        const { error: outErr } = await this.db.from("outcomes").insert(outRows);
        if (outErr) console.error("[episodicMemory] outcomes insert:", outErr.message);
      }

      return episodeId;
    }

    /**
     * Recall the top-k most similar past episodes using vector similarity.
     * Falls back to type-based filtering if no embedding is provided.
     */
    async recallSimilar(query, k) {
      k = k || 5;

      if (query.embedding) {
        // Vector similarity search via pgvector
        const { data, error } = await this.db.rpc("match_episodes", {
          query_embedding: query.embedding,
          match_count: k,
          episode_type: query.episode_type || null
        });
        if (error) {
          console.error("[episodicMemory] recallSimilar vector:", error.message);
          return [];
        }
        return data || [];
      }

      // Fallback: filter by type + success_score
      let q = this.db
        .from("episodes")
        .select("episode_id, patient_identifier, episode_type, outcome_summary, success_score, started_at")
        .order("started_at", { ascending: false })
        .limit(k * 3);

      if (query.episode_type) q = q.eq("episode_type", query.episode_type);
      if (query.success_score_min != null) q = q.gte("success_score", query.success_score_min);

      const { data, error } = await q;
      if (error) {
        console.error("[episodicMemory] recallSimilar fallback:", error.message);
        return [];
      }
      return (data || []).slice(0, k);
    }

    /**
     * Extract learnings from a completed episode by comparing
     * actions vs outcomes. Generates ni_memory.learnings records.
     */
    async extractLearnings(episodeId) {
      const { data: actions, error: aErr } = await this.db
        .from("actions")
        .select("action_id, nic_code, action_type")
        .eq("episode_id", episodeId);

      const { data: outcomes, error: oErr } = await this.db
        .from("outcomes")
        .select("outcome_id, action_id, outcome_type, outcome_value, expected_value, surprise_score")
        .eq("episode_id", episodeId);

      if (aErr || oErr || !actions || !outcomes) {
        console.error("[episodicMemory] extractLearnings fetch error");
        return [];
      }

      const learnings = [];
      for (const outcome of outcomes) {
        const action = actions.find(a => a.action_id === outcome.action_id);
        if (!action) continue;

        let learningType = null;
        let description = "";
        let weightAdjustment = 0;

        switch (outcome.outcome_type) {
          case "improved":
          case "resolved":
            learningType = "effective_intervention";
            description = `NIC ${action.nic_code} led to ${outcome.outcome_type} state`;
            weightAdjustment = 0.05;
            break;
          case "deteriorated":
            learningType = "ineffective_intervention";
            description = `NIC ${action.nic_code} was followed by ${outcome.outcome_type} state`;
            weightAdjustment = -0.05;
            break;
          case "adverse":
            learningType = "adverse_reaction";
            description = `Adverse outcome observed with NIC ${action.nic_code}`;
            weightAdjustment = -0.10;
            break;
          case "unchanged":
            continue;
        }

        if (learningType) {
          learnings.push({
            episode_id: episodeId,
            learning_type: learningType,
            description: description,
            weight_adjustment: weightAdjustment,
            applied: false,
            created_by: null
          });
        }
      }

      if (learnings.length > 0) {
        const { error } = await this.db.from("learnings").insert(learnings);
        if (error) console.error("[episodicMemory] learnings insert:", error.message);
      }

      return learnings;
    }

    /**
     * Compute surprise score = |outcome - expected|
     * High surprise = strong learning signal
     */
    _computeSurprise(outcome) {
      if (outcome.outcome_value == null || outcome.expected_value == null) return null;
      return Math.abs(outcome.outcome_value - outcome.expected_value);
    }

    /**
     * Generate embedding from episode metadata.
     * Production: use text-embedding-3-small or similar.
     */
    generateEmbedding(episode) {
      const text = [
        episode.episode_type,
        episode.outcome_summary,
        (episode.observations || []).map(o => o.observation_type).join(" ")
      ].join(" ");

      // Simple hash → 1536-dim vector (placeholder — NOT for production)
      const vec = new Array(1536).fill(0);
      for (let i = 0; i < text.length; i++) {
        vec[i % 1536] = (vec[i % 1536] + text.charCodeAt(i)) / 255;
      }
      return vec;
    }
  }

  global.EpisodicMemory = EpisodicMemory;
  global.EPISODE_TYPES = EPISODE_TYPES;
  global.OUTCOME_TYPES = OUTCOME_TYPES;
  global.LEARNING_TYPES = LEARNING_TYPES;

})(typeof module !== "undefined" ? module.exports : (this || window));
