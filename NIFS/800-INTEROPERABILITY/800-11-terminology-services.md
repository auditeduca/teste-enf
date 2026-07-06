# NIFS-800-11: Terminology Services

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-800-11                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir os serviços de terminologia do NIS — lookup, tradução, mapeamento e validação de códigos clínicos.

## 2. Supported Terminologies

| Terminology | Records | NKOS File |
|-------------|---------|-----------|
| NANDA-I | 244 | `nursing_diagnoses.json` |
| NIC | 575 | `nursing_interventions.json` |
| NOC | 550 | `nursing_outcomes.json` |
| SNOMED CT | cross-map | `standard_mappings.json` |
| ICD-11 | cross-map | `standard_mappings.json` |
| LOINC | 300+ | `lab_reference_values.json` |
| RxNorm | cross-map | `drug_references.json` |
| ATC | cross-map | `drug_references.json` |
| ISO 18104 | composition | (derived from NANDA/NIC) |

## 3. Service Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/terminology/lookup` | GET | Lookup code by system + code |
| `/terminology/search` | GET | Search by display text |
| `/terminology/translate` | GET | Map code between systems |
| `/terminology/validate` | POST | Validate code exists |
| `/terminology/subsumes` | GET | Check if code A subsumes code B |
| `/terminology/codesystem` | GET | List all code systems |

## 4. Lookup Example

```
GET /terminology/lookup?system=NANDA&code=00047

Response:
{
  "system": "NANDA",
  "code": "00047",
  "display": "Risk of Impaired Skin Integrity",
  "domain": "Safety/Protection",
  "class": "Physical Injury",
  "definition": "Vulnerable to alteration in skin integrity...",
  "cross_maps": {
    "SNOMED_CT": "420324007",
    "ICD_11": "...",
    "ISO_18104": { "focus": "skin_integrity", "judgment": "risk" }
  }
}
```

## 5. NKOS Reference

- `datasets/metadata/canonical_registry.json` — registry com todas as entidades e counts
- `datasets/master/standard_mappings.json` — mapeamentos entre sistemas
- `datasets/master/nursing_dictionary.json` — dicionário de enfermagem
- `datasets/master/search_synonyms.json` — sinônimos para busca

## 6. NIS Implementation

| Table | Role |
|-------|------|
| `ni_ref.code_systems` | Code system registry |
| `ni_onto.ontology_mappings` | Cross-maps |
| `ni_ref.terminology_values` | Code values |

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-400-15 | Code Systems (data model) |
| NIFS-500-08 | Ontology Mapping (graph) |
| NIFS-800-12 | Code Mapping (mapping service) |
