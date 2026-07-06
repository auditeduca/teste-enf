import { APGAR_NIC } from '../identifiers/apgarEntityCodes.js';

/** Efeito heurístico de cada NIC no score APGAR simulado (demo educacional). */
const NIC_EFFECTS = {
  [APGAR_NIC.AIRWAY_MANAGEMENT]: { scoreDelta: 2.8, riskReduction: 0.35, cost: 0.15 },
  [APGAR_NIC.VITAL_SIGNS_MONITORING]: { scoreDelta: 1.2, riskReduction: 0.18, cost: 0.08 },
  [APGAR_NIC.POSITIONING]: { scoreDelta: 0.9, riskReduction: 0.12, cost: 0.05 },
  [APGAR_NIC.OBSERVE]: { scoreDelta: -0.5, riskReduction: -0.25, cost: 0.02 },
};

/**
 * @typedef {Object} MctsState
 * @property {number} apgarScore
 * @property {string} primaryNanda
 * @property {number} nandaProbability
 * @property {string|null} selectedNic
 * @property {number} depth
 */

/**
 * @typedef {Object} MctsNode
 * @property {MctsState} state
 * @property {MctsNode|null} parent
 * @property {{ nic: string, child: MctsNode }[]} children
 * @property {number} visits
 * @property {number} totalReward
 * @property {string[]} untriedActions
 */

/**
 * @param {MctsState} state
 * @param {string} nic
 * @param {{ rewardWeights: Record<string, number>, mode: string }} config
 */
function simulateRollout(state, nic, config) {
  const effect = NIC_EFFECTS[nic] ?? NIC_EFFECTS[APGAR_NIC.OBSERVE];
  const projectedScore = Math.min(10, state.apgarScore + effect.scoreDelta);
  const clinicalGain = (projectedScore - state.apgarScore) / 10;
  const riskPenalty = Math.max(0, state.nandaProbability + effect.riskReduction * -1);
  const cost = effect.cost;
  const comprehension =
    config.mode === 'education' && nic === APGAR_NIC.VITAL_SIGNS_MONITORING ? 0.15 : 0.05;

  const w = config.rewardWeights;
  return (
    w.clinical_outcome * clinicalGain -
    w.risk_penalty * riskPenalty -
    w.intervention_cost * cost +
    w.user_comprehension * comprehension
  );
}

function ucb1(child, parentVisits, exploration = 1.41) {
  if (child.visits === 0) return Infinity;
  return child.totalReward / child.visits + exploration * Math.sqrt(Math.log(parentVisits) / child.visits);
}

/**
 * MCTS clínico simplificado — seleção/expansão/rollout/backprop.
 * @param {{ apgarScore: number, primaryNanda: string, nandaProbability: number, candidates: { entity_code: string }[], modifiers: ReturnType<import('./userContext.js').deriveContextModifiers>, mode: string }} params
 */
export function runClinicalMcts(params) {
  const { apgarScore, primaryNanda, nandaProbability, candidates, modifiers, mode } = params;
  const actions = candidates.map((c) => c.entity_code);
  const config = { rewardWeights: modifiers.rewardWeights, mode };

  /** @type {MctsNode} */
  const root = {
    state: {
      apgarScore,
      primaryNanda,
      nandaProbability,
      selectedNic: null,
      depth: 0,
    },
    parent: null,
    children: [],
    visits: 0,
    totalReward: 0,
    untriedActions: [...actions],
  };

  for (let i = 0; i < modifiers.mctsIterations; i++) {
    let node = root;
    const path = [node];

    while (node.untriedActions.length === 0 && node.children.length > 0) {
      const bestEntry = node.children.reduce((best, entry) =>
        ucb1(entry.child, node.visits) > ucb1(best.child, node.visits) ? entry : best
      );
      node = bestEntry.child;
      path.push(node);
    }

    if (node.untriedActions.length > 0 && node.state.depth < modifiers.mctsDepth) {
      const actionIdx = Math.floor(Math.random() * node.untriedActions.length);
      const nic = node.untriedActions.splice(actionIdx, 1)[0];
      const child = {
        state: {
          ...node.state,
          selectedNic: nic,
          depth: node.state.depth + 1,
        },
        parent: node,
        children: [],
        visits: 0,
        totalReward: 0,
        untriedActions: node.state.depth + 1 < modifiers.mctsDepth ? [...actions] : [],
      };
      node.children.push({ nic, child });
      node = child;
      path.push(node);
    }

    const nic = node.state.selectedNic ?? actions[0];
    const reward = simulateRollout(node.state, nic, config);

    for (const n of path) {
      n.visits += 1;
      n.totalReward += reward;
    }
  }

  const ranked = root.children
    .map(({ nic, child }) => ({
      entity_code: nic,
      visits: child.visits,
      avgReward: child.visits > 0 ? child.totalReward / child.visits : 0,
      confidence: root.visits > 0 ? child.visits / root.visits : 0,
    }))
    .sort((a, b) => b.avgReward - a.avgReward);

  const best = ranked[0] ?? {
    entity_code: APGAR_NIC.OBSERVE,
    visits: 0,
    avgReward: 0,
    confidence: 0,
  };

  return {
    bestAction: best,
    alternatives: ranked.slice(1, 4),
    simulations: modifiers.mctsIterations,
    depthLimit: modifiers.mctsDepth,
    rolloutTable: actions.map((nic) => ({
      entity_code: nic,
      reward: simulateRollout(root.state, nic, config),
    })),
  };
}
