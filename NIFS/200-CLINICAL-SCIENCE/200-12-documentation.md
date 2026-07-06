# NIFS-200-12: Documentation

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-200-12                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir documentação clínica de enfermagem no NIS — como registros são estruturados, armazenados e exportados.

## 2. Documentation Principles

- **Estruturada**: dados em JSONB, não texto livre quando possível
- **Rastreável**: todo registro tem `created_by`, `created_date`
- **Versionada**: alterações preservam histórico
- **Interoperável**: exportável em FHIR
- **Auditável**: `ni.audit_log` registra toda operação

## 3. Documentation Types

| Type | NIS Table | FHIR Resource |
|------|-----------|--------------|
| Assessment | `ni_temporal.observations` | Observation |
| Diagnosis | `ni.care_plans` | Condition |
| Intervention | `ni_memory.actions` | Procedure |
| Outcome | `ni_memory.outcomes` | Observation |
| Reasoning | `ni_reasoning.trace` | ClinicalImpression |
| Explanation | `ni_explain.explanations` | DiagnosticReport |

## 4. Audit Trail

```
Every create/update/delete → ni.audit_log
  {log_id, action, entity_type, entity_id, user, timestamp, changes}
```

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-1000-06 | Audit (security) |
| NIFS-800-01 | FHIR (export format) |
| NIFS-600-20 | Reasoning Trace (documentation of reasoning) |
