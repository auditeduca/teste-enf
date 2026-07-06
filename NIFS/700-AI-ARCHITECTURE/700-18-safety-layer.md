# NIFS-700-18: Safety Layer

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-700-18                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a camada de segurança que protege o Nurse-PaLM de emitir recomendações clinicamente perigosas.

## 2. Safety Architecture

```
Reasoning Output (recommendation)
    ↓
Safety Layer (pre-publication gate)
    ├── Contraindication Check
    ├── Allergy Check
    ├── Drug Interaction Check
    ├── High-Alert Medication Check
    ├── Dosage Range Check
    ├── Population Safety Check
    └── IPSG Compliance Check
    ↓
ALL PASS → Publish recommendation
ANY FAIL → Block + Alert + Log
    ↓
If blocked → Human review required
```

## 3. Safety Rules

### 3.1 Medication Safety
```
Rule: high_alert_medication → require_dual_check
Source: clinical/medication_rights.json (9 Rights)
Source: clinical/drug_references.json (high_alert flag)
```

### 3.2 Allergy Check
```
Rule: patient_allergy ∩ medication_class → BLOCK
Source: patient_context_schema.json (allergies field)
```

### 3.3 Drug Interaction
```
Rule: drug_A + drug_B → interaction_severity
Source: clinical/drug_interactions.json
Action: severity=major → BLOCK, severity=moderate → WARN
```

### 3.4 IPSG Compliance
```
Rule: intervention must map to WHO IPSG goals
Source: clinical/patient_safety_goals.json
IPSG 1-6: Identify patients, safe surgery, hand hygiene, etc.
```

## 4. Safety Agent

O Safety Agent (NIFS-700-08) tem **veto power** — pode bloquear qualquer recomendação independentemente do consenso dos outros agentes.

```
Consensus: NANDA 00047 → NIC 3540 (P=0.74, consensus=agreed)
Safety Agent: CHECK
  - Contraindications? → none found ✓
  - Allergies? → patient has latex allergy, NIC 3540 involves dressing → WARN
  - IPSG? → goal 4 (safe surgery) N/A, goal 6 (fall risk) → assess
  - Result: APPROVED WITH WARNINGS
```

## 5. NKOS Reference

- `clinical/safety_rules.json` — regras de segurança
- `clinical/medication_rights.json` — 9 Rights com verification_checklist
- `clinical/patient_safety_goals.json` — WHO IPSG goals
- `clinical/drug_interactions.json` — interações medicamentosas
- `operations/dual_check_sessions.json` — sessões de dupla checagem

## 6. NIS Implementation

| Table | Role |
|-------|------|
| `ni_safety.safety_rules` | Rule definitions |
| `ni_safety.safety_alerts` | Generated alerts |
| `ni_safety.safety_events` | Logged safety events |
| `ni_ops.dual_check_sessions` | Dual verification records |

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-700-08 | Agents (Safety Agent) |
| NIFS-700-10 | Consensus (Safety veto) |
| NIFS-700-19 | Hallucination Prevention |
| NIFS-100-06 | Clinical Safety (foundation) |
| NIFS-1000-01 | Security Overview |
