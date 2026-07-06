# NIFS-400-02: Data Dictionary

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-400-02                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o dicionário de dados canônico do NIS. O Excel v4.2 era o dicionário de dados; no NIFS, este documento referencia o canonical registry do NKOS.

## 2. Structure

Cada entrada do dicionário segue o formato:

| Field | Description |
|-------|-------------|
| Schema | PostgreSQL schema (ni, ni_cog, ni_graph, ...) |
| Table | Table name |
| Column | Column name |
| Type | PostgreSQL data type |
| Key | PK, FK, or null |
| FK Reference | target_table(target_column) |
| Description | PT-BR description |

## 3. Sources

| Source | Role | Records |
|--------|------|---------|
| Excel v4.2 (116 sheets) | Legacy data dictionary | 116 tables |
| NKOS `canonical_registry.json` | Canonical entity map | 50+ entities, ~45K records |
| NIFS DDL v5.0 | Cognitive layer DDL | 33 new tables |

## 4. Coverage

O dicionário cobre:
- **v4.2**: 116 tabelas, ~700 colunas, 152 FKs
- **v5.0 cognitivo**: 33 novas tabelas, ~280 colunas, ~80 FKs
- **v5.0 novos schemas**: ni_user (6), ni_legis (7), ni_pharm (3), ni_clinical (1) — ~17 tabelas

Total v5.0: ~166 tabelas, ~1000 colunas, ~250 FKs

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-400-01 | Naming Convention |
| NIFS-400-03 | Tables (physical) |
| NIFS-400-04 | Columns (field-level) |
