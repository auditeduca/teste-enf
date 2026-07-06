# NIFS-400-10: Audit Fields

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-400-10                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir campos de auditoria obrigatórios em todas as tabelas do NIS para rastreabilidade clínica.

## 2. Mandatory Audit Fields

| Field | Type | Auto? | Description |
|-------|------|-------|-------------|
| `created_date` | TIMESTAMPTZ | Yes | Quando o registro foi criado |
| `updated_date` | TIMESTAMPTZ | Yes | Última atualização |
| `created_by` | VARCHAR(128) | No | Quem/qual agente criou |

## 3. Extended Audit (Clinical Tables)

Tabelas clínicas críticas incluem campos adicionais:

| Field | Type | Tables |
|-------|------|--------|
| `reviewed_by` | VARCHAR(128) | ni_knowledge.versions, ni_mining.graded_evidence |
| `approved_by` | VARCHAR(128) | ni_protocol.protocols, ni_rules.decision_rules |
| `published_at` | TIMESTAMPTZ | ni_content.items |
| `deprecated_at` | TIMESTAMPTZ | ni.terminology_versions |

## 4. Audit Log Table

`ni.audit_log` captura ações transacionais:

| Field | Description |
|-------|-------------|
| `action` | create, update, delete, calculate |
| `entity_type` | Tipo da entidade afetada |
| `entity_id` | ID do registro |
| `user_id` | Quem executou |
| `timestamp` | Quando |
| `details` | JSONB com mudanças |

## 5. Compliance

Auditoria atende requisitos:
- **COFEN**: Resolução 543/2017 (documentação de enfermagem)
- **LGPD**: Art. 37 (registro de operações de tratamento)
- **ANVISA**: RDC 67/2007 (rastreabilidade)

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-400-09 | Version Fields |
| NIFS-1000-01 | Security (audit trail) |
