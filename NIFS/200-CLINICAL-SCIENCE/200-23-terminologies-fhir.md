# NIFS-200-23: Terminologies — FHIR

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-200-23                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a integração do FHIR (Fast Healthcare Interoperability Resources) no NIS como padrão de interoperabilidade.

## 2. FHIR Overview

| Aspect | Value |
|--------|-------|
| Full name | Fast Healthcare Interoperability Resources |
| Owner | HL7 International |
| Current version | R4 (R5 em transição) |
| Format | JSON / XML |
| NIS schema | `ni_interop` (profiles, resource_mappings, sync_history, message_validation) |

## 3. FHIR Resources Used by NIS

| NIS Entity | FHIR Resource | Direction |
|------------|--------------|-----------|
| `ni.cases` | Patient, Encounter | Inbound |
| `ni_temporal.observations` | Observation | Bidirectional |
| `ni.care_plans` | CarePlan, Condition | Bidirectional |
| `ni_memory.actions` | Procedure | Outbound |
| `ni_memory.outcomes` | Observation | Outbound |
| `ni_reasoning.trace` | ClinicalImpression | Outbound |
| `ni_explain.explanations` | DiagnosticReport | Outbound |
| `ni.medications_anvisa` | Medication, MedicationAdministration | Bidirectional |
| `ni_protocol.protocols` | PlanDefinition | Outbound |

## 4. NIS Interoperability Profiles

`ni_interop.profiles` define perfis de interoperabilidade:

| Profile | Standard | Use Case |
|---------|----------|----------|
| FHIR_R4_IPD | FHIR R4 | International Patient Summary |
| FHIR_R4_BR | FHIR R4 + RNDS | Brasil — RNDS (SUS) |
| OpenEHR | OpenEHR | Patient-centric longitudinal record |
| HL7_V2_ADT | HL7 v2 | Admission/Discharge/Transfer |

## 5. FHIR CodeSystems Used

| CodeSystem | NIS Use |
|-----------|---------|
| http://snomed.info/sct | Diagnoses, interventions, findings |
| http://loinc.org | Lab values, vital signs, assessments |
| http://www.nlm.nih.gov/research/umls/rxnorm | Medications |
| http://hl7.org/fhir/sid/icd-10 | Medical diagnoses (context) |
| http://hl7.org/fhir/sid/icd-11 | Medical diagnoses (context) |

## 6. NIS → FHIR Mapping Example

```json
{
  "resourceType": "Observation",
  "status": "final",
  "code": {
    "coding": [{"system": "http://loinc.org", "code": "2345-7", "display": "Glucose"}]
  },
  "valueQuantity": {"value": 145, "unit": "mg/dL"},
  "subject": {"reference": "Patient/{patient_identifier}"},
  "effectiveDateTime": "2026-07-05T10:30:00Z"
}
```

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-800-01 | FHIR (detailed implementation) |
| NIFS-200-18 | SNOMED CT (CodeSystem) |
| NIFS-200-19 | LOINC (CodeSystem) |
