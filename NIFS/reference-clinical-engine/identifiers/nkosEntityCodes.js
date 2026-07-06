/**
 * Códigos canônicos NKOS v2026.2.2 — entity_code + chaves legadas do dataset.
 * Padrão: {CONCEITO}_{ARTEFATO}_{NNN} | NANDA_{NNNNN} | NIC_{NNNN}
 */

/** Calculadora principal do motor de gotejamento (CAL-001). */
export const CAL_DRIP_RATE = 'DRIP_RATE_CAL_001';

/** NANDA usados no demo fisiológico de infusão (datasets/clinical/). */
export const NANDA = {
  /** Troca de gases prejudicada — proxy de hipoperfusão/oxigenação no demo. */
  IMPAIRED_GAS_EXCHANGE: 'NANDA_00046',
  /** Volume de líquido excessivo — datasets: NANDA.00031. */
  EXCESSIVE_FLUID_VOLUME: 'NANDA_00031',
  /** Padrão de risco — terceiro eixo do grafo demo. */
  RISK_PATTERN: 'NANDA_00033',
};

/** Chaves legadas do dataset JSON (diagnosis_code). */
export const NANDA_DATASET_KEY = {
  [NANDA.IMPAIRED_GAS_EXCHANGE]: 'NANDA.00046',
  [NANDA.EXCESSIVE_FLUID_VOLUME]: 'NANDA.00031',
  [NANDA.RISK_PATTERN]: 'NANDA.00033',
};

/** NIC vinculadas via nnn_linkages / nursing_interventions.json. */
export const NIC = {
  FLUID_MANAGEMENT: 'NIC_2500',
  VITAL_SIGNS_MONITORING: 'NIC_2510',
  INFUSION_RELATED: 'NIC_2550',
};

export const NIC_DATASET_KEY = {
  [NIC.FLUID_MANAGEMENT]: 'NIC.2500',
  [NIC.VITAL_SIGNS_MONITORING]: 'NIC.2510',
  [NIC.INFUSION_RELATED]: 'NIC.2550',
};

/** Fatores fisiológicos latentes (nós do DAG interno — não são entity_code publicados). */
export const PHYS_FACTOR = {
  VOLEMIA: 'PHYS.VOLEMIA',
  CONTRACTILITY: 'PHYS.CONTRACTILITY',
  RESISTANCE: 'PHYS.RESISTANCE_VASCULAR',
  OXYGENATION: 'PHYS.OXYGENATION',
  VENTILATION: 'PHYS.VENTILATION',
  RENAL: 'PHYS.RENAL_FUNCTION',
  INFLAMMATION: 'PHYS.INFLAMMATION',
  ELECTROLYTES: 'PHYS.ELECTROLYTES',
  CARDIAC_OUTPUT: 'PHYS.CARDIAC_OUTPUT',
  PERFUSION: 'PHYS.SYSTEMIC_PERFUSION',
};

/** Grau de evidência exigido para publicação (doc 13). */
export const EVIDENCE_GRADE = {
  A: 'EVID.GRADE.A',
  MODERATE: 'EVID.GRADE.MODERATE',
  LOW: 'EVID.GRADE.LOW',
};

/** Metadados mínimos exigidos em outputs clínicos auditáveis. */
export const ENGINE_META = {
  engine_id: CAL_DRIP_RATE,
  engine_version: '8.0.0',
  schema_version: '2026.2.2-draft',
  evidence_disclaimer:
    'Saída educacional/simulação — não substitui julgamento clínico nem diagnóstico formal.',
};
