# NIFS-200-18: Terminologies — SNOMED CT

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-200-18                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a integração do SNOMED CT no NIS como terminologia clínica de referência.

## 2. SNOMED CT Overview

| Aspect | Value |
|--------|-------|
| Full name | Systematized Nomenclature of Medicine — Clinical Terms |
| Concepts | ~350,000+ |
| Structure | Hierarchical taxonomy |
| Code format | Numeric (e.g., 420324007) |
| NIS table | `ni_mining.snomed_nanda_map` |

## 3. Nursing-relevant SNOMED subsets

| Subset | Use in NIS |
|--------|-----------|
| Nursing Practice | Cross-map to NANDA/NIC/NOC |
| Clinical Findings | Clinical observations |
| Procedures | Interventions |
| Situations | Context/setting |
| Body Structures | Assessment targets |
| Pharmaceutical/Biologic | Medication context |

## 4. SNOMED ↔ NANDA Mapping

```
NANDA 00047 ↔ SNOMED CT 420324007 (Risk for impaired skin integrity)
NIC 3540    ↔ SNOMED CT 38137001 (Pressure management)
NOC 1101    ↔ SNOMED CT related concept
```

Mapeamento em `ni_mining.snomed_nanda_map` com:
- `snomed_code`: código SNOMED
- `snomed_fsn`: Fully Specified Name
- `nanda_code`: código NANDA equivalente

## 5. Use Cases

| Use Case | How SNOMED Helps |
|----------|-----------------|
| Interoperabilidade EHR | SNOMED é padrão em muitos EHRs |
| Cross-mapping | Liga NANDA a terminologia médica |
| FHIR resource coding | FHIR usa SNOMED como CodeSystem |
| Evidence linking | Pesquisas indexadas por SNOMED |

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-14 | NANDA-I |
| NIFS-800-01 | FHIR (SNOMED as CodeSystem) |
| NIFS-500-08 | Ontology Mapping |
