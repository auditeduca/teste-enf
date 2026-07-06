# NIFS-300-15: Diagnoses

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-300-15                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir diagnósticos de enfermagem como conceitos centrais do processo de raciocínio.

## 2. Diagnosis Model

```
NursingDiagnosis
├── nanda_code (PK, e.g., "00047")
├── domain_code (13 domains)
├── class_code (within domain)
├── definition
├── diagnosis_type: actual | risk | wellness | health_promotion
├── defining_characteristics[] (for actual)
├── risk_factors[] (for risk)
├── related_factors[]
├── snomed_ct_code (cross-map)
├── icd11_code (context)
├── evidence_code (GRADE)
├── related_tool_codes[] (calculators that trigger)
└── ISO composition: focus + judgment
```

## 3. Diagnosis in Reasoning Pipeline

```
Observations → Findings → Hypotheses (NANDA candidates)
    ↓
Hypothesis: NANDA 00047, P=0.87
Hypothesis: NANDA 00046, P=0.23
Hypothesis: NANDA 00004, P=0.08
    ↓
Differential diagnosis: top-3 by probability
    ↓
Evidence for/against each → Bayesian update
    ↓
Selected diagnosis: NANDA 00047 (P=0.91)
```

## 4. NIS Data (NKOS 2026)

| Data | Count | Source |
|------|-------|--------|
| NANDA diagnoses | 244 | `nursing_diagnoses.json` |
| Domains | 13 | NANDA-I 2024-2026 |
| NNN linkages | 1,500 | `nnn_linkages.json` (NANDA→NIC→NOC) |
| ISO compositions | per NANDA | `ni_iso.compositions` |

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-14 | NANDA-I (terminology) |
| NIFS-600-04 | Hypothesis Generation |
| NIFS-600-05 | Differential Diagnosis |
