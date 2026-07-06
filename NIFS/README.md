# NIFS — Nursing Intelligence Foundation Specification

**Version:** 1.0.0-draft
**Status:** Draft
**Date:** 2026-07-05
**Author:** Leivis Melo
**Site:** [calculadorasdeenfermagem.com.br](https://calculadorasdeenfermagem.com.br)

---

## O que é o NIFS?

O **Nursing Intelligence Foundation Specification (NIFS)** é a especificação de engenharia que define toda a arquitetura do Nursing Intelligence System (NIS) — uma plataforma de inteligência clínica para enfermagem que evolui para uma arquitetura tipo **Nurse-PaLM**.

O NIFS não é uma aplicação. É a **fonte oficial da verdade** da qual banco de dados, APIs, motores de IA e interfaces são derivados como artefatos gerados.

## Princípio Fundamental

```
NIFS (Specification)
        │
        ▼
Knowledge Model (Excel canônico)
        │
        ▼
Generated Artifacts (SQL, OpenAPI, GraphQL, FHIR, Neo4j, TypeScript, Python)
        │
        ▼
Runtime Platform (PostgreSQL, API Server, AI Engine, Frontend)
```

O Excel nunca é consumido diretamente pela aplicação. Ele é a especificação que alimenta geradores automáticos.

## Estrutura

| Seção | Domínio | Documentos |
|-------|---------|-----------|
| [000](000-INTRODUCTION/) | Introduction | 15 |
| [100](100-FOUNDATION/) | Foundation | 17 |
| [200](200-CLINICAL-SCIENCE/) | Clinical Science | 24 |
| [300](300-KNOWLEDGE-MODEL/) | Knowledge Model | 23 |
| [400](400-DATA-MODEL/) | Data Model | 19 |
| [500](500-KNOWLEDGE-GRAPH/) | Knowledge Graph | 12 |
| [600](600-CLINICAL-REASONING/) | Clinical Reasoning | 20 |
| [700](700-AI-ARCHITECTURE/) | AI Architecture | 19 |
| [800](800-INTEROPERABILITY/) | Interoperability | 14 |
| [900](900-PLATFORM/) | Platform | 16 |
| [1000](1000-SECURITY/) | Security | 15 |
| [1100](1100-GOVERNANCE/) | Governance | 10 |
| [1200](1200-QUALITY/) | Quality | 10 |
| [1300](1300-DEVELOPER-GUIDE/) | Developer Guide | 11 |
| [1400](1400-DEPLOYMENT/) | Deployment | 10 |
| [1500](1500-ROADMAP/) | Roadmap | 7 |
| [APPENDIX](APPENDIX/) | Appendix | 19 |
| **Total** | | **261** |

## Documentos Pré-Desenvolvimento (Obrigatórios)

Antes de escrever uma única tabela SQL, estes documentos devem existir:

| # | Documento | Seção NIFS |
|---|-----------|------------|
| 1 | Visão do produto | NIFS-000-01 |
| 2 | Modelo conceitual | NIFS-300 |
| 3 | Ontologia | NIFS-300-05 |
| 4 | Dicionário de dados | NIFS-400-02 |
| 5 | Grafo de conhecimento | NIFS-500 |
| 6 | Arquitetura da IA | NIFS-700 |
| 7 | Motor de raciocínio clínico | NIFS-600 |
| 8 | APIs | NIFS-800 |
| 9 | Regras de negócio | NIFS-400-19 |
| 10 | Segurança | NIFS-1000 |
| 11 | Governança | NIFS-1100 |
| 12 | Estratégia de versionamento | NIFS-000-14 |
| 13 | ADRs | NIFS-APP-S |

## Versionamento

O NIFS segue **Semantic Versioning 2.0.0**:

- **MAJOR** (v1.0.0 → v2.0.0): mudanças incompatíveis na arquitetura
- **MINOR** (v1.0.0 → v1.1.0): nova funcionalidade backward-compatible
- **PATCH** (v1.0.0 → v1.0.1): correções e esclarecimentos

Cada documento tem seu próprio versionamento dentro do NIFS global.

## Como Navegar

1. Comece pelo **[NIFS-000-01: Vision](000-INTRODUCTION/000-01-vision.md)**
2. Leia os **[princípios](100-FOUNDATION/)**
3. Explore o **[modelo de conhecimento](300-KNOWLEDGE-MODEL/)**
4. Entenda o **[motor de raciocínio](600-CLINICAL-REASONING/)**
5. Consulte o **[índice completo](INDEX.md)** para referência

## Estado Atual

- **Marco Zero:** Excel v4.2 (116 tabelas, 28 schemas, 152+ FKs) congelado como NIFS-400-02
- **Camadas cognitivas:** 10 novas camadas projetadas (47 novas tabelas) — ver `NIS_Cognitive_Layers_v5.0_DDL.sql`
- **Próximo:** Preencher documentos prioritários antes de implementação

## Licenciamento

A definir. Ver [NIFS-000 — Licensing] (a ser criado).
