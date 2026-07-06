# NIFS-400-05: Data Types

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-400-05                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Padronizar os tipos de dados usados no NIS.

## 2. Type Catalog

| Type | Use | Example |
|------|-----|---------|
| UUID | Primary/foreign keys | `patient_id UUID PK` |
| VARCHAR(n) | Codes, labels | `nanda_code VARCHAR(8)` |
| TEXT | Descriptions, narratives | `definition TEXT` |
| JSONB | Flexible payloads | `input_data JSONB` |
| NUMERIC | Scores, probabilities | `probability NUMERIC` |
| NUMERIC(p,s) | Precise values | `score_value NUMERIC(10,4)` |
| SMALLINT | Ordinal, enum-like | `step_order SMALLINT` |
| INTEGER | Counts | `evidence_count INTEGER` |
| BOOLEAN | Flags | `is_active BOOLEAN` |
| TIMESTAMPTZ | Timestamps | `created_date TIMESTAMPTZ` |
| DATE | Dates only | `published_at DATE` |
| CHAR(1) | Single-char codes | `grade_level CHAR(1)` |
| TEXT[] | Arrays of strings | `defining_characteristics TEXT[]` |

## 3. Type Conventions

- **UUID** for all primary keys (see NIFS-400-08)
- **VARCHAR** for codes with known max length
- **TEXT** for free-form descriptions
- **JSONB** for flexible/payload data (enables indexing)
- **NUMERIC** for all clinical values (never FLOAT — precision matters)
- **TIMESTAMPTZ** for all timestamps (never TIMESTAMP without TZ)

## 4. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-400-04 | Columns |
| NIFS-400-14 | Enumerations |
