# NIFS-300-09: Aggregation

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-300-09                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o NIS agrega múltiplas observações/instâncias em conceitos de nível superior.

## 2. Aggregation Patterns

### 2.1 Temporal Aggregation
```
Multiple observations over time → Trend → Risk trend
  ni_temporal.observations (many)
    → ni_temporal.time_series (aggregated metric)
      → ni_reasoning.scores (trend-based risk score)
```

### 2.2 Population Aggregation
```
Multiple patient episodes → Population statistics → Prior beliefs
  ni_memory.episodes (many, same population)
    → aggregate success/failure rates
      → ni_prob.prior_beliefs (population-specific prior)
```

### 3.3 Graph Aggregation
```
Multiple edges between same nodes → Aggregate weight
  ni_graph.edges (many, same source/target)
    → average(weight × evidence_grade) → effective edge weight
```

## 3. NIS Implementation

| Pattern | Mechanism |
|---------|-----------|
| Temporal | `ni_temporal.time_series` rollups |
| Population | `ni_prob.prior_beliefs` by population_id |
| Graph | `ni_graph.edges` weight aggregation |
| Council | `ni_council.votes` → consensus aggregation |
| Attention | `ni_attention.attention_signals` → top-N selection |

## 4. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-300-07 | Inheritance |
| NIFS-300-08 | Composition |
| NIFS-600-10 | Clinical Attention (aggregation of signals) |
