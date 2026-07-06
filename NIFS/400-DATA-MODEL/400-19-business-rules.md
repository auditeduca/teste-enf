# NIFS-400-19: Business Rules

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-400-19                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir regras de negócio clínico do NIS — lógica que governa o comportamento do sistema além da estrutura de dados.

## 2. Rule Categories

### 2.1 Clinical Decision Rules (`ni_rules.decision_rules`)
```
Rule: "Braden ≤ 12 → NANDA 00047 (High Risk)"
Conditions: braden_score ≤ 12 AND population = ICU
Actions: activate NANDA 00047, suggest NIC 3540, alert safety
Weight: 0.87 (strong, GRADE B)
```

### 2.2 Safety Rules
```
Rule: "High-alert medication → double check required"
Conditions: medication.high_alert = true
Actions: require second verifier, log to audit
```

### 2.3 Escalation Rules
```
Rule: "NOC not improving at 24h → escalate"
Conditions: outcome_type = unchanged AND time_elapsed ≥ 24h
Actions: suggest alternative NIC, notify senior nurse
```

### 2.4 Consent Rules
```
Rule: "Clinical data processing requires explicit consent"
Conditions: consent_type = clinical_data AND status ≠ granted
Actions: block data processing, request consent
```

### 2.5 Interoperability Rules
```
Rule: "FHIR message must validate before processing"
Conditions: profile.standard = FHIR
Actions: validate via ni_interop.message_validation, reject if invalid
```

## 3. Rule Architecture

| Component | Table | Role |
|-----------|-------|------|
| Rule definition | `ni_rules.decision_rules` | Name, description, scope |
| Conditions | `ni_rules.rule_conditions` | Ordered condition chain |
| Actions | `ni_rules.rule_actions` | Ordered action chain |
| Weights | `ni_rules.rule_weights` | Relationship weights |
| Versions | `ni_rules.rule_versions` | Versioned rule history |
| Execution log | `ni_ops.rule_execution_logs` | Runtime audit |

## 4. Rule Evaluation Flow

```
Event triggers (assessment result, observation, alert)
    ↓
Load applicable rules (by calc_id, nanda_code, population)
    ↓
Evaluate conditions in order (AND/OR logic)
    ↓
If all conditions met → execute actions
    ↓
Log execution to ni_ops.rule_execution_logs
    ↓
Feed results to reasoning engine
```

## 5. NKOS Rule Data

- `clinical_decision_trees.json`: 50 árvores de decisão com nodes, branches, linked_tools
- `ni_rules` schema: 6 tabelas para regras versionadas
- APGAR decision algorithm: 3 bands (0-3, 4-6, 7-10) com steps e escalation

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-400-18 | Validation Rules |
| NIFS-600-12 | Intervention Selection (rule-driven) |
| NIFS-600-11 | Goal Planning (escalation rules) |
