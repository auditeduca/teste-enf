import { pdfNormal } from '../core/distributions.js';

function expectedVitals(state) {
  return {
    heartRate: 60 + (1 - state.contractilidade) * 50 + (1 - state.volemia) * 20,
    systolicBP: 80 + state.volemia * 60 - (1 - state.resistenciaVascular) * 30,
    diastolicBP: 50 + state.volemia * 30 - (1 - state.resistenciaVascular) * 10,
    respiratoryRate: 10 + (1 - state.oxigenacao) * 12 + (1 - state.ventilacao) * 6,
    spo2: 92 + state.oxigenacao * 7,
    temperature: 36 + state.inflamacao * 2,
    urineOutput: 30 + state.funcaoRenal * 70,
    gcs: 15 - (1 - state.oxigenacao) * 2,
  };
}

const STD = {
  heartRate: 8,
  systolicBP: 10,
  diastolicBP: 8,
  respiratoryRate: 3,
  spo2: 2,
  temperature: 0.3,
  urineOutput: 10,
  gcs: 1,
};

/** P(vitals | state) — produto de Gaussianas independentes. */
export function computeLikelihood(vitals, state) {
  const exp = expectedVitals(state);
  let likelihood = 1;
  for (const key of Object.keys(STD)) {
    likelihood *= pdfNormal(vitals[key], exp[key], STD[key] ** 2);
  }
  return Math.max(1e-300, likelihood);
}

export { expectedVitals };
