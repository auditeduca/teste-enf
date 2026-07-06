/**
 * NIFS v5.0 — TypeScript Types
 * Generated from: NIFS specification (600 Clinical Reasoning + 700 AI Architecture)
 * 
 * This file is GENERATED from the NIFS specification.
 * Do not edit manually — edit the spec, regenerate types.
 */

// ═══════════════════════════════════════════════════════════════════════════
// 1. ni_reasoning — Clinical Reasoning Engine
// ═══════════════════════════════════════════════════════════════════════════

export type ReasoningType = 'diagnostic' | 'therapeutic' | 'prioritization' | 'escalation';
export type ReasoningStatus = 'active' | 'awaiting_council' | 'awaiting_human' | 'completed' | 'aborted' | 'reassessing';
export type StepType = 'observation' | 'hypothesis' | 'evidence_for' | 'evidence_against' | 'bayesian_update' | 'ranking' | 'council' | 'planning' | 'explainability' | 'safety' | 'output';
export type GenerationStrategy = 'graph_traversal' | 'memory_retrieval' | 'rule_matching' | 'hybrid';
export type ScoreType = 'probability' | 'utility' | 'salience' | 'urgency' | 'priority' | 'attention';
export type ScoreBasis = 'rule_based' | 'bayesian' | 'learned' | 'heuristic' | 'empirical';

export interface ReasoningSession {
  session_id: string;
  patient_identifier: string;
  case_id?: string;
  council_session_id?: string;
  reasoning_type: ReasoningType;
  status: ReasoningStatus;
  started_at: string;
  completed_at?: string;
  final_nanda_code?: string;
  final_confidence?: number;
  final_entropy?: number;
  world_state_id?: string;
  created_date: string;
  updated_date: string;
}

export interface ReasoningStep {
  step_id: string;
  session_id: string;
  step_order: number;
  step_type: StepType;
  step_label?: string;
  input_data?: Record<string, any>;
  output_data?: Record<string, any>;
  node_id?: string;
  duration_ms?: number;
}

export interface ReasoningTrace {
  trace_id: string;
  session_id: string;
  step_id?: string;
  trace_order: number;
  trace_type: 'thought' | 'evaluation' | 'inference' | 'decision' | 'evidence_for' | 'evidence_against';
  content: string;
  evidence_ref?: string;
  confidence?: number;
}

export interface Hypothesis {
  hypothesis_id: string;
  session_id: string;
  nanda_code: string;
  prior_probability: number;
  posterior_probability?: number;
  confidence_interval_low?: number;
  confidence_interval_high?: number;
  entropy?: number;
  generation_strategy?: GenerationStrategy;
  rank?: number;
  status: 'active' | 'eliminated';
  rejection_reason?: string;
}

export interface ReasoningScore {
  score_id: string;
  session_id: string;
  step_id?: string;
  nanda_code?: string;
  nic_code?: string;
  noc_code?: string;
  score_type: ScoreType;
  score_value: number;
  score_basis: ScoreBasis;
}

// ═══════════════════════════════════════════════════════════════════════════
// 2. ni_memory — Episodic Memory
// ═══════════════════════════════════════════════════════════════════════════

export type EpisodeType = 'admission' | 'intervention' | 'crisis' | 'recovery' | 'discharge' | 'longitudinal';
export type OutcomeType = 'improved' | 'unchanged' | 'deteriorated' | 'resolved' | 'adverse';
export type LearningType = 'effective_intervention' | 'ineffective_intervention' | 'adverse_reaction' | 'time_pattern' | 'context_pattern';

export interface Episode {
  episode_id: string;
  patient_identifier: string;
  case_id?: string;
  episode_type: EpisodeType;
  started_at: string;
  ended_at?: string;
  outcome_summary?: string;
  success_score?: number;
  similarity_embedding?: number[];
}

export interface EpisodeObservation {
  observation_id: string;
  episode_id: string;
  observed_at: string;
  observation_type: string;
  observation_value: Record<string, any>;
  attention_score?: number;
  node_id?: string;
}

export interface EpisodeAction {
  action_id: string;
  episode_id: string;
  action_type: string;
  nic_code?: string;
  protocol_id?: string;
  action_data?: Record<string, any>;
  reasoning_session_id?: string;
  executed_at: string;
}

export interface EpisodeOutcome {
  outcome_id: string;
  episode_id: string;
  action_id?: string;
  noc_code?: string;
  outcome_type: OutcomeType;
  outcome_value?: number;
  expected_value?: number;
  surprise_score?: number;
  measured_at: string;
}

export interface EpisodeLearning {
  learning_id: string;
  episode_id: string;
  learning_type: LearningType;
  description: string;
  weight_adjustment?: number;
  applied: boolean;
  applied_at?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// 3. ni_world — World Model
// ═══════════════════════════════════════════════════════════════════════════

export type SeverityLevel = 'stable' | 'moderate' | 'critical' | 'terminal';
export type ResourceType = 'infusion_pump' | 'ventilator' | 'monitor' | 'defibrillator' | 'bed' | 'isolation_room' | 'crash_cart' | 'warmer';
export type ShiftType = 'morning' | 'evening' | 'night';

export interface PatientState {
  state_id: string;
  patient_identifier: string;
  severity_level?: SeverityLevel;
  acuity_score?: number;
  isolation_status?: string;
  mobility_status?: string;
  consciousness_level?: string;
  state_data?: Record<string, any>;
  captured_at: string;
}

export interface WardState {
  state_id: string;
  ward_identifier: string;
  ward_type?: string;
  occupancy: number;
  nurse_patient_ratio?: number;
  isolation_rooms_available?: number;
  captured_at: string;
}

export interface ResourceState {
  state_id: string;
  ward_identifier: string;
  resource_type: ResourceType;
  available: number;
  in_use: number;
  total: number;
  captured_at: string;
}

export interface StaffState {
  state_id: string;
  ward_identifier: string;
  shift_type: ShiftType;
  nurses_on_duty: number;
  nurses_available: number;
  specialty_coverage?: Record<string, boolean>;
  captured_at: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// 4. ni_attention — Clinical Attention
// ═══════════════════════════════════════════════════════════════════════════

export interface AttentionSignal {
  signal_id: string;
  reasoning_session_id?: string;
  patient_identifier?: string;
  observation_ref: string;
  observation_type?: string;
  clinical_domain?: string;
  attention_score: number;
  salience?: number;
  priority?: number;
  urgency?: number;
  components?: {
    domain: number;
    salience: number;
    urgency: number;
    priority: number;
    context: number;
    learned: number;
  };
  ignored: boolean;
  ignore_reason?: string;
  focus_window?: string;
}

export interface AttentionWeight {
  weight_id: string;
  context_type: string;
  context_value: string;
  observation_type: string;
  clinical_domain?: string;
  base_weight: number;
  learned_weight: number;
  last_updated_at: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// 5. ni_prob — Uncertainty Model
// ═══════════════════════════════════════════════════════════════════════════

export type PriorType = 'uniform' | 'informative' | 'empirical' | 'literature';
export type PriorSource = 'literature' | 'expert' | 'empirical' | 'default';
export type DistributionType = 'normal' | 'beta' | 'categorical' | 'uniform' | 'lognormal' | 'bernoulli';
export type AmbiguityFlagType = 'low_confidence' | 'high_entropy' | 'conflicting_evidence' | 'insufficient_data';

export interface PriorBelief {
  prior_id: string;
  node_id: string;
  population_id?: string;
  prior_type: PriorType;
  prior_value: number;
  prior_source: PriorSource;
  evidence_grade?: 'A' | 'B' | 'C' | 'D';
}

export interface BeliefUpdate {
  update_id: string;
  session_id: string;
  hypothesis_id?: string;
  node_id?: string;
  prior_value: number;
  likelihood?: number;
  posterior_value: number;
  bayes_factor?: number;
  evidence_ref?: string;
  update_order: number;
}

export interface AmbiguityFlag {
  flag_id: string;
  session_id: string;
  flag_type: AmbiguityFlagType;
  flag_value?: number;
  recommended_action?: string;
}

export interface UncertaintyDistribution {
  distribution_id: string;
  model_id: string;
  node_id?: string;
  distribution_type: DistributionType;
  parameters: Record<string, number>;
  sample_count: number;
}

export interface ConfidenceInterval {
  ci_id: string;
  model_id: string;
  node_id?: string;
  lower_bound: number;
  upper_bound: number;
  confidence_level: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// 6. ni_planner — Planner
// ═══════════════════════════════════════════════════════════════════════════

export type PlanType = 'intervention_sequence' | 'contingency' | 'escalation' | 'monitoring';
export type PlanStatus = 'proposed' | 'active' | 'completed' | 'abandoned' | 'revising';
export type PlanNodeType = 'action' | 'evaluation' | 'branch' | 'terminal' | 'escalation' | 'de_escalation';
export type ConditionType = 'success' | 'failure' | 'deterioration' | 'no_change' | 'timeout' | 'adverse_event' | 'escalation_trigger';

export interface Plan {
  plan_id: string;
  reasoning_session_id?: string;
  case_id?: string;
  care_plan_id?: string;
  plan_type: PlanType;
  goal_noc_code?: string;
  status: PlanStatus;
}

export interface PlanNode {
  node_id: string;
  plan_id: string;
  node_type: PlanNodeType;
  nic_code?: string;
  protocol_id?: string;
  expected_noc_delta?: number;
  node_order: number;
}

export interface PlanEdge {
  edge_id: string;
  plan_id: string;
  from_node_id: string;
  to_node_id: string;
  condition_type: ConditionType;
  condition_value?: Record<string, any>;
  probability?: number;
}

export interface PlanExecution {
  execution_id: string;
  plan_id: string;
  node_id: string;
  action_id?: string;
  execution_status: 'pending' | 'executed' | 'skipped' | 'failed' | 'cancelled';
  actual_outcome?: string;
  actual_noc_value?: number;
  expected_noc_value?: number;
  deviation?: string;
  executed_at?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// 7. ni_learning — Feedback Learning
// ═══════════════════════════════════════════════════════════════════════════

export type SignalType = 'positive' | 'negative' | 'neutral' | 'mixed';
export type TargetType = 'rule' | 'weight' | 'edge' | 'probability' | 'attention';
export type ValidationStatus = 'pending' | 'validated' | 'rejected' | 'rolled_back';

export interface ReinforcementSignal {
  signal_id: string;
  episode_id?: string;
  action_id?: string;
  outcome_id?: string;
  reward: number; // -1.0 to 1.0
  signal_type: SignalType;
  target_node_id?: string;
  target_type: TargetType;
}

export interface WeightUpdate {
  update_id: string;
  signal_id: string;
  edge_id?: string;
  rule_id?: string;
  weight_id?: string;
  prior_id?: string;
  attention_weight_id?: string;
  old_value: number;
  new_value: number;
  delta: number;
  validation_status: ValidationStatus;
  validated_by?: string;
  validated_at?: string;
  rejection_reason?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// 8. ni_twin — Simulation Engine
// ═══════════════════════════════════════════════════════════════════════════

export type SimulationType = 'monte_carlo' | 'mcts' | 'deterministic' | 'counterfactual' | 'stress_test';

export interface SimulationRun {
  sim_id: string;
  patient_state_id: string;
  plan_id?: string;
  reasoning_session_id?: string;
  simulation_type: SimulationType;
  iterations: number;
  started_at: string;
  completed_at?: string;
}

export interface SimulationResult {
  result_id: string;
  sim_id: string;
  trajectory_id?: string;
  outcome_type: OutcomeType;
  predicted_noc_code?: string;
  predicted_value?: number;
  probability?: number;
  confidence_interval?: { lower: number; upper: number };
  time_to_outcome_h?: number;
}

export interface Counterfactual {
  cf_id: string;
  sim_id: string;
  base_scenario: Record<string, any>;
  counterfactual_scenario: Record<string, any>;
  divergence_point: string;
  base_outcome?: Record<string, any>;
  cf_outcome?: Record<string, any>;
  causal_effect?: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// 9. ni_council — Multi-Agent Council
// ═══════════════════════════════════════════════════════════════════════════

export type AgentType = 'assessment' | 'nanda' | 'nic' | 'noc' | 'safety' | 'medication' | 'evidence' | 'consensus' | 'specialist';
export type AgentRole = 'primary' | 'secondary' | 'veto_holder' | 'arbitrator';
export type ConsensusProtocolType = 'majority' | 'weighted_majority' | 'unanimous' | 'threshold' | 'deliberative';
export type ConsensusType = 'reached' | 'partial' | 'no_consensus' | 'vetoed';

export interface CouncilAgent {
  agent_id: string;
  agent_type: AgentType;
  agent_name: string;
  specialty?: string;
  model_version?: string;
  voting_weight: number;
  veto_eligible: boolean;
  active: boolean;
}

export interface DeliberationEntry {
  deliberation_id: string;
  session_id: string;
  agent_id: string;
  round_number: number;
  position: {
    agree_with?: string;
    diagnosis?: string;
    intervention?: string;
    concerns?: string[];
    veto?: boolean;
    confidence: number;
  };
  argument_text?: string;
  evidence_refs?: string[];
  changed_from_prev: boolean;
}

export interface ConsensusResult {
  result_id: string;
  session_id: string;
  consensus_type: ConsensusType;
  agreement_score: number;
  rounds: number;
  final_decision?: Record<string, any>;
  dissent_summary?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// 10. API Types — Request/Response
// ═══════════════════════════════════════════════════════════════════════════

export interface StartReasoningRequest {
  patient_identifier: string;
  case_id?: string;
  reasoning_type: ReasoningType;
  observations: Array<{
    type: string;
    code?: string;
    value: any;
  }>;
  context?: {
    ward?: string;
    population?: string;
    shift?: string;
  };
}

export interface ReasoningResponse {
  session_id: string;
  status: ReasoningStatus;
  diagnosis: {
    nanda_code: string;
    label: string;
    probability: number;
    confidence_interval: [number, number];
    entropy: number;
  };
  alternatives: Array<{
    nanda_code: string;
    probability: number;
  }>;
  plan: {
    primary_nic: string;
    adjunct_nic?: string;
    expected_noc: {
      code: string;
      from: number;
      to: number;
      horizon: string;
    };
  };
  council: {
    agreement_score: number;
    rounds: number;
    dissent: Array<{
      agent: string;
      concern: string;
    }>;
  };
  explanation_id: string;
  trace_url: string;
}

export interface FeedbackRequest {
  decision: 'accept' | 'modify' | 'reject' | 'escalate';
  modified_diagnosis?: string;
  modified_interventions?: string[];
  reason?: string;
  reviewer_id: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// 11. Explanation Types
// ═══════════════════════════════════════════════════════════════════════════

export type ExplanationLevel = 'summary' | 'detailed' | 'full_trace' | 'machine';

export interface Explanation {
  explanation_id: string;
  session_id: string;
  level: ExplanationLevel;
  diagnosis: {
    nanda_code: string;
    probability: number;
    confidence_interval: [number, number];
    entropy: number;
  };
  observations_used: Array<{
    ref: string;
    label: string;
    attention: number;
  }>;
  observations_filtered: Array<{
    ref: string;
    label: string;
    attention: number;
    reason: string;
  }>;
  evidence_for: Array<{
    grade?: string;
    source?: string;
    description: string;
  }>;
  evidence_against: Array<{
    description: string;
  }>;
  alternatives: Array<{
    nanda_code: string;
    probability: number;
    rejection_reason: string;
  }>;
  council: {
    agreement_score: number;
    rounds: number;
    dissent: Array<{
      agent: string;
      concern: string;
    }>;
  };
  plan: {
    primary_nic: string;
    adjunct_nic?: string;
    expected_noc: {
      code: string;
      from: number;
      to: number;
      horizon: string;
    };
    contingency?: string;
    escalation?: string;
  };
  trace_steps: Array<{
    order: number;
    type: StepType;
    summary: string;
  }>;
}
