# NIFS-400-15: Code Systems

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-400-15                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Catalogar todos os sistemas de codificação clínica integrados ao NIS.

## 2. Code System Registry

| System | Code Format | NIS Table | Use |
|--------|------------|-----------|-----|
| NANDA-I | 00047 (5-digit) | `ni.nanda_diagnoses` | Nursing diagnoses |
| NIC | 3540 (4-digit) | `ni.nic_interventions` | Nursing interventions |
| NOC | 1101 (4-digit) | `ni.noc_outcomes` | Nursing outcomes |
| ISO 18104 | UUID + axis | `ni_iso.axis_terms` | Compositional model |
| SNOMED CT | 123456789 (numeric) | `ni_onto.ontology_mappings` | Cross-map reference |
| LOINC | 2345-7 (hyphenated) | `ni_mining.loinc_noc_map` | Labs, vitals, assessments |
| ICD-10/11 | I21.9, BA00 (alphanumeric) | `ni.cid_diagnoses` | Medical diagnoses |
| RxNorm | CUI 7388 (numeric) | `ni.medications_anvisa` (cross) | Medication nomenclature |
| ATC | C01CA03 (alphanumeric) | `ni.medications_anvisa` (cross) | Drug classification |
| UCUM | mmHg, kg/m2 | `ni_onto.ucum_units` | Clinical units |
| FHIR URI | http://hl7.org/fhir | `ni_interop.profiles` | Resource identification |

## 3. Cross-Mapping Architecture

```
NANDA 00047
  ├── snomed_ct: 420324007 (via ni_onto.ontology_mappings)
  ├── icd-11:    ED80 (via ni.cid_nanda_map)
  ├── iso:       focus=skin_integrity + judgment=risk_impaired
  └── loinc:     72514-3 (assessment tool)
```

## 4. Code System URIs (FHIR)

| System | URI |
|--------|-----|
| SNOMED CT | http://snomed.info/sct |
| LOINC | http://loinc.org |
| ICD-10 | http://hl7.org/fhir/sid/icd-10 |
| ICD-11 | http://hl7.org/fhir/sid/icd-11 |
| RxNorm | http://www.nlm.nih.gov/research/umls/rxnorm |

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-14 to 200-24 | Terminology documents (per system) |
| NIFS-400-16 | Reference Data |
| NIFS-800-01 | FHIR (CodeSystem resources) |
