/** @typedef {Object} PhysiologicalState
 * @property {number} volemia
 * @property {number} contractilidade
 * @property {number} resistenciaVascular
 * @property {number} oxigenacao
 * @property {number} ventilacao
 * @property {number} funcaoRenal
 * @property {number} inflamacao
 * @property {number} eletrolitos
 */

/** @typedef {Object} ControlInput
 * @property {number} fluid
 * @property {number} diuretic
 * @property {number} electrolyteCorrection
 * @property {number} ventilatorSupport
 */

/** @typedef {Object} VitalObservation
 * @property {number} heartRate
 * @property {number} systolicBP
 * @property {number} diastolicBP
 * @property {number} respiratoryRate
 * @property {number} spo2
 * @property {number} temperature
 * @property {number} urineOutput
 * @property {number} gcs
 */

export const DEFAULT_STATE = {
  volemia: 0.5,
  contractilidade: 0.7,
  resistenciaVascular: 0.6,
  oxigenacao: 0.8,
  ventilacao: 0.7,
  funcaoRenal: 0.8,
  inflamacao: 0.2,
  eletrolitos: 0.7,
};

export const TARGET_STATE = {
  volemia: 0.6,
  contractilidade: 0.8,
  resistenciaVascular: 0.6,
  oxigenacao: 0.9,
  ventilacao: 0.8,
  funcaoRenal: 0.8,
  inflamacao: 0.2,
  eletrolitos: 0.8,
};

export function clamp01(value) {
  return Math.max(0, Math.min(1, value));
}
