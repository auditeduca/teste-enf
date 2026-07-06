import { nandaNodes, parentValues } from './nandaGraph.js';

export function inferDiagnoses(particles) {
  if (!particles.length) return [];

  const scores = {};
  for (const node of nandaNodes) {
    scores[node.entity_code] = [];
  }

  for (const p of particles) {
    const pv = parentValues(p.state);
    for (const node of nandaNodes) {
      const inputs = {};
      for (const parent of node.parents) {
        inputs[parent] = pv[parent] ?? p.state[parent] ?? 0.5;
      }
      scores[node.entity_code].push(node.cpt(inputs) * p.weight);
    }
  }

  return nandaNodes
    .map((node) => {
      const vals = scores[node.entity_code];
      const probability = vals.reduce((a, b) => a + b, 0);
      const variance =
        vals.reduce((a, b) => a + (b - probability) ** 2, 0) / Math.max(1, vals.length);
      const confidence = 1 - Math.min(1, Math.sqrt(variance) / 0.3);

      const samplePv = parentValues(particles[0].state);
      const evidence = node.parents.map((parent) => {
        const val = samplePv[parent] ?? particles[0].state[parent] ?? 0.5;
        const status = val > 0.7 ? '↑' : val < 0.3 ? '↓' : '≈';
        return `${parent} ${status} (${(val * 100).toFixed(0)}%)`;
      });

      return {
        entity_code: node.entity_code,
        title: node.title,
        probability,
        confidence,
        evidence,
      };
    })
    .sort((a, b) => b.probability - a.probability);
}
