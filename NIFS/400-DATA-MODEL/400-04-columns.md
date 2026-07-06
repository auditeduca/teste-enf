# NIFS-400-04: Columns

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-400-04                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir padrões de nomenclatura e estrutura de colunas no NIS.

## 2. Column Naming

| Pattern | Example | Rule |
|---------|---------|------|
| Primary key | `{entity}_id` | UUID, always PK |
| Foreign key | `{referenced_entity}_id` | Matches PK of referenced table |
| Code field | `{entity}_code` | VARCHAR, human-readable (e.g., nanda_code) |
| Label PT | `label_pt` | VARCHAR(256) |
| Label EN | `label_en` | VARCHAR(256) |
| Timestamp | `created_date`, `updated_date` | TIMESTAMPTZ, auto |
| Score/value | `score_value`, `weight` | NUMERIC |
| Probability | `probability`, `confidence` | NUMERIC(0,1) |
| JSONB payload | `input_data`, `output_data` | JSONB |
| Status | `status` | VARCHAR(16), enum |

## 3. System Columns (Auto)

Every table includes:

| Column | Type | Description |
|--------|------|-------------|
| `id` or `{entity}_id` | UUID | Primary key |
| `created_date` | TIMESTAMPTZ | Auto-set on insert |
| `updated_date` | TIMESTAMPTZ | Auto-set on update |
| `created_by` | VARCHAR(128) | User/agent who created |

## 4. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-400-03 | Tables |
| NIFS-400-05 | Data Types |
| NIFS-400-08 | UUID Strategy |
