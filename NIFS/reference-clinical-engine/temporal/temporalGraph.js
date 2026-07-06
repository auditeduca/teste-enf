/* ======================================================================
   temporalGraph.js — Temporal Graph Engine (Nurse-PaLM Layer 3)
   Clinical Engine V9 — NIFS v5.0

   Materializa a evolução temporal de estados clínicos como um grafo
   explícito. O particle filter do V8 já rastreia estados ao longo do
   tempo implicitamente — este módulo persiste essa evolução como
   snapshots e arestas temporais (state_t → state_t+1), permitindo
   queries como "como evoluiu a volemia do paciente X nas últimas 6h?"

   Schema: ni_temporal.event_sequences, .event_sequence_items,
           .causal_chains, .clinical_events
   Dependency: ni_world (patient_states), ni_graph (nodes/edges)

   API:
     const tg = new TemporalGraph(supabaseClient);
     await tg.recordEvent(event);              // persist clinical event
     await tg.buildSequence(patientId, type);  // assemble event sequence
     await tg.detectCausalChain(patientId);    // infer causal relationships
     await tg.queryEvolution(patientId, state, window); // state over time
   ====================================================================== */
(function (global) {
  "use strict";

  const SEQUENCE_TYPES = [
    "deterioration", "recovery", "crisis", "stabilization", "oscillation"
  ];

  const CAUSALITY_TYPES = [
    "direct", "contributing", "temporal_correlation", "confounded"
  ];

  // Window presets in seconds
  const WINDOWS = {
    "1h": 3600,
    "6h": 21600,
    "24h": 86400,
    "7d": 604800,
    "30d": 2592000
  };

  class TemporalGraph {
    constructor(supabaseClient) {
      this.db = supabaseClient;
      this.schema = "ni_temporal";
      this._eventCache = new Map();
    }

    /**
     * Record a clinical event with its state snapshot.
     * Events are the nodes of the temporal graph.
     */
    async recordEvent(event) {
      if (!event || !event.patient_identifier) {
        throw new Error("recordEvent: patient_identifier required");
      }

      const eventRow = {
        patient_identifier: event.patient_identifier,
        event_type: event.event_type || "observation",
        event_data: event.event_data || {},
        state_snapshot: event.state_snapshot || null,
        occurred_at: event.occurred_at || new Date().toISOString(),
        severity: event.severity || "routine",
        source: event.source || "clinical_engine",
        created_by: event.created_by || null
      };

      const { data, error } = await this.db
        .from("clinical_events")
        .insert(eventRow)
        .select("event_id, occurred_at")
        .single();

      if (error) {
        console.error("[temporalGraph] recordEvent:", error.message);
        return null;
      }

      // Update cache
      const patientEvents = this._eventCache.get(event.patient_identifier) || [];
      patientEvents.push({ ...data, ...eventRow });
      this._eventCache.set(event.patient_identifier, patientEvents);

      return data.event_id;
    }

    /**
     * Build an event sequence for a patient.
     * Groups temporally related events into a named sequence
     * (deterioration, recovery, crisis, etc.)
     */
    async buildSequence(patientId, sequenceType) {
      if (SEQUENCE_TYPES.indexOf(sequenceType) === -1) {
        throw new Error("buildSequence: invalid type: " + sequenceType);
      }

      // Fetch recent events for the patient
      const { data: events, error } = await this.db
        .from("clinical_events")
        .select("event_id, event_type, occurred_at, severity, state_snapshot")
        .eq("patient_identifier", patientId)
        .order("occurred_at", { ascending: true })
        .limit(200);

      if (error || !events || events.length === 0) {
        return { sequence_id: null, items: 0 };
      }

      // Detect sequence boundaries based on type
      const boundaries = this._detectBoundaries(events, sequenceType);
      if (!boundaries) {
        return { sequence_id: null, items: 0, reason: "no pattern detected" };
      }

      // Create sequence record
      const { data: seq, error: sErr } = await this.db
        .from("event_sequences")
        .insert({
          patient_identifier: patientId,
          sequence_type: sequenceType,
          started_at: boundaries.start,
          ended_at: boundaries.end
        })
        .select("sequence_id")
        .single();

      if (sErr) {
        console.error("[temporalGraph] buildSequence:", sErr.message);
        return { sequence_id: null, items: 0 };
      }

      // Link events to sequence with ordering and deltas
      const items = [];
      const startTime = new Date(boundaries.start).getTime();
      const seqEvents = events.filter(e => {
        const t = new Date(e.occurred_at).getTime();
        return t >= startTime && t <= new Date(boundaries.end).getTime();
      });

      for (let i = 0; i < seqEvents.length; i++) {
        const evt = seqEvents[i];
        const delta = Math.round((new Date(evt.occurred_at).getTime() - startTime) / 1000);
        items.push({
          sequence_id: seq.sequence_id,
          event_id: evt.event_id,
          item_order: i + 1,
          delta_seconds: delta
        });
      }

      if (items.length > 0) {
        const { error: iErr } = await this.db.from("event_sequence_items").insert(items);
        if (iErr) console.error("[temporalGraph] items insert:", iErr.message);
      }

      return { sequence_id: seq.sequence_id, items: items.length };
    }

    /**
     * Detect causal chains between events.
     * Uses temporal correlation + state change analysis.
     */
    async detectCausalChain(patientId) {
      const { data: events, error } = await this.db
        .from("clinical_events")
        .select("event_id, event_type, occurred_at, state_snapshot, severity")
        .eq("patient_identifier", patientId)
        .order("occurred_at", { ascending: true })
        .limit(100);

      if (error || !events || events.length < 2) return [];

      const chains = [];
      const eventPairs = this._findCandidatePairs(events);

      for (const pair of eventPairs) {
        const causality = this._assessCausality(pair.cause, pair.effect);
        if (causality.confidence > 0.3) {
          const { data, error: cErr } = await this.db
            .from("causal_chains")
            .insert({
              patient_identifier: patientId,
              cause_event_id: pair.cause.event_id,
              effect_event_id: pair.effect.event_id,
              causality_type: causality.type,
              confidence: causality.confidence
            })
            .select("chain_id")
            .single();

          if (!cErr && data) {
            chains.push({
              chain_id: data.chain_id,
              cause: pair.cause.event_type,
              effect: pair.effect.event_type,
              type: causality.type,
              confidence: causality.confidence
            });
          }
        }
      }

      return chains;
    }

    /**
     * Query the evolution of a specific state variable over a time window.
     * Returns a time series: [{ timestamp, value, delta }]
     */
    async queryEvolution(patientId, stateVariable, windowStr) {
      const windowSec = WINDOWS[windowStr] || 86400;
      const since = new Date(Date.now() - windowSec * 1000).toISOString();

      const { data: events, error } = await this.db
        .from("clinical_events")
        .select("occurred_at, state_snapshot")
        .eq("patient_identifier", patientId)
        .gte("occurred_at", since)
        .order("occurred_at", { ascending: true })
        .limit(500);

      if (error || !events) return [];

      const series = [];
      let prevValue = null;

      for (const evt of events) {
        if (!evt.state_snapshot) continue;
        const value = evt.state_snapshot[stateVariable];
        if (value == null) continue;

        const delta = prevValue != null ? value - prevValue : 0;
        series.push({
          timestamp: evt.occurred_at,
          value: value,
          delta: delta,
          trend: delta > 0.01 ? "increasing" : delta < -0.01 ? "decreasing" : "stable"
        });
        prevValue = value;
      }

      return series;
    }

    /**
     * Detect deterioration patterns in real-time.
     * Returns alert if a deterioration sequence is forming.
     */
    async detectDeterioration(patientId) {
      const series = await this.queryEvolution(patientId, null, "6h");
      if (series.length < 3) return { alert: false, reason: "insufficient data" };

      // Check for consistent decline across multiple state variables
      let declineCount = 0;
      let totalVars = 0;

      const stateVars = ["volemia", "contractilidade", "oxigenacao", "funcaoRenal"];
      for (const v of stateVars) {
        const varSeries = await this.queryEvolution(patientId, v, "6h");
        if (varSeries.length < 2) continue;
        totalVars++;
        const recent = varSeries.slice(-3);
        const declining = recent.every((p, i) => i === 0 || p.value <= recent[i - 1].value + 0.02);
        if (declining) declineCount++;
      }

      const alert = declineCount >= 2 && totalVars >= 3;
      return {
        alert: alert,
        decline_count: declineCount,
        total_vars: totalVars,
        severity: alert ? "warning" : "normal",
        recommendation: alert ? "Consider escalating assessment — multi-variable decline detected" : null
      };
    }

    // ═════════════════════════════════════════════════════════
    // PRIVATE
    // ═════════════════════════════════════════════════════════

    _detectBoundaries(events, type) {
      if (events.length < 2) return null;

      const first = events[0];
      const last = events[events.length - 1];

      switch (type) {
        case "deterioration": {
          // Find a window where severity increases
          for (let i = 0; i < events.length - 2; i++) {
            if (events[i].severity === "routine" &&
                events[i + 2] && events[i + 2].severity === "urgent") {
              return { start: events[i].occurred_at, end: events[i + 2].occurred_at };
            }
          }
          return null;
        }
        case "recovery": {
          // Find a window where severity decreases
          for (let i = 0; i < events.length - 2; i++) {
            if (events[i].severity === "urgent" &&
                events[i + 2] && events[i + 2].severity === "routine") {
              return { start: events[i].occurred_at, end: events[i + 2].occurred_at };
            }
          }
          return null;
        }
        case "crisis": {
          // Find a window with emergency severity
          const crisis = events.find(e => e.severity === "emergency");
          if (crisis) {
            const idx = events.indexOf(crisis);
            const start = events[Math.max(0, idx - 1)];
            const end = events[Math.min(events.length - 1, idx + 1)];
            return { start: start.occurred_at, end: end.occurred_at };
          }
          return null;
        }
        case "stabilization": {
          // Find a window of stable routine events
          let runStart = null;
          let runLength = 0;
          for (const evt of events) {
            if (evt.severity === "routine") {
              if (!runStart) runStart = evt;
              runLength++;
            } else {
              if (runLength >= 3) {
                return { start: runStart.occurred_at, end: events[events.indexOf(evt) - 1].occurred_at };
              }
              runStart = null;
              runLength = 0;
            }
          }
          if (runLength >= 3) {
            return { start: runStart.occurred_at, end: last.occurred_at };
          }
          return null;
        }
        case "oscillation": {
          // Find alternating severity
          let alternating = 0;
          for (let i = 1; i < events.length; i++) {
            if (events[i].severity !== events[i - 1].severity) alternating++;
          }
          if (alternating >= 3) {
            return { start: first.occurred_at, end: last.occurred_at };
          }
          return null;
        }
        default:
          return { start: first.occurred_at, end: last.occurred_at };
      }
    }

    _findCandidatePairs(events) {
      const pairs = [];
      for (let i = 0; i < events.length; i++) {
        for (let j = i + 1; j < Math.min(i + 5, events.length); j++) {
          const timeGap = (new Date(events[j].occurred_at) - new Date(events[i].occurred_at)) / 1000;
          if (timeGap > 0 && timeGap < 3600) { // within 1 hour
            pairs.push({ cause: events[i], effect: events[j], timeGap });
          }
        }
      }
      return pairs;
    }

    _assessCausality(cause, effect) {
      // Simple heuristic: if cause is an intervention and effect is a state change
      const interventionTypes = ["intervention", "medication", "procedure"];
      const isIntervention = interventionTypes.indexOf(cause.event_type) !== -1;

      // Check state change in effect
      let stateChanged = false;
      if (cause.state_snapshot && effect.state_snapshot) {
        for (const key of Object.keys(cause.state_snapshot)) {
          if (effect.state_snapshot[key] != null) {
            const diff = Math.abs(effect.state_snapshot[key] - cause.state_snapshot[key]);
            if (diff > 0.05) stateChanged = true;
          }
        }
      }

      let type = "temporal_correlation";
      let confidence = 0.2;

      if (isIntervention && stateChanged) {
        type = "direct";
        confidence = 0.7;
      } else if (isIntervention) {
        type = "contributing";
        confidence = 0.4;
      } else if (stateChanged) {
        type = "contributing";
        confidence = 0.35;
      }

      return { type, confidence };
    }
  }

  global.TemporalGraph = TemporalGraph;
  global.SEQUENCE_TYPES = SEQUENCE_TYPES;
  global.CAUSALITY_TYPES = CAUSALITY_TYPES;
  global.WINDOWS = WINDOWS;

})(typeof module !== "undefined" ? module.exports : (this || window));
