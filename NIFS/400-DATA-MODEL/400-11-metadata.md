# NIFS-400-11: Metadata

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-400-11                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a estratégia de metadata no NIS — dados sobre dados clínicos.

## 2. Metadata Categories

| Category | Description | NIS Table |
|----------|-------------|-----------|
| **Descriptive** | Título, descrição, tags, especialidade | `ni_content.metadata` |
| **Structural** | Hierarquia, relacionamentos, tipos | `ni_graph.nodes`, `ni_graph.edges` |
| **Administrative** | Status, versão, owner, permissions | `ni_knowledge.versions` |
| **Technical** | Schema, tipo, índices, constraints | NIFS-400 docs |
| **Provenance** | Origem, fonte, GRADE, DOI | `ni_mining.graded_evidence` |
| **Semantic** | SNOMED, LOINC, ICD, ISO mappings | `ni_onto.ontology_mappings` |
| **Usage** | Views, ratings, bookmarks | `ni_content.metadata` |

## 3. Content Metadata Fields

`ni_content.metadata` armazena por item de conteúdo:

| Field | Example |
|-------|---------|
| `specialty` | Neurologia, Cardiologia, UTI |
| `audience` | student, technician, nurse, academic, manager |
| `reading_time_min` | 8 |
| `difficulty_level` | beginner, intermediate, advanced |
| `seo_score` | 85/100 |
| `evidence_grade` | A, B, C, D (GRADE) |

## 4. SEO Metadata

NKOS `seo.json` + `ni_api.endpoints` gerenciam:
- Meta tags, Open Graph, canonical URLs
- Structured data (Schema.org MedicalEntity)
- GEO (Generative Engine Optimization)

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-400-15 | Code Systems (semantic metadata) |
| NIFS-900-04 | SEO (platform metadata) |
