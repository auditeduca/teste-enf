import { DEFAULT_STATE } from '../core/types.js';
import { generativeTransition } from '../physiology/generativeModel.js';
import { computeLikelihood } from './bayesianUpdater.js';

export function initializeParticles(initialMean, numParticles = 300) {
  const particles = [];
  for (let i = 0; i < numParticles; i++) {
    const state = {};
    for (const key of Object.keys(DEFAULT_STATE)) {
      const mean = initialMean[key] ?? DEFAULT_STATE[key];
      state[key] = Math.max(0, Math.min(1, mean + (Math.random() - 0.5) * 0.15));
    }
    particles.push({ state, weight: 1 / numParticles });
  }
  return { particles, numParticles };
}

export function predictParticles(particleState, control, dt = 1) {
  return {
    particles: particleState.particles.map((p) => ({
      state: generativeTransition(p.state, control, dt),
      weight: p.weight,
    })),
    numParticles: particleState.numParticles,
  };
}

export function updateParticles(particleState, vitals) {
  const updated = particleState.particles.map((p) => ({
    ...p,
    weight: p.weight * computeLikelihood(vitals, p.state),
  }));
  const total = updated.reduce((s, p) => s + p.weight, 0);
  if (total === 0) {
    const w = 1 / updated.length;
    return { particles: updated.map((p) => ({ ...p, weight: w })), numParticles: particleState.numParticles };
  }
  return {
    particles: updated.map((p) => ({ ...p, weight: p.weight / total })),
    numParticles: particleState.numParticles,
  };
}

export function effectiveSampleSize(particles) {
  return 1 / particles.reduce((s, p) => s + p.weight * p.weight, 0);
}

export function resampleParticles(particleState, targetNum = particleState.numParticles) {
  const { particles } = particleState;
  const cum = [];
  let acc = 0;
  for (const p of particles) {
    acc += p.weight;
    cum.push(acc);
  }
  const step = acc / targetNum;
  let pos = Math.random() * step;
  let idx = 0;
  const next = [];
  for (let i = 0; i < targetNum; i++) {
    while (pos > cum[idx]) idx++;
    next.push({ state: { ...particles[idx].state }, weight: 1 / targetNum });
    pos += step;
  }
  return { particles: next, numParticles: targetNum };
}

export function meanState(particleState) {
  const keys = Object.keys(DEFAULT_STATE);
  const mean = {};
  for (const key of keys) {
    mean[key] = particleState.particles.reduce((s, p) => s + p.state[key] * p.weight, 0);
  }
  return mean;
}

export function stateDistribution(particleState) {
  const keys = Object.keys(DEFAULT_STATE);
  const dist = {};
  for (const key of keys) {
    const values = particleState.particles.map((p) => p.state[key]);
    const mean = values.reduce((s, v, i) => s + v * particleState.particles[i].weight, 0);
    const variance = particleState.particles.reduce(
      (s, p) => s + p.weight * (p.state[key] - mean) ** 2,
      0
    );
    dist[key] = { mean, variance };
  }
  return dist;
}
