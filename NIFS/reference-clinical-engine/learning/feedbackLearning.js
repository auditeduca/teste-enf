/* ======================================================================
   feedbackLearning.js — Feedback Learning Engine (Nurse-PaLM Layer 8)
   Clinical Engine V9 — NIFS v5.0

   Closes the learning loop: outcome → reward signal → weight update.
   Adjusts graph edge weights, rule confidences, probability priors,
   and attention scores based on observed vs expected outcomes.

   Schema: ni_learning.reinforcement_signals, .weight_updates, .learning_curves
   Dependency: ni_memory (episodes/outcomes), ni_graph (edges), ni_prob (priors)

   API:
     const learner = new FeedbackLearning(supabaseClient);
     await learner.processOutcome(episodeId);  // full pipeline
     await learner.applyWeightUpdates(batchId); // validate + apply
     await learner.recordMetric(component, metric, value); // learning curve
   ====================================================================== */
(function (global) {
  "use strict";

  const SIGNAL_TYPES = ["positive", "negative", "neutral", "mixed"];
  const TARGET_TYPES = ["rule", "weight", "edge", "probability", "attention"];
  const MAX_DELTA = 0.15; // weight change cap per update
  const VALIDATION_STATUS = ["pending", "validated", "rejected", "rolled_back"];

  class FeedbackLearning {
    constructor(supabaseClient) {
      this.db = supabaseClient;
      this.schema = "ni_learning";
    }

    /**
     * Full pipeline: scan episode outcomes → generate reward signals →
     * compute weight updates → store for validation.
     */
    async processOutcome(episodeId) {
      // 1. Fetch outcomes with linked actions
      const { data: outcomes, error: oErr } = await this.db
        .from("outcomes")
        .select(`
          outcome_id, action_id, outcome_type, outcome_value,
          expected_value, surprise_score, measured_at,
          actions (action_id, nic_code, action_type)
        `)
        .eq("episode_id", episodeId);

      if (oErr || !outcomes || outcomes.length === 0) {
        return { signals: 0, updates: 0 };
      }

      // 2. Generate reinforcement signals
      const signals = [];
      for (const outcome of outcomes) {
        const reward = this._computeReward(outcome);
        const signalType = this._classifyReward(reward);
        const action = outcome.actions;

        signals.push({
          episode_id: episodeId,
          action_id: outcome.action_id,
          outcome_id: outcome.outcome_id,
          reward: reward,
          signal_type: signalType,
          target_node_id: action ? action.nic_code : null,
          target_type: "edge",
          created_by: null
        });
      }

      if (signals.length === 0) return { signals: 0, updates: 0 };

      const { data: insertedSignals, error: sErr } = await this.db
        .from("reinforcement_signals")
        .insert(signals)
        .select("signal_id, reward, target_node_id, target_type");

      if (sErr || !insertedSignals) {
        console.error("[feedbackLearning] signal insert:", sErr?.message);
        return { signals: 0, updates: 0 };
      }

      // 3. Compute weight updates from signals
      const updates = [];
      for (const sig of insertedSignals) {
        // Find the graph edge connecting the NANDA diagnosis → NIC intervention
        // For now, we update the target node's related edges
        const { data: edges, error: eErr } = await this.db
          .from("edges")
          .select("edge_id, weight")
          .eq("to_node", sig.target_node_id)
          .limit(10);

        if (eErr || !edges) continue;

        for (const edge of edges) {
          const oldWeight = edge.weight;
          const delta = Math.max(-MAX_DELTA, Math.min(MAX_DELTA, sig.reward * 0.05));
          const newWeight = Math.max(0, Math.min(1, oldWeight + delta));

          if (Math.abs(delta) < 0.001) continue; // skip negligible updates

          updates.push({
            signal_id: sig.signal_id,
            edge_id: edge.edge_id,
            old_value: oldWeight,
            new_value: newWeight,
            delta: delta,
            validation_status: "pending",
            created_by: null
          });
        }
      }

      if (updates.length > 0) {
        const { error: uErr } = await this.db.from("weight_updates").insert(updates);
        if (uErr) console.error("[feedbackLearning] weight_updates insert:", uErr.message);
      }

      // 4. Record learning curve metric
      const avgReward = signals.reduce((s, sig) => s + sig.reward, 0) / signals.length;
      await this.recordMetric("feedback_learning", "avg_reward", avgReward);
      await this.recordMetric("feedback_learning", "signal_count", signals.length);
      await this.recordMetric("feedback_learning", "update_count", updates.length);

      return { signals: signals.length, updates: updates.length };
    }

    /**
     * Validate and apply pending weight updates.
     * In production, a human reviewer or safety agent validates before apply.
     */
    async applyWeightUpdates(batchId) {
      // Fetch pending updates
      let q = this.db
        .from("weight_updates")
        .select("update_id, edge_id, old_value, new_value, delta, validation_status")
        .eq("validation_status", "pending")
        .limit(100);

      if (batchId) q = q.eq("signal_id", batchId);

      const { data: updates, error } = await q;
      if (error || !updates) return { applied: 0, rejected: 0 };

      let applied = 0;
      let rejected = 0;

      for (const u of updates) {
        // Safety check: reject if delta exceeds safety threshold
        if (Math.abs(u.delta) > MAX_DELTA) {
          await this.db.from("weight_updates")
            .update({ validation_status: "rejected", rejection_reason: "delta exceeds safety threshold" })
            .eq("update_id", u.update_id);
          rejected++;
          continue;
        }

        // Apply: update the edge weight
        const { error: edgeErr } = await this.db
          .from("edges")
          .update({ weight: u.new_value })
          .eq("edge_id", u.edge_id);

        if (edgeErr) {
          console.error("[feedbackLearning] edge update:", edgeErr.message);
          rejected++;
          continue;
        }

        // Mark as validated
        await this.db.from("weight_updates")
          .update({ validation_status: "validated", validated_at: new Date().toISOString() })
          .eq("update_id", u.update_id);
        applied++;
      }

      await this.recordMetric("feedback_learning", "updates_applied", applied);
      await this.recordMetric("feedback_learning", "updates_rejected", rejected);

      return { applied, rejected };
    }

    /**
     * Record a learning curve metric for tracking improvement over time.
     */
    async recordMetric(component, metricName, value) {
      const { error } = await this.db.from("learning_curves").insert({
        component: component,
        metric_name: metricName,
        metric_value: value
      });
      if (error) console.error("[feedbackLearning] metric record:", error.message);
    }

    /**
     * Compute reward signal from outcome.
     * reward ∈ [-1, 1]
     *   improved/resolved → positive
     *   deteriorated/adverse → negative
     *   unchanged → neutral
     * 
     * If surprise_score is available, it modulates the magnitude:
     *   high surprise + positive outcome = stronger positive signal
     *   high surprise + negative outcome = stronger negative signal
     */
    _computeReward(outcome) {
      const baseRewards = {
        "improved": 0.6,
        "resolved": 0.8,
        "unchanged": 0.0,
        "deteriorated": -0.5,
        "adverse": -0.9
      };

      let reward = baseRewards[outcome.outcome_type] || 0.0;

      // Modulate by surprise (if available)
      if (outcome.surprise_score != null) {
        const surpriseMod = Math.min(0.3, outcome.surprise_score * 0.1);
        if (reward > 0) reward += surpriseMod;
        else if (reward < 0) reward -= surpriseMod;
      }

      // Modulate by outcome_value vs expected_value (if available)
      if (outcome.outcome_value != null && outcome.expected_value != null) {
        const diff = outcome.outcome_value - outcome.expected_value;
        reward += Math.max(-0.2, Math.min(0.2, diff * 0.1));
      }

      return Math.max(-1, Math.min(1, reward));
    }

    /**
     * Classify a numeric reward into a signal type.
     */
    _classifyReward(reward) {
      if (reward > 0.2) return "positive";
      if (reward < -0.2) return "negative";
      if (Math.abs(reward) < 0.05) return "neutral";
      return "mixed";
    }
  }

  global.FeedbackLearning = FeedbackLearning;
  global.MAX_DELTA = MAX_DELTA;

})(typeof module !== "undefined" ? module.exports : (this || window));
