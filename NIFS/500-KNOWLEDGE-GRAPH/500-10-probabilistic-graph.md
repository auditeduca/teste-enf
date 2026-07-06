# NIFS-500-10: Probabilistic Graph

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-500-10                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a camada probabilística do grafo — como distribuições de probabilidade são propagadas entre nós.

## 2. Bayesian Graph Structure

```
         Braden ≤ 12
            ↓ P=0.87
    NANDA 00047 ──── P=0.85 ──→ NIC 3540
       ↓ P=0.70                         ↓ P=0.65
    NOC 1101 ←───────────────────────────┘
```

Cada aresta carrega uma probabilidade condicional além do peso determinístico.

## 3. NIS Implementation

| Table | Role |
|-------|------|
| `ni_prob.probability_models` | Modelos: conditional, bayesian, markov, logistic |
| `ni_prob.bayesian_links` | Links P(A\|B) entre nós do grafo |
| `ni_prob.uncertainty_distributions` | Distribuições completas (beta, normal, etc.) |
| `ni_prob.confidence_intervals` | Intervalos de confiança por nó |
| `ni_prob.prior_beliefs` | Priors por população |

## 4. Belief Propagation

```
1. Start: Priors from ni_prob.prior_beliefs
   P(NANDA 00047 | ICU) = 0.12 (base rate)

2. Evidence: Braden = 12 observed
   P(Braden ≤ 12 | NANDA 00047) = 0.87

3. Bayesian update:
   P(NANDA 00047 | Braden=12) = [0.87 × 0.12] / P(Braden=12)
                              = 0.91

4. Propagate to connected nodes:
   P(NIC 3540 recommended) = 0.91 × 0.85 = 0.77
   P(NOC 1101 will improve) = 0.77 × 0.70 = 0.54
```

## 5. Model Types

| Type | Use | Example |
|------|-----|---------|
| conditional | P(A\|B) direta | P(Úlcera\|Braden≤12) = 0.87 |
| bayesian | Rede bayesiana completa | Multi-evidence hypothesis ranking |
| markov | Cadeia de estados | P(critical→stable) = 0.35 em 24h |
| logistic | Regressão | P(infection\|age, comorbidity, LOS) |

## 6. APGAR Simulator Integration

`apgar_result_simulator.json` já tem probabilidades:
```json
{"score_range": "0-3", "probability": 0.75, "outcome": "recovery_with_intervention"}
```
Isso mapeia diretamente para `ni_prob.probability_models` (type=conditional).

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-500-05 | Confidence (probability as confidence) |
| NIFS-600-08 | Bayesian Network |
| NIFS-600-09 | Risk Prediction |
