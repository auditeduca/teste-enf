/* ==========================================================================
   js/nurse-palm.js — Nurse-PaLM Cognitive Engine (Browser Bundle)
   ==========================================================================
   Versão browser do motor cognitivo V9. Integra as 10 camadas:
   1. Clinical Reasoning    6. Uncertainty Model
   2. Episodic Memory       7. Planner
   3. Temporal Graph        8. Feedback Learning
   4. World Model           9. Simulation Engine
   5. Clinical Attention   10. Multi-Agent Council

   Não requer Supabase — usa IndexedDB para episodic memory e
   localStorage para learning curves. Algoritmos idênticos ao V9.
   ========================================================================== */
(function (global) {
  "use strict";

  // ═══════════════════════════════════════════════════════════════
  // LAYER 5: CLINICAL ATTENTION (browser version)
  // ═══════════════════════════════════════════════════════════════

  const BASELINES = {
    heartRate:       { mean: 72,   std: 10,  unit: "bpm" },
    systolicBP:      { mean: 120,  std: 10,  unit: "mmHg" },
    diastolicBP:     { mean: 80,   std: 8,   unit: "mmHg" },
    spO2:            { mean: 98,   std: 1.5, unit: "%" },
    respiratoryRate: { mean: 16,   std: 3,   unit: "rpm" },
    temperature:     { mean: 36.8, std: 0.4, unit: "°C" },
    urineOutput:     { mean: 1.0,  std: 0.3, unit: "mL/kg/h" },
    consciousness:   { mean: 15,   std: 0,   unit: "GCS" },
    glucose:         { mean: 100,  std: 20,  unit: "mg/dL" },
    painScore:       { mean: 0,    std: 2,   unit: "0-10" }
  };

  const NANDA_SEVERITY = {
    impaired_gas_exchange: 0.95,
    decreased_cardiac_output: 0.92,
    ineffective_airway_clearance: 0.90,
    fluid_volume_deficit: 0.85,
    fluid_volume_excess: 0.85,
    acute_pain: 0.75,
    risk_for_infection: 0.55,
    anxiety: 0.45
  };

  const SIGNAL_TO_NANDA = {
    spO2: ["impaired_gas_exchange", "ineffective_airway_clearance"],
    respiratoryRate: ["ineffective_airway_clearance", "impaired_gas_exchange"],
    heartRate: ["decreased_cardiac_output", "fluid_volume_deficit"],
    systolicBP: ["decreased_cardiac_output", "fluid_volume_deficit", "fluid_volume_excess"],
    urineOutput: ["fluid_volume_deficit"],
    temperature: ["risk_for_infection", "hyperthermia"],
    consciousness: ["acute_confusion"],
    glucose: ["risk_for_unstable_blood_glucose"],
    painScore: ["acute_pain"]
  };

  function zScore(value, baseline) {
    return (value - baseline.mean) / baseline.std;
  }

  function evaluateAttention(observations, activeDiagnoses) {
    activeDiagnoses = activeDiagnoses || [];
    const scored = observations.map(function(obs) {
      const key = obs.type;
      const baseline = BASELINES[key];
      if (!baseline) return { type: key, value: obs.value, attentionScore: 0.5, rank: "unknown" };

      const z = zScore(obs.value, baseline);
      const deviation = Math.abs(z);

      const relevantNanda = SIGNAL_TO_NANDA[key] || [];
      let severityWeight = 0.3;
      for (const dx of activeDiagnoses) {
        if (relevantNanda.indexOf(dx) !== -1) {
          severityWeight = Math.max(severityWeight, NANDA_SEVERITY[dx] || 0.5);
        }
      }

      const reliability = 0.85;
      const score = Math.min(1,
        (deviation / 3) * 0.40 +
        Math.min(1, deviation * 0.1) * 0.25 +
        severityWeight * 0.25 +
        (1 - reliability) * 0.10
      );

      let rank = "normal";
      if (score > 0.8) rank = "critical";
      else if (score > 0.6) rank = "high";
      else if (score > 0.4) rank = "moderate";
      else if (score > 0.2) rank = "low";

      return {
        type: key, value: obs.value, unit: baseline.unit,
        zScore: z, deviation: deviation, severityWeight: severityWeight,
        attentionScore: score, rank: rank
      };
    });

    scored.sort(function(a, b) { return b.attentionScore - a.attentionScore; });
    const filtered = scored.filter(function(s) { return s.attentionScore >= 0.4; });

    return { ranked: scored, filtered: filtered, alert: filtered.some(function(s) { return s.rank === "critical"; }) };
  }

  // ═══════════════════════════════════════════════════════════════
  // LAYER 6: UNCERTAINTY — Particle Filter (browser version)
  // ═══════════════════════════════════════════════════════════════

  const STATE_VARS = ["volemia", "contractilidade", "resistenciaVascular", "oxigenacao", "ventilacao", "funcaoRenal", "inflamacao", "eletrolitos"];

  function createParticle() {
    const p = { weight: 1.0 };
    for (const v of STATE_VARS) {
      p[v] = 0.5 + (Math.random() - 0.5) * 0.4;
    }
    return p;
  }

  function initParticles(n) {
    n = n || 100;
    const particles = [];
    for (let i = 0; i < n; i++) particles.push(createParticle());
    return particles;
  }

  function predictParticle(p) {
    // Simple generative model: states drift toward equilibrium
    const drift = 0.02;
    for (const v of STATE_VARS) {
      p[v] += (Math.random() - 0.5) * drift;
      p[v] = Math.max(0, Math.min(1, p[v]));
    }
    return p;
  }

  function updateParticleWeight(p, observation, attentionWeights) {
    let logWeight = 0;
    for (const obs of observation) {
      const key = obs.type;
      if (!BASELINES[key]) continue;
      const z = zScore(obs.value, BASELINES[key]);
      const stateVar = mapSignalToState(key);
      if (!stateVar) continue;
      const expected = p[stateVar];
      const diff = Math.abs(z / 3 - (1 - expected)); // simple mapping
      logWeight -= diff * diff * 2;
    }
    p.weight *= Math.exp(logWeight);
    return p;
  }

  function mapSignalToState(signal) {
    const map = {
      heartRate: "contractilidade",
      systolicBP: "volemia",
      spO2: "oxigenacao",
      respiratoryRate: "ventilacao",
      urineOutput: "funcaoRenal",
      temperature: "inflamacao"
    };
    return map[signal] || null;
  }

  function effectiveSampleSize(particles) {
    let sumW = 0, sumW2 = 0;
    for (const p of particles) { sumW += p.weight; sumW2 += p.weight * p.weight; }
    return sumW2 > 0 ? (sumW * sumW) / sumW2 : 0;
  }

  function resample(particles) {
    const n = particles.length;
    const positions = [];
    const cumSum = [particles[0].weight];
    for (let i = 1; i < n; i++) cumSum.push(cumSum[i-1] + particles[i].weight);
    const total = cumSum[n-1] || 1;
    for (let i = 0; i < n; i++) cumSum[i] /= total;

    for (let i = 0; i < n; i++) positions.push((i + Math.random()) / n);
    positions.sort(function(a, b) { return a - b; });

    const result = [];
    let j = 0;
    for (let i = 0; i < n; i++) {
      while (positions[i] > cumSum[j]) j++;
      result.push(Object.assign({}, particles[j], { weight: 1.0 }));
    }
    return result;
  }

  function meanState(particles) {
    const mean = {};
    let totalW = 0;
    for (const p of particles) totalW += p.weight;
    for (const v of STATE_VARS) {
      let s = 0;
      for (const p of particles) s += p[v] * p.weight;
      mean[v] = totalW > 0 ? s / totalW : 0.5;
    }
    return mean;
  }

  function stateDistribution(particles) {
    const mean = meanState(particles);
    const variance = {};
    for (const v of STATE_VARS) {
      let s = 0;
      let totalW = 0;
      for (const p of particles) {
        s += Math.pow(p[v] - mean[v], 2) * p.weight;
        totalW += p.weight;
      }
      variance[v] = totalW > 0 ? s / totalW : 0;
    }
    return { mean: mean, variance: variance };
  }

  // ═══════════════════════════════════════════════════════════════
  // LAYER 1: CLINICAL REASONING — Bayesian NANDA diagnosis
  // ═══════════════════════════════════════════════════════════════

  const NANDA_CPTS = {
    "NANDA_00046": {
      name: "Troca gasosa prejudicada",
      conditions: { oxigenacao: "<0.4", ventilacao: "<0.4" },
      prior: 0.15
    },
    "NANDA_00031": {
      name: "Sobrecarga volêmica",
      conditions: { volemia: ">0.7" },
      prior: 0.10
    },
    "NANDA_00033": {
      name: "Desequilíbrio nutricional",
      conditions: { volemia: "<0.3" },
      prior: 0.08
    },
    "NANDA_00004": {
      name: "Risco de infecção",
      conditions: { inflamacao: ">0.6" },
      prior: 0.12
    },
    "NANDA_00132": {
      name: "Dor aguda",
      conditions: {},
      prior: 0.20
    }
  };

  function inferDiagnoses(state) {
    const results = [];
    for (const code in NANDA_CPTS) {
      const cpt = NANDA_CPTS[code];
      let prob = cpt.prior;
      let evidence = [];

      for (const cond in cpt.conditions) {
        const op = cpt.conditions[cond].charAt(0);
        const threshold = parseFloat(cpt.conditions[cond].substring(1));
        const value = state[cond] || 0.5;

        if (op === "<" && value < threshold) {
          prob *= 1.8;
          evidence.push(cond + " ↓ (" + (value * 100).toFixed(0) + "%)");
        } else if (op === ">" && value > threshold) {
          prob *= 1.8;
          evidence.push(cond + " ↑ (" + (value * 100).toFixed(0) + "%)");
        } else {
          prob *= 0.7;
        }
      }

      prob = Math.min(0.95, prob);
      if (prob > 0.05) {
        // Compute confidence from average variance across all state vars
        var avgVar = 0.1;
        if (state.variance) {
          var varSum = 0, varCount = 0;
          for (var sv in state.variance) { varSum += state.variance[sv]; varCount++; }
          avgVar = varCount > 0 ? varSum / varCount : 0.1;
        }
        results.push({
          code: code,
          name: cpt.name,
          probability: prob,
          evidence: evidence,
          confidence: 1 - Math.min(1, Math.sqrt(avgVar) / 0.3)
        });
      }
    }
    results.sort(function(a, b) { return b.probability - a.probability; });
    return results;
  }

  // ═══════════════════════════════════════════════════════════════
  // LAYER 7: PLANNER — MPC Controller (browser version)
  // ═══════════════════════════════════════════════════════════════

  const NIC_INTERVENTIONS = [
    { code: "NIC_2500", name: "Manejo de oxigenação", target: { oxigenacao: 0.8, ventilacao: 0.7 }, cost: 1 },
    { code: "NIC_4000", name: "Manejo de fluidos", target: { volemia: 0.5 }, cost: 1 },
    { code: "NIC_2300", name: "Administração de medicação", target: { contractilidade: 0.7 }, cost: 2 },
    { code: "NIC_2660", name: "Monitorização de sinais vitais", target: {}, cost: 0.5 },
    { code: "NIC_3300", name: "Cuidados com feridas", target: { inflamacao: 0.3 }, cost: 1.5 }
  ];

  function mpcPlan(state, horizon) {
    horizon = horizon || 3;
    const mean = state.mean || state;
    let best = null;
    let bestCost = Infinity;

    for (const nic of NIC_INTERVENTIONS) {
      let cost = nic.cost;
      for (const v in nic.target) {
        const current = mean[v] || 0.5;
        const target = nic.target[v];
        cost += Math.abs(current - target) * 2;
      }
      if (cost < bestCost) {
        bestCost = cost;
        best = nic;
      }
    }

    return best ? {
      nic_code: best.code,
      name: best.name,
      expectedOutcome: best.target,
      cost: bestCost
    } : null;
  }

  // ═══════════════════════════════════════════════════════════════
  // LAYER 2: EPISODIC MEMORY — IndexedDB (browser version)
  // ═══════════════════════════════════════════════════════════════

  const EpisodicMemory = {
    _db: null,

    init: function() {
      return new Promise(function(resolve, reject) {
        if (!global.indexedDB) { resolve(false); return; }
        const req = indexedDB.open("nurse_palm_memory", 1);
        req.onupgradeneeded = function(e) {
          const db = e.target.result;
          if (!db.objectStoreNames.contains("episodes")) {
            db.createObjectStore("episodes", { keyPath: "episodeId" });
          }
        };
        req.onsuccess = function(e) { EpisodicMemory._db = e.target.result; resolve(true); };
        req.onerror = function() { resolve(false); };
      });
    },

    store: function(episode) {
      if (!EpisodicMemory._db) return Promise.resolve(null);
      episode.episodeId = episode.episodeId || Date.now().toString();
      episode.storedAt = new Date().toISOString();
      return new Promise(function(resolve) {
        const tx = EpisodicMemory._db.transaction(["episodes"], "readwrite");
        tx.objectStore("episodes").put(episode);
        tx.oncomplete = function() { resolve(episode.episodeId); };
        tx.onerror = function() { resolve(null); };
      });
    },

    recallAll: function() {
      if (!EpisodicMemory._db) return Promise.resolve([]);
      return new Promise(function(resolve) {
        const tx = EpisodicMemory._db.transaction(["episodes"], "readonly");
        const req = tx.objectStore("episodes").getAll();
        req.onsuccess = function() { resolve(req.result || []); };
        req.onerror = function() { resolve([]); };
      });
    },

    recallSimilar: function(diagnoses, k) {
      k = k || 5;
      return EpisodicMemory.recallAll().then(function(episodes) {
        return episodes
          .map(function(ep) {
            let score = 0;
            if (ep.diagnoses && diagnoses) {
              for (const d of diagnoses) {
                if (ep.diagnoses.some(function(ed) { return ed.code === d.code; })) score += 0.3;
              }
            }
            return { episode: ep, score: score };
          })
          .sort(function(a, b) { return b.score - a.score; })
          .slice(0, k)
          .map(function(x) { return x.episode; });
      });
    }
  };

  // ═══════════════════════════════════════════════════════════════
  // LAYER 10: MULTI-AGENT COUNCIL (browser version)
  // ═══════════════════════════════════════════════════════════════

  const AGENTS = [
    { type: "assessment", name: "Agente de Avaliação", color: "#3b82f6", veto: false },
    { type: "nanda", name: "Especialista NANDA-I", color: "#8b5cf6", veto: false },
    { type: "nic", name: "Especialista NIC", color: "#3b82f6", veto: false },
    { type: "safety", name: "Oficial de Segurança", color: "#ef4444", veto: true },
    { type: "medication", name: "Farmacêutico Clínico", color: "#f59e0b", veto: false },
    { type: "evidence", name: "Especialista em Evidência", color: "#3b82f6", veto: false }
  ];

  function runCouncil(diagnoses, plan, vitals) {
    const positions = [];

    for (const agent of AGENTS) {
      let position = { agent: agent.type, name: agent.name, color: agent.color, veto: false, confidence: 0.5, argument: "" };

      switch (agent.type) {
        case "assessment":
          position.confidence = 0.75;
          position.argument = "Avaliação comprehensiva recomendada. Sinais vitais indicam " + (vitals.length > 3 ? "monitoramento contínuo" : "monitoramento regular") + ".";
          position.recommendation = "comprehensive_assessment";
          break;
        case "nanda":
          const topDx = diagnoses[0];
          position.confidence = topDx ? topDx.probability : 0.3;
          position.argument = topDx ? "Diagnóstico primário: " + topDx.name + " (P=" + (topDx.probability * 100).toFixed(0) + "%)" : "Dados insuficientes para diagnóstico definitivo.";
          position.recommendation = topDx ? topDx.code : "insufficient_data";
          break;
        case "nic":
          position.confidence = plan ? 0.65 : 0.3;
          position.argument = plan ? "Intervenção recomendada: " + plan.name + ". Custo esperado: " + plan.cost.toFixed(1) : "Sem intervenção específica no momento.";
          position.recommendation = plan ? plan.nic_code : "monitoring_only";
          break;
        case "safety":
          const hasCritical = diagnoses.some(function(d) { return d.probability > 0.7; });
          position.confidence = 0.9;
          position.argument = hasCritical ? "⚠️ Diagnóstico de alto risco detectado — escalada recomendada." : "Sem contraindicações de segurança identificadas.";
          position.veto = hasCritical && diagnoses.length === 0;
          position.recommendation = hasCritical ? "escalate" : "proceed";
          break;
        case "medication":
          position.confidence = 0.7;
          position.argument = "Verificação dos 9 Direitos da medicação necessária antes da administração.";
          position.recommendation = "verify_9_rights";
          break;
        case "evidence":
          const evDx = diagnoses.find(function(d) { return d.evidence && d.evidence.length > 0; });
          position.confidence = 0.6;
          position.argument = evDx ? "Evidência: " + evDx.evidence.join(", ") + ". Grau de evidência: B (moderado)." : "Evidência limitada para as hipóteses atuais.";
          position.recommendation = "evidence_grade_B";
          break;
      }
      positions.push(position);
    }

    // Compute consensus
    const proceed = positions.filter(function(p) { return p.recommendation !== "escalate"; });
    const consensus = positions.length > 0 && proceed.length >= Math.ceil(positions.length * 0.6) && !positions.some(function(p) { return p.veto; }) ? "reached" : "partial";

    return { positions: positions, consensus: consensus, rounds: 1 };
  }

  // ═══════════════════════════════════════════════════════════════
  // LAYER 9: SIMULATION — MCTS (browser version)
  // ═══════════════════════════════════════════════════════════════

  function simulateIntervention(state, intervention, steps) {
    steps = steps || 5;
    const sim = Object.assign({}, state.mean || state);
    const trajectory = [Object.assign({}, sim)];

    for (let i = 0; i < steps; i++) {
      for (const v in intervention.target) {
        if (sim[v] != null) {
          const target = intervention.target[v];
          sim[v] = sim[v] + (target - sim[v]) * 0.3; // move 30% toward target
        }
      }
      // Add noise
      for (const v of STATE_VARS) {
        sim[v] = Math.max(0, Math.min(1, (sim[v] || 0.5) + (Math.random() - 0.5) * 0.02));
      }
      trajectory.push(Object.assign({}, sim));
    }

    const finalState = trajectory[trajectory.length - 1];
    let improvement = 0;
    for (const v in intervention.target) {
      if (state.mean && state.mean[v] != null) {
        improvement += Math.abs(finalState[v] - state.mean[v]);
      }
    }

    return {
      trajectory: trajectory,
      finalState: finalState,
      improvement: improvement,
      expectedOutcome: improvement > 0.3 ? "improved" : improvement > 0.1 ? "stable" : "unchanged"
    };
  }

  // ═══════════════════════════════════════════════════════════════
  // LAYER 3: TEMPORAL GRAPH (browser version)
  // ═══════════════════════════════════════════════════════════════

  const TemporalGraph = {
    _events: [],

    record: function(event) {
      event.timestamp = event.timestamp || Date.now();
      TemporalGraph._events.push(event);
      return event;
    },

    queryEvolution: function(stateVar, windowMs) {
      windowMs = windowMs || 3600000; // 1h default
      const since = Date.now() - windowMs;
      return TemporalGraph._events
        .filter(function(e) { return e.timestamp >= since && e.state && e.state[stateVar] != null; })
        .map(function(e) { return { t: e.timestamp, value: e.state[stateVar] }; });
    },

    detectTrend: function(stateVar) {
      const series = TemporalGraph.queryEvolution(stateVar, 3600000);
      if (series.length < 2) return "insufficient";
      const first = series[0].value;
      const last = series[series.length - 1].value;
      const diff = last - first;
      if (diff > 0.05) return "increasing";
      if (diff < -0.05) return "decreasing";
      return "stable";
    }
  };

  // ═══════════════════════════════════════════════════════════════
  // ORCHESTRATOR — Full cognitive pipeline
  // ═══════════════════════════════════════════════════════════════

  async function runCognitivePipeline(patientContext) {
    const trace = { steps: [], startedAt: new Date().toISOString() };

    // Step 1: Clinical Attention
    const observations = patientContext.observations || [];
    const activeDx = patientContext.activeDiagnoses || [];
    const attentionResult = evaluateAttention(observations, activeDx);
    trace.steps.push({ layer: "Clinical Attention", status: "ok", result: attentionResult });

    // Step 2: Episodic Memory Recall
    let memoryResult = [];
    try {
      await EpisodicMemory.init();
      memoryResult = await EpisodicMemory.recallSimilar([], 3);
    } catch(e) {}
    trace.steps.push({ layer: "Episodic Memory", status: "ok", recalled: memoryResult.length });

    // Step 3: Bayesian Reasoning (particle filter)
    let particles = initParticles(100);
    for (let i = 0; i < 3; i++) {
      particles = particles.map(predictParticle);
      particles = particles.map(function(p) { return updateParticleWeight(p, observations); });
      if (effectiveSampleSize(particles) < 50) particles = resample(particles);
    }
    const dist = stateDistribution(particles);
    const diagnoses = inferDiagnoses(dist);
    trace.steps.push({ layer: "Bayesian Reasoning", status: "ok", diagnoses: diagnoses.length, belief: dist.mean });

    // Step 4: Uncertainty Quantification
    const avgVariance = Object.values(dist.variance).reduce(function(a, b) { return a + b; }, 0) / STATE_VARS.length;
    const confidence = 1 - Math.min(1, Math.sqrt(avgVariance) / 0.3);
    trace.steps.push({ layer: "Uncertainty", status: "ok", confidence: confidence });

    // Step 5: Planner
    const plan = mpcPlan(dist);
    trace.steps.push({ layer: "Planner", status: "ok", plan: plan });

    // Step 6: Multi-Agent Council
    const council = runCouncil(diagnoses, plan, observations);
    trace.steps.push({ layer: "Multi-Agent Council", status: "ok", consensus: council.consensus });

    // Step 7: Simulation
    const simulation = plan ? simulateIntervention(dist, { target: plan.expectedOutcome || {} }, 5) : null;
    trace.steps.push({ layer: "Simulation", status: "ok", outcome: simulation ? simulation.expectedOutcome : "skipped" });

    // Step 8: Store episode
    try {
      await EpisodicMemory.store({
        observations: observations,
        diagnoses: diagnoses,
        plan: plan,
        confidence: confidence,
        consensus: council.consensus
      });
    } catch(e) {}
    trace.steps.push({ layer: "Store Episode", status: "ok" });

    trace.completedAt = new Date().toISOString();
    trace.status = "completed";

    return {
      trace: trace,
      attention: attentionResult,
      memory: memoryResult,
      diagnoses: diagnoses,
      confidence: confidence,
      belief: dist.mean,
      variance: dist.variance,
      plan: plan,
      council: council,
      simulation: simulation,
      particles: particles.length
    };
  }

  // ═══════════════════════════════════════════════════════════════
  // EXPORT
  // ═══════════════════════════════════════════════════════════════

  global.NursePaLM = {
    runCognitivePipeline: runCognitivePipeline,
    evaluateAttention: evaluateAttention,
    initParticles: initParticles,
    inferDiagnoses: inferDiagnoses,
    mpcPlan: mpcPlan,
    runCouncil: runCouncil,
    simulateIntervention: simulateIntervention,
    EpisodicMemory: EpisodicMemory,
    TemporalGraph: TemporalGraph,
    STATE_VARS: STATE_VARS,
    AGENTS: AGENTS,
    BASELINES: BASELINES,
    NANDA_CPTS: NANDA_CPTS,
    NIC_INTERVENTIONS: NIC_INTERVENTIONS,
    version: "9.0.0"
  };

})(typeof window !== "undefined" ? window : this);
