import { ENGINE_META } from './identifiers/nkosEntityCodes.js';
import {
  initializeParticles,
  predictParticles,
  updateParticles,
  resampleParticles,
  effectiveSampleSize,
  meanState,
  stateDistribution,
} from './inference/particleFilter.js';
import { inferDiagnoses } from './diagnosis/bayesianDiagnosis.js';
import { mpcController } from './control/mpcController.js';

const RISK_EVENTS = {
  NANDA_00046: { name: 'Hipoperfusão / troca gasosa crítica', severity: 5 },
  NANDA_00031: { name: 'Sobrecarga volêmica', severity: 3 },
  NANDA_00033: { name: 'Desequilíbrio metabólico (demo)', severity: 4 },
};

function computeRisk(diagnoses) {
  const events = diagnoses
    .filter((d) => d.probability > 0.05 && RISK_EVENTS[d.entity_code])
    .map((d) => ({
      entity_code: d.entity_code,
      name: RISK_EVENTS[d.entity_code].name,
      probability: d.probability,
      severity: RISK_EVENTS[d.entity_code].severity,
    }));

  const expectedLoss = Math.min(
    100,
    Math.round(
      events.reduce((acc, ev) => acc + ev.probability * (ev.severity / 5), 0) * 100
    )
  );

  return { expectedLoss, events };
}

function vitalsToPrior(vitals) {
  return {
    volemia: Math.max(0, Math.min(1, (vitals.systolicBP - 80) / 60)),
    contractilidade: Math.max(0, Math.min(1, 1 - (vitals.heartRate - 60) / 80)),
    oxigenacao: Math.max(0, Math.min(1, (vitals.spo2 - 90) / 9)),
    funcaoRenal: Math.max(0, Math.min(1, vitals.urineOutput / 100)),
    inflamacao: Math.max(0, Math.min(1, (vitals.temperature - 36) / 2)),
  };
}

/**
 * Pipeline V8 — referência NKOS.
 * @param {import('./core/types.js').VitalObservation} initialVitals
 * @param {import('./core/types.js').VitalObservation[]} vitalsSequence
 * @param {{ numParticles?: number, control?: import('./core/types.js').ControlInput }} options
 */
export function runV8(initialVitals, vitalsSequence, options = {}) {
  const numParticles = options.numParticles ?? 300;
  const control = options.control ?? {
    fluid: 0,
    diuretic: 0,
    electrolyteCorrection: 0,
    ventilatorSupport: 0,
  };

  let particleState = initializeParticles(vitalsToPrior(initialVitals), numParticles);

  for (const vitals of vitalsSequence) {
    particleState = predictParticles(particleState, control, 1);
    particleState = updateParticles(particleState, vitals);
    if (effectiveSampleSize(particleState.particles) < numParticles * 0.5) {
      particleState = resampleParticles(particleState, numParticles);
    }
  }

  const diagnoses = inferDiagnoses(particleState.particles);
  const risk = computeRisk(diagnoses);
  const mpc = mpcController(particleState.particles, 6);
  const mean = meanState(particleState);
  const belief = stateDistribution(particleState);
  const top = diagnoses[0];

  const clinicalSummary =
    `[${ENGINE_META.engine_id}] volemia=${mean.volemia.toFixed(2)}, ` +
    `oxigenação=${mean.oxigenacao.toFixed(2)}. ` +
    `Top: ${top?.entity_code} (${((top?.probability ?? 0) * 100).toFixed(1)}%). ` +
    `Risco=${risk.expectedLoss}. NIC sugerida: ${mpc.entity_code}. ` +
    ENGINE_META.evidence_disclaimer;

  return {
    meta: ENGINE_META,
    timestamp: new Date().toISOString(),
    belief,
    meanState: mean,
    diagnoses,
    risk,
    recommendedIntervention: mpc,
    clinicalSummary,
  };
}

export { ENGINE_META };
