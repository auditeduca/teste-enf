# NIFS-400-17: Master Data

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-400-17                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir master data do NIS — entidades centrais que estruturam o domínio e são referenciadas transacionalmente.

## 2. Master Data Entities

| Entity | Table | Role |
|--------|-------|------|
| **Countries** | NKOS `Country` (195) | Base geográfica |
| **Languages** | NKOS `Language` (30) | i18n base |
| **Locales** | `ni_i18n.locales` (400+) | Localization |
| **Clinical Concepts** | `ni.concepts` / `ni_graph.nodes` (2000) | Conceito clínico universal |
| **Master Entities** | NKOS `MasterEntity` (2000) | Entidades canônicas |
| **NANDA/NIC/NOC** | Terminology tables (1369) | Núcleo de enfermagem |
| **Safety Goals** | `ni.safety_goals` (6) | WHO IPSG |
| **9 Rights** | `ni.nine_rights_medication` (9) | Medication safety |
| **Populations** | `ni.populations` (6+) | Contexto populacional |
| **Gordon Patterns** | `ni_cog.gordon_patterns` (11) | Assessment framework |
| **Metaparadigm** | `ni_cog.metaparadigm_concepts` (4) | Pessoa, Ambiente, Saúde, Enfermagem |

## 3. Master Data vs Reference Data

| Aspect | Reference Data | Master Data |
|--------|---------------|-------------|
| Scope | Catálogos externos (CID, UCUM) | Núcleo do domínio NIS |
| Ownership | Standards bodies | NIS/Leivis |
| Change frequency | Por edição de terminologia | Por release do NIS |
| FK references | Muitas tabelas referenciam | Praticamente todas referenciam |

## 4. NKOS Canonical Registry

`canonical_registry.json` lista ~50 entidades master com contagem:
- ClinicalConcept: 2,000
- NursingDx: 244 | NursingInt: 575 | NursingOut: 550
- EntityRelation: 4,999 | EntityApplicability: 10,000
- NursingDictionary: 5,000 | SearchSynonyms: 10,000
- NNNLinkage: 1,500 | DrugInteraction: 2,000

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-400-16 | Reference Data |
| NIFS-300-02 | Entity Catalog |
