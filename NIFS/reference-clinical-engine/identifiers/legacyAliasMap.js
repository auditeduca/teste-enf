/**
 * Ponte entre IDs legados da conversa V3–V7 e entity_code NKOS.
 * Use apenas em migração / testes de regressão.
 */
import { NANDA, NIC, CAL_DRIP_RATE } from './nkosEntityCodes.js';

/** IDs usados nos protótipos TypeScript (n1, i3, 00027…). */
export const LEGACY_NANDA_TO_ENTITY = {
  n1: NANDA.IMPAIRED_GAS_EXCHANGE,
  n2: NANDA.EXCESSIVE_FLUID_VOLUME,
  n3: NANDA.RISK_PATTERN,
  '00027': NANDA.IMPAIRED_GAS_EXCHANGE,
  '00030': NANDA.EXCESSIVE_FLUID_VOLUME,
  '00032': NANDA.RISK_PATTERN,
  '00046': NANDA.IMPAIRED_GAS_EXCHANGE,
  '00031': NANDA.EXCESSIVE_FLUID_VOLUME,
};

export const LEGACY_NIC_TO_ENTITY = {
  i1: NIC.FLUID_MANAGEMENT,
  i2: NIC.VITAL_SIGNS_MONITORING,
  i3: NIC.INFUSION_RELATED,
  '4120': NIC.FLUID_MANAGEMENT,
  '4210': NIC.VITAL_SIGNS_MONITORING,
  '4030': NIC.INFUSION_RELATED,
};

export const LEGACY_CAL_TO_ENTITY = {
  'CAL-001': CAL_DRIP_RATE,
  CAL001: CAL_DRIP_RATE,
};

export function resolveEntityCode(legacyId) {
  return (
    LEGACY_NANDA_TO_ENTITY[legacyId] ||
    LEGACY_NIC_TO_ENTITY[legacyId] ||
    LEGACY_CAL_TO_ENTITY[legacyId] ||
    legacyId
  );
}
