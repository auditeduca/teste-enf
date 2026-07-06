# NIFS-600-20: Reasoning Trace

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-600-20                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o formato, armazenamento e recuperação do rastro de raciocínio — a base material da explicabilidade e auditoria clínica.

## 2. What is a Reasoning Trace?

Um reasoning trace é o **registro cronológico completo** de cada inferência que o sistema fez para chegar a uma recomendação. É a "caixa branca" do Nurse-PaLM.

```
Sem trace:   "Recomendo NANDA 00047"           → Caixa preta
Com trace:   "Recomendo NANDA 00047 porque..."  → Caixa branca
             [10 etapas, 4 evidências, 8 votos, 3 hipóteses]
```

## 3. Trace Structure

### 3.1 Session-Level Trace

```json
{
  "session_id": "uuid",
  "patient_identifier": "hash_xxx",
  "started_at": "2026-07-05T10:30:00Z",
  "completed_at": "2026-07-05T10:33:12Z",
  "reasoning_type": "diagnostic",
  "final_decision": {
    "nanda_code": "00047",
    "probability": 0.74,
    "confidence_interval": [0.68, 0.80]
  },
  "total_steps": 10,
  "total_evidence_used": 7,
  "council_rounds": 2,
  "agents_participated": 8,
  "agreement_score": 0.87,
  "human_decision": "accepted",
  "trace_completeness": 1.0
}
```

### 3.2 Step-Level Trace

Cada passo do pipeline tem seu próprio trace:

```json
[
  {
    "step_order": 1,
    "step_type": "observation",
    "step_label": "Observation Ingestion",
    "input": {"raw_observations": 200},
    "output": {"filtered_observations": 6, "ignored": 194},
    "duration_ms": 45,
    "trace": "200 raw observations ingested. Clinical Attention filtered to 6 critical (score > 0.50). Top: Braden=12 (0.92), Imobilidade (0.88)."
  },
  {
    "step_order": 2,
    "step_type": "hypothesis",
    "step_label": "Hypothesis Generation",
    "input": {"critical_observations": 6},
    "output": {"hypotheses": 3},
    "duration_ms": 312,
    "trace": "3 hypotheses generated via graph traversal (2) + memory retrieval (1). H1: 00047 (graph_score=0.82, prior=0.32). H2: 00046 (graph_score=0.65, prior=0.18). H3: 00085 (memory_score=0.71, prior=0.08).",
    "evidence_refs": ["graph_path_1", "graph_path_2", "episode_4823"]
  },
  {
    "step_order": 3,
    "step_type": "evidence_for",
    "step_label": "Evidence Gathering (For)",
    "output": {"evidence_count": 4},
    "trace": "4 supporting evidence found. GRADE A: Cochrane 2023 (Braden≤12→UP 87%). GRADE B: Rev Lat-Am 2022 (imobility+ICU→UP 74%). Rule: 'Braden≤12 AND ICU→00047' (match=1.0). Case: Episode #4823 (sim=0.89, success=0.82).",
    "evidence_refs": ["grade_id_1", "grade_id_2", "rule_id_1", "episode_4823"]
  },
  {
    "step_order": 4,
    "step_type": "evidence_against",
    "step_label": "Evidence Gathering (Against)",
    "output": {"evidence_count": 2},
    "trace": "2 counter-evidence found. Mudança de decúbito q2h (reduz P em 15%). Colchão pressão alternativo em uso (modifica risco)."
  },
  {
    "step_order": 5,
    "step_type": "bayesian_update",
    "step_label": "Bayesian Belief Update",
    "input": {"prior_00047": 0.32},
    "output": {"posterior_00047": 0.74},
    "trace": "Prior P(00047|ICU,postop)=0.32. After evidence_for: P→0.78. After evidence_against: P→0.74. Bayes factor: 6.17. Entropy: 0.82 bits (moderate). IC 95%: [0.68, 0.80].",
    "probability_refs": ["belief_update_id_1", "belief_update_id_2"]
  },
  {
    "step_order": 6,
    "step_type": "council",
    "step_label": "Council Deliberation",
    "output": {"agreement": 0.87, "rounds": 2},
    "trace": "8 agents deliberated in 2 rounds. Round 1: independent positions. Round 2: cross-examination. 7/8 agree on 00047. Safety Agent: partial (wants Protocol C backup). No vetoes.",
    "council_refs": ["deliberation_id_1", "consensus_id_1"]
  },
  {
    "step_order": 7,
    "step_type": "planning",
    "step_label": "Plan Generation",
    "output": {"plan_nodes": 5, "plan_edges": 6},
    "trace": "Plan graph generated. Primary: NIC 3540. Adjunct: NIC 6540. Expected: NOC 1101 from 2→4 in 72h. Contingency: NIC 2250 if no improvement. Escalation: Protocol C if deterioration.",
    "plan_ref": "plan_id_1"
  },
  {
    "step_order": 8,
    "step_type": "explainability",
    "step_label": "Explanation Compilation",
    "output": {"explanation_level": "detailed"},
    "trace": "Full explanation card compiled with: diagnosis, probability, evidence for/against, alternatives, council summary, plan, trace link.",
    "explanation_ref": "explanation_id_1"
  },
  {
    "step_order": 9,
    "step_type": "safety",
    "step_label": "Safety Check",
    "output": {"passed": true, "warnings": 1},
    "trace": "Safety Layer passed. 1 warning: Safety Agent ressalva (Protocol C backup recommended). No vetoes. Human review not required (P > 0.60)."
  },
  {
    "step_order": 10,
    "step_type": "output",
    "step_label": "Final Output",
    "output": {"recommendation": "00047 + NIC 3540/6540"},
    "trace": "Recommendation output to nurse interface. Probability: 74%. Explanation: available. Override: available. Disclaimer: present."
  }
]
```

## 4. Trace Storage

| Level | Table | Granularity | Retention |
|-------|-------|------------|-----------|
| Session | `ni_reasoning.sessions` | Summary | Permanent |
| Steps | `ni_reasoning.steps` | Per step | Permanent |
| Trace entries | `ni_reasoning.trace` | Per trace line | Permanent |
| Evidence | `ni_explain.recommendation_reasons` | Per reason | Permanent |
| Decision trace | `ni_explain.decision_traces` | Per trace step | Permanent |
| Council log | `ni_council.deliberation_log` | Per agent/round | Permanent |

## 5. Trace Retrieval

### 5.1 By Session

```sql
SELECT * FROM ni_reasoning.trace
WHERE session_id = 'uuid'
ORDER BY trace_order;
```

### 5.2 By Patient (all sessions)

```sql
SELECT s.session_id, s.started_at, s.final_nanda_code, s.final_confidence
FROM ni_reasoning.sessions s
WHERE s.patient_identifier = 'hash_xxx'
ORDER BY s.started_at DESC;
```

### 5.3 By Diagnosis (audit)

```sql
SELECT s.session_id, s.started_at, s.final_confidence, e.explanation_id
FROM ni_reasoning.sessions s
JOIN ni_explain.explanations e ON s.session_id = e.session_id
WHERE s.final_nanda_code = '00047'
ORDER BY s.started_at DESC
LIMIT 100;
```

## 6. Trace Completeness Score

Cada trace tem um `trace_completeness` score (0.0–1.0):

| Component | Weight | Present? |
|-----------|--------|----------|
| Observations listed | 0.15 | ☐ |
| Attention scores shown | 0.10 | ☐ |
| Hypotheses with priors | 0.15 | ☐ |
| Evidence for/against | 0.20 | ☐ |
| Bayesian update shown | 0.10 | ☐ |
| Council deliberation | 0.10 | ☐ |
| Plan with branches | 0.10 | ☐ |
| Safety check result | 0.05 | ☐ |
| Alternatives rejected | 0.05 | ☐ |

Target: `trace_completeness = 1.0` for every session.

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-02 | Reasoning Pipeline (generates trace) |
| NIFS-600-19 | Explainability (uses trace for explanation) |
| NIFS-1000-06 | Audit (trace is audit trail) |
| NIFS-700-19 | Hallucination Prevention (trace validates) |

## 8. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — full trace format + storage | Leivis Melo |
