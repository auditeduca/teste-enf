# NIFS-400-09: Version Fields

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-400-09                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o NIS rastreia versões de entidades de conhecimento clínico.

## 2. Versioning Layers

| Layer | Table | Scope |
|-------|-------|-------|
| Terminology editions | `ni.terminology_versions` | NANDA 2024-2026, NIC 7th, NOC 6th |
| Knowledge entities | `ni_knowledge.versions` + `change_sets` | Diagnósticos, protocolos, regras, relações |
| Protocols | `ni_protocol.protocol_versions` | Versões de protocolo institucional |
| Rules | `ni_rules.rule_versions` + `rule_history` | Versões de regras clínicas |
| DDL | Git tags + SemVer | NIFS v4.2 → v5.0 → v5.1 |

## 3. Convention

| Field | Type | Example |
|-------|------|---------|
| `version` | VARCHAR(16) | "1.0.0", "2.1.3" (SemVer) |
| `edition` | VARCHAR(32) | "2024-2026" (terminologias) |
| `status` | VARCHAR(16) | draft → review → active → superseded → deprecated |

## 4. Change Tracking

`ni_knowledge.change_sets` registra cada alteração individual:
- `change_type`: add, modify, deprecate, realign, merge, split
- `field_name`: qual campo mudou
- `old_value` / `new_value`: valores antes/depois
- `justification`: motivo clínico da mudança

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-400-10 | Audit Fields |
| NIFS-000-14 | Versioning (SemVer policy) |
