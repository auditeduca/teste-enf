/**
 * Entity codes NKOS — conceito APGAR (neonatal assessment).
 * RULE proposto v2026.2.3 — artefato lógico do motor, ainda fora do catálogo Master Data.
 */

export const APGAR_SCL = 'APGAR_SCL_001';
export const APGAR_RULE = 'APGAR_RULE_001';
export const APGAR_FLA = 'APGAR_FLA_001';

export const APGAR_NANDA = {
  INEFFECTIVE_BREATHING: 'NANDA_00162',
  IMPAIRED_GAS_EXCHANGE: 'NANDA_00046',
};

export const APGAR_NIC = {
  AIRWAY_MANAGEMENT: 'NIC_2380',
  VITAL_SIGNS_MONITORING: 'NIC_2300',
  POSITIONING: 'NIC_1120',
  OBSERVE: 'NIC.NULL',
};

export const APGAR_NOC = {
  OUTCOME_0405: 'NOC_0405',
  SLEEP: 'NOC_1100',
};

export const APGAR_META = {
  concept_code: 'APGAR',
  engine_id: APGAR_SCL,
  engine_version: '9.0.0-mcts',
  schema_version: '2026.2.2-draft',
  canonical_url: 'https://calculadorasdeenfermagem.com.br/ferramentas/apgar/',
  evidence_disclaimer:
    'Simulação educacional APGAR + MCTS — não substitui reanimação neonatal nem diagnóstico formal.',
};

/** Títulos alinhados a datasets/clinical/ (campo name). */
export const APGAR_LABELS = {
  [APGAR_NANDA.INEFFECTIVE_BREATHING]: 'Ineffective breathing pattern',
  [APGAR_NANDA.IMPAIRED_GAS_EXCHANGE]: 'Impaired gas exchange (demo proxy)',
  [APGAR_NIC.AIRWAY_MANAGEMENT]: 'Airway management',
  [APGAR_NIC.VITAL_SIGNS_MONITORING]: 'Vital signs monitoring',
  [APGAR_NIC.POSITIONING]: 'Positioning',
  [APGAR_NIC.OBSERVE]: 'Observation only',
  [APGAR_NOC.OUTCOME_0405]: 'Risk control (NOC.0405)',
};
