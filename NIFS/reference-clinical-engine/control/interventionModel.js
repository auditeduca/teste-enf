import { NIC } from '../identifiers/nkosEntityCodes.js';

/** NIC catalog — entity_code + efeito no vetor de controle. */
export const availableInterventions = [
  {
    entity_code: NIC.FLUID_MANAGEMENT,
    name: 'Controle de líquidos',
    cost: 0.3,
    effect: () => ({ fluid: 0, diuretic: 0.6, electrolyteCorrection: 0.2, ventilatorSupport: 0 }),
  },
  {
    entity_code: NIC.VITAL_SIGNS_MONITORING,
    name: 'Monitorização de sinais vitais',
    cost: 0.15,
    effect: () => ({ fluid: 0, diuretic: 0, electrolyteCorrection: 0, ventilatorSupport: 0.3 }),
  },
  {
    entity_code: NIC.INFUSION_RELATED,
    name: 'Reposição volêmica (infusão)',
    cost: 0.2,
    effect: () => ({ fluid: 0.6, diuretic: 0, electrolyteCorrection: 0.3, ventilatorSupport: 0 }),
  },
  {
    entity_code: 'NIC.NULL',
    name: 'Observação (sem intervenção)',
    cost: 0,
    effect: () => ({ fluid: 0, diuretic: 0, electrolyteCorrection: 0, ventilatorSupport: 0 }),
  },
];

export function controlFromNicEntityCode(entityCode) {
  const nic = availableInterventions.find((i) => i.entity_code === entityCode);
  return nic ? nic.effect({}) : availableInterventions[3].effect({});
}
