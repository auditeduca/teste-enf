# NIFS-300-20: Protocols

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-300-20                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir protocolos clínicos como sequências estruturadas de ações com regras e versões.

## 2. Protocol Structure

```
Protocol
├── protocol_name, category (sepse, queda, úlcera, dor, infecção)
├── source_guideline_code (WHO, MS-BR, institutional)
├── related_tool_codes[] (calculators linked)
├── Steps (ordered actions)
│   ├── step_order, action, condition
│   └── linked_nic_code
├── Rules (conditional logic)
│   ├── rule_name, condition, action
│   └── escalation_threshold
└── Versions (change history)
```

## 3. NIS Data (NKOS 2026)

| Data | Count | Source |
|------|-------|--------|
| Institutional protocols | 20 | `institutional_protocols.json` |
| Clinical guidelines | 200 | `clinical_guidelines.json` (WHO, MS-BR) |
| Decision trees | 50 | `clinical_decision_trees.json` |

## 4. Protocol in Reasoning

```
NANDA 00047 → Protocol: "Prevenção de Úlcera por Pressão"
    ↓
Step 1: Assess Braden q12h (TOOL.BRADEN)
Step 2: Position change q2h (NIC 3540)
Step 3: Skin inspection each shift (NIC 6540)
Rule: If Braden ≤ 12 → escalate to mattress + q1h repositioning
Rule: If skin breakdown → activate wound care protocol (NIC 2250)
```

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-11 | Goal Planning (protocol-driven plans) |
| NIFS-600-12 | Intervention Selection |
