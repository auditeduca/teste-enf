# NIFS-200-11: Risk Management

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-200-11                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir gestão de risco clínico no contexto do NIS.

## 2. Risk Identification

| Risk Category | Calculator/Tool | NIS Table |
|---------------|----------------|-----------|
| Pressure ulcer | Braden, Norton, Waterlow | `ni_cog.calculator_mappings` |
| Falls | Morse, Schmid | `ni_cog.calculator_mappings` |
| Sepsis | NEWS2, qSOFA | `ni_cog.calculator_mappings` |
| Deterioration | MEWS, NEWS2 | `ni_cog.calculator_mappings` |
| Malnutrition | MUST, NRS-2002 | `ni_cog.calculator_mappings` |
| Bleeding | HAS-BLED | `ni_cog.calculator_mappings` |
| Thromboembolism | Caprini, Padua | `ni_cog.calculator_mappings` |

## 3. Risk Stratification

| Level | P(event) | Color | Action |
|-------|----------|-------|--------|
| Low | < 0.10 | Green | Routine |
| Moderate | 0.10–0.30 | Yellow | Preventive |
| High | 0.30–0.60 | Orange | Active intervention |
| Critical | > 0.60 | Red | Immediate + escalation |

## 4. Temporal Risk Tracking

```
Risk score over time → trend analysis
    ↓
If trend worsening → alert even if still "moderate"
    ↓
ni_temporal.time_series → trend detection
    ↓
ni_reasoning.scores → risk score per session
```

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-09 | Patient Safety |
| NIFS-600-09 | Risk Prediction |
| NIFS-100-06 | Clinical Safety |
