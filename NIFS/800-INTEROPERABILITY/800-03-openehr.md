# NIFS-800-03: openEHR

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-800-03                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o NIS interoperabilidade via openEHR — padrão de prontuário eletrônico com archetypes e templates.

## 2. openEHR Architecture

```
openEHR Template (OPT)
    ↓
Archetypes (clinical concepts)
    ↓
Compositions (actual patient data)
    ↓
NIS Adapter maps to ni_clinical entities
```

## 3. Key openEHR Templates for Nursing

| Template | openEHR Concept | NIS Mapping |
|----------|----------------|-------------|
| Nursing Assessment | openEHR-EHR-SECTION.nursing_assessment | `ni_clinical.observations` |
| Nursing Diagnosis | openEHR-EHR-EVALUATION.nursing_diagnosis | `ni_clinical.diagnoses` |
| Care Plan | openEHR-EHR-SECTION.care_plan | `ni_planner.plans` |
| Vital Signs | openEHR-EHR-CLUSTER.vital_signs | `ni_clinical.observations` |
| Medication Administration | openEHR-EHR-INSTRUCTION.medication | `ni_pharm.administrations` |

## 4. NIS Implementation

| Table | Role |
|-------|------|
| `ni_interop.openehr_templates` | Template registry |
| `ni_interop.openehr_compositions` | Imported compositions |
| `ni_interop.archetype_mappings` | Archetype → NIS entity mapping |

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-800-01 | FHIR (alternative standard) |
| NIFS-800-02 | HL7 v2 (legacy standard) |
