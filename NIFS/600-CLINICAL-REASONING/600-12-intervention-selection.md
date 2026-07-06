# NIFS-600-12: Intervention Selection

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-600-12                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o NIS seleciona e prioriza intervenções de enfermagem (NIC) a partir de um diagnóstico confirmado.

## 2. Selection Pipeline

```
Confirmed NANDA diagnosis
    ↓
Graph traversal: NANDA → NIC candidates
    ↓
Filter by: population, context, contraindications
    ↓
Rank by: edge_weight × evidence_grade × expected_noc_delta
    ↓
Select: Primary (highest) + Adjunct (second) + Contingency
    ↓
Safety check: contraindication? interaction? resource available?
    ↓
Output: Intervention set with rationale
```

## 3. Ranking Formula

```
nic_score = edge_weight(NANDA→NIC) 
          × evidence_grade_factor
          × expected_noc_delta
          × context_fit
          × resource_availability
          × population_match
```

| Factor | Source | Range |
|--------|--------|-------|
| `edge_weight` | `ni_graph.edges` | 0.0–1.0 |
| `evidence_grade_factor` | `ni_mining.graded_evidence` | 0.25–0.95 |
| `expected_noc_delta` | `ni_planner.plan_nodes` | 0.0–3.0 |
| `context_fit` | World Model | 0.5–1.0 |
| `resource_availability` | `ni_world.resource_contexts` | 0.0–1.0 |
| `population_match` | `ni.populations` | 0.6–1.0 |

## 4. Selection Tiers

| Tier | Role | Selection Rule |
|------|------|---------------|
| **Primary** | Main intervention | Highest nic_score |
| **Adjunct** | Complementary | Second highest, synergistic with primary |
| **Contingency** | If primary fails | Alternative with different mechanism |
| **Escalation** | If deterioration | Protocol-based, highest intensity |

## 5. Example

```
NANDA 00047 → NIC candidates:

NIC 3540 (Pressure Management):     score = 0.85 × 0.95 × 2.0 × 1.0 × 1.0 × 1.0 = 1.62
NIC 6540 (Positioning):             score = 0.72 × 0.70 × 1.5 × 1.0 × 1.0 × 1.0 = 0.76
NIC 2250 (Skin Surveillance):       score = 0.55 × 0.50 × 1.0 × 1.0 × 1.0 × 1.0 = 0.28
NIC 2252 (Wound Care):              score = 0.40 × 0.50 × 0.5 × 1.0 × 1.0 × 1.0 = 0.10

Selection:
  Primary:     NIC 3540 (1.62)
  Adjunct:     NIC 6540 (0.76)
  Contingency: NIC 2250 (0.28) — if no improvement in 72h
  Escalation:  Protocol C — if deterioration
```

## 6. Context-Aware Adjustments

```
Context: UTI lotada, sem bomba de infusão
    ↓
NIC 3540 (manual turning):     resource_factor = 1.0 (no equipment needed)
NIC 2252 (wound care):         resource_factor = 0.5 (needs supplies)
NIC 3590 (pressure ulcer care): resource_factor = 0.3 (needs specialized bed)

→ Manual interventions ranked higher when resources scarce
```

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-11 | Goal Planning (uses selected interventions) |
| NIFS-600-13 | Outcome Prediction (predicts NIC effect) |
| NIFS-300-16 | Interventions (conceptual model) |
| NIFS-200-15 | NIC (terminology) |

## 8. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — 4-tier selection + context-aware | Leivis Melo |
