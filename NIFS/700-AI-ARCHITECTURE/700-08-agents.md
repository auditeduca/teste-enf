# NIFS-700-08: Agents

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-700-08                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a arquitetura de agentes clínicos do Nurse-PaLM — cada agente é especialista em um domínio.

## 2. Agent Architecture

```
Clinical Context
    ↓
Agent Router (selects agent by domain)
    ↓
Specialist Agent
    ├── Assessment Agent (observation → findings)
    ├── NANDA Agent (findings → diagnoses)
    ├── NIC Agent (diagnoses → interventions)
    ├── NOC Agent (interventions → outcomes)
    ├── Evidence Agent (claims → graded evidence)
    ├── Safety Agent (interventions → safety checks)
    ├── Pharm Agent (medications → interactions)
    └── Legislation Agent (actions → compliance)
    ↓
Agent Output (structured recommendation)
    ↓
Consensus Engine (reconcile multiple agents)
```

## 3. Agent Specification

| Agent | Domain | Input | Output | NKOS Reference |
|-------|--------|-------|--------|----------------|
| Assessment | Observações | Raw vitals, labs | Structured findings | `operations/assessment_results.json` |
| NANDA | Diagnóstico | Findings | Ranked diagnoses | `clinical/nursing_diagnoses.json` |
| NIC | Intervenção | Diagnoses | Recommended NICs | `clinical/nursing_interventions.json` |
| NOC | Outcomes | NIC + NANDA | Expected outcomes | `clinical/nursing_outcomes.json` |
| Evidence | Evidência | Claims | GRADE-graded evidence | `clinical/evidence.json` |
| Safety | Segurança | Interventions | Safety alerts | `clinical/safety_rules.json` |
| Pharm | Farmácia | Medications | Interactions, rights | `clinical/drug_interactions.json` |
| Legislation | Legal | Actions | Compliance check | `regulatory/br/legal_provisions.json` |

## 4. Agent Protocol

```json
{
  "agent_type": "NANDA",
  "input": {
    "findings": [{"code": "BRADEN_12", "value": 12}],
    "context": {"population": "ICU", "age": 67}
  },
  "output": {
    "diagnoses": [
      {"code": "NANDA_00047", "probability": 0.91, "confidence": 0.85},
      {"code": "NANDA_00046", "probability": 0.18, "confidence": 0.62}
    ],
    "evidence": ["E1: GRADE A", "E2: GRADE B"],
    "trace": ["BRADEN → activates → 00047 (w=0.87)"]
  },
  "vote_weight": 0.35
}
```

## 5. NKOS Reference

O CALENF-NKD já tem agentes Python implementados:
- `scripts/apgar_agents/` — agentes APGAR com phases, prompts, validators
- `scripts/anvisa_open_data_agents/` — agentes ANVISA (discover, extract, validate)
- `scripts/ai_factory_agents/` — agentes AI factory (catalog, workflow_runner)

## 6. NIS Implementation

| Table | Role |
|-------|------|
| `ni_council.agent_votes` | Agent votes on hypotheses |
| `ni_council.arbitration_decisions` | Conflict resolution |
| `ni_reasoning.steps` | Agent execution log |
| `ni_ops.audit_logs` | Agent action audit |

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-700-09 | Multi-Agent Council (consensus) |
| NIFS-600-18 | Consensus Engine (cognitive layer) |
| NIFS-700-14 | Tool Calling (agent tools) |
