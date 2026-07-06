# NIFS-700-12: Verification

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-700-12                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o Nurse-PaLM verifica a validade epistêmica de suas inferências antes de publicá-las.

## 2. Verification Layers (V1-V4)

| Level | Name | Check | Pass Criteria |
|-------|------|-------|---------------|
| V1 | Ontology | Conceito existe no grafo? | Node exists, code valid |
| V2 | Code validity | Código canônico válido? | Matches ni_ref registry |
| V3 | ISO composition | Focus + action alinhados? | ISO 18104 compliant |
| V4 | Scope | Dentro do escopo NIS? | In ni_scope.definitions |

## 3. Verification Pipeline

```
Reasoning Output (hypothesis + intervention)
    ↓
V1: Ontology check — node exists in ni_graph.nodes?
    → FAIL: reject, log to ni_epist.verification_log
    → PASS: continue
    ↓
V2: Code validity — entity_code matches canonical registry?
    → FAIL: flag as invalid, suggest correction
    → PASS: continue
    ↓
V3: ISO composition — NANDA focus aligns with NIC action?
    → FAIL: flag composition mismatch
    → PASS: continue
    ↓
V4: Scope — within NIS clinical scope?
    → FAIL: reject as out-of-scope
    → PASS: publish recommendation
    ↓
Verification certificate attached to output
```

## 4. NKOS Reference

O CALENF-NKD já valida identificadores:
- `clinical-engine/examples/validate-identifiers.mjs` — valida entity_code vs datasets
- `scripts/apgar/validate_apgar.py` — validação APGAR
- `scripts/validate_phases_1_7.py` — validador de datasets NKOS

## 5. Verification Certificate

```json
{
  "verification_id": "uuid",
  "reasoning_session": "uuid",
  "v1_ontology": { "passed": true, "node": "NANDA_00047" },
  "v2_code_validity": { "passed": true, "canonical": "NANDA.00047" },
  "v3_iso_composition": { "passed": true, "focus": "skin_integrity" },
  "v4_scope": { "passed": true, "scope": "clinical_nursing" },
  "overall": "verified",
  "timestamp": "2026-07-05T16:00:00Z"
}
```

## 6. NIS Implementation

| Table | Role |
|-------|------|
| `ni_epist.verification_log` | Verification results |
| `ni_epist.epistemic_states` | Epistemic status of knowledge |

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-700-11 | Reflection (pre-verification) |
| NIFS-600-19 | Explainability (verification in trace) |
| NIFS-1100-03 | Knowledge Curation (governance) |
