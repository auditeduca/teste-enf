/**
 * Arestas de exemplo alinhadas a relation_dictionary.json (edge layer).
 */
import { CAL_DRIP_RATE, NANDA, NIC } from './nkosEntityCodes.js';

export const SAMPLE_ENGINE_EDGES = [
  {
    from: CAL_DRIP_RATE,
    to: NANDA.IMPAIRED_GAS_EXCHANGE,
    relation_type: 'supports_diagnosis',
    weight: 0.85,
    evidence_grade: 'A',
    status: 'draft',
    notes: 'Gotejamento baixo → risco de hipoperfusão (demo educacional)',
  },
  {
    from: CAL_DRIP_RATE,
    to: NANDA.EXCESSIVE_FLUID_VOLUME,
    relation_type: 'triggers',
    weight: 0.9,
    evidence_grade: 'A',
    status: 'draft',
    notes: 'Taxa elevada → risco de sobrecarga volêmica',
  },
  {
    from: NANDA.EXCESSIVE_FLUID_VOLUME,
    to: NIC.FLUID_MANAGEMENT,
    relation_type: 'treated_by',
    weight: 1,
    evidence_grade: 'MODERATE',
    status: 'draft',
  },
  {
    from: NANDA.IMPAIRED_GAS_EXCHANGE,
    to: NIC.INFUSION_RELATED,
    relation_type: 'maps_to',
    weight: 0.8,
    evidence_grade: 'MODERATE',
    status: 'draft',
  },
];
