# NIFS-600-01: Clinical Workflow

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-600-01                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o fluxo clínico macro que orquestra o pipeline de raciocínio — o contexto no qual o motor cognitivo opera.

## 2. The Nursing Process as Workflow

O processo de enfermagem (ADPIE) é o workflow macro:

```
A — Assess     → Coleta de dados clínicos
D — Diagnose   → Raciocínio diagnóstico (NANDA)
P — Plan       → Planejamento de intervenções (NIC + NOC)
I — Implement  → Execução do plano
E — Evaluate   → Avaliação de desfechos
    ↓ (loop)
A — Assess     → Reavaliação
```

Cada fase do ADPIE mapeia para estágios do Reasoning Pipeline (NIFS-600-02):

| ADPIE Phase | Reasoning Stage | NIS Module |
|-------------|----------------|------------|
| Assess | Stage 1-2 (Observation + Attention) | `ni_attention`, `ni_temporal` |
| Diagnose | Stage 3-5 (Hypothesis + Evidence + Bayesian) | `ni_reasoning`, `ni_prob` |
| Plan | Stage 6-7 (Council + Planning) | `ni_council`, `ni_planner` |
| Implement | Stage 8 (Output + Execution) | `ni_memory.actions` |
| Evaluate | Stage 9-10 (Monitoring + Learning) | `ni_memory.outcomes`, `ni_learning` |

## 3. Workflow States

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ ASSESS   │───→│ DIAGNOSE │───→│  PLAN    │───→│IMPLEMENT │───→│ EVALUATE │
│          │    │          │    │          │    │          │    │          │
│ Collect  │    │ Reason   │    │ Generate │    │ Execute  │    │ Measure  │
│ data     │    │ P(D)     │    │ plan     │    │ plan     │    │ outcomes │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └────┬─────┘
      ↑              ↑               ↑                              │
      │              │               │                              │
      └──────────────┴───────────────┴──────────────────────────────┘
                              Reassessment loop
```

### State Machine

| State | Trigger to Enter | Trigger to Exit |
|-------|-----------------|----------------|
| `assessing` | New session or reassessment | Sufficient observations |
| `diagnosing` | Observations complete | Top hypothesis P > 0.40 |
| `planning` | Diagnosis confirmed | Plan graph generated + simulated |
| `implementing` | Plan approved | Intervention executed |
| `evaluating` | Intervention executed | Outcome measured |
| `reassessing` | Evaluation complete | New assessment started |
| `completed` | Goal achieved | — |
| `escalated` | Deterioration detected | Human intervention |

## 4. Entry Points

O workflow pode ser iniciado por:

| Trigger | Entry State | Source |
|---------|------------|--------|
| New patient admission | `assessing` | EHR/FHIR Encounter |
| New observation received | `assessing` | FHIR Observation / manual |
| Calculator result | `diagnosing` | Calculator API |
| Deterioration alert | `reassessing` | Temporal graph monitor |
| Scheduled reassessment | `assessing` | Scheduler (q4h, q shift) |
| Manual nurse request | `assessing` | User interface |
| Council request | `diagnosing` | Multi-agent trigger |

## 5. Interruption Handling

| Scenario | Action |
|----------|--------|
| New critical observation mid-diagnosis | Pause, re-enter `assessing` |
| Council veto mid-planning | Return to `diagnosing`, flag conflict |
| Patient deterioration mid-implementation | Escalate to emergency protocol |
| Human override at any point | Log, execute override, continue or abort |
| System timeout | Save state, resume when possible |

## 6. Multi-Session Coordination

Um paciente pode ter múltiplas sessões de raciocínio simultâneas:

```
Patient X
├── Session 1: Diagnostic (active) — "Qual o diagnóstico?"
├── Session 2: Therapeutic (active) — "Qual a melhor intervenção?"
└── Session 3: Prioritization (completed) — "O que é mais urgente?"
```

Coordenação via `ni_reasoning.sessions.case_id` — todas as sessões de um caso compartilham contexto.

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-02 | Nursing Process (ADPIE — clinical science) |
| NIFS-600-02 | Reasoning Pipeline (10-stage detail) |
| NIFS-600-03 | Assessment Pipeline (Assess phase) |
| NIFS-900-09 | Scheduler (trigger management) |

## 8. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — ADPIE as state machine | Leivis Melo |
