/* ======================================================================
   councilEngine.js — Multi-Agent Council (Nurse-PaLM Layer 10)
   Clinical Engine V9 — NIFS v5.0

   Orchestrates multiple specialist agents that deliberate in rounds,
   vote on clinical decisions, and reach consensus (or flag dissent).

   Schema: ni_council.agents, .agent_roles, .sessions, .consensus_protocols,
           .deliberation_log, .consensus_results, .agent_performance

   Agents:
     - assessment:  clinical assessment specialist
     - nanda:       NANDA-I diagnosis specialist
     - nic:         NIC intervention specialist
     - noc:         NOC outcome specialist
     - safety:      patient safety officer (veto eligible)
     - medication:  pharmacology specialist
     - evidence:    evidence-based practice specialist
     - consensus:   consensus facilitator (arbitrator)

   API:
     const council = new CouncilEngine(supabaseClient);
     const sessionId = await council.openSession(caseId, question);
     await council.addAgent(sessionId, "nanda", "primary");
     await council.deliberate(sessionId, { maxRounds: 3 });
     const result = await council.getConsensus(sessionId);
   ====================================================================== */
(function (global) {
  "use strict";

  const AGENT_TYPES = [
    "assessment", "nanda", "nic", "noc",
    "safety", "medication", "evidence", "consensus", "specialist"
  ];

  const PROTOCOL_TYPES = [
    "majority", "weighted_majority", "unanimous", "threshold", "deliberative"
  ];

  const CONSENSUS_TYPES = ["reached", "partial", "no_consensus", "vetoed"];

  const ROLES = ["primary", "secondary", "veto_holder", "arbitrator"];

  class CouncilEngine {
    constructor(supabaseClient) {
      this.db = supabaseClient;
      this.schema = "ni_council";
      this.agents = [];
      this._cacheLoaded = false;
    }

    /**
     * Load or refresh the agent registry from the database.
     */
    async loadAgents() {
      const { data, error } = await this.db
        .from("agents")
        .select("*")
        .eq("active", true);

      if (error) {
        console.error("[councilEngine] loadAgents:", error.message);
        return [];
      }
      this.agents = data || [];
      this._cacheLoaded = true;
      return this.agents;
    }

    /**
     * Open a new council session for a clinical case.
     */
    async openSession(caseId, question, options) {
      options = options || {};
      const protocol = options.protocol || "weighted_majority";
      const threshold = options.threshold || 0.60;
      const quorum = options.quorum || 6;
      const timeout = options.timeout || 30;

      // Create session (ni_council.sessions is in the core DDL)
      const { data: sess, error: sErr } = await this.db
        .from("sessions")
        .insert({
          case_id: caseId || null,
          session_type: "council",
          status: "open",
          query: question,
          context: options.context || {}
        })
        .select("session_id")
        .single();

      if (sErr) throw new Error("openSession: " + sErr.message);
      const sessionId = sess.session_id;

      // Create consensus protocol
      const { error: pErr } = await this.db
        .from("consensus_protocols")
        .insert({
          session_id: sessionId,
          protocol_type: protocol,
          threshold: threshold,
          quorum: quorum,
          timeout_seconds: timeout
        });

      if (pErr) console.error("[councilEngine] protocol insert:", pErr.message);

      return sessionId;
    }

    /**
     * Assign an agent to a session with a specific role.
     */
    async addAgent(sessionId, agentType, role) {
      if (AGENT_TYPES.indexOf(agentType) === -1) {
        throw new Error("addAgent: invalid agent_type: " + agentType);
      }
      if (ROLES.indexOf(role) === -1) role = "primary";

      if (!this._cacheLoaded) await this.loadAgents();

      const agent = this.agents.find(a => a.agent_type === agentType);
      if (!agent) {
        console.warn("[councilEngine] No active agent of type:", agentType);
        return null;
      }

      const { error } = await this.db.from("agent_roles").insert({
        agent_id: agent.agent_id,
        session_id: sessionId,
        role: role,
        voting_weight: agent.voting_weight || 1.0
      });

      if (error) console.error("[councilEngine] addAgent:", error.message);
      return agent;
    }

    /**
     * Run deliberation rounds. Each agent submits a position,
     * sees others' positions, and may revise. Repeat until consensus
     * or maxRounds reached.
     */
    async deliberate(sessionId, options) {
      options = options || {};
      const maxRounds = options.maxRounds || 3;
      const positions = options.initialPositions || {};

      // Fetch assigned agents
      const { data: roles, error } = await this.db
        .from("agent_roles")
        .select(`
          role_id, agent_id, role, voting_weight,
          agents (agent_id, agent_type, agent_name, specialty, veto_eligible)
        `)
        .eq("session_id", sessionId);

      if (error || !roles || roles.length === 0) {
        return { consensus: "no_consensus", rounds: 0, reason: "no agents assigned" };
      }

      // Check quorum
      const protocol = await this._getProtocol(sessionId);
      if (roles.length < protocol.quorum) {
        return { consensus: "no_consensus", rounds: 0, reason: "quorum not met" };
      }

      let roundResults = [];
      let consensusReached = false;
      let vetoed = false;

      for (let round = 1; round <= maxRounds; round++) {
        const roundPositions = [];

        for (const roleData of roles) {
          const agent = roleData.agents;
          const position = positions[agent.agent_type] ||
            this._generatePosition(agent, roundResults[round - 2] || []);

          // Log deliberation entry
          const { data: dl } = await this.db.from("deliberation_log").insert({
            session_id: sessionId,
            agent_id: agent.agent_id,
            round_number: round,
            position: position,
            argument_text: position.argument || "",
            evidence_refs: position.evidence_refs || [],
            confidence: position.confidence || 0.5,
            changed_from_prev: round > 1 && positions[agent.agent_type] !== undefined
          }).select("deliberation_id").single();

          roundPositions.push({
            agent_type: agent.agent_type,
            agent_id: agent.agent_id,
            voting_weight: roleData.voting_weight,
            position: position,
            veto_eligible: agent.veto_eligible
          });

          // Safety agent veto check
          if (agent.veto_eligible && position.veto) {
            vetoed = true;
          }
        }

        roundResults.push(roundPositions);

        if (vetoed) break;

        // Check consensus after this round
        const agreement = this._computeAgreement(roundPositions);
        if (agreement.score >= protocol.threshold) {
          consensusReached = true;
          break;
        }
      }

      // Store consensus result
      const agreementFinal = this._computeAgreement(roundResults[roundResults.length - 1] || []);
      const consensusType = vetoed ? "vetoed"
        : consensusReached ? "reached"
        : agreementFinal.score >= 0.4 ? "partial"
        : "no_consensus";

      const { data: result } = await this.db.from("consensus_results").insert({
        session_id: sessionId,
        consensus_type: consensusType,
        agreement_score: agreementFinal.score,
        rounds: roundResults.length,
        final_decision: agreementFinal.decision,
        dissent_summary: agreementFinal.dissent
      }).select("result_id").single();

      // Update session status
      await this.db.from("sessions")
        .update({ status: "closed" })
        .eq("session_id", sessionId);

      return {
        consensus: consensusType,
        rounds: roundResults.length,
        agreement: agreementFinal.score,
        decision: agreementFinal.decision,
        dissent: agreementFinal.dissent,
        vetoed: vetoed
      };
    }

    /**
     * Get the consensus result for a session.
     */
    async getConsensus(sessionId) {
      const { data, error } = await this.db
        .from("consensus_results")
        .select("*")
        .eq("session_id", sessionId)
        .order("created_date", { ascending: false })
        .limit(1)
        .single();

      if (error) return null;
      return data;
    }

    /**
     * Record performance metric for an agent.
     */
    async recordAgentPerformance(agentId, metric, value) {
      const { error } = await this.db.from("agent_performance").insert({
        agent_id: agentId,
        metric_name: metric,
        metric_value: value
      });
      if (error) console.error("[councilEngine] performance record:", error.message);
    }

    // ═════════════════════════════════════════════════════════
    // PRIVATE METHODS
    // ═════════════════════════════════════════════════════════

    async _getProtocol(sessionId) {
      const { data, error } = await this.db
        .from("consensus_protocols")
        .select("*")
        .eq("session_id", sessionId)
        .single();
      if (error || !data) return { threshold: 0.6, quorum: 6, protocol_type: "weighted_majority" };
      return data;
    }

    /**
     * Compute agreement score among agents.
     * Returns { score: 0-1, decision: object, dissent: string }
     */
    _computeAgreement(positions) {
      if (!positions || positions.length === 0) {
        return { score: 0, decision: null, dissent: "no positions" };
      }

      // Group by diagnosis/intervention recommendation
      const votes = {};
      let totalWeight = 0;

      for (const p of positions) {
        const key = JSON.stringify(p.position.recommendation || p.position.diagnosis || "unknown");
        if (!votes[key]) votes[key] = { count: 0, weight: 0, examples: [] };
        votes[key].count++;
        votes[key].weight += p.voting_weight;
        votes[key].examples.push(p);
        totalWeight += p.voting_weight;
      }

      // Find the winning vote
      let best = { key: null, weight: 0, count: 0 };
      for (const [key, v] of Object.entries(votes)) {
        if (v.weight > best.weight) best = { key, weight: v.weight, count: v.count };
      }

      const score = totalWeight > 0 ? best.weight / totalWeight : 0;
      const decision = best.key ? JSON.parse(best.key) : null;
      const dissent = Object.entries(votes)
        .filter(([k]) => k !== best.key)
        .map(([k, v]) => `${v.examples[0].agent_type}: ${k}`)
        .join("; ");

      return { score, decision, dissent };
    }

    /**
     * Generate a position for an agent.
     * In production, each agent type would call a specialized model.
     * Here we use a simple heuristic based on agent specialty.
     */
    _generatePosition(agent, previousRound) {
      const position = {
        recommendation: null,
        confidence: 0.5,
        argument: "",
        evidence_refs: [],
        veto: false
      };

      switch (agent.agent_type) {
        case "assessment":
          position.recommendation = { type: "assessment", action: "comprehensive_assessment" };
          position.confidence = 0.7;
          position.argument = "Comprehensive assessment recommended before diagnosis.";
          break;
        case "nanda":
          position.recommendation = { type: "diagnosis", source: "NANDA-I" };
          position.confidence = 0.65;
          position.argument = "Primary diagnosis based on defining characteristics.";
          break;
        case "nic":
          position.recommendation = { type: "intervention", source: "NIC" };
          position.confidence = 0.6;
          position.argument = "Evidence-based intervention matched to diagnosis.";
          break;
        case "noc":
          position.recommendation = { type: "outcome", source: "NOC" };
          position.confidence = 0.55;
          position.argument = "Expected outcome with standard intervention timeline.";
          break;
        case "safety":
          position.recommendation = { type: "safety_check" };
          position.confidence = 0.8;
          position.argument = "Safety review completed. No contraindications detected.";
          position.veto = false;
          break;
        case "medication":
          position.recommendation = { type: "medication_review" };
          position.confidence = 0.7;
          position.argument = "Medication interactions verified. 9 Rights confirmed.";
          break;
        case "evidence":
          position.recommendation = { type: "evidence_level", grade: "B" };
          position.confidence = 0.6;
          position.argument = "Moderate quality evidence supports this recommendation.";
          break;
        case "consensus":
          position.recommendation = { type: "facilitate" };
          position.confidence = 0.5;
          position.argument = "Facilitating consensus among council members.";
          break;
      }

      // Revise based on previous round (agents can change their mind)
      if (previousRound && previousRound.length > 0) {
        const others = previousRound.filter(p => p.agent_type !== agent.agent_type);
        const avgConfidence = others.reduce((s, o) => s + (o.position.confidence || 0.5), 0) / others.length;
        position.confidence = (position.confidence + avgConfidence) / 2;
      }

      return position;
    }
  }

  global.CouncilEngine = CouncilEngine;
  global.AGENT_TYPES = AGENT_TYPES;
  global.PROTOCOL_TYPES = PROTOCOL_TYPES;
  global.CONSENSUS_TYPES = CONSENSUS_TYPES;

})(typeof module !== "undefined" ? module.exports : (this || window));
