# NIFS-700-10: Consensus

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-700-10                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como múltiplos agentes clínicos chegam a consenso quando suas recomendações divergem.

## 2. Consensus Protocol

```
Agent A: NANDA 00047 (P=0.91, vote=0.35)
Agent B: NANDA 00046 (P=0.65, vote=0.25)
Agent C: NANDA 00047 (P=0.82, vote=0.40)
    ↓
Aggregation: weighted vote
    NANDA 00047: (0.91×0.35) + (0.82×0.40) = 0.64
    NANDA 00046: (0.65×0.25) = 0.16
    ↓
Consensus: NANDA 00047 (aggregated P=0.74)
    ↓
If conflict (agents disagree strongly) → arbitration
```

## 3. Arbitration Rules

| Scenario | Resolution |
|----------|-----------|
| Agents agree (same top diagnosis) | Direct consensus, no arbitration |
| Agents disagree but top-2 overlap | Weighted average, flag as "moderate confidence" |
| Agents fully disagree | Trigger arbitration: Evidence Agent decides |
| Safety-critical conflict | Human review required before action |

## 4. Vote Weight Allocation

| Agent | Base Weight | Rationale |
|-------|-------------|-----------|
| NANDA Agent | 0.35 | Primary diagnostic authority |
| Evidence Agent | 0.25 | Evidence-based backing |
| Safety Agent | 0.20 | Safety override authority |
| Pharm Agent | 0.10 | Medication-specific |
| Legislation Agent | 0.10 | Compliance-specific |

Safety Agent has **veto power** on safety-critical interventions regardless of weight.

## 5. NIS Implementation

| Table | Role |
|-------|------|
| `ni_council.council_sessions` | Consensus session container |
| `ni_council.agent_votes` | Individual agent votes |
| `ni_council.arbitration_decisions` | Conflict resolutions |
| `ni_council.consensus_results` | Final aggregated output |

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-700-09 | Multi-Agent Council (architecture) |
| NIFS-600-18 | Consensus Engine (cognitive layer) |
| NIFS-700-08 | Agents (voters) |
