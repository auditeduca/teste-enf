# NIFS-400-01: Naming Convention

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-400-01                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir as regras de nomenclatura que governam todos os artefatos do NIS — schemas, tabelas, colunas, APIs, arquivos e código.

## 2. Database Naming

### 2.1 Schemas

```
Prefix: ni_
Pattern: ni_{domain}
Style: snake_case, lowercase

Examples:
  ni           — core clinical (legacy, kept for compatibility)
  ni_cog       — cognitive/knowledge
  ni_reasoning — reasoning engine
  ni_memory    — episodic memory
  ni_prob      — probabilistic engine
  ni_attention — clinical attention
  ni_planner   — planning engine
  ni_world     — world model
  ni_twin      — digital twin
  ni_council   — multi-agent council
  ni_learning  — learning loop
  ni_graph     — knowledge graph
  ni_temporal  — temporal events
  ni_mining    — evidence mining
  ni_explain   — explainability
  ni_rules     — decision rules
  ni_protocol  — clinical protocols
  ni_interop   — interoperability
  ni_content   — content management
  ni_i18n      — internationalization
  ni_design    — design system
  ni_ai        — AI readiness
  ni_obs       — observability
  ni_api       — API layer
  ni_qg        — quality gates
  ni_platform  — platform/plugins
  ni_cache     — caching
  ni_ops       — operations
  ni_test      — testing
  ni_iso       — ISO 18104
  ni_epist     — epistemology
  ni_onto      — ontology mapping
  ni_knowledge — knowledge versioning
```

### 2.2 Tables

```
Pattern: {schema}.{entity_name}
Style: snake_case, plural for collections, singular for singletons

Examples:
  ni.nanda_diagnoses        (collection)
  ni.care_plans             (collection)
  ni.safety_goals           (collection)
  ni_reasoning.sessions     (collection)
  ni_reasoning.hypotheses   (collection)
  ni_memory.episodes        (collection)
```

### 2.3 Columns

```
Style: snake_case, lowercase
Primary key: {entity}_id (e.g., case_id, session_id, episode_id)
Foreign key: {referenced_entity}_id (e.g., nanda_code, nic_code)
Timestamps: {event}_at (e.g., started_at, completed_at, captured_at)
Booleans: is_{adjective} or has_{noun} (e.g., is_active, has_evidence)
JSONB: {name}_data or {name}_payload (e.g., state_data, input_payload)
Arrays: {name}_ids or plural (e.g., evidence_refs, tags)
```

### 2.4 Reserved Column Names

Every table has:

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Surrogate key (if not natural PK) |
| `created_date` | TIMESTAMPTZ | Record creation |
| `updated_date` | TIMESTAMPTZ | Last update |
| `created_by` | VARCHAR(64) | Creator |

## 3. API Naming

### 3.1 URL Paths

```
Pattern: /api/v{version}/{resource}[/{id}[/{sub-resource}]]

Examples:
  /api/v1/nanda
  /api/v1/nanda/00047
  /api/v1/nanda/00047/interventions
  /api/v1/reasoning/sessions/{id}/trace
```

### 3.2 JSON Fields

```
Style: snake_case
Booleans: is_{x}, has_{x}
Timestamps: {event}_at
IDs: {entity}_id or {entity}_code
```

## 4. Graph Node IDs

```
Pattern: {TYPE}:{CODE}

Examples:
  NANDA:00047
  NIC:3540
  NOC:1101
  CALC:BRADEN
  GORDON:4
  CID:I21.9
  SAFETY:META_3
  PROTOCOL:uuid
  POP:ICU
```

## 5. Agent IDs

```
Pattern: COUNCIL.{TYPE}.{NUMBER}

Examples:
  COUNCIL.ASSESS.001
  COUNCIL.NANDA.001
  COUNCIL.SAFETY.001
  COUNCIL.CONS.001
```

## 6. File Naming (NIFS documents)

```
Pattern: {SECTION}-{NUMBER}-{name}.md

Examples:
  000-01-vision.md
  600-02-reasoning-pipeline.md
  700-09-multi-agent.md
```

## 7. Code Naming

| Language | Style | Example |
|----------|-------|---------|
| TypeScript | camelCase (vars), PascalCase (types) | `reasoningSession` |
| Python | snake_case | `reasoning_session` |
| SQL | snake_case | `reasoning_sessions` |
| JSON | snake_case | `"reasoning_session"` |

## 8. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — complete naming convention | Leivis Melo |
