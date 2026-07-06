# NIFS-600-09: Risk Prediction

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-600-09                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir os modelos de predição de risco do NIS — como o sistema estratifica pacientes por probabilidade de eventos adversos.

## 2. Risk Layers

| Layer | What It Predicts | Models |
|-------|-----------------|--------|
| **Fall risk** | Probabilidade de queda | Morse, Schmid |
| **Pressure ulcer risk** | Risco de UP | Braden, Norton, Waterlow |
| **Sepsis risk** | Risco de sepse | NEWS2, qSOFA, SIRS |
| **Deterioration risk** | Risco de piora clínica | MEWS, NEWS2 |
| **Medication risk** | Risco de erro medicação | 9 Rights check |
| **Infection risk** | Risco de infecção | CDC criteria |
| **Readmission risk** | Risco de reinternação | LACE+ index |

## 3. Risk Score Pipeline

```
Patient observations
    ↓
Risk calculator (e.g., Braden)
    ↓
Score: 12
    ↓
Risk category: High (Braden ≤ 12 = high risk)
    ↓
P(event) from probability model: P(UP|Braden≤12, ICU) = 0.87
    ↓
Linked NANDA: 00047 (Risk of Impaired Skin Integrity)
    ↓
Recommended NIC: 3540, 6540
    ↓
Risk alert + safety check
```

## 4. Risk Categories

| Category | Range | Color | Action |
|----------|-------|-------|--------|
| Low | P < 0.10 | Green | Routine monitoring |
| Moderate | P 0.10–0.30 | Yellow | Preventive interventions |
| High | P 0.30–0.60 | Orange | Active interventions + protocol |
| Critical | P > 0.60 | Red | Immediate intervention + escalation |

## 5. Temporal Risk

Risco não é estático — muda ao longo do tempo:

```
Admission (Day 0): Braden = 18 → P(UP) = 0.08 (low)
Day 1: Braden = 15 → P(UP) = 0.15 (moderate)
Day 2: Braden = 12 → P(UP) = 0.32 (high) ← ALERT
Day 3: Braden = 11 → P(UP) = 0.45 (high) ← TREND WORSENING
Day 4: +NIC 3540 → Braden = 13 → P(UP) = 0.22 (moderate, improving)
```

Trend analysis: se P está subindo → alerta mesmo que ainda não seja "high".

## 6. Schema Summary

| Table | Purpose |
|-------|---------|
| `ni_cog.calculator_mappings` | Calculadoras de risco |
| `ni_cog.calculator_nnn_cross` | Risco → NANDA/NIC/NOC |
| `ni_prob.probability_models` | Modelos de P(event) |
| `ni_temporal.time_series` | Séries temporais de risco |
| `ni_reasoning.scores` | Scores de risco por sessão |

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-08 | Bayesian Network (P computation) |
| NIFS-600-10 | Clinical Attention (risk drives attention) |
| NIFS-200-11 | Risk Management (clinical science) |
| NIFS-100-06 | Clinical Safety (risk → safety) |

## 8. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — risk layers + temporal trend | Leivis Melo |
