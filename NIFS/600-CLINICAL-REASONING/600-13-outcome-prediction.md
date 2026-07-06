# NIFS-600-13: Outcome Prediction

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-600-13                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o NIS prevê desfechos clínicos (NOC) — qual valor esperado, em quanto tempo, e com qual incerteza.

## 2. Prediction Model

```
predicted_noc = current_noc + expected_delta

expected_delta = edge_weight(NANDA→NIC) × edge_weight(NIC→NOC) × context_modifier × time_factor

P(improved) = sigmoid(expected_delta - threshold)
```

## 3. Prediction Components

### 3.1 Expected NOC Delta

```
NANDA 00047 → NIC 3540 → NOC 1101

edge_weight(00047→3540) = 0.85
edge_weight(3540→1101) = 0.72
context_modifier(ICU, postop) = 1.1
time_factor(72h) = 0.90

expected_delta = 0.85 × 0.72 × 1.1 × 0.90 = 0.61
current_noc = 2
predicted_noc = 2 + (0.61 × 3) = 3.83 → round to 4
```

### 3.2 Time to Improvement

| Intervention Type | Typical Time | Distribution |
|-------------------|-------------|--------------|
| Position change | 24-48h | Lognormal(μ=1.5, σ=0.5) |
| Pressure management | 48-96h | Lognormal(μ=1.8, σ=0.6) |
| Wound care | 5-14 days | Lognormal(μ=2.5, σ=0.8) |
| Medication | 1-6h | Lognormal(μ=1.2, σ=0.4) |

### 3.3 Outcome Probabilities

```
P(improved)     = 0.72  (NOC increases ≥ 1 point)
P(unchanged)    = 0.18  (NOC stays same)
P(deteriorated) = 0.06  (NOC decreases)
P(adverse)      = 0.04  (adverse event)

Expected NOC: 3.83 ± 0.80
Time to improvement: 72h (median, CI: 48-120h)
```

## 4. Multi-Intervention Prediction

When multiple NICs are applied simultaneously:

```
NIC 3540 + NIC 6540 combined:

combined_delta = delta(3540) + delta(6540) × synergy_factor

synergy_factor = 0.3 (diminishing returns — not additive)

delta(3540) = 0.61
delta(6540) = 0.45

combined_delta = 0.61 + (0.45 × 0.3) = 0.75
predicted_noc = 2 + (0.75 × 3) = 4.25 → round to 4
```

## 5. Validation

```
Predicted: NOC = 3.83 (72h)
Actual:    NOC = 4.0 (68h)

Prediction error: |3.83 - 4.0| = 0.17 (good)
Time error: |72 - 68| = 4h (good)
Calibration: predicted P(improved)=0.72, actual=improved ✓
```

Systematic errors feed back to `ni_learning.weight_updates` to adjust edge weights.

## 6. Schema Summary

| Table | Purpose |
|-------|---------|
| `ni_planner.plan_nodes` | Expected NOC delta per node |
| `ni_prob.probability_models` | P(outcome) models |
| `ni_twin.simulation_results` | Simulated outcomes |
| `ni_memory.outcomes` | Actual outcomes for validation |
| `ni_twin.simulation_validations` | Predicted vs actual |

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-11 | Goal Planning (uses predictions) |
| NIFS-600-14 | Simulation (validates predictions) |
| NIFS-600-15 | Digital Twin (carries predictions) |
| NIFS-600-17 | Learning Loop (corrects predictions) |

## 8. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — delta model + multi-NIC + validation | Leivis Melo |
