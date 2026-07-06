# NIFS-200-09: Patient Safety

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-200-09                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir segurança do paciente como domínio clínico integrado ao NIS.

## 2. Safety Domains

| Domain | NIS Implementation |
|--------|-------------------|
| Medication safety | 9 Rights check, `ni.nine_rights_medication` |
| Fall prevention | Morse/Schmid calculators, risk prediction |
| Pressure ulcer prevention | Braden, `ni.safety_goal_medication_cross` |
| Infection control | Protocol engine, safety goals |
| Surgical safety | Checklist protocol, timeout |
| Patient identification | Hash único, double verification |
| Communication safety | Structured handoff, `ni_temporal.clinical_events` |

## 3. Safety Goals (WHO/ANS)

O NIS integra as 6 metas de segurança em `ni.safety_goals`:

| # | Goal | NIS Check |
|---|------|-----------|
| 1 | Patient identification | Hash match |
| 2 | Safe surgery | Protocol + timeout |
| 3 | Safe procedures | Protocol steps |
| 4 | Safe communication | Structured handoff |
| 5 | High-alert medications | Double check |
| 6 | Hand hygiene | Protocol reminders |

## 4. Adverse Event Detection

```
Observation trend → deviation from expected → adverse_event flag
    ↓
ni_memory.outcomes[outcome_type='adverse']
    ↓
Alert + trace + root cause analysis
    ↓
Reinforcement signal (-1.0) → learning
    ↓
NEVER decay this memory
```

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-100-06 | Clinical Safety (4-layer model) |
| NIFS-200-11 | Risk Management |
| NIFS-600-09 | Risk Prediction |
