# NIFS-500-01: Node Types

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-500-01                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir todos os tipos de nós do grafo de conhecimento clínico do NIS. Cada nó representa um conceito clínico que existe no universo modelado.

## 2. Design Principle

> "O conhecimento clínico é fundamentalmente relacional. Tabelas são uma projeção do grafo, não o contrário."

Os nós do grafo são a **representação canônica** do conhecimento. As tabelas PostgreSQL são uma projeção operacional.

## 3. Node Type Catalog

### 3.1 Primary Node Types

| Node Type | Code Prefix | ID Format | Example |
|-----------|-------------|-----------|---------|
| NANDA Diagnosis | `NANDA:` | NANDA:00047 | Úlcera por Pressão |
| NIC Intervention | `NIC:` | NIC:3540 | Pressure Management |
| NOC Outcome | `NOC:` | NOC:1101 | Tissue Integrity |
| ISO Focus Term | `ISO_FOCUS:` | ISO_FOCUS:uuid | Integridade tissular |
| ISO Judgment Term | `ISO_JUDGE:` | ISO_JUDGE:uuid | Risco de comprometida |
| ISO Action Term | `ISO_ACTION:` | ISO_ACTION:uuid | Reduzir |
| Gordon Pattern | `GORDON:` | GORDON:4 | Atividade-Exercício |
| Calculator | `CALC:` | CALC:BRADEN | Braden Scale |
| CID Diagnosis | `CID:` | CID:I21.9 | Infarto Agudo do Miocárdio |
| Medication | `MED:` | MED:uuid | Noradrenalina |
| Safety Goal | `SAFETY:` | SAFETY:META_3 | Medication Safety |
| Protocol | `PROTOCOL:` | PROTOCOL:uuid | Sepse Protocol 2024 |
| Population | `POP:` | POP:ICU | UTI Adulto |
| MRT (Middle Range Theory) | `MRT:` | MRT:uuid | Teoria do Conforto |
| Metaparadigm | `META:` | META:person | Pessoa |

### 3.2 Cognitive Node Types (v5.0)

| Node Type | Code Prefix | ID Format | Purpose |
|-----------|-------------|-----------|---------|
| Hypothesis | `HYP:` | HYP:uuid | Hipótese diagnóstica em uma sessão |
| Plan Node | `PLAN:` | PLAN:uuid | Nó do grafo de planejamento |
| Episode | `EP:` | EP:uuid | Episódio de memória |
| Simulation | `SIM:` | SIM:uuid | Execução de simulação |
| Council Agent | `AGENT:` | AGENT:COUNCIL.NANDA.001 | Agente do conselho |

### 3.3 Context Node Types

| Node Type | Code Prefix | ID Format | Purpose |
|-----------|-------------|-----------|---------|
| Hospital | `HOSP:` | HOSP:uuid | Instituição |
| Ward | `WARD:` | WARD:uuid | Unidade/enfermaria |
| Resource | `RES:` | RES:uuid | Dispositivo/recurso |
| Staff Role | `STAFF:` | STAFF:uuid | Papel de equipe |

## 4. Node Properties

Todo nó possui propriedades obrigatórias e opcionais:

### 4.1 Mandatory Properties

| Property | Type | Description |
|----------|------|-------------|
| `node_id` | VARCHAR(64) | Identificador único (prefix:code) |
| `node_type` | VARCHAR(32) | Tipo do nó (ver catálogo acima) |
| `node_label` | VARCHAR(256) | Rótulo legível |
| `label_pt` | VARCHAR(256) | Rótulo em português |
| `label_en` | VARCHAR(256) | Rótulo em inglês |
| `description` | TEXT | Descrição completa |
| `status` | VARCHAR(16) | active, deprecated, draft |
| `version` | VARCHAR(16) | Versão semântica |

### 4.2 Optional Properties (by node type)

| Node Type | Extra Properties |
|-----------|-----------------|
| NANDA | domain, class, diagnosis_type, defining_characteristics[], risk_factors[] |
| NIC | domain, class, activities[] |
| NOC | domain, class, indicators[], scale_type |
| CALC | category, formula, score_ranges[], nnn_links[] |
| MED | principio_ativo, atc_code, rxnorm_code, anvisa_registration |
| PROTOCOL | category, version, steps[], triggers[] |
| POP | name, description, prior_modifiers{} |

## 5. Node Lifecycle

| State | Description | Transitions |
|-------|-------------|------------|
| `draft` | Criado, não revisado | → review |
| `review` | Em revisão clínica | → active / draft |
| `active` | Válido e em uso | → deprecated |
| `deprecated` | Substituído ou obsoleto | (terminal) |

## 6. Node Creation Rules

### 6.1 Who Creates Nodes

| Node Type | Created By | Approval Required |
|-----------|-----------|-------------------|
| NANDA/NIC/NOC | Knowledge import (terminology version) | Clinical board |
| ISO terms | Ontologist | Clinical board |
| Calculator mappings | Clinical analyst | Clinical review |
| Protocols | Clinical specialist | Clinical governance |
| Medications | ANVISA import | Automated (with review) |
| Population priors | System (empirical) | Human validation |

### 6.2 ID Generation

```
NANDA: code from NANDA-I (e.g., 00047)
NIC:   code from NIC (e.g., 3540)
NOC:   code from NOC (e.g., 1101)
CALC:  calc_id (e.g., BRADEN, GLASGOW)
UUID:  gen_random_uuid() for all others
```

## 7. Node Statistics (Current v4.2)

| Node Type | Count | Source |
|-----------|-------|--------|
| NANDA diagnoses | ~267 | NANDA-I 2024-2026 |
| NIC interventions | ~565 | NIC 7th Edition |
| NOC outcomes | ~540 | NOC 6th Edition |
| ISO focus terms | ~300 | ISO 18104 |
| ISO judgment terms | ~80 | ISO 18104 |
| Gordon patterns | 11 | Gordon's framework |
| Calculators | ~40 | Site calculadorasdeenfermagem.com.br |
| CID diagnoses | ~12,000 | CID-10 + CID-11 |
| Medications | ~5,000 | ANVISA |
| Safety goals | 6 | ANS/Metas de Segurança |
| Protocols | ~20 | Clinical protocols |
| Populations | ~9 | Defined in spec |

**Total: ~19,000 nodes**

## 8. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-500-02 | Edge Types (how nodes connect) |
| NIFS-500-03 | Properties (detail) |
| NIFS-300-02 | Entity Catalog (conceptual) |
| NIFS-400-03 | Tables (SQL projection) |
| NIFS-500-08 | Ontology Mapping (cross-ontology) |

## 9. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — complete node type catalog | Leivis Melo |
