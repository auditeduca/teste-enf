/** @typedef {'standard'|'education'|'emergency'|'exam'} UserMode */
/** @typedef {'low_detail'|'standard'|'deep_clinical'} ScaleMode */
/** @typedef {'low'|'medium'|'high'|'critical'} Urgency */
/** @typedef {'mobile'|'desktop'} Device */
/** @typedef {'clinical'|'flashcard'|'quiz'|'simulation'} ContentType */
/** @typedef {'student'|'nurse'|'specialist'} ExpertiseLevel */
/** @typedef {'learn'|'decide'|'revise'|'train'} InteractionGoal */

/**
 * @typedef {Object} UserContext
 * @property {UserMode} mode
 * @property {ScaleMode} scale_mode
 * @property {Urgency} urgency
 * @property {Device} device
 * @property {ContentType} content_type
 * @property {ExpertiseLevel} expertise_level
 * @property {InteractionGoal} interaction_goal
 * @property {string} [locale]
 */

export const DEFAULT_USER_CONTEXT = {
  mode: 'standard',
  scale_mode: 'standard',
  urgency: 'medium',
  device: 'desktop',
  content_type: 'clinical',
  expertise_level: 'nurse',
  interaction_goal: 'decide',
  locale: 'pt-BR',
};

/**
 * @param {Partial<UserContext>} partial
 * @returns {UserContext}
 */
export function normalizeUserContext(partial = {}) {
  return { ...DEFAULT_USER_CONTEXT, ...partial };
}

/**
 * Modificadores de runtime derivados do contexto — afetam MCTS e UI.
 * @param {UserContext} ctx
 */
export function deriveContextModifiers(ctx) {
  const urgencyRank = { low: 0, medium: 1, high: 2, critical: 3 };
  const urgencyLevel = urgencyRank[ctx.urgency] ?? 1;

  let mctsDepth = 3;
  let mctsIterations = 800;
  let graphDepth = 4;
  let showExplainability = true;

  if (ctx.mode === 'emergency' || ctx.urgency === 'critical') {
    mctsDepth = 2;
    mctsIterations = 400;
    graphDepth = 2;
    showExplainability = false;
  } else if (ctx.mode === 'education' || ctx.content_type === 'flashcard') {
    mctsDepth = 4;
    mctsIterations = 600;
    graphDepth = ctx.scale_mode === 'deep_clinical' ? 4 : 2;
  } else if (ctx.mode === 'exam') {
    mctsDepth = 3;
    mctsIterations = 500;
    graphDepth = 2;
    showExplainability = false;
  }

  if (ctx.device === 'mobile') {
    mctsDepth = Math.max(1, mctsDepth - 1);
    graphDepth = Math.max(1, graphDepth - 1);
    mctsIterations = Math.round(mctsIterations * 0.75);
  }

  if (ctx.scale_mode === 'low_detail') {
    graphDepth = 1;
    showExplainability = false;
  }

  const rewardWeights = {
    clinical_outcome: ctx.mode === 'education' ? 0.5 : 0.75 + urgencyLevel * 0.05,
    risk_penalty: 0.2 + urgencyLevel * 0.08,
    intervention_cost: ctx.mode === 'emergency' ? 0.05 : 0.12,
    user_comprehension:
      ctx.mode === 'education' || ctx.interaction_goal === 'learn' ? 0.35 : 0.08,
  };

  const sum = Object.values(rewardWeights).reduce((a, b) => a + b, 0);
  for (const k of Object.keys(rewardWeights)) {
    rewardWeights[k] /= sum;
  }

  return {
    mctsDepth,
    mctsIterations,
    graphDepth,
    showExplainability,
    rewardWeights,
    time_pressure: urgencyLevel / 3,
  };
}
