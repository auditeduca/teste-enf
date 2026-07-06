import { APGAR_RULE } from '../identifiers/apgarEntityCodes.js';

/** Regras determinísticas APGAR_RULE_001 — espelho de apgar_edges.json inference_rules. */
const THRESHOLD_RULES = [
  {
    match: (score) => score <= 3,
    label: 'severe_distress',
    label_pt: 'Depressão neonatal severa',
    nanda_boost: { NANDA_00162: 0.87, NANDA_00046: 0.75 },
  },
  {
    match: (score) => score >= 4 && score <= 6,
    label: 'moderate_distress',
    label_pt: 'Depressão neonatal moderada',
    nanda_boost: { NANDA_00162: 0.72, NANDA_00046: 0.55 },
  },
  {
    match: (score) => score >= 7,
    label: 'stable',
    label_pt: 'Adaptação neonatal adequada',
    nanda_boost: { NANDA_00162: 0.15, NANDA_00046: 0.1 },
  },
];

/**
 * @param {number} score
 */
export function interpretApgarScore(score) {
  const rule = THRESHOLD_RULES.find((r) => r.match(score)) ?? THRESHOLD_RULES[2];
  return {
    entity_code: APGAR_RULE,
    logic_type: 'threshold_mapping',
    clinical_state: rule.label,
    clinical_state_pt: rule.label_pt,
    nanda_probabilities: Object.entries(rule.nanda_boost).map(([entity_code, probability]) => ({
      entity_code,
      probability,
    })),
    rules_applied: THRESHOLD_RULES.map((r) => ({
      condition: r.label,
      active: r.match(score),
    })),
  };
}
