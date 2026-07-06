# NIFS-300-13: Findings

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-300-13                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir findings clínicos — interpretações de observações que indicam anormalidade.

## 2. Finding vs Observation

| Concept | Definition | Example |
|---------|-----------|---------|
| Observation | Dado bruto | "Glicemia 320 mg/dL" |
| Finding | Interpretação anormal | "Hiperglicemia severa" |
| Hypothesis | Possível diagnóstico | "NANDA 00179 (Risco de glicemia instável)" |

## 3. Finding Generation

```
Observation: Glicemia 320 mg/dL
    ↓ Compare against lab_reference_values (70-99 fasting)
Finding: Hiperglicemia (value > reference_high × 3)
    ↓ SNOMED CT: "Hyperglycemia" (74095-7)
    ↓ Attention score: 0.92 (critical)
    ↓ Feeds reasoning as evidence_for hypothesis
```

## 4. Finding Types

| Type | Example | NIS Path |
|------|---------|----------|
| Deviation | Lab value outside reference | `lab_reference_values` comparison |
| Score interpretation | Braden ≤ 12 = high risk | `calculator_definitions.interpretation_bands` |
| Pattern | Trend worsening over 4h | `ni_temporal.time_series` trend analysis |
| Absence | Expected finding missing | Inference from checklist |
| Contradiction | Two findings conflict | `ni_cog.conflicting_evidence` |

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-300-12 | Observations (findings derive from observations) |
| NIFS-300-14 | Assessments (findings feed assessment) |
| NIFS-600-04 | Hypothesis Generation (findings as evidence) |
