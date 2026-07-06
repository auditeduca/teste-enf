import { APGAR_FLA, APGAR_SCL } from '../identifiers/apgarEntityCodes.js';

/**
 * Roteador de conteúdo adaptativo — flashcard / clinical / emergency.
 * @param {import('./userContext.js').UserContext} ctx
 * @param {{ score: number, breakdown: Record<string, number>, clinical_state_pt: string, diagnoses: object[], bestNic: object, causalPath: string[] }} clinical
 */
export function routeApgarContent(ctx, clinical) {
  const renderMode = resolveRenderMode(ctx);

  if (ctx.content_type === 'flashcard' || ctx.mode === 'education') {
    return buildFlashcardPayload(ctx, clinical, renderMode);
  }

  if (ctx.mode === 'emergency' || ctx.urgency === 'critical') {
    return buildEmergencyPayload(clinical, renderMode);
  }

  return buildClinicalPayload(clinical, renderMode, ctx);
}

function resolveRenderMode(ctx) {
  if (ctx.device === 'mobile') {
    if (ctx.scale_mode === 'low_detail') return 'microcard';
    if (ctx.scale_mode === 'deep_clinical') return 'expanded_case';
    return 'card';
  }
  if (ctx.scale_mode === 'deep_clinical') return 'expanded_case';
  if (ctx.scale_mode === 'low_detail') return 'summary';
  return 'standard_panel';
}

function buildFlashcardPayload(ctx, clinical, renderMode) {
  const cards = [
    {
      id: 'apgar-components',
      front: '5 componentes do APGAR (0–2 cada)',
      back: 'Aparência · Pulso · Irritabilidade · Atividade · Respiração',
    },
    {
      id: 'apgar-score',
      front: `Score total = ? (demo: ${clinical.score})`,
      back: `Total ${clinical.score}/10 — ${clinical.clinical_state_pt}`,
    },
  ];

  if (renderMode !== 'microcard') {
    cards.push({
      id: 'apgar-nanda',
      front: 'NANDA principal sugerida',
      back: clinical.diagnoses[0]
        ? `${clinical.diagnoses[0].entity_code}: ${clinical.diagnoses[0].title}`
        : 'N/A',
    });
  }

  if (renderMode === 'expanded_case') {
    cards.push({
      id: 'apgar-nic',
      front: 'NIC prioritária (MCTS)',
      back: `${clinical.bestNic.entity_code} (conf ${(clinical.bestNic.confidence * 100).toFixed(0)}%)`,
    });
  }

  return {
    entity_code: APGAR_FLA,
    content_type: 'flashcard',
    render_mode: renderMode,
    parent_entity_code: APGAR_SCL,
    deck: cards,
    locale: ctx.locale,
  };
}

function buildEmergencyPayload(clinical, renderMode) {
  return {
    content_type: 'clinical',
    render_mode: renderMode,
    alert_level: clinical.score <= 3 ? 'critical' : 'warning',
    headline: clinical.clinical_state_pt,
    score: clinical.score,
    primary_nic: clinical.bestNic.entity_code,
    nanda: clinical.diagnoses.slice(0, 1),
    graph_depth: 2,
    hide_explainer: true,
  };
}

function buildClinicalPayload(clinical, renderMode, ctx) {
  return {
    content_type: 'clinical',
    render_mode: renderMode,
    score: clinical.score,
    breakdown: clinical.breakdown,
    clinical_state: clinical.clinical_state_pt,
    diagnoses: clinical.diagnoses,
    recommended_intervention: clinical.bestNic,
    causal_path: clinical.causalPath,
    locale: ctx.locale,
  };
}
