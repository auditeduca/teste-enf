# NIFS-100-15: Data-Driven Design

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-100-15                        |
| Status        | Draft                              |
| Version       | 1.0.0 |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o NIS usa dados para evoluir — priors empíricos, weight updates, calibração e auditoria contínua.

## 2. Data Flows

```
Clinical Data (episodes, outcomes)
    ↓
Aggregation (by population, by diagnosis, by intervention)
    ↓
Statistical Analysis (frequencies, correlations, effectiveness)
    ↓
Knowledge Update (priors, weights, distributions)
    ↓
Human Validation (mandatory)
    ↓
Applied to Graph + Probabilistic Models
```

## 3. Data Sources

| Source | Data | Frequency |
|--------|------|-----------|
| `ni_memory.episodes` | Casos completos | Real-time |
| `ni_memory.outcomes` | Desfechos | Real-time |
| `ni_reasoning.sessions` | Decisões | Real-time |
| `ni_council.human_decisions` | Feedback humano | Real-time |
| `ni.assessment_log` | Calculadoras | Real-time |
| `ni_temporal.time_series` | Séries temporais | Continuous |

## 4. Data Quality

| Dimension | Metric | Target |
|-----------|--------|--------|
| Completeness | % campos preenchidos | > 95% |
| Accuracy | % valores corretos | > 98% |
| Timeliness | Idade dos dados | < 24h |
| Consistency | Conflitos entre fontes | 0% |
| Validity | Códigos válidos | 100% |

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-100-14 | Domain-Driven Design |
| NIFS-100-16 | Event-Driven Design |
| NIFS-1200-06 | Data Quality |
| NIFS-600-17 | Learning Loop |
