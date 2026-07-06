# NIFS-000-08: Engineering Philosophy

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-000-08                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a filosofia de engenharia que distingue o NIS de projetos convencionais e estabelece as bases para uma plataforma de referência.

## 2. The Inversion Principle

A maioria dos projetos faz:

```
Banco → API → Front-end → "vamos ajustando"
```

O NIS faz o inverso:

```
Conhecimento → Especificação → Arquitetura → Banco → Código → IA → Interface
```

Esta inversão é o que separa um projeto comum de uma plataforma de referência.

## 3. The Specification as Product

O NIFS não é documentação auxiliar. É o **produto principal**. A aplicação é um artefato derivado.

### 3.1 Implications

- O NIFS tem seu próprio repositório Git
- O NIFS tem versionamento semântico independente
- O NIFS tem processo de revisão e aprovação
- Mudanças no runtime SEMPRE começam no NIFS
- O Excel é uma instância do NIFS-400-02, não o contrário

### 3.2 The Excel as Generator, Not Consumer

```
Excel (Canonical Model)
    ↓
SPEC (NIFS documents)
    ↓
Code Generator
    ↓
SQL + Neo4j + OpenAPI + GraphQL + FHIR + TypeScript + Python + React
    ↓
Runtime
```

O Excel nunca é consumido diretamente pela aplicação. Ele alimenta geradores que produzem artefatos.

## 4. RFC-Inspired Documentation

A documentação segue um padrão inspirado em RFCs (IETF), W3C, OpenEHR e FHIR:

| Documento | Conteúdo |
|-----------|----------|
| NIFS-000 | Visão e princípios do ecossistema |
| NIFS-100 | Princípios arquiteturais |
| NIFS-200 | Ciência clínica e terminologias |
| NIFS-300 | Modelo conceitual e ontologia |
| NIFS-400 | Dicionário de dados |
| NIFS-500 | Grafo de conhecimento |
| NIFS-600 | Motor de raciocínio clínico |
| NIFS-700 | Arquitetura de IA |
| NIFS-800 | APIs e interoperabilidade |
| NIFS-900 | Arquitetura de plataforma |
| NIFS-1000 | Segurança e privacidade |
| NIFS-1100 | Governança |
| NIFS-1200 | Padrões de qualidade |
| NIFS-1300 | Guia do desenvolvedor |
| NIFS-1400 | Deployment e infraestrutura |
| NIFS-1500 | Roadmap e pesquisa |
| NIFS-APP | Apêndices e referências |

## 5. Excel Reorganization (Proposed)

A versão v4.2 possui 116 abas. A reorganização proposta por domínio:

### 00 — Governance
- 00_Index, 00_Changelog, 00_Roadmap, 00_Glossary, 00_Standards, 00_References, 00_Licensing

### 01 — Clinical Knowledge
- NANDA, NIC, NOC, Assessments, Protocols, Guidelines, Safety, Risk, Care Plans, Clinical Concepts, Cases

### 02 — Knowledge Graph
- Entities, Relationships, Ontology, Taxonomy, Evidence Links, Clinical Graph, Temporal Graph, Inference Graph

### 03 — Data Model
- Tables, Columns, Constraints, Enums, Indexes, Views, Materialized Views, Metadata

### 04 — Interoperability
- FHIR, HL7, LOINC, SNOMED, ICNP, ICD, ATC, RxNorm, Mappings

### 05 — AI
- Reasoning, Evidence Ranking, Clinical Attention, Bayesian, Digital Twin, Simulation, Memory, Planning, Consensus, Agents

### 06 — Quality
- Validation Rules, Quality Gates, Completeness, Consistency, Evidence Quality, Review Workflow

### 07 — Platform
- API, Permissions, RBAC, Localization, Search, Logging, Observability

### 08 — Developer
- Naming, Generators, Folder Structure, Code Templates, Versioning

## 6. Metadata Columns for Every Entity

Toda entidade da especificação deve possuir estes metadados:

| Campo | Finalidade | Tipo |
|-------|-----------|------|
| Domain | Domínio clínico | VARCHAR(32) |
| Module | Módulo do sistema | VARCHAR(32) |
| Owner | Responsável | VARCHAR(64) |
| Status | Draft / Review / Approved / Deprecated | VARCHAR(16) |
| Version | Versionamento semântico | VARCHAR(16) |
| Source | Origem científica | VARCHAR(256) |
| Evidence Level | Nível de evidência GRADE | CHAR(1) |
| Confidence | Grau de confiança | NUMERIC |
| Review Date | Última revisão | DATE |
| Next Review | Próxima revisão | DATE |
| Tags | Busca | TEXT[] |
| FHIR Mapping | Correspondência FHIR | VARCHAR(128) |
| SNOMED Mapping | Correspondência SNOMED | VARCHAR(32) |
| API Exposure | Será exposto por API? | BOOLEAN |
| Searchable | Participa da busca? | BOOLEAN |
| AI Enabled | Utilizado pelo motor de IA? | BOOLEAN |

## 7. The Four-Level Architecture

```
Nível 1: NIFS (Specification)     — Documentação definitiva
    ↓
Nível 2: Knowledge Model (Excel)   — Modelo canônico
    ↓
Nível 3: Generated Artifacts       — SQL, Neo4j, OpenAPI, FHIR, TypeScript
    ↓
Nível 4: Runtime Platform          — PostgreSQL, API, IA, Frontend
```

Cada nível é gerado a partir do anterior. Mudanças fluem de cima para baixo. Nunca o contrário.

## 8. Pre-Development Document Checklist

| Documento | Status Antes do Desenvolvimento |
|-----------|-------------------------------|
| Visão do produto | ✅ Obrigatório |
| Modelo conceitual | ✅ Obrigatório |
| Ontologia | ✅ Obrigatório |
| Dicionário de dados | ✅ Obrigatório |
| Grafo de conhecimento | ✅ Obrigatório |
| Arquitetura da IA | ✅ Obrigatório |
| Motor de raciocínio clínico | ✅ Obrigatório |
| APIs | ✅ Obrigatório |
| Regras de negócio | ✅ Obrigatório |
| Segurança | ✅ Obrigatório |
| Governança | ✅ Obrigatório |
| Estratégia de versionamento | ✅ Obrigatório |
| ADRs (Architecture Decision Records) | ✅ Obrigatório |

## 9. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft | Leivis Melo |
