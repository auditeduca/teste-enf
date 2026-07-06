# NIFS-600-02: Reasoning Pipeline

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-600-02                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o pipeline cognitivo completo do motor de raciocínio clínico — o coração do Nurse-PaLM.

## 2. The Cognitive Pipeline

O enfermeiro pensa em etapas. O sistema modela este processo:

```
Paciente
    ↓
Observações (com Clinical Attention)
    ↓
Hipóteses (Hypothesis Generation)
    ↓
Diagnósticos prováveis (com probabilidades)
    ↓
Evidências favoráveis (Evidence For)
    ↓
Evidências contrárias (Evidence Against)
    ↓
Atualização Bayesiana (Belief Update)
    ↓
Ranking de hipóteses (Differential Diagnosis)
    ↓
Escolha ótima (Selection)
    ↓
Plano (Planner)
    ↓
Monitoramento (Temporal Graph)
    ↓
Reavaliação (Feedback → Learning)
```

## 3. Pipeline Stages

### Stage 1: Observation Ingestion

**Input:** Raw clinical data (vital signs, assessment scores, lab results, patient reports)
**Process:**
- Normalize observations to canonical format
- Apply Clinical Attention module to score salience
- Filter: 200 observations → 6 critical (attention_score > threshold)
**Output:** Weighted observation set
**Schema:** `ni_attention.signals`, `ni_reasoning.steps[step_type=observation]`

### Stage 2: Hypothesis Generation

**Input:** Weighted observation set + patient context (World Model)
**Process:**
- Traverse knowledge graph from observations to NANDA nodes
- For each path, calculate preliminary match score
- Generate N candidate hypotheses
**Output:** List of hypotheses with prior probabilities
**Schema:** `ni_reasoning.hypotheses[prior_probability]`

### Stage 3: Evidence Gathering

**Input:** Hypotheses + observations
**Process:**
- For each hypothesis, find supporting evidence (rules, graph paths, literature)
- For each hypothesis, find contradicting evidence
- Weight evidence by GRADE level and confidence
**Output:** Evidence matrix per hypothesis
**Schema:** `ni_reasoning.trace[trace_type=evidence_for/against]`

### Stage 4: Bayesian Update

**Input:** Prior probabilities + evidence
**Process:**
- P(Diagnosis|Evidence) = P(Evidence|Diagnosis) × P(Diagnosis) / P(Evidence)
- Update each hypothesis with Bayes' theorem
- Calculate posterior probabilities
- Calculate entropy (uncertainty measure)
**Output:** Updated hypotheses with posterior probabilities
**Schema:** `ni_prob.belief_updates`, `ni_reasoning.hypotheses[posterior_probability]`

### Stage 5: Differential Ranking

**Input:** Updated hypotheses
**Process:**
- Rank by posterior probability
- Flag ambiguity (if top-2 are within 10%, recommend more data)
- Generate confidence intervals
**Output:** Ranked differential diagnosis
**Schema:** `ni_reasoning.scores[score_type=probability]`, `ni_prob.ambiguity_flags`

### Stage 6: Council Deliberation

**Input:** Ranked diagnosis + evidence + context
**Process:**
- Assessment Agent: validates observation quality
- NANDA Agent: validates diagnostic reasoning
- NIC Agent: proposes interventions
- NOC Agent: defines expected outcomes
- Safety Agent: checks for safety concerns
- Medication Agent: verifies medication interactions
- Evidence Agent: validates evidence quality
- Consensus Agent: aggregates votes
- Veto holders can block
**Output:** Consensus decision with agreement score
**Schema:** `ni_council.deliberation_log`, `ni_council.consensus_results`

### Stage 7: Planning

**Input:** Consensus diagnosis + interventions + context
**Process:**
- Generate intervention plan as directed graph
- Define expected NOC outcomes
- Define contingency branches (if not improved → alternative)
- Define escalation triggers
**Output:** Care plan graph
**Schema:** `ni_planner.plans`, `ni_planner.plan_nodes`, `ni_planner.plan_edges`

### Stage 8: Explainability

**Input:** Full reasoning trace
**Process:**
- Compile natural language explanation
- List: observations used, rules fired, probabilities, evidence, alternatives rejected
- Generate decision trace (step-by-step)
**Output:** Explanation document
**Schema:** `ni_explain.explanations`, `ni_explain.recommendation_reasons`, `ni_explain.decision_traces`

### Stage 9: Monitoring & Reassessment

**Input:** Plan + temporal observations
**Process:**
- Track NOC outcomes over time
- Detect deviations from expected trajectory
- If deviation: trigger reassessment (loop back to Stage 1)
- If adverse event: trigger escalation
**Output:** Monitoring status + reassessment trigger
**Schema:** `ni_temporal.time_series`, `ni_planner.plan_executions`

### Stage 10: Learning

**Input:** Plan + actual outcome
**Process:**
- Compare expected vs actual outcome
- Calculate surprise score (|expected - actual|)
- Generate reinforcement signal (reward/penalty)
- Suggest weight adjustments
- Queue for human validation
**Output:** Learning entry + weight update proposal
**Schema:** `ni_memory.learnings`, `ni_learning.reinforcement_signals`, `ni_learning.weight_updates`

## 4. Data Flow Diagram

```
                    ┌──────────────┐
                    │  World Model │
                    │  (Context)   │
                    └──────┬───────┘
                           │
    ┌──────────────┐       │       ┌──────────────┐
    │ Observations │───────┼───────│   Attention   │
    │ (Temporal)   │       │       │   Module      │
    └──────────────┘       │       └──────┬───────┘
                           │              │
                    ┌──────▼──────────────▼──────┐
                    │    Hypothesis Generation     │
                    │    (Graph Traversal)         │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │    Evidence Gathering        │
                    │    (For & Against)           │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │    Bayesian Update           │
                    │    (Prior → Posterior)       │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │    Council Deliberation      │
                    │    (Multi-Agent Vote)        │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │    Planning                  │
                    │    (Intervention Graph)      │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │    Explainability            │
                    │    (Decision Trace)          │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │    Monitoring → Reassessment │
                    │    (Temporal Loop)           │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │    Learning                  │
                    │    (Feedback → Weight Update)│
                    └──────────────┬──────────────┘
                                   │
                           (loop back to top)
```

## 5. Reasoning Session Lifecycle

| State | Description | Trigger |
|-------|-------------|---------|
| `active` | Pipeline in progress | Session created |
| `awaiting_council` | Council deliberating | Stage 6 reached |
| `awaiting_human` | Human review needed | Ambiguity or veto |
| `completed` | Pipeline finished | Final decision made |
| `aborted` | Session cancelled | User or system abort |
| `reassessing` | Loop back for new data | Deviation detected |

## 6. Performance Requirements

| Stage | Max Latency | Notes |
|-------|-------------|-------|
| Observation + Attention | 200ms | Must be real-time |
| Hypothesis Generation | 500ms | Graph traversal |
| Evidence Gathering | 800ms | Parallel queries |
| Bayesian Update | 100ms | In-memory computation |
| Council Deliberation | 1500ms | Multi-round voting |
| Planning | 300ms | Graph construction |
| Explainability | 200ms | Template rendering |
| **Total** | **< 3.6s** | End-to-end |

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-01 | Clinical Workflow (parent) |
| NIFS-600-04 | Hypothesis Generation (detail) |
| NIFS-600-08 | Bayesian Network (detail) |
| NIFS-600-10 | Clinical Attention (detail) |
| NIFS-600-18 | Consensus Engine (detail) |
| NIFS-600-19 | Explainability (detail) |
| NIFS-700-09 | Multi-Agent (AI implementation) |

## 8. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — full pipeline specification | Leivis Melo |
