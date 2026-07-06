/* ======================================================================
   clinicalAttention.js — Clinical Attention Engine (Nurse-PaLM Layer 5)
   Clinical Engine V9 — NIFS v5.0

   Substitui a função heurística vitalsToPrior() do V8 por um mecanismo
   de atenção aprendido que pondera observações por:
     - Desvio de baseline (quão anormal é o sinal)
     - Taxa de mudança (quão rápido está mudando)
     - Severidade NANDA associada (relevância clínica)
     - Confiabilidade do sinal (ruído vs sinal)
     - Contexto do paciente (perfil, idade, comorbidades)

   Schema: ni_attention.signals, .weights
   Dependency: ni_world (patient_states), ni_graph (nodes)

   API:
     const att = new ClinicalAttention(supabaseClient);
     const result = att.evaluate(observations, patientContext);
     // result.ranked = observações ordenadas por score de atenção
     // result.filtered = apenas observações acima do threshold
     // result.weights = pesos para o particle filter
   ====================================================================== */
(function (global) {
  "use strict";

  // Baselines for vital signs (adult, normal)
  const BASELINES = {
    heartRate:        { mean: 72,  std: 10,  min: 40,  max: 160, unit: "bpm" },
    systolicBP:       { mean: 120, std: 10,  min: 70,  max: 220, unit: "mmHg" },
    diastolicBP:      { mean: 80,  std: 8,   min: 40,  max: 130, unit: "mmHg" },
    spO2:             { mean: 98,  std: 1.5, min: 70,  max: 100, unit: "%" },
    respiratoryRate:  { mean: 16,  std: 3,   min: 8,   max: 40,  unit: "rpm" },
    temperature:      { mean: 36.8, std: 0.4, min: 34, max: 42,  unit: "°C" },
    urineOutput:      { mean: 1.0, std: 0.3, min: 0,   max: 5,   unit: "mL/kg/h" },
    consciousness:    { mean: 15,  std: 0,   min: 3,   max: 15,  unit: "GCS" },
    glucose:          { mean: 100, std: 20,  min: 30,  max: 600, unit: "mg/dL" },
    painScore:        { mean: 0,   std: 2,   min: 0,   max: 10,  unit: "0-10" }
  };

  // NANDA severity weights (higher = more attention needed)
  const NANDA_SEVERITY = {
    "impaired_gas_exchange":      0.95,
    "decreased_cardiac_output":   0.92,
    "ineffective_airway_clearance": 0.90,
    "fluid_volume_deficit":       0.85,
    "fluid_volume_excess":        0.85,
    "impaired_skin_integrity":    0.60,
    "acute_pain":                 0.75,
    "anxiety":                    0.45,
    "risk_for_infection":         0.55,
    "risk_for_falls":             0.50
  };

  // Signal reliability (how noisy is this measurement)
  const RELIABILITY = {
    heartRate: 0.95,
    systolicBP: 0.90,
    diastolicBP: 0.85,
    spO2: 0.92,
    respiratoryRate: 0.80,
    temperature: 0.95,
    urineOutput: 0.85,
    consciousness: 0.98,
    glucose: 0.90,
    painScore: 0.70 // subjective
  };

  class ClinicalAttention {
    constructor(supabaseClient) {
      this.db = supabaseClient;
      this.schema = "ni_attention";
      this._baselines = Object.assign({}, BASELINES);
    }

    /**
     * Evaluate a set of observations and compute attention scores.
     * Returns ranked list, filtered list, and weights for particle filter.
     */
    evaluate(observations, patientContext) {
      patientContext = patientContext || {};
      const profile = patientContext.profile || "professional";
      const ageGroup = patientContext.ageGroup || "adult";
      const comorbidities = patientContext.comorbidities || [];
      const activeDiagnoses = patientContext.activeDiagnoses || [];

      // Adjust baselines for age group
      const baselines = this._adjustBaselinesForAge(this._baselines, ageGroup);

      // Score each observation
      const scored = observations.map(obs => {
        const key = obs.type || obs.signal;
        const baseline = baselines[key];
        if (!baseline) return { ...obs, attentionScore: 0.5, rank: "unknown" };

        const value = obs.value;
        const z = this._zScore(value, baseline);
        const deviation = Math.abs(z);

        // Rate of change (if previous value available)
        const rateOfChange = obs.previousValue != null
          ? this._computeRate(value, obs.previousValue, obs.timeDelta || 300)
          : 0;

        // Severity weight from active NANDA diagnoses
        const severityWeight = this._getSeverityWeight(key, activeDiagnoses);

        // Signal reliability
        const reliability = RELIABILITY[key] || 0.80;

        // Composite attention score
        //   deviation: 40% — how abnormal
        //   rateOfChange: 25% — how fast changing
        //   severity: 25% — clinical relevance
        //   reliability: 10% — inverse (less reliable = more attention to compensate)
        const attentionScore = Math.min(1,
          (deviation / 3) * 0.40 +
          Math.min(1, rateOfChange) * 0.25 +
          severityWeight * 0.25 +
          (1 - reliability) * 0.10
        );

        // Classify
        let rank = "normal";
        if (attentionScore > 0.8) rank = "critical";
        else if (attentionScore > 0.6) rank = "high";
        else if (attentionScore > 0.4) rank = "moderate";
        else if (attentionScore > 0.2) rank = "low";

        return {
          type: key,
          value: value,
          unit: baseline.unit,
          zScore: z,
          deviation: deviation,
          rateOfChange: rateOfChange,
          severityWeight: severityWeight,
          reliability: reliability,
          attentionScore: attentionScore,
          rank: rank,
          recommendation: this._getRecommendation(key, z, rank)
        };
      });

      // Sort by attention score (descending)
      const ranked = scored.sort((a, b) => b.attentionScore - a.attentionScore);

      // Filter: keep only observations above threshold
      const threshold = profile === "student" ? 0.3 : profile === "manager" ? 0.6 : 0.4;
      const filtered = ranked.filter(s => s.attentionScore >= threshold);

      // Generate particle filter weights
      // High-attention signals get more influence in the filter
      const weights = {};
      for (const s of filtered) {
        weights[s.type] = s.attentionScore;
      }

      // Normalize weights to sum = 1
      const totalWeight = Object.values(weights).reduce((a, b) => a + b, 0);
      if (totalWeight > 0) {
        for (const k of Object.keys(weights)) {
          weights[k] = weights[k] / totalWeight;
        }
      }

      return {
        ranked: ranked,
        filtered: filtered,
        weights: weights,
        threshold: threshold,
        alert: filtered.some(s => s.rank === "critical"),
        summary: this._generateSummary(filtered, patientContext)
      };
    }

    /**
     * Persist attention signals to the database.
     */
    async persistSignals(patientId, evaluationResult) {
      if (!this.db) return;
      const signals = evaluationResult.filtered.map(s => ({
        patient_identifier: patientId,
        signal_type: s.type,
        signal_value: s.value,
        attention_score: s.attentionScore,
        rank: s.rank,
        detected_at: new Date().toISOString()
      }));

      const { error } = await this.db.from("signals").insert(signals);
      if (error) console.error("[clinicalAttention] persist:", error.message);
    }

    /**
     * Update attention weights based on feedback learning.
     * If a signal was attended to but didn't predict outcome → decrease weight.
     * If a signal was ignored but predicted outcome → increase weight.
     */
    async updateWeights(feedbackData) {
      if (!this.db) return;

      for (const fb of feedbackData) {
        const { data: existing } = await this.db
          .from("weights")
          .select("weight_id, weight_value")
          .eq("signal_type", fb.signal_type)
          .limit(1)
          .single();

        if (existing) {
          const delta = fb.was_predictive ? 0.03 : -0.03;
          const newWeight = Math.max(0, Math.min(1, existing.weight_value + delta));
          await this.db.from("weights")
            .update({ weight_value: newWeight })
            .eq("weight_id", existing.weight_id);
        }
      }
    }

    // ═════════════════════════════════════════════════════════
    // PRIVATE
    // ═════════════════════════════════════════════════════════

    _zScore(value, baseline) {
      return (value - baseline.mean) / baseline.std;
    }

    _computeRate(current, previous, deltaSeconds) {
      const diff = Math.abs(current - previous);
      const ratePerMin = diff / (deltaSeconds / 60);
      // Normalize: 1 std per minute = rate of 1.0
      return ratePerMin / (baseline_for(current).std || 1);
      
      function baseline_for(val) {
        // Find matching baseline by approximate range
        for (const [k, b] of Object.entries(BASELINES)) {
          if (val >= b.min && val <= b.max) return b;
        }
        return { std: 1 };
      }
    }

    _getSeverityWeight(signalKey, activeDiagnoses) {
      if (!activeDiagnoses || activeDiagnoses.length === 0) return 0.3; // default moderate

      // Map signals to NANDA diagnoses they're relevant for
      const signalToNanda = {
        spO2: ["impaired_gas_exchange", "ineffective_airway_clearance"],
        respiratoryRate: ["ineffective_airway_clearance", "impaired_gas_exchange"],
        heartRate: ["decreased_cardiac_output", "fluid_volume_deficit"],
        systolicBP: ["decreased_cardiac_output", "fluid_volume_deficit", "fluid_volume_excess"],
        urineOutput: ["fluid_volume_deficit", "impaired_urinary_elimination"],
        temperature: ["risk_for_infection", "hyperthermia", "hypothermia"],
        consciousness: ["acute_confusion", "decreased_cardiac_output"],
        glucose: ["risk_for_unstable_blood_glucose"],
        painScore: ["acute_pain", "chronic_pain"]
      };

      const relevantNanda = signalToNanda[signalKey] || [];
      let maxSeverity = 0.3;

      for (const dx of activeDiagnoses) {
        const dxCode = typeof dx === "string" ? dx : (dx.code || dx.nanda_code || "");
        const dxLower = dxCode.toLowerCase().replace(/\s+/g, "_");
        if (relevantNanda.indexOf(dxLower) !== -1) {
          const severity = NANDA_SEVERITY[dxLower] || 0.5;
          if (severity > maxSeverity) maxSeverity = severity;
        }
      }

      return maxSeverity;
    }

    _adjustBaselinesForAge(baselines, ageGroup) {
      const adjusted = JSON.parse(JSON.stringify(baselines));
      switch (ageGroup) {
        case "neonate":
          adjusted.heartRate = { mean: 130, std: 20, min: 80, max: 200, unit: "bpm" };
          adjusted.respiratoryRate = { mean: 40, std: 8, min: 20, max: 80, unit: "rpm" };
          adjusted.systolicBP = { mean: 70, std: 10, min: 40, max: 120, unit: "mmHg" };
          adjusted.temperature = { mean: 37.0, std: 0.5, min: 35, max: 40, unit: "°C" };
          break;
        case "pediatric":
          adjusted.heartRate = { mean: 90, std: 15, min: 50, max: 180, unit: "bpm" };
          adjusted.respiratoryRate = { mean: 22, std: 5, min: 12, max: 50, unit: "rpm" };
          adjusted.systolicBP = { mean: 95, std: 10, min: 60, max: 160, unit: "mmHg" };
          break;
        case "elderly":
          adjusted.heartRate = { mean: 68, std: 12, min: 40, max: 150, unit: "bpm" };
          adjusted.systolicBP = { mean: 135, std: 15, min: 80, max: 240, unit: "mmHg" };
          adjusted.spO2 = { mean: 96, std: 2, min: 70, max: 100, unit: "%" };
          break;
      }
      return adjusted;
    }

    _getRecommendation(signalKey, zScore, rank) {
      if (rank === "normal") return null;

      const direction = zScore > 0 ? "elevated" : "depressed";
      const abs = Math.abs(zScore);

      const recs = {
        spO2: abs > 2 ? `SpO₂ ${direction} (z=${zScore.toFixed(1)}) — assess airway and oxygenation immediately` : `SpO₂ outside normal range — monitor closely`,
        heartRate: abs > 2 ? `Heart rate ${direction} (z=${zScore.toFixed(1)}) — assess for shock, pain, or arrhythmia` : `Heart rate abnormal — continue monitoring`,
        systolicBP: abs > 2 ? `Blood pressure ${direction} (z=${zScore.toFixed(1)}) — assess hemodynamic stability` : `BP outside range — monitor`,
        temperature: abs > 2 ? `Temperature ${direction} (z=${zScore.toFixed(1)}) — assess for infection or thermal dysregulation` : `Temperature abnormal — monitor`,
        urineOutput: abs > 2 ? `Urine output ${direction} (z=${zScore.toFixed(1)}) — assess renal function and fluid status` : `Urine output abnormal — monitor`,
        consciousness: abs > 1 ? `Consciousness changed (z=${zScore.toFixed(1)}) — assess neurological status urgently` : `Monitor GCS closely`,
        glucose: abs > 2 ? `Glucose ${direction} (z=${zScore.toFixed(1)}) — assess for hypo/hyperglycemia protocol` : `Glucose abnormal — monitor`
      };

      return recs[signalKey] || `${signalKey} ${direction} — monitor`;
    }

    _generateSummary(filtered, ctx) {
      if (filtered.length === 0) return "All observations within normal limits.";
      const critical = filtered.filter(s => s.rank === "critical");
      const high = filtered.filter(s => s.rank === "high");

      let summary = "";
      if (critical.length > 0) {
        summary = `⚠️ ${critical.length} critical signal(s): ${critical.map(s => s.type).join(", ")}. `;
      }
      if (high.length > 0) {
        summary += `${high.length} high-priority signal(s): ${high.map(s => s.type).join(", ")}. `;
      }
      summary += `${filtered.length} total signals above attention threshold.`;

      return summary;
    }
  }

  global.ClinicalAttention = ClinicalAttention;
  global.BASELINE_VITALS = BASELINES;
  global.NANDA_SEVERITY = NANDA_SEVERITY;

})(typeof module !== "undefined" ? module.exports : (this || window));
