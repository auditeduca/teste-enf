# NIFS-300-18: Outcomes

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-300-18                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir outcomes como os resultados mensurados das intervenções — o fechamento do ciclo de raciocínio.

## 2. Outcome Types

| Type | Description | Example |
|------|-------------|---------|
| Improved | NOC score increased toward target | 2→4 |
| Unchanged | NOC score stayed same | 3→3 |
| Deteriorated | NOC score worsened | 4→2 |
| Resolved | Problem fully resolved | NANDA no longer applicable |
| Adverse | Unexpected negative outcome | Skin breakdown despite intervention |

## 3. Outcome Measurement

```
Goal: NOC 1101, target 4, horizon 72h
    ↓ T+24h
Measurement: NOC 1101 = 3 (improved from 2)
    ↓ T+48h
Measurement: NOC 1101 = 4 (target achieved ✅)
    ↓
Outcome type: "improved"
Success: true
    ↓
Learning: "NIC 3540 effective for NANDA 00047 in ICU population"
    ↓
Reinforcement signal: +0.8 (positive)
```

## 4. Outcome → Learning Loop

```
ni_memory.outcomes
    ↓
ni_learning.feedback (accepted, modified, rejected)
    ↓
ni_learning.reinforcement_signals (reward -1 to +1)
    ↓
ni_learning.weight_updates (adjust edge weights)
    ↓
ni_graph.edges weight updated (with validation)
```

## 5. NIS Implementation

| Table | Role |
|-------|------|
| `ni_memory.outcomes` | Per-episode outcome measurement |
| `ni_learning.feedback` | Nurse's feedback on recommendation |
| `ni_twin.outcome_feedback` | Actual outcome for simulated trajectory |
| `ni_reasoning.scores` | Score type "outcome" with value |

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-16 | NOC (terminology) |
| NIFS-300-17 | Goals (targets) |
| NIFS-600-17 | Learning Loop |
