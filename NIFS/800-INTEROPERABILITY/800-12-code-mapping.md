# NIFS-800-12: Code Mapping

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-800-12                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o NIS mapeia códigos entre diferentes terminologias clínicas (NANDA ↔ SNOMED CT ↔ ICD-11, etc.).

## 2. Mapping Types

| Type | Meaning | Confidence | Example |
|------|---------|------------|---------|
| exact | Same concept | 1.0 | NANDA 00047 ↔ SNOMED 420324007 |
| broader | NIS concept is broader | 0.85 | NANDA 00046 → ICD-11 broader category |
| narrower | NIS concept is narrower | 0.85 | NIC 3540 → SNOMED narrower procedure |
| related | Similar but not identical | 0.60 | NANDA 00033 ↔ ICD-11 related |
| unmapped | No mapping exists | 0.0 | — |

## 3. Mapping Matrix

| From ↓ / To → | NANDA | NIC | NOC | SNOMED CT | ICD-11 | LOINC |
|----------------|-------|-----|-----|-----------|--------|-------|
| NANDA | — | NNN | NNN | ✅ | ✅ | — |
| NIC | NNN | — | NNN | ✅ | — | — |
| NOC | NNN | NNN | — | ✅ | — | ✅ |
| SNOMED CT | ✅ | ✅ | ✅ | — | ✅ | ✅ |
| ICD-11 | ✅ | — | — | ✅ | — | — |

NNN = via `nnn_linkages.json` (1500 linkages with strength)
✅ = direct cross-map in `standard_mappings.json`

## 4. Mapping Service

```
POST /terminology/translate
{
  "from": { "system": "NANDA", "code": "00047" },
  "to": "SNOMED_CT"
}

Response:
{
  "mappings": [
    { "system": "SNOMED_CT", "code": "420324007", "type": "exact", "confidence": 1.0 }
  ]
}
```

## 5. NKOS Reference

- `datasets/master/standard_mappings.json` — mapeamentos padrão
- `datasets/clinical/nnn_linkages.json` — 1500 NANDA→NIC→NOC linkages
- `datasets/clinical/nursing_diagnoses.json` — cada NANDA tem `snomed_ct_code` + `icd_11_code`

## 6. NIS Implementation

| Table | Role |
|-------|------|
| `ni_onto.ontology_mappings` | Cross-map registry |
| `ni_ref.code_systems` | Code system definitions |

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-800-11 | Terminology Services |
| NIFS-500-08 | Ontology Mapping (graph level) |
| NIFS-400-15 | Code Systems (data registry) |
