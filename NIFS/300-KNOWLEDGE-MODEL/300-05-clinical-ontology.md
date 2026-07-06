# NIFS-300-05: Clinical Ontology

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-300-05                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a ontologia clínica formal do NIS — a estrutura lógica que dá significado semântico às entidades e relações do universo de enfermagem.

## 2. What is an Ontology?

Uma ontologia é uma **especificação formal de uma conceitualização** — define:

- **Classes** (tipos de coisas que existem)
- **Properties** (atributos das coisas)
- **Relations** (como as coisas se conectam)
- **Axioms** (regras que são sempre verdadeiras)
- **Instances** (coisas específicas que existem)

O NIS não é apenas um banco de dados. É uma **ontologia computacional** que pode ser inferida, validada e rastreada.

## 3. Upper Ontology (DOLCE-inspired)

```
┌─────────────────────────────────────────────┐
│              ENTITY (top)                    │
├──────────────┬──────────────────────────────┤
│  PARTICULAR  │     UNIVERSAL                │
│  (instances) │     (types/classes)          │
├──────────────┼──────────────────────────────┤
│ PATIENT      │ NURSING_CONCEPT              │
│ NURSE        │ NANDA_CLASS                  │
│ HOSPITAL     │ NIC_DOMAIN                   │
│ OBSERVATION  │ NOC_DOMAIN                   │
│ INTERVENTION │ ISO_AXIS                     │
│ OUTCOME      │ POPULATION_TYPE              │
└──────────────┴──────────────────────────────┘
```

## 4. Core Classes

### 4.1 Clinical Entity Hierarchy

```
ClinicalEntity (abstract)
├── Patient
│   ├── PatientState
│   └── PatientContext
├── Observation
│   ├── VitalSign
│   ├── AssessmentScore
│   ├── LabResult
│   ├── ClinicalFinding
│   └── PatientReport
├── Diagnosis
│   ├── NursingDiagnosis (NANDA-I)
│   │   ├── ActualDiagnosis
│   │   ├── RiskDiagnosis
│   │   ├── WellnessDiagnosis
│   │   └── HealthPromotionDiagnosis
│   └── MedicalDiagnosis (CID — cross-mapped, not diagnosed)
├── Intervention
│   ├── NursingIntervention (NIC)
│   ├── Protocol
│   └── MedicationAdministration
├── Goal
│   └── NursingGoal
├── Outcome
│   └── NursingOutcome (NOC)
├── Evidence
│   ├── ResearchEvidence
│   ├── ExpertOpinion
│   └── ClinicalExperience
└── Context
    ├── HospitalContext
    ├── WardContext
    ├── ResourceContext
    └── StaffContext
```

### 4.2 NANDA-I Taxonomy Hierarchy

```
NANDA-I
├── Domain 1: Health Promotion
│   ├── Class 1: Health Awareness
│   ├── Class 2: Health Management
│   └── ...
├── Domain 2: Nutrition
│   └── ...
├── Domain 11: Safety/Protection
│   ├── Class 1: Infection
│   ├── Class 2: Physical Injury
│   │   └── 00047: Risk of Impaired Skin Integrity
│   └── Class 3: Violence
└── Domain 12: Comfort
    └── ...
```

### 4.3 NIC Taxonomy Hierarchy

```
NIC
├── Domain 1: Basic Physiological
│   ├── Class: Activity and Exercise Management
│   │   └── 3540: Pressure Management
│   └── ...
├── Domain 2: Complex Physiological
├── Domain 3: Behavioral
├── Domain 4: Safety
├── Domain 5: Family
└── Domain 6: Health System
```

### 4.4 NOC Taxonomy Hierarchy

```
NOC
├── Domain 1: Functional Health
├── Domain 2: Physiologic Health
│   ├── Class: Tissue Integrity
│   │   └── 1101: Tissue Integrity: Skin & Mucous Membranes
│   └── ...
├── Domain 3: Psychosocial Health
├── Domain 4: Health Knowledge & Behavior
└── Domain 5: Perceived Health
```

## 5. ISO 18104 Axis Model

A ISO 18104 define que diagnósticos e intervenções de enfermagem são **composições de eixos**:

### 5.1 Diagnosis Statement

```
NursingDiagnosis = Focus + Judgment + [Duration] + [Context] + [Target]

Example:
  Focus: "Integridade tissular"
  Judgment: "Risco de comprometida"
  Context: "imobilidade, fricção"
  Target: "pele"
  → NANDA 00047
```

### 5.2 Action Statement

```
NursingAction = Action + Target + [Means] + [Context]

Example:
  Action: "Reduzir"
  Target: "Pressão"
  Means: "mudança de decúbito q2h"
  → NIC 3540
```

### 5.3 Axis Types

| Axis | Code | Example |
|------|------|---------|
| Focus | `focus` | Integridade tissular, dor, ansiedade |
| Judgment | `judgment` | Risco, comprometida, aumentada, diminuída |
| Action | `action` | Reduzir, monitorar, ensinar, administrar |
| Target | `target` | Pele, respiração, conhecimento |
| Means | `means` | Mudança de decúbito, oxigenoterapia |
| Duration | `duration` | Agudo, crônico, intermitente |
| Context | `context` | UTI, domicílio, pré-operatório |
| Topology | `topology` | Localizado, difuso, sistêmico |
| Certainty | `certainty` | Confirmado, suspeito, risco |

## 6. Ontological Axioms (Always True)

### 6.1 NANDA Axioms

```
A1: Every ActualDiagnosis has ≥1 definingCharacteristic
A2: Every RiskDiagnosis has ≥1 riskFactor
A3: Every WellnessDiagnosis has ≥1 wellnessIndicator
A4: No diagnosis can be both Actual AND Risk for the same Focus
A5: Every NANDA diagnosis belongs to exactly 1 Domain and 1 Class
```

### 6.2 NIC-NOC Axioms

```
A6: Every Intervention targets ≥1 Goal
A7: Every Outcome measures ≥1 Diagnosis or Intervention
A8: An Outcome without a linked Intervention is a monitoring point, not a goal
```

### 6.3 ISO Composition Axioms

```
A9:  Every NursingDiagnosis has exactly 1 Focus and ≥1 Judgment
A10: Every NursingAction has exactly 1 Action and ≥1 Target
A11: A Judgment without a Focus is semantically invalid
```

### 6.4 Safety Axioms

```
A12: Every recommendation with P < 0.40 must flag insufficient_data
A13: Every recommendation must have an explanation trace
A14: No weight update is applied without human validation
A15: Every adverse outcome must generate a learning signal
```

## 7. Cross-Ontology Mapping

O NIS mantém mapeamentos entre ontologias:

```
NANDA 00047 ←→ SNOMED CT 420324007
NANDA 00047 ←→ ICNP 10036217
NIC 3540    ←→ SNOMED CT 38137001
NOC 1101    ←→ LOINC 72174-6
```

Estes mapeamentos vivem em `ni_onto.ontology_mappings` e são validados pela `ni_epist.epistemology_rules` (V3_iso_composition).

## 8. Epistemological Validation

O schema `ni_epist` valida a integridade ontológica:

| Rule Type | What It Validates |
|-----------|------------------|
| V1_ontology | Estrutura hierárquica válida (Domain→Class→Concept) |
| V2_code_validity | Códigos existem e são válidos na versão da terminologia |
| V3_iso_composition | Composições ISO seguem os axiomas (A9-A11) |
| V4_scope | Conceitos estão no escopo da enfermagem (não médico) |

## 9. Schema Mapping

| Table | Ontological Role |
|-------|-----------------|
| `ni_graph.nodes` | Instances of ontology classes |
| `ni_graph.edge_types` | Ontological relations |
| `ni_graph.edges` | Relation instances |
| `ni_onto.ontology_mappings` | Cross-ontology equivalence |
| `ni_iso.axis_terms` | ISO 18104 axis values |
| `ni_iso.compositions` | ISO diagnosis compositions |
| `ni_iso.action_compositions` | ISO action compositions |
| `ni_epist.epistemology_rules` | Axiom enforcement |
| `ni_epist.verification_log` | Validation results |

## 10. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-300-01 | Universe Model (entities) |
| NIFS-300-02 | Entity Catalog (complete list) |
| NIFS-300-03 | Relationship Catalog (complete relations) |
| NIFS-200-24 | ISO 18104 (terminology standard) |
| NIFS-500-01 | Node Types (graph implementation) |
| NIFS-500-02 | Edge Types (graph relations) |

## 11. References

- Guarino, N. (1998). Formal Ontology in Information Systems
- Gangemi, A. et al. (2002). Sweetening Ontologies with DOLCE
- ISO 18104:2003 — Health Informatics: Integration of a Reference Terminology Model for Nursing
- NANDA-I 2024-2026 Definitions and Classification
- Cimino, J.J. (1998). Desiderata for Controlled Medical Vocabularies in the 21st Century

## 12. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — formal ontology with ISO axes | Leivis Melo |
