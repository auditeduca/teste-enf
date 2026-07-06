# NIFS-200-19: Terminologies — LOINC

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-200-19                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a integração do LOINC (Logical Observation Identifiers Names and Codes) no NIS.

## 2. LOINC Overview

| Aspect | Value |
|--------|-------|
| Full name | Logical Observation Identifiers Names and Codes |
| Codes | ~100,000+ |
| Purpose | Padronizar observações laboratoriais e clínicas |
| Code format | nnnnn-n (e.g., 8867-4) |
| NIS table | `ni_mining.loinc_noc_map` |

## 3. LOINC in NIS

| Use | Example |
|-----|---------|
| Vital signs coding | 8867-4 (Heart rate), 8480-6 (BP systolic) |
| Lab results | 2160-0 (Creatinine), 33747-0 (Lactate) |
| Assessment scales | LOINC codes for Braden, Glasgow, etc. |
| NOC mapping | LOINC ↔ NOC cross-map |

## 4. LOINC ↔ NOC Mapping

```
LOINC 72174-6 (Pressure ulcer assessment) ↔ NOC 1101 (Tissue Integrity)
LOINC 8867-4 (Heart rate) ↔ NOC related vital sign outcomes
```

Mapeamento em `ni_mining.loinc_noc_map` com:
- `loinc_code`: código LOINC
- `loinc_name`: nome do código
- `noc_code`: código NOC equivalente

## 5. FHIR Integration

LOINC é o sistema padrão para FHIR Observation codes:

```json
{
  "resourceType": "Observation",
  "code": {
    "coding": [{"system": "http://loinc.org", "code": "8867-4", "display": "Heart rate"}]
  },
  "valueQuantity": {"value": 110, "unit": "/min"}
}
```

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-16 | NOC |
| NIFS-800-01 | FHIR (LOINC as Observation codes) |
| NIFS-600-03 | Assessment Pipeline (uses LOINC codes) |
