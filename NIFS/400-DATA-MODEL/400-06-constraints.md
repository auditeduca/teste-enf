# NIFS-400-06: Constraints

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-400-06                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir as restrições de integridade do banco NIS.

## 2. Constraint Types

| Type | Implementation | Example |
|------|---------------|---------|
| **PRIMARY KEY** | UUID, per table | `nanda_code VARCHAR(8) PK` |
| **FOREIGN KEY** | Cross-table reference | `case_id UUID FK → ni.cases(case_id)` |
| **UNIQUE** | Prevent duplicates | `nanda_code UNIQUE` |
| **CHECK** | Value constraints | `probability CHECK (probability >= 0 AND probability <= 1)` |
| **NOT NULL** | Required fields | `nanda_code NOT NULL` |
| **ENUM** | Controlled vocabularies | `status VARCHAR(16) CHECK (status IN ('draft','review','validated','published','deprecated'))` |

## 3. Key Constraints (v5.0)

- **~250 FK constraints** across 166 tables
- **Probability fields**: CHECK (0 ≤ value ≤ 1)
- **Score fields**: CHECK (min ≤ value ≤ max per interpretation_bands)
- **Status fields**: CHECK against enum values
- **Temporal**: CHECK (started_at ≤ ended_at) where applicable

## 4. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-400-03 | Tables |
| NIFS-400-18 | Validation Rules |
