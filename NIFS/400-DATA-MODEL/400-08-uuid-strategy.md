# NIFS-400-08: UUID Strategy

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-400-08                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a estratégia de geração e uso de UUIDs no NIS.

## 2. Strategy

| Aspect | Decision |
|--------|----------|
| UUID version | UUID v4 (random) for most entities |
| Code-based PK | VARCHAR codes for terminologies (nanda_code, nic_code, noc_code, cid_code) |
| Hybrid | UUID for transactional, VARCHAR for reference data |
| Generation | Database-side `gen_random_uuid()` (PostgreSQL pgcrypto) |

## 3. Why UUID v4

- **No coordination needed**: Multi-service generation without central authority
- **Merge-safe**: No ID conflicts when merging datasets
- **Security**: Non-sequential, non-guessable
- **Distributed**: Works with microservices and event sourcing

## 4. Exceptions (Code-based PK)

| Table | PK Type | Reason |
|-------|---------|--------|
| `ni.nanda_diagnoses` | `nanda_code VARCHAR(8)` | Standard code, human-readable |
| `ni.nic_interventions` | `nic_code VARCHAR(8)` | Standard code |
| `ni.noc_outcomes` | `noc_code VARCHAR(8)` | Standard code |
| `ni.cid_diagnoses` | `cid_code VARCHAR(16)` | Standard code |
| `ni.safety_goals` | `goal_number SMALLINT` | Fixed set (1-6) |
| `ni_graph.nodes` | `node_id VARCHAR(64)` | Semantic ID (NANDA:00047, CALC:BRADEN) |

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-400-04 | Columns |
| NIFS-400-05 | Data Types |
