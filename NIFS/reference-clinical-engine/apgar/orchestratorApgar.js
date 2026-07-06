import { APGAR_META, APGAR_SCL } from '../identifiers/apgarEntityCodes.js';
import { computeApgarScore } from './apgarScale.js';
import { interpretApgarScore } from './apgarRules.js';
import { normalizeUserContext, deriveContextModifiers } from './userContext.js';
import {
  buildDiagnosisState,
  getInterventionCandidates,
  buildCausalPath,
  getPrimaryNanda,
} from './apgarGraph.js';
import { runClinicalMcts } from './mctsClinical.js';
import { routeApgarContent } from './contentRouter.js';

/**
 * Pipeline APGAR + RULE + MCTS + User Context (NKOS V9 demo).
 * @param {import('./apgarScale.js').ApgarComponents} components
 * @param {Partial<import('./userContext.js').UserContext>} [userContext]
 */
export function runApgarMCTS(components, userContext = {}) {
  const ctx = normalizeUserContext(userContext);
  const modifiers = deriveContextModifiers(ctx);

  const { score, breakdown } = computeApgarScore(components);
  const ruleLayer = interpretApgarScore(score);
  const diagnoses = buildDiagnosisState(score, ruleLayer.nanda_probabilities);
  const primaryNanda = getPrimaryNanda(diagnoses);
  const candidates = getInterventionCandidates(primaryNanda);

  const mcts = runClinicalMcts({
    apgarScore: score,
    primaryNanda,
    nandaProbability: diagnoses[0]?.probability ?? 0.5,
    candidates,
    modifiers,
    mode: ctx.mode,
  });

  const bestNic = {
    entity_code: mcts.bestAction.entity_code,
    confidence: mcts.bestAction.confidence,
    avg_reward: mcts.bestAction.avgReward,
    rationale: buildRationale(mcts, ctx, score),
  };

  const causalPath = buildCausalPath(primaryNanda, bestNic.entity_code, modifiers.graphDepth);

  const drivers = scoreDrivers(breakdown, score);

  const safety = runSafetyLayer(score, bestNic.entity_code);

  const content = routeApgarContent(ctx, {
    score,
    breakdown,
    clinical_state_pt: ruleLayer.clinical_state_pt,
    diagnoses,
    bestNic,
    causalPath,
  });

  const counterfactual = buildCounterfactual(score, diagnoses[0]?.probability ?? 0.5, mcts);

  return {
    meta: {
      ...APGAR_META,
      user_context: ctx,
      context_modifiers: modifiers,
    },
    timestamp: new Date().toISOString(),
    observation: {
      entity_code: APGAR_SCL,
      score,
      breakdown,
      unit: 'score',
    },
    rule_layer: ruleLayer,
    probabilistic_layer: { diagnoses },
    intervention_layer: {
      selected_nic: bestNic,
      alternatives: mcts.alternatives,
      mcts: {
        simulations: mcts.simulations,
        depth_limit: mcts.depthLimit,
        rollout_table: mcts.rolloutTable,
      },
    },
    outcomes: {
      noc_prediction: predictNoc(bestNic.entity_code, score),
      risk_score: Math.min(1, (10 - score) / 10 * (diagnoses[0]?.probability ?? 0.5)),
      counterfactual,
    },
    explainability: modifiers.showExplainability
      ? {
          drivers,
          causal_path: causalPath,
          decision_trace: 'MCTS clínico + filtro RULE threshold (demo NKOS)',
        }
      : null,
    safety_layer: safety,
    content,
    clinicalSummary: buildSummary(score, ruleLayer, bestNic, ctx),
  };
}

function scoreDrivers(breakdown, score) {
  return Object.entries(breakdown)
    .map(([feature, value]) => ({
      feature,
      impact: (2 - value) / 10,
    }))
    .filter((d) => d.impact > 0.05)
    .sort((a, b) => b.impact - a.impact)
    .slice(0, 3);
}

function buildRationale(mcts, ctx, score) {
  const action = mcts.bestAction.entity_code;
  if (ctx.mode === 'emergency' || ctx.urgency === 'critical') {
    return `Modo emergência: ${action} maximiza redução de risco em profundidade ${mcts.depthLimit} (score=${score}).`;
  }
  if (ctx.mode === 'education') {
    return `Modo educação: ${action} balanceia outcome clínico e compreensão (reward MCTS).`;
  }
  return `MCTS (${mcts.simulations} sim.): ${action} — reward médio ${mcts.bestAction.avgReward.toFixed(3)}.`;
}

function runSafetyLayer(score, nic) {
  const rules = [];
  if (score <= 3) {
    rules.push('APGAR_RULE_SEVERE: reanimação neonatal imediata — escalar equipe');
  }
  if (score <= 6 && nic === 'NIC.NULL') {
    rules.push('BLOCK_OBSERVE: observação isolada inadequada com score ≤6');
  }
  return {
    status: rules.some((r) => r.startsWith('BLOCK')) ? 'blocked' : 'pass',
    rules_triggered: rules,
    blocked_actions: rules.filter((r) => r.startsWith('BLOCK')).map(() => 'NIC.NULL'),
    notes: score <= 3 ? 'Limiar crítico neonatal — fluxo emergency recomendado' : null,
  };
}

function predictNoc(nicCode, score) {
  const baseline = Math.max(30, score * 8);
  return {
    entity_code: 'NOC_0405',
    baseline,
    predicted_6h: Math.min(100, baseline + (nicCode === 'NIC_2380' ? 18 : 8)),
    predicted_24h: Math.min(100, baseline + (nicCode === 'NIC_2380' ? 35 : 15)),
    trend: score <= 6 ? 'improving_with_intervention' : 'stable',
  };
}

function buildCounterfactual(score, nandaP, mcts) {
  const observe = mcts.rolloutTable.find((r) => r.entity_code === 'NIC.NULL');
  const best = mcts.rolloutTable.reduce((a, b) => (b.reward > a.reward ? b : a), { reward: 0 });
  return {
    without_intervention_risk: Math.min(1, ((10 - score) / 10) * nandaP + (observe?.reward < 0 ? 0.15 : 0)),
    with_intervention_risk: Math.min(1, ((10 - score) / 10) * nandaP * 0.55),
    best_vs_observe_delta: best.reward - (observe?.reward ?? 0),
  };
}

function buildSummary(score, ruleLayer, bestNic, ctx) {
  return (
    `[${APGAR_META.engine_id}] APGAR=${score} (${ruleLayer.clinical_state_pt}). ` +
    `Modo=${ctx.mode}/${ctx.device}. NIC=${bestNic.entity_code} ` +
    `(conf ${(bestNic.confidence * 100).toFixed(0)}%). ${APGAR_META.evidence_disclaimer}`
  );
}

export { APGAR_META };
