-- ============================================================================
-- NURSING INTELLIGENCE SYSTEM — Cognitive Layers v5.0
-- 10 Camadas Cognitivas para evolução Nurse-PaLM
-- Autor: Leivis Melo | calculadorasdeenfermagem.com.br
-- Data: 2026-07-05
-- ============================================================================
-- Prioridades:
-- ⭐⭐⭐⭐⭐ 1. Clinical Reasoning Engine (ni_reasoning)
-- ⭐⭐⭐⭐⭐ 6. Uncertainty Model (ni_prob extensions)
-- ⭐⭐⭐⭐⭐ 2. Episodic Memory (ni_memory)
-- ⭐⭐⭐⭐  3. Temporal Graph (ni_temporal extensions)
-- ⭐⭐⭐⭐  7. Planner (ni_planner)
-- ⭐⭐⭐⭐  5. Clinical Attention (ni_attention)
-- ⭐⭐⭐⭐  4. World Model (ni_world)
-- ⭐⭐⭐⭐  8. Feedback Learning (ni_learning extensions)
-- ⭐⭐⭐⭐ 10. Multi-Agent Council (ni_council extensions)
-- ⭐⭐⭐   9. Simulation Engine (ni_twin extensions)
-- ============================================================================

-- ============================================================================
-- ⭐⭐⭐⭐⭐ LAYER 1: CLINICAL REASONING ENGINE (ni_reasoning)
-- ============================================================================
-- O pipeline cognitivo do enfermeiro: Observação → Hipótese → Evidência →
-- Diagnóstico → Plano → Monitoramento → Reavaliação
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS ni_reasoning;

-- ni_reasoning.sessions — Uma sessão de raciocínio clínico completo
CREATE TABLE ni_reasoning.sessions (
    session_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_identifier  VARCHAR(64),
    case_id             UUID REFERENCES ni.cases(case_id),
    council_session_id  UUID REFERENCES ni_council.sessions(session_id),
    reasoning_type      VARCHAR(32) NOT NULL,  -- diagnostic, therapeutic, prioritization, escalation, reassessment
    status              VARCHAR(16) NOT NULL DEFAULT 'active',  -- active, completed, aborted
    started_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at        TIMESTAMPTZ,
    final_nanda_code    VARCHAR(8) REFERENCES ni.nanda_diagnoses(nanda_code),
    final_confidence    NUMERIC,  -- 0.0–1.0
    context_snapshot    JSONB,  -- estado do mundo no momento (world model)
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_reasoning.steps — Cada passo no pipeline cognitivo
CREATE TABLE ni_reasoning.steps (
    step_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID NOT NULL REFERENCES ni_reasoning.sessions(session_id) ON DELETE CASCADE,
    step_order          SMALLINT NOT NULL,
    step_type           VARCHAR(32) NOT NULL,
    -- observation, hypothesis, evidence_for, evidence_against,
    -- differential, selection, planning, monitoring, reassessment, escalation
    step_label          VARCHAR(256),
    input_data          JSONB,   -- dados de entrada do passo
    output_data         JSONB,   -- resultado do passo
    node_id             VARCHAR(64) REFERENCES ni_graph.nodes(node_id),  -- nó do grafo associado
    duration_ms         INTEGER,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_reasoning.trace — Rastro explicável de cada inferência
CREATE TABLE ni_reasoning.trace (
    trace_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID NOT NULL REFERENCES ni_reasoning.sessions(session_id) ON DELETE CASCADE,
    step_id             UUID REFERENCES ni_reasoning.steps(step_id) ON DELETE CASCADE,
    trace_order         SMALLINT NOT NULL,
    trace_type          VARCHAR(32) NOT NULL,  -- thought, evaluation, inference, decision, justification
    content             TEXT NOT NULL,          -- descrição em linguagem natural
    evidence_ref        UUID REFERENCES ni_mining.graded_evidence(grade_id),
    rule_ref            UUID REFERENCES ni_rules.decision_rules(rule_id),
    confidence          NUMERIC,  -- 0.0–1.0
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_reasoning.scores — Probabilidades e scores em cada etapa
CREATE TABLE ni_reasoning.scores (
    score_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID NOT NULL REFERENCES ni_reasoning.sessions(session_id) ON DELETE CASCADE,
    step_id             UUID REFERENCES ni_reasoning.steps(step_id) ON DELETE CASCADE,
    nanda_code          VARCHAR(8) REFERENCES ni.nanda_diagnoses(nanda_code),
    nic_code            VARCHAR(8) REFERENCES ni.nic_interventions(nic_code),
    noc_code            VARCHAR(8) REFERENCES ni.noc_outcomes(noc_code),
    score_type          VARCHAR(32) NOT NULL,  -- probability, utility, salience, urgency, match
    score_value         NUMERIC NOT NULL,
    score_basis         VARCHAR(32) NOT NULL,  -- rule_based, bayesian, learned, heuristic, attention_weighted
    model_id            UUID REFERENCES ni_prob.probability_models(model_id),
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_reasoning.hypotheses — Hipóteses diagnósticas diferenciais
CREATE TABLE ni_reasoning.hypotheses (
    hypothesis_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID NOT NULL REFERENCES ni_reasoning.sessions(session_id) ON DELETE CASCADE,
    step_id             UUID REFERENCES ni_reasoning.steps(step_id) ON DELETE CASCADE,
    nanda_code          VARCHAR(8) NOT NULL REFERENCES ni.nanda_diagnoses(nanda_code),
    prior_probability   NUMERIC,   -- P(diagnóstico) antes da evidência
    posterior_probability NUMERIC,  -- P(diagnóstico|evidência) após atualização bayesiana
    evidence_for        JSONB,     -- lista de evidências a favor
    evidence_against    JSONB,     -- lista de evidências contra
    status              VARCHAR(16) DEFAULT 'active',  -- active, confirmed, ruled_out, deferred
    rank                SMALLINT,  -- 1 = mais provável
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- ⭐⭐⭐⭐⭐ LAYER 2: EPISODIC MEMORY (ni_memory)
-- ============================================================================
-- Memória de casos: Episode → Observation → Action → Outcome → Learning
-- Permite que o sistema "lembre" o que funcionou para pacientes similares
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS ni_memory;

-- ni_memory.episodes — Um episódio clínico completo
CREATE TABLE ni_memory.episodes (
    episode_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_identifier  VARCHAR(64) NOT NULL,
    case_id             UUID REFERENCES ni.cases(case_id),
    population_id       UUID REFERENCES ni.populations(population_id),
    episode_type        VARCHAR(32) NOT NULL,  -- admission, intervention, crisis, recovery, discharge
    started_at          TIMESTAMPTZ NOT NULL,
    ended_at            TIMESTAMPTZ,
    outcome_summary     TEXT,
    success_score       NUMERIC,  -- 0.0–1.0, funcionou?
    similarity_embedding VECTOR(1536),  -- embedding para busca de casos similares
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_memory.observations — Observações dentro do episódio
CREATE TABLE ni_memory.observations (
    observation_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    episode_id          UUID NOT NULL REFERENCES ni_memory.episodes(episode_id) ON DELETE CASCADE,
    observed_at         TIMESTAMPTZ NOT NULL,
    observation_type    VARCHAR(32) NOT NULL,
    -- vital_sign, assessment_score, clinical_finding, lab_result, patient_report
    observation_code    VARCHAR(32),  -- ex: LOINC code, calculadora ID
    observation_value   JSONB NOT NULL,
    attention_score     NUMERIC,      -- vindo do módulo de Clinical Attention
    node_id             VARCHAR(64) REFERENCES ni_graph.nodes(node_id),
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_memory.actions — Intervenções executadas no episódio
CREATE TABLE ni_memory.actions (
    action_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    episode_id          UUID NOT NULL REFERENCES ni_memory.episodes(episode_id) ON DELETE CASCADE,
    action_type         VARCHAR(32) NOT NULL,  -- intervention, medication, protocol, monitoring, positioning
    nic_code            VARCHAR(8) REFERENCES ni.nic_interventions(nic_code),
    protocol_id         UUID REFERENCES ni_protocol.protocols(protocol_id),
    med_id              UUID REFERENCES ni.medications_anvisa(med_id),
    action_data         JSONB,
    reasoning_session_id UUID REFERENCES ni_reasoning.sessions(session_id),
    executed_at         TIMESTAMPTZ NOT NULL,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_memory.outcomes — Desfechos observados após ações
CREATE TABLE ni_memory.outcomes (
    outcome_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    episode_id          UUID NOT NULL REFERENCES ni_memory.episodes(episode_id) ON DELETE CASCADE,
    action_id           UUID NOT NULL REFERENCES ni_memory.actions(action_id) ON DELETE CASCADE,
    noc_code            VARCHAR(8) REFERENCES ni.noc_outcomes(noc_code),
    outcome_type        VARCHAR(32) NOT NULL,
    -- improved, unchanged, deteriorated, resolved, adverse, partial
    outcome_value       NUMERIC,    -- NOC score ou métrica
    expected_value      NUMERIC,    -- valor que o planner previu
    surprise_score      NUMERIC,    -- |actual - expected|, alimenta learning
    measured_at         TIMESTAMPTZ NOT NULL,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_memory.learnings — O que o sistema aprendeu com este episódio
CREATE TABLE ni_memory.learnings (
    learning_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    episode_id          UUID NOT NULL REFERENCES ni_memory.episodes(episode_id) ON DELETE CASCADE,
    learning_type       VARCHAR(32) NOT NULL,
    -- effective_intervention, ineffective_intervention, adverse_reaction,
    -- time_pattern, population_specific, context_dependent
    description         TEXT NOT NULL,
    target_node_id      VARCHAR(64) REFERENCES ni_graph.nodes(node_id),
    target_edge_id      UUID REFERENCES ni_graph.edges(edge_id),
    suggested_weight_delta NUMERIC,  -- ajuste sugerido no peso
    confidence          NUMERIC,  -- 0.0–1.0
    applied             BOOLEAN NOT NULL DEFAULT false,
    applied_at          TIMESTAMPTZ,
    model_adjustment_id UUID REFERENCES ni_learning.model_adjustments(adjustment_id),
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_memory.case_similarity — Busca de casos similares (retrieval)
CREATE TABLE ni_memory.case_similarity (
    similarity_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_episode_id   UUID NOT NULL REFERENCES ni_memory.episodes(episode_id) ON DELETE CASCADE,
    similar_episode_id  UUID NOT NULL REFERENCES ni_memory.episodes(episode_id) ON DELETE CASCADE,
    similarity_score    NUMERIC NOT NULL,  -- 0.0–1.0
    similarity_basis    VARCHAR(32),  -- embedding, clinical_features, population, diagnosis
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- ⭐⭐⭐⭐ LAYER 3: TEMPORAL GRAPH (ni_temporal extensions)
-- ============================================================================
-- O banco atual é estático. O Nurse-PaLM pensa em sequências temporais.
-- Extende o schema ni_temporal existente com sequências e causalidade.
-- ============================================================================

-- ni_temporal.event_sequences — Sequências temporais de eventos
CREATE TABLE ni_temporal.event_sequences (
    sequence_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_identifier  VARCHAR(64) NOT NULL,
    sequence_type       VARCHAR(32) NOT NULL,
    -- deterioration, recovery, crisis, stabilization, oscillation
    started_at          TIMESTAMPTZ NOT NULL,
    ended_at            TIMESTAMPTZ,
    outcome_sequence    VARCHAR(32),  -- improved, deteriorated, stable, mixed
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_temporal.event_sequence_items — Itens ordenados da sequência
CREATE TABLE ni_temporal.event_sequence_items (
    item_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sequence_id         UUID NOT NULL REFERENCES ni_temporal.event_sequences(sequence_id) ON DELETE CASCADE,
    event_id            UUID NOT NULL REFERENCES ni_temporal.clinical_events(event_id) ON DELETE CASCADE,
    item_order          SMALLINT NOT NULL,
    delta_seconds       INTEGER,  -- segundos desde o evento anterior
    delta_label         VARCHAR(32),  -- '30s', '5min', '2h', '1d' — legibilidade
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_temporal.causal_chains — Cadeias causais inferidas
CREATE TABLE ni_temporal.causal_chains (
    chain_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_identifier  VARCHAR(64) NOT NULL,
    cause_event_id      UUID NOT NULL REFERENCES ni_temporal.clinical_events(event_id) ON DELETE CASCADE,
    effect_event_id     UUID NOT NULL REFERENCES ni_temporal.clinical_events(event_id) ON DELETE CASCADE,
    causality_type      VARCHAR(32) NOT NULL,  -- direct, contributing, temporal_correlation, confounded
    confidence          NUMERIC,  -- 0.0–1.0
    evidence_ref        UUID REFERENCES ni_mining.graded_evidence(grade_id),
    confounders         JSONB,  -- fatores de confusão identificados
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_temporal.pattern_templates — Padrões temporais recorrentes
CREATE TABLE ni_temporal.pattern_templates (
    pattern_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_name        VARCHAR(128) NOT NULL,
    pattern_type        VARCHAR(32) NOT NULL,  -- deterioration_curve, recovery_curve, crisis_threshold
    pattern_sequence    JSONB NOT NULL,  -- sequência canônica de eventos
    typical_duration    INTERVAL,
    severity_range      VARCHAR(32),  -- mild, moderate, severe, critical
    occurrence_count    INTEGER DEFAULT 0,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- ⭐⭐⭐⭐ LAYER 4: WORLD MODEL (ni_world)
-- ============================================================================
-- Contexto que muda a decisão: paciente grave + UTI lotada + sem bomba
-- = decisão diferente de paciente grave + UTI com vagas
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS ni_world;

-- ni_world.patient_contexts — Estado contextual do paciente
CREATE TABLE ni_world.patient_contexts (
    context_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_identifier  VARCHAR(64) NOT NULL,
    severity_level      VARCHAR(16) NOT NULL,  -- stable, moderate, critical, terminal
    acuity_score        NUMERIC,  -- ex: MEWS, NEWS2
    isolation_status    VARCHAR(16),  -- none, contact, droplet, airborne
    mobility_status     VARCHAR(16),  -- independent, assisted, bedridden
    consciousness_level VARCHAR(16),  -- alert, drowsy, confused, unresponsive
    fall_risk           VARCHAR(16),  -- low, moderate, high
    pregnancy_status    BOOLEAN,
    age_band            VARCHAR(16),  -- neonatal, pediatric, adult, elderly
    captured_at         TIMESTAMPTZ NOT NULL,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_world.hospital_contexts — Estado do hospital
CREATE TABLE ni_world.hospital_contexts (
    context_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hospital_identifier VARCHAR(64) NOT NULL,
    occupancy_rate      NUMERIC,  -- 0.0–1.0
    er_status           VARCHAR(16),  -- normal, congested, critical, overflow
    bed_availability    INTEGER,
    or_availability     INTEGER,
    lab_turnaround_min  INTEGER,
    code_team_available BOOLEAN,
    captured_at         TIMESTAMPTZ NOT NULL,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_world.ward_contexts — Estado da enfermaria/unidade
CREATE TABLE ni_world.ward_contexts (
    context_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ward_identifier     VARCHAR(64) NOT NULL,
    ward_type           VARCHAR(32) NOT NULL,  -- ICU, ER, general, pediatrics, neonatal, stepdown
    occupancy           INTEGER,
    capacity            INTEGER,
    nurse_patient_ratio NUMERIC,
    isolation_rooms_available INTEGER,
    acuity_mix          VARCHAR(32),  -- low, mixed, high, critical
    captured_at         TIMESTAMPTZ NOT NULL,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_world.resource_contexts — Disponibilidade de recursos
CREATE TABLE ni_world.resource_contexts (
    context_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ward_identifier     VARCHAR(64) NOT NULL,
    resource_type       VARCHAR(32) NOT NULL,
    -- infusion_pump, ventilator, cardiac_monitor, defibrillator, ultrasound, pulse_oximeter
    resource_name       VARCHAR(64),
    available           INTEGER NOT NULL DEFAULT 0,
    in_use              INTEGER NOT NULL DEFAULT 0,
    total               INTEGER NOT NULL DEFAULT 0,
    maintenance_count   INTEGER DEFAULT 0,
    captured_at         TIMESTAMPTZ NOT NULL,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_world.staff_contexts — Equipe disponível
CREATE TABLE ni_world.staff_contexts (
    context_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ward_identifier     VARCHAR(64) NOT NULL,
    shift_type          VARCHAR(16) NOT NULL,  -- morning, evening, night
    nurses_on_duty      INTEGER,
    nurses_available    INTEGER,
    charge_nurse_present BOOLEAN,
    specialist_coverage JSONB,  -- {cardiology: true, neurology: false, nephrology: true}
    years_experience_avg NUMERIC,
    overtime_hours      NUMERIC,
    captured_at         TIMESTAMPTZ NOT NULL,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_world.context_decisions — Como o contexto influenciou a decisão
CREATE TABLE ni_world.context_decisions (
    decision_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reasoning_session_id UUID NOT NULL REFERENCES ni_reasoning.sessions(session_id) ON DELETE CASCADE,
    patient_context_id  UUID REFERENCES ni_world.patient_contexts(context_id),
    ward_context_id     UUID REFERENCES ni_world.ward_contexts(context_id),
    resource_context_id UUID REFERENCES ni_world.resource_contexts(context_id),
    staff_context_id    UUID REFERENCES ni_world.staff_contexts(context_id),
    context_summary     TEXT,  -- "Paciente crítico + UTI lotada + sem bomba"
    decision_modification TEXT,  -- "Adaptado protocolo para bomba alternativa"
    impact_score        NUMERIC,  -- quanto o contexto mudou a decisão
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- ⭐⭐⭐⭐ LAYER 5: CLINICAL ATTENTION (ni_attention)
-- ============================================================================
-- 200 observações → IA identifica as 6 críticas → ignora o resto
-- Atenção seletiva como mecanismo de priorização dinâmica
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS ni_attention;

-- ni_attention.signals — Sinais de atenção para cada observação
CREATE TABLE ni_attention.signals (
    signal_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reasoning_session_id UUID NOT NULL REFERENCES ni_reasoning.sessions(session_id) ON DELETE CASCADE,
    patient_identifier  VARCHAR(64) NOT NULL,
    observation_ref     VARCHAR(128),  -- ref para observação (ni_temporal, ni_memory, etc.)
    attention_score     NUMERIC NOT NULL,  -- 0.0–1.0, peso de atenção
    salience            NUMERIC,  -- quanto se destaca do baseline
    priority            SMALLINT,  -- 1–5 (1=baixa, 5=crítica)
    urgency             SMALLINT,  -- 1–5 (1=rotina, 5=emergência)
    clinical_domain     VARCHAR(32),  -- cardiovascular, respiratory, neurological, renal, etc.
    ignored             BOOLEAN NOT NULL DEFAULT false,
    ignore_reason       VARCHAR(64),  -- below_threshold, redundant, not_relevant
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_attention.weights — Pesos de atenção aprendidos por contexto
CREATE TABLE ni_attention.weights (
    weight_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    context_type        VARCHAR(32) NOT NULL,  -- population, ward, acuity, shift, diagnosis
    context_value       VARCHAR(64) NOT NULL,
    observation_type    VARCHAR(32) NOT NULL,  -- vital_sign, lab, score, finding
    observation_code    VARCHAR(32),
    base_weight         NUMERIC NOT NULL,  -- peso inicial (regra)
    learned_weight      NUMERIC,  -- peso ajustado por aprendizado
    last_updated_at     TIMESTAMPTZ,
    update_count        INTEGER DEFAULT 0,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_attention.focus_windows — Janelas de foco ativo
CREATE TABLE ni_attention.focus_windows (
    window_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reasoning_session_id UUID NOT NULL REFERENCES ni_reasoning.sessions(session_id) ON DELETE CASCADE,
    window_type         VARCHAR(32) NOT NULL,  -- crisis, monitoring, routine, discharge_prep
    focused_domains     JSONB,  -- ["cardiovascular", "neurological"]
    focused_observations JSONB, -- lista de observation_refs em foco
    started_at          TIMESTAMPTZ NOT NULL,
    ended_at            TIMESTAMPTZ,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- ⭐⭐⭐⭐⭐ LAYER 6: UNCERTAINTY MODEL (ni_prob extensions)
-- ============================================================================
-- "NANDA A 74%, NANDA B 18%, NANDA C 6%" — nunca apenas "Diagnóstico: X"
-- Extende o schema ni_prob existente
-- ============================================================================

-- ni_prob.uncertainty_distributions — Distribuições de probabilidade
CREATE TABLE ni_prob.uncertainty_distributions (
    distribution_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id            UUID REFERENCES ni_prob.probability_models(model_id),
    node_id             VARCHAR(64) NOT NULL REFERENCES ni_graph.nodes(node_id),
    distribution_type   VARCHAR(16) NOT NULL,  -- normal, beta, categorical, dirichlet, uniform
    parameters          JSONB NOT NULL,  -- {mean: 0.74, std: 0.08} ou {alpha: 3, beta: 1}
    sample_count        INTEGER DEFAULT 0,
    entropy             NUMERIC,  -- medida de incerteza (Shannon entropy)
    last_updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_prob.confidence_intervals — Intervalos de confiança
CREATE TABLE ni_prob.confidence_intervals (
    ci_id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id            UUID REFERENCES ni_prob.probability_models(model_id),
    node_id             VARCHAR(64) NOT NULL REFERENCES ni_graph.nodes(node_id),
    lower_bound         NUMERIC NOT NULL,
    upper_bound         NUMERIC NOT NULL,
    point_estimate      NUMERIC,
    confidence_level    NUMERIC NOT NULL,  -- 0.90, 0.95, 0.99
    method              VARCHAR(32),  -- bootstrap, analytical, bayesian_posterior
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_prob.prior_beliefs — Crenças prévias por população
CREATE TABLE ni_prob.prior_beliefs (
    prior_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_id             VARCHAR(64) NOT NULL REFERENCES ni_graph.nodes(node_id),
    population_id       UUID REFERENCES ni.populations(population_id),
    prior_type          VARCHAR(16) NOT NULL,  -- uniform, informative, empirical, jeffreys
    prior_value         NUMERIC NOT NULL,
    prior_source        VARCHAR(32),  -- literature, expert_elicit, empirical, default
    evidence_grade      CHAR(1),  -- A, B, C, D (GRADE)
    reference           VARCHAR(256),  -- citação
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_prob.belief_updates — Log de atualizações bayesianas
CREATE TABLE ni_prob.belief_updates (
    update_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id            UUID REFERENCES ni_prob.probability_models(model_id),
    node_id             VARCHAR(64) NOT NULL REFERENCES ni_graph.nodes(node_id),
    prior_value         NUMERIC NOT NULL,
    likelihood          NUMERIC,  -- P(evidence|hypothesis)
    posterior_value     NUMERIC NOT NULL,
    evidence_ref        UUID REFERENCES ni_mining.graded_evidence(grade_id),
    reasoning_session_id UUID REFERENCES ni_reasoning.sessions(session_id),
    bayes_factor        NUMERIC,  -- razão de verossimilhança
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_prob.ambiguity_flags — Casos com alta incerteza/ambiguidade
CREATE TABLE ni_prob.ambiguity_flags (
    flag_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reasoning_session_id UUID NOT NULL REFERENCES ni_reasoning.sessions(session_id) ON DELETE CASCADE,
    flag_type           VARCHAR(32) NOT NULL,
    -- low_confidence, high_entropy, conflicting_evidence, insufficient_data
    top_probability     NUMERIC,  -- P(diagnóstico mais provável)
    second_probability  NUMERIC,  -- P(segundo mais provável)
    entropy             NUMERIC,
    recommended_action  VARCHAR(32),  -- collect_more_data, escalate, defer, human_review
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- ⭐⭐⭐⭐ LAYER 7: PLANNER (ni_planner)
-- ============================================================================
-- Se NIC A → NOC melhora → se não → NIC B → se piorar → protocolo C
-- Grafo de planejamento com branches condicionais
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS ni_planner;

-- ni_planner.plans — Planos de ação gerados pelo raciocínio
CREATE TABLE ni_planner.plans (
    plan_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reasoning_session_id UUID NOT NULL REFERENCES ni_reasoning.sessions(session_id) ON DELETE CASCADE,
    case_id             UUID REFERENCES ni.cases(case_id),
    care_plan_id        UUID REFERENCES ni.care_plans(plan_id),
    plan_type           VARCHAR(32) NOT NULL,  -- intervention_sequence, contingency, escalation, de_escalation
    goal_noc_code       VARCHAR(8) REFERENCES ni.noc_outcomes(noc_code),
    goal_value          NUMERIC,  -- NOC target
    time_horizon        INTERVAL,  -- janela temporal do plano
    status              VARCHAR(16) NOT NULL DEFAULT 'proposed',
    -- proposed, active, completed, abandoned, superseded
    success_probability NUMERIC,  -- P(plano atinge objetivo)
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_planner.plan_nodes — Nós do grafo de planejamento
CREATE TABLE ni_planner.plan_nodes (
    node_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id             UUID NOT NULL REFERENCES ni_planner.plans(plan_id) ON DELETE CASCADE,
    node_type           VARCHAR(32) NOT NULL,
    -- action, evaluation, branch, terminal, escalation, de_escalation
    nic_code            VARCHAR(8) REFERENCES ni.nic_interventions(nic_code),
    protocol_id         UUID REFERENCES ni_protocol.protocols(protocol_id),
    expected_noc_delta  NUMERIC,  -- mudança esperada no NOC
    expected_duration   INTERVAL,
    node_order          SMALLINT,
    is_entry_point      BOOLEAN DEFAULT false,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_planner.plan_edges — Transições condicionais entre nós
CREATE TABLE ni_planner.plan_edges (
    edge_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id             UUID NOT NULL REFERENCES ni_planner.plans(plan_id) ON DELETE CASCADE,
    from_node_id        UUID NOT NULL REFERENCES ni_planner.plan_nodes(node_id) ON DELETE CASCADE,
    to_node_id          UUID NOT NULL REFERENCES ni_planner.plan_nodes(node_id) ON DELETE CASCADE,
    condition_type      VARCHAR(32) NOT NULL,
    -- success, failure, deterioration, no_change, timeout, adverse_event, escalation_trigger
    condition_expression JSONB,  -- {noc_value: {operator: ">=", value: 4}}
    probability         NUMERIC,  -- P(esta branch | condição)
    priority            SMALLINT,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_planner.plan_executions — Execução real de um plano
CREATE TABLE ni_planner.plan_executions (
    execution_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id             UUID NOT NULL REFERENCES ni_planner.plans(plan_id) ON DELETE CASCADE,
    node_id             UUID NOT NULL REFERENCES ni_planner.plan_nodes(node_id) ON DELETE CASCADE,
    action_id           UUID REFERENCES ni_memory.actions(action_id),
    execution_status    VARCHAR(16) NOT NULL,  -- executed, skipped, failed, pending
    actual_outcome      VARCHAR(32),  -- improved, unchanged, deteriorated
    actual_noc_value    NUMERIC,
    deviation_from_plan TEXT,  -- descrição de desvio do plano original
    executed_at         TIMESTAMPTZ,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- ⭐⭐⭐⭐ LAYER 8: FEEDBACK LEARNING (ni_learning extensions)
-- ============================================================================
-- Plano → Resultado → Funcionou? → Atualizar pesos
-- Extende o schema ni_learning existente
-- ============================================================================

-- ni_learning.reinforcement_signals — Sinais de reforço (reward/penalty)
CREATE TABLE ni_learning.reinforcement_signals (
    signal_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    episode_id          UUID NOT NULL REFERENCES ni_memory.episodes(episode_id) ON DELETE CASCADE,
    action_id           UUID REFERENCES ni_memory.actions(action_id) ON DELETE CASCADE,
    outcome_id          UUID REFERENCES ni_memory.outcomes(outcome_id) ON DELETE CASCADE,
    reward              NUMERIC NOT NULL,  -- -1.0 a 1.0
    signal_type         VARCHAR(32) NOT NULL,  -- positive, negative, neutral, mixed
    target_node_id      VARCHAR(64) REFERENCES ni_graph.nodes(node_id),
    target_edge_id      UUID REFERENCES ni_graph.edges(edge_id),
    target_type         VARCHAR(16) NOT NULL,  -- rule, weight, edge, probability, threshold
    discount_factor     NUMERIC DEFAULT 0.95,  -- para aprendizado temporal
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_learning.weight_updates — Atualizações de peso derivadas de feedback
CREATE TABLE ni_learning.weight_updates (
    update_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    signal_id           UUID NOT NULL REFERENCES ni_learning.reinforcement_signals(signal_id) ON DELETE CASCADE,
    edge_id             UUID REFERENCES ni_graph.edges(edge_id) ON DELETE CASCADE,
    rule_id             UUID REFERENCES ni_rules.decision_rules(rule_id) ON DELETE CASCADE,
    weight_id           UUID REFERENCES ni_rules.rule_weights(weight_id) ON DELETE CASCADE,
    old_value           NUMERIC NOT NULL,
    new_value           NUMERIC NOT NULL,
    delta               NUMERIC NOT NULL,
    update_method       VARCHAR(32),  -- gradient, bayesian_update, td_learning, rule_adjustment
    validation_status   VARCHAR(16) NOT NULL DEFAULT 'pending',  -- pending, validated, rejected
    validated_by        VARCHAR(64),
    validated_at        TIMESTAMPTZ,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_learning.learning_curves — Curvas de aprendizado por componente
CREATE TABLE ni_learning.learning_curves (
    curve_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    component_type      VARCHAR(32) NOT NULL,  -- rule, edge_weight, probability, attention
    component_id        VARCHAR(128),  -- ID do componente
    measurement_at      TIMESTAMPTZ NOT NULL,
    accuracy            NUMERIC,
    precision           NUMERIC,
    recall              NUMERIC,
    f1_score            NUMERIC,
    sample_count        INTEGER,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_learning.experience_replay — Buffer de experiências para treino
CREATE TABLE ni_learning.experience_replay (
    replay_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    episode_id          UUID REFERENCES ni_memory.episodes(episode_id) ON DELETE CASCADE,
    state_snapshot      JSONB NOT NULL,  -- estado no momento da decisão
    action_taken        JSONB NOT NULL,
    reward              NUMERIC,
    next_state_snapshot JSONB,
    priority            NUMERIC,  -- prioridade de amostragem (prioritized replay)
    sampled_count       INTEGER DEFAULT 0,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- ⭐⭐⭐ LAYER 9: SIMULATION ENGINE (ni_twin extensions)
-- ============================================================================
-- Paciente virtual → executar plano → simular → resultado provável
-- Extende o schema ni_twin existente
-- ============================================================================

-- ni_twin.simulation_runs — Execuções de simulação
CREATE TABLE ni_twin.simulation_runs (
    sim_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_state_id    UUID NOT NULL REFERENCES ni_twin.patient_states(state_id) ON DELETE CASCADE,
    plan_id             UUID REFERENCES ni_planner.plans(plan_id) ON DELETE CASCADE,
    reasoning_session_id UUID REFERENCES ni_reasoning.sessions(session_id) ON DELETE CASCADE,
    simulation_type     VARCHAR(32) NOT NULL,
    -- mcts, monte_carlo, deterministic, counterfactual, stress_test
    iterations          INTEGER NOT NULL DEFAULT 1,
    time_horizon        INTERVAL,  -- quanto tempo simular
    started_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at        TIMESTAMPTZ,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_twin.simulation_results — Resultados de cada simulação
CREATE TABLE ni_twin.simulation_results (
    result_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sim_id              UUID NOT NULL REFERENCES ni_twin.simulation_runs(sim_id) ON DELETE CASCADE,
    trajectory_id       UUID REFERENCES ni_twin.trajectories(trajectory_id) ON DELETE CASCADE,
    outcome_type        VARCHAR(32) NOT NULL,
    -- improved, unchanged, deteriorated, adverse, mortality, recovery
    predicted_noc_code  VARCHAR(8) REFERENCES ni.noc_outcomes(noc_code),
    predicted_value     NUMERIC,
    probability         NUMERIC NOT NULL,  -- P(este desfecho)
    confidence_interval JSONB,  -- {lower: 0.6, upper: 0.9}
    time_to_outcome     INTERVAL,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_twin.counterfactuals — "E se fizéssemos X em vez de Y?"
CREATE TABLE ni_twin.counterfactuals (
    cf_id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sim_id              UUID NOT NULL REFERENCES ni_twin.simulation_runs(sim_id) ON DELETE CASCADE,
    base_scenario       JSONB NOT NULL,  -- o que realmente aconteceu
    counterfactual_scenario JSONB NOT NULL,  -- o que teria acontecido com ação alternativa
    divergence_point    TEXT,  -- onde os cenários divergem
    divergence_action   VARCHAR(128),  -- "NIC 3540" vs "NIC 6540"
    base_outcome        JSONB,
    cf_outcome          JSONB,
    causal_effect       NUMERIC,  -- efeito estimado da diferença
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_twin.simulation_validations — Validação de simulações contra realidade
CREATE TABLE ni_twin.simulation_validations (
    validation_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sim_id              UUID NOT NULL REFERENCES ni_twin.simulation_runs(sim_id) ON DELETE CASCADE,
    trajectory_id       UUID REFERENCES ni_twin.trajectories(trajectory_id) ON DELETE CASCADE,
    predicted_outcome   JSONB,
    actual_outcome      JSONB,
    prediction_error    NUMERIC,  -- |predicted - actual|
    calibration_score   NUMERIC,  -- quão bem calibrada estava a predição
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- ⭐⭐⭐⭐ LAYER 10: MULTI-AGENT CLINICAL COUNCIL (ni_council extensions)
-- ============================================================================
-- Assessment → NANDA → NIC → NOC → Safety → Medication → Evidence → Consensus
-- Todos votam, Consensus Agent gera a decisão final
-- Extende o schema ni_council existente
-- ============================================================================

-- ni_council.agents — Registro de agentes do conselho
CREATE TABLE ni_council.agents (
    agent_id            VARCHAR(64) PRIMARY KEY,  -- ex: COUNCIL.ASSESS.001
    agent_type          VARCHAR(32) NOT NULL,
    -- assessment, nanda, nic, noc, safety, medication, evidence, consensus, arbitrator
    agent_name          VARCHAR(128) NOT NULL,
    specialty           VARCHAR(64),
    model_version       VARCHAR(32),
    knowledge_scope     JSONB,  -- {domains: ["cardiovascular", "neurological"], populations: ["adult", "icu"]}
    voting_weight       NUMERIC DEFAULT 1.0,
    veto_eligible       BOOLEAN DEFAULT false,
    active              BOOLEAN DEFAULT true,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_council.agent_roles — Papéis dos agentes em cada sessão
CREATE TABLE ni_council.agent_roles (
    role_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id            VARCHAR(64) NOT NULL REFERENCES ni_council.agents(agent_id) ON DELETE CASCADE,
    session_id          UUID NOT NULL REFERENCES ni_council.sessions(session_id) ON DELETE CASCADE,
    role                VARCHAR(32) NOT NULL,  -- primary, secondary, veto_holder, arbitrator, observer
    session_voting_weight NUMERIC,
    assigned_domains    JSONB,  -- domains this agent covers in this session
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_council.consensus_protocols — Protocolos de consenso
CREATE TABLE ni_council.consensus_protocols (
    protocol_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID NOT NULL REFERENCES ni_council.sessions(session_id) ON DELETE CASCADE,
    protocol_type       VARCHAR(32) NOT NULL,
    -- majority, weighted_majority, unanimous, threshold, deliberative
    threshold           NUMERIC,  -- score mínimo para consenso
    quorum              INTEGER,  -- mínimo de agentes
    timeout_seconds     INTEGER,
    max_rounds          INTEGER DEFAULT 3,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_council.deliberation_log — Log de deliberação por rodada
CREATE TABLE ni_council.deliberation_log (
    deliberation_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID NOT NULL REFERENCES ni_council.sessions(session_id) ON DELETE CASCADE,
    agent_id            VARCHAR(64) NOT NULL REFERENCES ni_council.agents(agent_id),
    round_number        SMALLINT NOT NULL,
    position            JSONB,  -- {diagnosis: "00047", confidence: 0.74, reasoning: "..."}
    argument_text       TEXT,
    evidence_refs       UUID[],  -- refs para ni_mining.graded_evidence
    proposed_action     JSONB,
    confidence          NUMERIC,
    changed_from_previous BOOLEAN DEFAULT false,  -- mudou de posição?
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_council.consensus_results — Resultado do consenso
CREATE TABLE ni_council.consensus_results (
    result_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID NOT NULL REFERENCES ni_council.sessions(session_id) ON DELETE CASCADE,
    consensus_type      VARCHAR(32) NOT NULL,  -- reached, no_consensus, partial, escalated
    final_decision      JSONB,  -- {diagnosis: "00047", interventions: [...], confidence: 0.78}
    agreement_score     NUMERIC,  -- 0.0–1.0, quão de acordo os agentes estão
    dissenting_agents   VARCHAR(64)[],  -- IDs dos agentes que discordaram
    rounds_completed    INTEGER,
    human_override      BOOLEAN DEFAULT false,
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ni_council.agent_performance — Métricas de performance por agente
CREATE TABLE ni_council.agent_performance (
    perf_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id            VARCHAR(64) NOT NULL REFERENCES ni_council.agents(agent_id) ON DELETE CASCADE,
    measurement_period  VARCHAR(16),  -- daily, weekly, monthly
    period_start        TIMESTAMPTZ,
    period_end          TIMESTAMPTZ,
    sessions_participated INTEGER,
    votes_correct       NUMERIC,  -- % de votos que alinharam com desfecho real
    vetoes_correct      NUMERIC,
    avg_confidence      NUMERIC,
    calibration_error   NUMERIC,  -- |predicted confidence - actual accuracy|
    created_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- ÍNDICES RECOMENDADOS
-- ============================================================================

-- Reasoning
CREATE INDEX idx_reasoning_sessions_patient ON ni_reasoning.sessions(patient_identifier);
CREATE INDEX idx_reasoning_sessions_case ON ni_reasoning.sessions(case_id);
CREATE INDEX idx_reasoning_steps_session ON ni_reasoning.steps(session_id);
CREATE INDEX idx_reasoning_scores_session ON ni_reasoning.scores(session_id);
CREATE INDEX idx_reasoning_hypotheses_session ON ni_reasoning.hypotheses(session_id);

-- Memory
CREATE INDEX idx_memory_episodes_patient ON ni_memory.episodes(patient_identifier);
CREATE INDEX idx_memory_episodes_case ON ni_memory.episodes(case_id);
CREATE INDEX idx_memory_observations_episode ON ni_memory.observations(episode_id);
CREATE INDEX idx_memory_actions_episode ON ni_memory.actions(episode_id);
CREATE INDEX idx_memory_outcomes_episode ON ni_memory.outcomes(episode_id);
CREATE INDEX idx_memory_learnings_episode ON ni_memory.learnings(episode_id);

-- Temporal
CREATE INDEX idx_temporal_sequences_patient ON ni_temporal.event_sequences(patient_identifier);
CREATE INDEX idx_temporal_seq_items_sequence ON ni_temporal.event_sequence_items(sequence_id);
CREATE INDEX idx_temporal_causal_patient ON ni_temporal.causal_chains(patient_identifier);

-- World
CREATE INDEX idx_world_patient_ctx_patient ON ni_world.patient_contexts(patient_identifier);
CREATE INDEX idx_world_ward_ctx_ward ON ni_world.ward_contexts(ward_identifier);

-- Attention
CREATE INDEX idx_attention_signals_session ON ni_attention.signals(reasoning_session_id);
CREATE INDEX idx_attention_signals_patient ON ni_attention.signals(patient_identifier);

-- Planner
CREATE INDEX idx_planner_plans_session ON ni_planner.plans(reasoning_session_id);
CREATE INDEX idx_planner_nodes_plan ON ni_planner.plan_nodes(plan_id);
CREATE INDEX idx_planner_edges_plan ON ni_planner.plan_edges(plan_id);

-- Learning
CREATE INDEX idx_learning_signals_episode ON ni_learning.reinforcement_signals(episode_id);
CREATE INDEX idx_learning_updates_signal ON ni_learning.weight_updates(signal_id);

-- Twin
CREATE INDEX idx_twin_sims_state ON ni_twin.simulation_runs(patient_state_id);
CREATE INDEX idx_twin_sim_results_sim ON ni_twin.simulation_results(sim_id);

-- Council
CREATE INDEX idx_council_agent_roles_session ON ni_council.agent_roles(session_id);
CREATE INDEX idx_council_deliberation_session ON ni_council.deliberation_log(session_id);
CREATE INDEX idx_council_consensus_session ON ni_council.consensus_results(session_id);

-- ============================================================================
-- RESUMO DA ARQUITETURA COGNITIVA
-- ============================================================================
-- 10 novos schemas / extensões:
--   ni_reasoning     — 5 tabelas (sessions, steps, trace, scores, hypotheses)
--   ni_memory        — 6 tabelas (episodes, observations, actions, outcomes, learnings, case_similarity)
--   ni_temporal +    — 4 tabelas (event_sequences, event_sequence_items, causal_chains, pattern_templates)
--   ni_world         — 6 tabelas (patient, hospital, ward, resource, staff contexts, context_decisions)
--   ni_attention     — 3 tabelas (signals, weights, focus_windows)
--   ni_prob +        — 5 tabelas (distributions, confidence_intervals, priors, belief_updates, ambiguity_flags)
--   ni_planner       — 4 tabelas (plans, plan_nodes, plan_edges, plan_executions)
--   ni_learning +    — 4 tabelas (reinforcement_signals, weight_updates, learning_curves, experience_replay)
--   ni_twin +        — 4 tabelas (simulation_runs, simulation_results, counterfactuals, simulation_validations)
--   ni_council +     — 6 tabelas (agents, agent_roles, consensus_protocols, deliberation_log, consensus_results, agent_performance)
--
-- Total: ~47 novas tabelas
-- Novas FKs: ~90+ relações
-- Fluxo cognitivo completo:
--   World Model → Attention → Reasoning → Hypotheses → Probability →
--   Council → Planner → Execution → Memory → Outcome → Learning →
--   (loop) Simulation valida Planner → Learning atualiza Attention/Prob/Council
-- ============================================================================
