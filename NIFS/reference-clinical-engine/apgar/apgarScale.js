/**
 * APGAR score — 5 componentes 0–2, total 0–10.
 * @typedef {{ appearance: 0|1|2, pulse: 0|1|2, grimace: 0|1|2, activity: 0|1|2, respiration: 0|1|2 }} ApgarComponents
 */

const COMPONENT_KEYS = ['appearance', 'pulse', 'grimace', 'activity', 'respiration'];

/**
 * @param {ApgarComponents} components
 */
export function computeApgarScore(components) {
  let score = 0;
  const breakdown = {};
  for (const key of COMPONENT_KEYS) {
    const value = clamp02(components[key] ?? 0);
    breakdown[key] = value;
    score += value;
  }
  return { score, breakdown, unit: 'score', range: '0-10' };
}

function clamp02(n) {
  return Math.max(0, Math.min(2, Math.round(Number(n))));
}

/** Componentes demo — recém-nascido com depressão moderada (score 4). */
export function demoModerateDistressComponents() {
  return {
    appearance: 1,
    pulse: 1,
    grimace: 0,
    activity: 1,
    respiration: 1,
  };
}

/** Score 3 — depressão severa (emergency demo). */
export function demoSevereDistressComponents() {
  return {
    appearance: 0,
    pulse: 1,
    grimace: 0,
    activity: 1,
    respiration: 1,
  };
}

export { COMPONENT_KEYS };
