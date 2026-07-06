import { clamp01 } from '../core/types.js';
import { sampleNormal } from '../core/distributions.js';

const NOISE = {
  volemia: 0.03,
  contractilidade: 0.02,
  resistenciaVascular: 0.025,
  oxigenacao: 0.015,
  ventilacao: 0.015,
  funcaoRenal: 0.025,
  inflamacao: 0.035,
  eletrolitos: 0.02,
};

function deterministicEvolve(state, control) {
  const cardiacOutput = state.volemia * state.contractilidade;

  let volemia = state.volemia + 0.05 * (control.fluid - control.diuretic) - 0.02 * (1 - state.funcaoRenal);
  let contractilidade =
    state.contractilidade - 0.03 * state.inflamacao + 0.05 * Math.min(state.volemia, 0.6);
  let resistenciaVascular = state.resistenciaVascular + 0.04 * state.inflamacao - 0.02 * state.volemia;
  let oxigenacao =
    state.oxigenacao + 0.06 * state.ventilacao - 0.08 * state.inflamacao + 0.02 * cardiacOutput;
  let ventilacao = state.ventilacao + 0.04 * (1 - state.oxigenacao) - 0.02 * state.inflamacao;
  let funcaoRenal = state.funcaoRenal + 0.05 * cardiacOutput - 0.03 * state.inflamacao;
  let inflamacao = state.inflamacao * 0.95 + 0.03 * (1 - state.oxigenacao);
  let eletrolitos = state.eletrolitos + 0.03 * state.funcaoRenal + 0.06 * control.electrolyteCorrection;

  return {
    volemia: clamp01(volemia),
    contractilidade: clamp01(Math.max(0.1, contractilidade)),
    resistenciaVascular: clamp01(Math.max(0.1, resistenciaVascular)),
    oxigenacao: clamp01(Math.max(0.1, oxigenacao)),
    ventilacao: clamp01(Math.max(0.1, ventilacao)),
    funcaoRenal: clamp01(Math.max(0.05, funcaoRenal)),
    inflamacao: clamp01(Math.max(0.01, inflamacao)),
    eletrolitos: clamp01(Math.max(0.05, eletrolitos)),
  };
}

/** P(S(t+1) | S(t), U) — amostra única (particle filter). */
export function generativeTransition(state, control, _dt = 1) {
  const base = deterministicEvolve(state, control);
  return {
    volemia: clamp01(base.volemia + sampleNormal(0, NOISE.volemia ** 2)),
    contractilidade: clamp01(base.contractilidade + sampleNormal(0, NOISE.contractilidade ** 2)),
    resistenciaVascular: clamp01(
      base.resistenciaVascular + sampleNormal(0, NOISE.resistenciaVascular ** 2)
    ),
    oxigenacao: clamp01(base.oxigenacao + sampleNormal(0, NOISE.oxigenacao ** 2)),
    ventilacao: clamp01(base.ventilacao + sampleNormal(0, NOISE.ventilacao ** 2)),
    funcaoRenal: clamp01(base.funcaoRenal + sampleNormal(0, NOISE.funcaoRenal ** 2)),
    inflamacao: clamp01(base.inflamacao + sampleNormal(0, NOISE.inflamacao ** 2)),
    eletrolitos: clamp01(base.eletrolitos + sampleNormal(0, NOISE.eletrolitos ** 2)),
  };
}

export { deterministicEvolve };
