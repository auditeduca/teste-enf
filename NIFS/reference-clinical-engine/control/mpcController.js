import { TARGET_STATE } from '../core/types.js';
import { predictParticles } from '../inference/particleFilter.js';
import { availableInterventions } from './interventionModel.js';

function expectedCost(particles) {
  let total = 0;
  for (const p of particles) {
    const s = p.state;
    total +=
      p.weight *
      (Math.abs(s.volemia - TARGET_STATE.volemia) * 2 +
        Math.abs(s.contractilidade - TARGET_STATE.contractilidade) * 2 +
        Math.abs(s.oxigenacao - TARGET_STATE.oxigenacao) * 1.5 +
        Math.abs(s.funcaoRenal - TARGET_STATE.funcaoRenal) * 2 +
        Math.abs(s.inflamacao - TARGET_STATE.inflamacao) * 3 +
        Math.abs(s.eletrolitos - TARGET_STATE.eletrolitos) * 1.5);
  }
  return total;
}

function simulateAction(particles, intervention, horizon = 6) {
  let state = { particles, numParticles: particles.length };
  const control = intervention.effect({});
  for (let t = 0; t < horizon; t++) {
    state = predictParticles(state, control, 1);
  }
  return expectedCost(state.particles);
}

export function mpcController(particles, horizon = 6) {
  let best = availableInterventions[availableInterventions.length - 1];
  let bestCost = Infinity;
  let nullCost = simulateAction(particles, best, horizon);

  for (const intervention of availableInterventions) {
    const cost = simulateAction(particles, intervention, horizon) + intervention.cost * 10;
    if (cost < bestCost) {
      bestCost = cost;
      best = intervention;
    }
  }

  const reduction =
    nullCost > 0 ? (((nullCost - bestCost) / nullCost) * 100).toFixed(0) : '0';

  return {
    entity_code: best.entity_code,
    name: best.name,
    expectedOutcome: `Melhora esperada ~${reduction}% vs. observação em ${horizon}h (demo).`,
    rationale: `NIC ${best.entity_code} minimiza desvio do estado alvo (MPC demo).`,
    control: best.effect({}),
  };
}
