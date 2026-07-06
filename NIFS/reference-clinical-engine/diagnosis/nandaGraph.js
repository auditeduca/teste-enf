import { NANDA, PHYS_FACTOR } from '../identifiers/nkosEntityCodes.js';

function parentValues(state) {
  const cardiacOutput = state.volemia * state.contractilidade;
  const perfusion = cardiacOutput * (1 - state.resistenciaVascular) * state.oxigenacao;
  return {
    [PHYS_FACTOR.CARDIAC_OUTPUT]: cardiacOutput,
    [PHYS_FACTOR.PERFUSION]: perfusion,
    volemia: state.volemia,
    funcaoRenal: state.funcaoRenal,
    eletrolitos: state.eletrolitos,
  };
}

/** CPTs demo — entity_code como chave primária. */
export const nandaNodes = [
  {
    entity_code: NANDA.IMPAIRED_GAS_EXCHANGE,
    title: 'Troca de gases prejudicada',
    parents: [PHYS_FACTOR.CARDIAC_OUTPUT, PHYS_FACTOR.PERFUSION],
    cpt(parents) {
      const dc = parents[PHYS_FACTOR.CARDIAC_OUTPUT] ?? 0.5;
      const perf = parents[PHYS_FACTOR.PERFUSION] ?? 0.5;
      return Math.max(0, Math.min(1, 1 - (0.7 * dc + 0.3 * perf)));
    },
  },
  {
    entity_code: NANDA.EXCESSIVE_FLUID_VOLUME,
    title: 'Volume de líquido excessivo',
    parents: ['volemia', 'funcaoRenal'],
    cpt(parents) {
      const vol = parents.volemia ?? 0.5;
      const renal = parents.funcaoRenal ?? 0.5;
      return Math.max(0, Math.min(1, vol * (1 - renal) * 1.5));
    },
  },
  {
    entity_code: NANDA.RISK_PATTERN,
    title: 'Padrão de risco (demo)',
    parents: ['funcaoRenal', 'eletrolitos'],
    cpt(parents) {
      const renal = parents.funcaoRenal ?? 0.5;
      const eletro = parents.eletrolitos ?? 0.5;
      return Math.max(0, Math.min(1, (1 - renal) * 0.6 + (1 - eletro) * 0.4));
    },
  },
];

export function evaluateNandaCpt(entityCode, state) {
  const node = nandaNodes.find((n) => n.entity_code === entityCode);
  if (!node) return 0;
  const pv = parentValues(state);
  const inputs = {};
  for (const p of node.parents) {
    inputs[p] = pv[p] ?? state[p] ?? 0.5;
  }
  return node.cpt(inputs);
}

export { parentValues };
