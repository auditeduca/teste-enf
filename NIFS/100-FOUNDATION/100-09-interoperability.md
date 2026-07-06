# NIFS-100-09: Interoperability

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-100-09                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o princípio de interoperabilidade — o NIS não é uma ilha, é um nó no ecossistema de saúde.

## 2. Interoperability Standards

| Standard | Use | Section |
|----------|-----|---------|
| FHIR R4 | Troca de dados clínicos | NIFS-800-01 |
| HL7 v2 | Sistemas legacy | NIFS-800-02 |
| OpenEHR | Record longitudinal | NIFS-800-03 |
| SMART on FHIR | Auth + app launch | NIFS-800-04 |
| ISO 18104 | Terminologia de enfermagem | NIFS-200-24 |
| SNOMED CT | Terminologia clínica | NIFS-200-18 |
| LOINC | Códigos de laboratório | NIFS-200-19 |
| UCUM | Unidades clínicas | NIFS-300-05 |

## 3. Principles

- **Standards-first**: usar padrões existentes, não inventar
- **Bi-directional**: ler EHR e escrever de volta
- **Lossless**: mapeamento preserva semântica
- **Versioned**: FHIR R4 hoje, R5 quando maduro
- **Profiled**: NIS publica FHIR Profiles para nursing-specific resources

## 4. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-800-01 | FHIR (implementation) |
| NIFS-800-05 | REST (API) |
| NIFS-800-11 | Terminology Services |
