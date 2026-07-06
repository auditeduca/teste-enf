-- ═══════════════════════════════════════════════════════════════════════════
-- NIFS v5.0 — Cognitive Layers DDL
-- Generated from: NIFS-600 (Clinical Reasoning) + NIFS-700 (AI Architecture)
-- Database: PostgreSQL 15+ with pgvector extension
-- 
-- This file is GENERATED from the NIFS specification.
-- Do not edit manually — edit the spec, regenerate the DDL.
-- ═══════════════════════════════════════════════════════════════════════════

-- Required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pgvector";

-- ═══════════════════════════════════════════════════════════════════════════
-- 1. ni_reasoning — Clinical Reasoning Engine ⭐⭐⭐⭐⭐
-- ═══════════════════════════════════════════════════════════════════════════

CREATE SCHEMA IF NOT EXISTS ni_reasoning;

-- 1.1 Reasoning Sessions
CREATE TABLE ni_reasoning.sessions (
    session_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_identifier  VARCHAR(64) NOT NULL,
    case_id             UUID REFERENCES ni.cases(case_id),
    council_session_id  UUID REFERENCES ni_council.sessions(session_id),
    reasoning_type      VARCHAR(32) NOT NULL DEFAULT 'diagnostic',
    status              VARCHAR(16) NOT NULL DEFAULT 'active',
    started_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at        TIMESTAMPTZ,
    final_nanda_code    VARCHAR(8) REFERENCES ni.nanda_diagnoses(nanda_code),
    final_confidence    NUMERIC,
    final_entropy       NUMERIC,
    world_state_id      UUID,  -- FK to ni_world.patient_states (created later)
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_reasoning_status CHECK (
        status IN ('active', 'awaiting_council', 'awaiting_human', 
                   'completed', 'aborted', 'reassessing')
    ),
    CONSTRAINT chk_reasoning_type CHECK (
        reasoning_type IN ('diagnostic', 'therapeutic', 'prioritization', 'escalation')
    )
);

CREATE INDEX idx_reasoning_sessions_patient ON ni_reasoning.sessions(patient_identifier);
CREATE INDEX idx_reasoning_sessions_status ON ni_reasoning.sessions(status);
CREATE INDEX idx_reasoning_sessions_case ON ni_reasoning.sessions(case_id);

-- 1.2 Reasoning Steps
CREATE TABLE ni_reasoning.steps (
    step_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID NOT NULL REFERENCES ni_reasoning.sessions(session_id) ON DELETE CASCADE,
    step_order          SMALLINT NOT NULL,
    step_type           VARCHAR(32) NOT NULL,
    step_label          VARCHAR(128),
    input_data          JSONB,
    output_data         JSONB,
    node_id             VARCHAR(64) REFERENCES ni_graph.nodes(node_id),
    duration_ms         INTEGER,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_step_type CHECK (
        step_type IN ('observation', 'hypothesis', 'evidence_for', 'evidence_against',
                      'bayesian_update', 'ranking', 'council', 'planning', 
                      'explainability', 'safety', 'output')
    ),
    CONSTRAINT uq_reasoning_step_order UNIQUE (session_id, step_order)
);

CREATE INDEX idx_reasoning_steps_session ON ni_reasoning.steps(session_id);

-- 1.3 Reasoning Trace
CREATE TABLE ni_reasoning.trace (
    trace_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID NOT NULL REFERENCES ni_reasoning.sessions(session_id) ON DELETE CASCADE,
    step_id             UUID REFERENCES ni_reasoning.steps(step_id) ON DELETE CASCADE,
    trace_order         SMALLINT NOT NULL,
    trace_type          VARCHAR(32) NOT NULL,
    content             TEXT NOT NULL,
    evidence_ref        UUID REFERENCES ni_mining.graded_evidence(grade_id),
    confidence          NUMERIC,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_trace_type CHECK (
        trace_type IN ('thought', 'evaluation', 'inference', 'decision', 'evidence_for', 'evidence_against')
    )
);

CREATE INDEX idx_reasoning_trace_session ON ni_reasoning.trace(session_id);

-- 1.4 Reasoning Hypotheses
CREATE TABLE ni_reasoning.hypotheses (
    hypothesis_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID NOT NULL REFERENCES ni_reasoning.sessions(session_id) ON DELETE CASCADE,
    nanda_code          VARCHAR(8) NOT NULL REFERENCES ni.nanda_diagnoses(nanda_code),
    prior_probability   NUMERIC NOT NULL,
    posterior_probability NUMERIC,
    confidence_interval_low  NUMERIC,
    confidence_interval_high NUMERIC,
    entropy             NUMERIC,
    generation_strategy VARCHAR(32),
    rank                SMALLINT,
    status              VARCHAR(16) DEFAULT 'active',
    rejection_reason    TEXT,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_hypothesis_prob CHECK (prior_probability >= 0 AND prior_probability <= 1),
    CONSTRAINT chk_hypothesis_strategy CHECK (
        generation_strategy IN ('graph_traversal', 'memory_retrieval', 'rule_matching', 'hybrid')
    )
);

CREATE INDEX idx_reasoning_hypotheses_session ON ni_reasoning.hypotheses(session_id);
CREATE INDEX idx_reasoning_hypotheses_nanda ON ni_reasoning.hypotheses(nanda_code);

-- 1.5 Reasoning Scores
CREATE TABLE ni_reasoning.scores (
    score_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID NOT NULL REFERENCES ni_reasoning.sessions(session_id) ON DELETE CASCADE,
    step_id             UUID REFERENCES ni_reasoning.steps(step_id) ON DELETE CASCADE,
    nanda_code          VARCHAR(8) REFERENCES ni.nanda_diagnoses(nanda_code),
    nic_code            VARCHAR(8) REFERENCES ni.nic_interventions(nic_code),
    noc_code            VARCHAR(8) REFERENCES ni.noc_outcomes(noc_code),
    score_type          VARCHAR(32) NOT NULL,
    score_value         NUMERIC NOT NULL,
    score_basis         VARCHAR(32) NOT NULL DEFAULT 'rule_based',
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_score_type CHECK (
        score_type IN ('probability', 'utility', 'salience', 'urgency', 'priority', 'attention')
    ),
    CONSTRAINT chk_score_basis CHECK (
        score_basis IN ('rule_based', 'bayesian', 'learned', 'heuristic', 'empirical')
    )
);

-- ═══════════════════════════════════════════════════════════════════════════
-- 2. ni_memory — Episodic Memory ⭐⭐⭐⭐⭐
-- ═══════════════════════════════════════════════════════════════════════════

CREATE SCHEMA IF NOT EXISTS ni_memory;

-- 2.1 Episodes
CREATE TABLE ni_memory.episodes (
    episode_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_identifier  VARCHAR(64) NOT NULL,
    case_id             UUID REFERENCES ni.cases(case_id),
    episode_type        VARCHAR(32) NOT NULL,
    started_at          TIMESTAMPTZ NOT NULL,
    ended_at            TIMESTAMPTZ,
    outcome_summary     TEXT,
    success_score       NUMERIC,
    similarity_embedding VECTOR(1536),
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_episode_type CHECK (
        episode_type IN ('admission', 'intervention', 'crisis', 'recovery', 'discharge', 'longitudinal')
    ),
    CONSTRAINT chk_success_score CHECK (success_score >= 0 AND success_score <= 1)
);

CREATE INDEX idx_memory_episodes_patient ON ni_memory.episodes(patient_identifier);
CREATE INDEX idx_memory_episodes_type ON ni_memory.episodes(episode_type);
CREATE INDEX idx_memory_episodes_embedding ON ni_memory.episodes 
    USING ivfflat (similarity_embedding vector_cosine_ops) WITH (lists = 100);

-- 2.2 Episode Observations
CREATE TABLE ni_memory.observations (
    observation_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    episode_id          UUID NOT NULL REFERENCES ni_memory.episodes(episode_id) ON DELETE CASCADE,
    observed_at         TIMESTAMPTZ NOT NULL,
    observation_type    VARCHAR(32) NOT NULL,
    observation_value   JSONB NOT NULL,
    attention_score     NUMERIC,
    node_id             VARCHAR(64) REFERENCES ni_graph.nodes(node_id),
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64)
);

CREATE INDEX idx_memory_observations_episode ON ni_memory.observations(episode_id);

-- 2.3 Episode Actions
CREATE TABLE ni_memory.actions (
    action_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    episode_id          UUID NOT NULL REFERENCES ni_memory.episodes(episode_id) ON DELETE CASCADE,
    action_type         VARCHAR(32) NOT NULL,
    nic_code            VARCHAR(8) REFERENCES ni.nic_interventions(nic_code),
    protocol_id         UUID REFERENCES ni_protocol.protocols(protocol_id),
    action_data         JSONB,
    reasoning_session_id UUID REFERENCES ni_reasoning.sessions(session_id),
    executed_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64)
);

CREATE INDEX idx_memory_actions_episode ON ni_memory.actions(episode_id);

-- 2.4 Episode Outcomes
CREATE TABLE ni_memory.outcomes (
    outcome_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    episode_id          UUID NOT NULL REFERENCES ni_memory.episodes(episode_id) ON DELETE CASCADE,
    action_id           UUID REFERENCES ni_memory.actions(action_id),
    noc_code            VARCHAR(8) REFERENCES ni.noc_outcomes(noc_code),
    outcome_type        VARCHAR(32) NOT NULL,
    outcome_value       NUMERIC,
    expected_value      NUMERIC,
    surprise_score      NUMERIC,
    measured_at         TIMESTAMPTZ NOT NULL,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_outcome_type CHECK (
        outcome_type IN ('improved', 'unchanged', 'deteriorated', 'resolved', 'adverse')
    )
);

CREATE INDEX idx_memory_outcomes_episode ON ni_memory.outcomes(episode_id);

-- 2.5 Learnings
CREATE TABLE ni_memory.learnings (
    learning_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    episode_id          UUID NOT NULL REFERENCES ni_memory.episodes(episode_id) ON DELETE CASCADE,
    learning_type       VARCHAR(32) NOT NULL,
    description         TEXT NOT NULL,
    weight_adjustment   NUMERIC,
    applied             BOOLEAN NOT NULL DEFAULT FALSE,
    applied_at          TIMESTAMPTZ,
    model_adjustment_id UUID,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_learning_type CHECK (
        learning_type IN ('effective_intervention', 'ineffective_intervention', 
                          'adverse_reaction', 'time_pattern', 'context_pattern')
    )
);

-- ═══════════════════════════════════════════════════════════════════════════
-- 3. ni_world — World Model ⭐⭐⭐⭐
-- ═══════════════════════════════════════════════════════════════════════════

CREATE SCHEMA IF NOT EXISTS ni_world;

-- 3.1 Patient States
CREATE TABLE ni_world.patient_states (
    state_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_identifier  VARCHAR(64) NOT NULL,
    severity_level      VARCHAR(16),
    acuity_score        NUMERIC,
    isolation_status    VARCHAR(16),
    mobility_status     VARCHAR(16),
    consciousness_level VARCHAR(16),
    state_data          JSONB,
    captured_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_severity CHECK (severity_level IN ('stable', 'moderate', 'critical', 'terminal'))
);

-- 3.2 Hospital States
CREATE TABLE ni_world.hospital_states (
    state_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hospital_identifier VARCHAR(64) NOT NULL,
    occupancy_rate      NUMERIC,
    er_status           VARCHAR(16),
    bed_availability    INTEGER,
    captured_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64)
);

-- 3.3 Ward States
CREATE TABLE ni_world.ward_states (
    state_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ward_identifier     VARCHAR(64) NOT NULL,
    ward_type           VARCHAR(32),
    occupancy           INTEGER,
    nurse_patient_ratio NUMERIC,
    isolation_rooms_available INTEGER,
    captured_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64)
);

-- 3.4 Resource States
CREATE TABLE ni_world.resource_states (
    state_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ward_identifier     VARCHAR(64) NOT NULL,
    resource_type       VARCHAR(32) NOT NULL,
    available           INTEGER NOT NULL DEFAULT 0,
    in_use              INTEGER NOT NULL DEFAULT 0,
    total               INTEGER NOT NULL DEFAULT 0,
    captured_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_resource_type CHECK (
        resource_type IN ('infusion_pump', 'ventilator', 'monitor', 'defibrillator', 
                          'bed', 'isolation_room', 'crash_cart', 'warmer')
    )
);

-- 3.5 Staff States
CREATE TABLE ni_world.staff_states (
    state_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ward_identifier     VARCHAR(64) NOT NULL,
    shift_type          VARCHAR(16),
    nurses_on_duty      INTEGER,
    nurses_available    INTEGER,
    specialty_coverage  JSONB,
    captured_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_shift_type CHECK (shift_type IN ('morning', 'evening', 'night'))
);

-- ═══════════════════════════════════════════════════════════════════════════
-- 4. ni_attention — Clinical Attention ⭐⭐⭐⭐
-- ═══════════════════════════════════════════════════════════════════════════

CREATE SCHEMA IF NOT EXISTS ni_attention;

-- 4.1 Attention Signals
CREATE TABLE ni_attention.signals (
    signal_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reasoning_session_id UUID REFERENCES ni_reasoning.sessions(session_id) ON DELETE CASCADE,
    patient_identifier  VARCHAR(64),
    observation_ref     VARCHAR(128),
    observation_type    VARCHAR(32),
    clinical_domain     VARCHAR(32),
    attention_score     NUMERIC NOT NULL,
    salience            NUMERIC,
    priority            SMALLINT,
    urgency             SMALLINT,
    components          JSONB,
    ignored             BOOLEAN NOT NULL DEFAULT FALSE,
    ignore_reason       VARCHAR(64),
    focus_window        VARCHAR(32),
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_attention_score CHECK (attention_score >= 0 AND attention_score <= 1),
    CONSTRAINT chk_priority CHECK (priority >= 1 AND priority <= 5),
    CONSTRAINT chk_urgency CHECK (urgency >= 1 AND urgency <= 5)
);

CREATE INDEX idx_attention_signals_session ON ni_attention.signals(reasoning_session_id);
CREATE INDEX idx_attention_signals_ignored ON ni_attention.signals(ignored);

-- 4.2 Attention Weights (learned)
CREATE TABLE ni_attention.weights (
    weight_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    context_type        VARCHAR(32) NOT NULL,
    context_value       VARCHAR(64) NOT NULL,
    observation_type    VARCHAR(32) NOT NULL,
    clinical_domain     VARCHAR(32),
    base_weight         NUMERIC NOT NULL DEFAULT 0.50,
    learned_weight      NUMERIC NOT NULL DEFAULT 0.50,
    last_updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT uq_attention_weight UNIQUE (context_type, context_value, observation_type)
);

-- ═══════════════════════════════════════════════════════════════════════════
-- 5. ni_prob extensions — Uncertainty Model ⭐⭐⭐⭐⭐
-- ═══════════════════════════════════════════════════════════════════════════

-- 5.1 Prior Beliefs
CREATE TABLE ni_prob.prior_beliefs (
    prior_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_id             VARCHAR(64) NOT NULL REFERENCES ni_graph.nodes(node_id),
    population_id       UUID REFERENCES ni.populations(population_id),
    prior_type          VARCHAR(16) NOT NULL DEFAULT 'uniform',
    prior_value         NUMERIC NOT NULL,
    prior_source        VARCHAR(32) NOT NULL DEFAULT 'default',
    evidence_grade      CHAR(1),
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_prior_type CHECK (prior_type IN ('uniform', 'informative', 'empirical', 'literature')),
    CONSTRAINT chk_prior_source CHECK (
        prior_source IN ('literature', 'expert', 'empirical', 'default')
    )
);

CREATE INDEX idx_prior_beliefs_node ON ni_prob.prior_beliefs(node_id);
CREATE INDEX idx_prior_beliefs_population ON ni_prob.prior_beliefs(population_id);

-- 5.2 Belief Updates (Bayesian update log)
CREATE TABLE ni_prob.belief_updates (
    update_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID NOT NULL REFERENCES ni_reasoning.sessions(session_id) ON DELETE CASCADE,
    hypothesis_id       UUID REFERENCES ni_reasoning.hypotheses(hypothesis_id),
    node_id             VARCHAR(64) REFERENCES ni_graph.nodes(node_id),
    prior_value         NUMERIC NOT NULL,
    likelihood          NUMERIC,
    posterior_value     NUMERIC NOT NULL,
    bayes_factor        NUMERIC,
    evidence_ref        UUID REFERENCES ni_mining.graded_evidence(grade_id),
    update_order        SMALLINT NOT NULL,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64)
);

CREATE INDEX idx_belief_updates_session ON ni_prob.belief_updates(session_id);

-- 5.3 Ambiguity Flags
CREATE TABLE ni_prob.ambiguity_flags (
    flag_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID NOT NULL REFERENCES ni_reasoning.sessions(session_id) ON DELETE CASCADE,
    flag_type           VARCHAR(32) NOT NULL,
    flag_value          NUMERIC,
    recommended_action  VARCHAR(32),
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_flag_type CHECK (
        flag_type IN ('low_confidence', 'high_entropy', 'conflicting_evidence', 'insufficient_data')
    )
);

-- 5.4 Uncertainty Distributions
CREATE TABLE ni_prob.uncertainty_distributions (
    distribution_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id            UUID NOT NULL REFERENCES ni_prob.probability_models(model_id),
    node_id             VARCHAR(64) REFERENCES ni_graph.nodes(node_id),
    distribution_type   VARCHAR(16) NOT NULL,
    parameters          JSONB NOT NULL,
    sample_count        INTEGER DEFAULT 0,
    last_updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_dist_type CHECK (
        distribution_type IN ('normal', 'beta', 'categorical', 'uniform', 'lognormal', 'bernoulli')
    )
);

-- 5.5 Confidence Intervals
CREATE TABLE ni_prob.confidence_intervals (
    ci_id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id            UUID NOT NULL REFERENCES ni_prob.probability_models(model_id),
    node_id             VARCHAR(64) REFERENCES ni_graph.nodes(node_id),
    lower_bound         NUMERIC NOT NULL,
    upper_bound         NUMERIC NOT NULL,
    confidence_level    NUMERIC NOT NULL DEFAULT 0.95,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_ci_bounds CHECK (lower_bound <= upper_bound),
    CONSTRAINT chk_ci_level CHECK (confidence_level > 0 AND confidence_level < 1)
);

-- ═══════════════════════════════════════════════════════════════════════════
-- 6. ni_planner — Planner ⭐⭐⭐⭐
-- ═══════════════════════════════════════════════════════════════════════════

CREATE SCHEMA IF NOT EXISTS ni_planner;

-- 6.1 Plans
CREATE TABLE ni_planner.plans (
    plan_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reasoning_session_id UUID REFERENCES ni_reasoning.sessions(session_id),
    case_id             UUID REFERENCES ni.cases(case_id),
    care_plan_id        UUID REFERENCES ni.care_plans(plan_id),
    plan_type           VARCHAR(32) NOT NULL,
    goal_noc_code       VARCHAR(8) REFERENCES ni.noc_outcomes(noc_code),
    status              VARCHAR(16) NOT NULL DEFAULT 'proposed',
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_plan_type CHECK (
        plan_type IN ('intervention_sequence', 'contingency', 'escalation', 'monitoring')
    ),
    CONSTRAINT chk_plan_status CHECK (
        status IN ('proposed', 'active', 'completed', 'abandoned', 'revising')
    )
);

-- 6.2 Plan Nodes
CREATE TABLE ni_planner.plan_nodes (
    node_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id             UUID NOT NULL REFERENCES ni_planner.plans(plan_id) ON DELETE CASCADE,
    node_type           VARCHAR(32) NOT NULL,
    nic_code            VARCHAR(8) REFERENCES ni.nic_interventions(nic_code),
    protocol_id         UUID REFERENCES ni_protocol.protocols(protocol_id),
    expected_noc_delta  NUMERIC,
    node_order          SMALLINT NOT NULL,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_plan_node_type CHECK (
        node_type IN ('action', 'evaluation', 'branch', 'terminal', 'escalation', 'de_escalation')
    )
);

CREATE INDEX idx_planner_nodes_plan ON ni_planner.plan_nodes(plan_id);

-- 6.3 Plan Edges (conditional transitions)
CREATE TABLE ni_planner.plan_edges (
    edge_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id             UUID NOT NULL REFERENCES ni_planner.plans(plan_id) ON DELETE CASCADE,
    from_node_id        UUID NOT NULL REFERENCES ni_planner.plan_nodes(node_id) ON DELETE CASCADE,
    to_node_id          UUID NOT NULL REFERENCES ni_planner.plan_nodes(node_id) ON DELETE CASCADE,
    condition_type      VARCHAR(32) NOT NULL,
    condition_value     JSONB,
    probability         NUMERIC,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_condition_type CHECK (
        condition_type IN ('success', 'failure', 'deterioration', 'no_change', 
                          'timeout', 'adverse_event', 'escalation_trigger')
    ),
    CONSTRAINT chk_edge_probability CHECK (probability >= 0 AND probability <= 1)
);

-- 6.4 Plan Executions
CREATE TABLE ni_planner.plan_executions (
    execution_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id             UUID NOT NULL REFERENCES ni_planner.plans(plan_id),
    node_id             UUID NOT NULL REFERENCES ni_planner.plan_nodes(node_id),
    action_id           UUID REFERENCES ni_memory.actions(action_id),
    execution_status    VARCHAR(16) NOT NULL DEFAULT 'pending',
    actual_outcome      VARCHAR(32),
    actual_noc_value    NUMERIC,
    expected_noc_value  NUMERIC,
    deviation           TEXT,
    executed_at         TIMESTAMPTZ,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_exec_status CHECK (
        execution_status IN ('pending', 'executed', 'skipped', 'failed', 'cancelled')
    )
);

-- ═══════════════════════════════════════════════════════════════════════════
-- 7. ni_learning extensions — Feedback Learning ⭐⭐⭐⭐
-- ═══════════════════════════════════════════════════════════════════════════

-- 7.1 Reinforcement Signals
CREATE TABLE ni_learning.reinforcement_signals (
    signal_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    episode_id          UUID REFERENCES ni_memory.episodes(episode_id),
    action_id           UUID REFERENCES ni_memory.actions(action_id),
    outcome_id          UUID REFERENCES ni_memory.outcomes(outcome_id),
    reward              NUMERIC NOT NULL,
    signal_type         VARCHAR(32) NOT NULL,
    target_node_id      VARCHAR(64) REFERENCES ni_graph.nodes(node_id),
    target_type         VARCHAR(16) NOT NULL,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_reward CHECK (reward >= -1 AND reward <= 1),
    CONSTRAINT chk_signal_type CHECK (signal_type IN ('positive', 'negative', 'neutral', 'mixed')),
    CONSTRAINT chk_target_type CHECK (target_type IN ('rule', 'weight', 'edge', 'probability', 'attention'))
);

-- 7.2 Weight Updates
CREATE TABLE ni_learning.weight_updates (
    update_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    signal_id           UUID NOT NULL REFERENCES ni_learning.reinforcement_signals(signal_id),
    edge_id             UUID REFERENCES ni_graph.edges(edge_id),
    rule_id             UUID REFERENCES ni_rules.decision_rules(rule_id),
    weight_id           UUID REFERENCES ni_rules.rule_weights(weight_id),
    prior_id            UUID REFERENCES ni_prob.prior_beliefs(prior_id),
    attention_weight_id UUID,
    old_value           NUMERIC NOT NULL,
    new_value           NUMERIC NOT NULL,
    delta               NUMERIC NOT NULL,
    validation_status   VARCHAR(16) NOT NULL DEFAULT 'pending',
    validated_by        VARCHAR(64),
    validated_at        TIMESTAMPTZ,
    rejection_reason    TEXT,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_validation_status CHECK (
        validation_status IN ('pending', 'validated', 'rejected', 'rolled_back')
    ),
    CONSTRAINT chk_weight_delta CHECK (delta >= -0.15 AND delta <= 0.15)
);

CREATE INDEX idx_weight_updates_status ON ni_learning.weight_updates(validation_status);

-- 7.3 Learning Curves
CREATE TABLE ni_learning.learning_curves (
    curve_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    component           VARCHAR(32) NOT NULL,
    metric_name         VARCHAR(64) NOT NULL,
    metric_value        NUMERIC NOT NULL,
    measured_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    target_value        NUMERIC,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64)
);

CREATE INDEX idx_learning_curves_component ON ni_learning.learning_curves(component, metric_name);

-- ═══════════════════════════════════════════════════════════════════════════
-- 8. ni_twin extensions — Simulation Engine ⭐⭐⭐
-- ═══════════════════════════════════════════════════════════════════════════

-- 8.1 Simulation Runs
CREATE TABLE ni_twin.simulation_runs (
    sim_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_state_id    UUID NOT NULL REFERENCES ni_twin.patient_states(state_id),
    plan_id             UUID REFERENCES ni_planner.plans(plan_id),
    reasoning_session_id UUID REFERENCES ni_reasoning.sessions(session_id),
    simulation_type     VARCHAR(32) NOT NULL,
    iterations          INTEGER NOT NULL DEFAULT 1000,
    started_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at        TIMESTAMPTZ,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_sim_type CHECK (
        simulation_type IN ('monte_carlo', 'mcts', 'deterministic', 'counterfactual', 'stress_test')
    )
);

-- 8.2 Simulation Results
CREATE TABLE ni_twin.simulation_results (
    result_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sim_id              UUID NOT NULL REFERENCES ni_twin.simulation_runs(sim_id) ON DELETE CASCADE,
    trajectory_id       UUID REFERENCES ni_twin.trajectories(trajectory_id),
    outcome_type        VARCHAR(32) NOT NULL,
    predicted_noc_code  VARCHAR(8) REFERENCES ni.noc_outcomes(noc_code),
    predicted_value     NUMERIC,
    probability         NUMERIC,
    confidence_interval JSONB,
    time_to_outcome_h   NUMERIC,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_sim_outcome CHECK (
        outcome_type IN ('improved', 'unchanged', 'deteriorated', 'adverse')
    )
);

CREATE INDEX idx_sim_results_sim ON ni_twin.simulation_results(sim_id);

-- 8.3 Counterfactuals
CREATE TABLE ni_twin.counterfactuals (
    cf_id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sim_id              UUID NOT NULL REFERENCES ni_twin.simulation_runs(sim_id) ON DELETE CASCADE,
    base_scenario       JSONB NOT NULL,
    counterfactual_scenario JSONB NOT NULL,
    divergence_point    TEXT,
    base_outcome        JSONB,
    cf_outcome          JSONB,
    causal_effect       NUMERIC,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64)
);

-- 8.4 Simulation Validations
CREATE TABLE ni_twin.simulation_validations (
    validation_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sim_id              UUID NOT NULL REFERENCES ni_twin.simulation_runs(sim_id),
    predicted_value     NUMERIC NOT NULL,
    actual_value        NUMERIC NOT NULL,
    prediction_error    NUMERIC NOT NULL,
    is_calibrated       BOOLEAN NOT NULL,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64)
);

-- ═══════════════════════════════════════════════════════════════════════════
-- 9. ni_council extensions — Multi-Agent Council ⭐⭐⭐⭐⭐
-- ═══════════════════════════════════════════════════════════════════════════

-- 9.1 Agents
CREATE TABLE ni_council.agents (
    agent_id            VARCHAR(64) PRIMARY KEY,
    agent_type          VARCHAR(32) NOT NULL,
    agent_name          VARCHAR(128) NOT NULL,
    specialty           VARCHAR(64),
    model_version       VARCHAR(32),
    voting_weight       NUMERIC NOT NULL DEFAULT 1.0,
    veto_eligible       BOOLEAN NOT NULL DEFAULT FALSE,
    active              BOOLEAN NOT NULL DEFAULT TRUE,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_agent_type CHECK (
        agent_type IN ('assessment', 'nanda', 'nic', 'noc', 'safety', 
                       'medication', 'evidence', 'consensus', 'specialist')
    )
);

-- 9.2 Agent Roles (per session)
CREATE TABLE ni_council.agent_roles (
    role_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id            VARCHAR(64) NOT NULL REFERENCES ni_council.agents(agent_id),
    session_id          UUID NOT NULL REFERENCES ni_council.sessions(session_id) ON DELETE CASCADE,
    role                VARCHAR(32) NOT NULL DEFAULT 'primary',
    voting_weight       NUMERIC NOT NULL DEFAULT 1.0,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_agent_role CHECK (role IN ('primary', 'secondary', 'veto_holder', 'arbitrator'))
);

-- 9.3 Consensus Protocols
CREATE TABLE ni_council.consensus_protocols (
    protocol_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID NOT NULL REFERENCES ni_council.sessions(session_id) ON DELETE CASCADE,
    protocol_type       VARCHAR(32) NOT NULL DEFAULT 'weighted_majority',
    threshold           NUMERIC NOT NULL DEFAULT 0.60,
    quorum              INTEGER NOT NULL DEFAULT 6,
    timeout_seconds     INTEGER NOT NULL DEFAULT 30,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_protocol_type CHECK (
        protocol_type IN ('majority', 'weighted_majority', 'unanimous', 'threshold', 'deliberative')
    )
);

-- 9.4 Deliberation Log
CREATE TABLE ni_council.deliberation_log (
    deliberation_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID NOT NULL REFERENCES ni_council.sessions(session_id) ON DELETE CASCADE,
    agent_id            VARCHAR(64) NOT NULL REFERENCES ni_council.agents(agent_id),
    round_number        SMALLINT NOT NULL,
    position            JSONB NOT NULL,
    argument_text       TEXT,
    evidence_refs       UUID[],
    confidence          NUMERIC,
    changed_from_prev   BOOLEAN NOT NULL DEFAULT FALSE,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64)
);

CREATE INDEX idx_deliberation_session ON ni_council.deliberation_log(session_id, round_number);

-- 9.5 Consensus Results
CREATE TABLE ni_council.consensus_results (
    result_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID NOT NULL REFERENCES ni_council.sessions(session_id) ON DELETE CASCADE,
    consensus_type      VARCHAR(16) NOT NULL,
    agreement_score     NUMERIC NOT NULL,
    rounds              SMALLINT NOT NULL,
    final_decision      JSONB,
    dissent_summary     TEXT,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_consensus_type CHECK (consensus_type IN ('reached', 'partial', 'no_consensus', 'vetoed'))
);

-- ═══════════════════════════════════════════════════════════════════════════
-- 10. ni_temporal extensions — Temporal Graph ⭐⭐⭐⭐
-- ═══════════════════════════════════════════════════════════════════════════

-- 10.1 Event Sequences
CREATE TABLE ni_temporal.event_sequences (
    sequence_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_identifier  VARCHAR(64) NOT NULL,
    sequence_type       VARCHAR(32) NOT NULL,
    started_at          TIMESTAMPTZ NOT NULL,
    ended_at            TIMESTAMPTZ,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_sequence_type CHECK (
        sequence_type IN ('deterioration', 'recovery', 'crisis', 'stabilization', 'oscillation')
    )
);

-- 10.2 Event Sequence Items
CREATE TABLE ni_temporal.event_sequence_items (
    item_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sequence_id         UUID NOT NULL REFERENCES ni_temporal.event_sequences(sequence_id) ON DELETE CASCADE,
    event_id            UUID NOT NULL REFERENCES ni_temporal.clinical_events(event_id),
    item_order          SMALLINT NOT NULL,
    delta_seconds       INTEGER,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64)
);

-- 10.3 Causal Chains
CREATE TABLE ni_temporal.causal_chains (
    chain_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_identifier  VARCHAR(64) NOT NULL,
    cause_event_id      UUID NOT NULL REFERENCES ni_temporal.clinical_events(event_id),
    effect_event_id     UUID NOT NULL REFERENCES ni_temporal.clinical_events(event_id),
    causality_type      VARCHAR(32) NOT NULL DEFAULT 'temporal_correlation',
    confidence          NUMERIC,
    evidence_ref        UUID REFERENCES ni_mining.graded_evidence(grade_id),
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_causality_type CHECK (
        causality_type IN ('direct', 'contributing', 'temporal_correlation', 'confounded')
    )
);

-- ═══════════════════════════════════════════════════════════════════════════
-- 11. ni_ai extensions — AI Readiness
-- ═══════════════════════════════════════════════════════════════════════════

-- 11.1 Model Registry
CREATE TABLE ni_ai.model_registry (
    model_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name          VARCHAR(128) NOT NULL,
    model_version       VARCHAR(32) NOT NULL,
    model_type          VARCHAR(32) NOT NULL,
    base_model          VARCHAR(64),
    status              VARCHAR(16) NOT NULL DEFAULT 'draft',
    f1_score            NUMERIC,
    brier_score         NUMERIC,
    latency_ms          INTEGER,
    deployed_at         TIMESTAMPTZ,
    config              JSONB,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64),
    
    CONSTRAINT chk_model_status CHECK (status IN ('draft', 'experiment', 'staging', 'production', 'deprecated')),
    CONSTRAINT uq_model_name_version UNIQUE (model_name, model_version)
);

-- 11.2 Agent Performance Metrics
CREATE TABLE ni_council.agent_performance (
    performance_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id            VARCHAR(64) NOT NULL REFERENCES ni_council.agents(agent_id),
    metric_name         VARCHAR(64) NOT NULL,
    metric_value        NUMERIC NOT NULL,
    measured_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(64)
);

CREATE INDEX idx_agent_perf_agent ON ni_council.agent_performance(agent_id, metric_name);

-- ═══════════════════════════════════════════════════════════════════════════
-- END OF COGNITIVE LAYERS DDL v5.0
-- 
-- Summary:
--   New schemas:     5 (ni_reasoning, ni_memory, ni_world, ni_attention, ni_planner)
--   Extended schemas: 5 (ni_prob, ni_learning, ni_twin, ni_council, ni_temporal, ni_ai)
--   New tables:      33
--   New indexes:     18
--   New constraints: 25+
--   Extensions:      pgvector (for memory embeddings)
--
-- Dependencies (must exist before this DDL):
--   ni.* (core tables)
--   ni_graph.* (knowledge graph)
--   ni_cog.* (cognitive/knowledge)
--   ni_council.sessions (council base)
--   ni_mining.graded_evidence (evidence)
--   ni_prob.probability_models (probability base)
--   ni_protocol.protocols (protocols)
--   ni_rules.* (decision rules)
--   ni_twin.patient_states (twin base)
--   ni_temporal.clinical_events (temporal base)
--   ni_ai.content_embeddings (embeddings base)
-- ═══════════════════════════════════════════════════════════════════════════
