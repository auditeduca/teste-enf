# NIFS-500-05: Confidence

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-500-05                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o modelo de confiança (confidence) que complementa os pesos determinísticos do grafo.

## 2. Confidence vs Weight

| Aspect | Weight | Confidence |
|--------|--------|-----------|
| Nature | Determinístico (regra/curador) | Probabilístico (bayesiano/empírico) |
| Source | NNN linkages, regras | Dados observados, inferência bayesiana |
| Update | Via validação humana | Via atualização bayesiana automática |
| Table | `ni_graph.edges.weight` | `ni_graph.edges.confidence` |
| Range | 0-1 | 0-1 |

## 3. Bayesian Confidence

```
Prior: P(NANDA 00047 | ICU population) = 0.12
Likelihood: P(Braden ≤ 12 | NANDA 00047) = 0.87
Evidence: Braden = 12 observed
Posterior: P(NANDA 00047 | Braden=12, ICU) = 0.91
    → confidence = 0.91
```

## 4. Confidence Propagation

```
Observation (confidence=0.95)
    → Edge (weight=0.85, confidence=null)
    → Bayesian update: confidence = 0.95 × 0.85 = 0.81
    → Propagate to connected nodes
    → Updated beliefs across graph
```

## 5. NIS Implementation

| Table | Field | Role |
|-------|-------|------|
| `ni_graph.edges` | `confidence` | Edge-level confidence |
| `ni_reasoning.scores` | `score_value` (type=probability) | Per-hypothesis confidence |
| `ni_prob.bayesian_links` | `conditional_prob` | Bayesian parameters |
| `ni_prob.confidence_intervals` | lower/upper | CI for confidence |
| `ni_prob.uncertainty_distributions` | parameters | Full distribution |

## 6. Uncertainty Communication

O Nurse-PaLM nunca responde apenas "Diagnóstico: X". Responde:

```
NANDA 00047 (Risco de Integridade Tissular) — P=0.91 [CI 0.82-0.96]
NANDA 00046 (Integridade Tissular Prejudicada) — P=0.18 [CI 0.08-0.34]
NANDA 00004 (Risco de Infecção) — P=0.06 [CI 0.02-0.15]
```

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-500-04 | Weights (deterministic complement) |
| NIFS-600-08 | Bayesian Network |
| NIFS-600-06 | Evidence Ranking |
