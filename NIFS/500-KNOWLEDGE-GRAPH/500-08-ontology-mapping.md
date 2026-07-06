# NIFS-500-08: Ontology Mapping

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-500-08                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o NIS mapeia seus conceitos internos para ontologias externas (SNOMED CT, LOINC, ICD, FHIR).

## 2. Mapping Architecture

```
ni_graph.nodes (NIS internal)
    ↕
ni_onto.ontology_mappings (bridge table)
    ↕
External ontologies (SNOMED CT, LOINC, ICD-11, RxNorm, ATC)
```

## 3. Mapping Table

`ni_onto.ontology_mappings` conecta conceito NIS ↔ sistema externo:

| Field | Example |
|-------|---------|
| `ni_concept_type` | NANDA |
| `ni_concept_code` | 00047 |
| `external_system` | SNOMED_CT |
| `external_code` | 420324007 |
| `external_name` | "Risk of impaired skin integrity" |
| `mapping_confidence` | 1.0 (exact) / 0.85 (close) / 0.60 (broader) |
| `mapping_type` | exact, broader, narrower, related |

## 4. Cross-Map Coverage

| NIS Concept | → SNOMED CT | → ICD-11 | → LOINC |
|-------------|-------------|----------|---------|
| NANDA (244) | ✅ per diagnosis | ✅ via cid_nanda_map | ✅ via assessment tool |
| NIC (575) | ✅ per intervention | — | — |
| NOC (550) | ✅ per outcome | — | ✅ via loinc_noc_map |
| Calculadoras (100) | — | — | ✅ per tool (LOINC) |
| Medicamentos (500) | ✅ | — | ✅ via RxNorm |

## 5. NKOS Data

- `nursing_diagnoses.json`: cada NANDA tem `snomed_ct_code` + `icd_11_code`
- `nursing_interventions.json`: cada NIC tem `snomed_ct_code`
- `drug_references.json`: cada drug tem `snomed_ct_code` + `atc_code`
- `lab_reference_values.json`: cada lab value tem `loinc_code`
- `clinical_concepts.json`: 2000 conceitos com `snomed_ct_code` + `icd_11_code`

## 6. FHIR CodeSystem Mapping

```json
{
  "system": "http://snomed.info/sct",
  "code": "420324007",
  "display": "Risk of impaired skin integrity",
  "nis_mapping": "NANDA:00047"
}
```

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-400-15 | Code Systems (registry) |
| NIFS-800-01 | FHIR (resource mapping) |
| NIFS-200-18 | SNOMED CT (terminology) |
