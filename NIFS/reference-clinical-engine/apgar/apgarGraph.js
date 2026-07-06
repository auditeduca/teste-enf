import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import {
  APGAR_LABELS,
  APGAR_NIC,
  APGAR_NANDA,
} from '../identifiers/apgarEntityCodes.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const apgarOntology = JSON.parse(
  readFileSync(join(__dirname, '../../datasets/ontology/apgar_edges.json'), 'utf8')
);

/** @typedef {{ from: string, to: string, relation_type: string, weight: number }} ClinicalEdge */

/**
 * @param {string} from
 * @param {string} relationType
 */
export function getEdgesFrom(from, relationType) {
  return apgarOntology.edges.filter(
    (e) => e.from === from && (!relationType || e.relation_type === relationType)
  );
}

/**
 * NANDA ativados a partir do score + arestas SCL/RULE.
 * @param {number} score
 * @param {{ entity_code: string, probability: number }[]} ruleProbabilities
 */
export function buildDiagnosisState(score, ruleProbabilities) {
  const sclBoost = getEdgesFrom('APGAR_SCL_001', 'supports_diagnosis');
  const diagnoses = new Map();

  for (const { entity_code, probability } of ruleProbabilities) {
    diagnoses.set(entity_code, {
      entity_code,
      title: APGAR_LABELS[entity_code] ?? entity_code,
      probability,
      sources: ['APGAR_RULE_001'],
    });
  }

  for (const edge of sclBoost) {
    const existing = diagnoses.get(edge.to);
    const blended = existing
      ? Math.min(1, (existing.probability + edge.weight * (1 - score / 10)) / 1.5)
      : edge.weight * (1 - score / 10);
    diagnoses.set(edge.to, {
      entity_code: edge.to,
      title: APGAR_LABELS[edge.to] ?? edge.to,
      probability: Math.min(1, blended),
      sources: existing ? [...existing.sources, 'APGAR_SCL_001'] : ['APGAR_SCL_001'],
    });
  }

  return [...diagnoses.values()].sort((a, b) => b.probability - a.probability);
}

/**
 * NIC candidatas para o NANDA dominante.
 * @param {string} nandaCode
 */
export function getInterventionCandidates(nandaCode) {
  const treated = getEdgesFrom(nandaCode, 'treated_by');
  const mapped = getEdgesFrom(nandaCode, 'maps_to');
  const seen = new Set();
  const candidates = [];

  for (const edge of [...treated, ...mapped]) {
    if (seen.has(edge.to)) continue;
    seen.add(edge.to);
    candidates.push({
      entity_code: edge.to,
      title: APGAR_LABELS[edge.to] ?? edge.to,
      edge_weight: edge.weight,
      relation_type: edge.relation_type,
      expected_noc: getEdgesFrom(edge.to, 'impacts').map((e) => ({
        entity_code: e.to,
        title: APGAR_LABELS[e.to] ?? e.to,
        weight: e.weight,
      })),
    });
  }

  candidates.push({
    entity_code: APGAR_NIC.OBSERVE,
    title: APGAR_LABELS[APGAR_NIC.OBSERVE],
    edge_weight: 0.3,
    relation_type: 'observe',
    expected_noc: [],
  });

  return candidates.sort((a, b) => b.edge_weight - a.edge_weight);
}

/**
 * Caminho causal para explainability (limitado por graphDepth).
 * @param {string} primaryNanda
 * @param {string} selectedNic
 * @param {number} graphDepth
 */
export function buildCausalPath(primaryNanda, selectedNic, graphDepth = 4) {
  const path = ['APGAR_SCL_001', 'APGAR_RULE_001', primaryNanda];
  if (graphDepth >= 3 && selectedNic && selectedNic !== APGAR_NIC.OBSERVE) {
    path.push(selectedNic);
    if (graphDepth >= 4) {
      const noc = getEdgesFrom(selectedNic, 'impacts')[0];
      if (noc) path.push(noc.to);
    }
  }
  return path;
}

export function getPrimaryNanda(diagnoses) {
  return diagnoses[0]?.entity_code ?? APGAR_NANDA.INEFFECTIVE_BREATHING;
}

export { apgarOntology };
