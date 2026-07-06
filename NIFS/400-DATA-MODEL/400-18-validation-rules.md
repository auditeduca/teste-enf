# NIFS-400-18: Validation Rules

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-400-18                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir regras de validação de dados clínicos no NIS — garantindo integridade além das constraints de banco.

## 2. Validation Layers

| Layer | Where | Examples |
|-------|-------|---------|
| **Database** | PostgreSQL CHECK constraints | probability 0-1, status enums |
| **Application** | Backend functions | NANDA code exists before care_plan insert |
| **Epistemic** | `ni_epist.epistemology_rules` | V1-V4 validation types |
| **Quality Gate** | `ni_qg` pipeline | Clinical validation stage |
| **Council** | Multi-agent validation | Safety Agent veto on unsafe recommendations |

## 3. Epistemic Validation Rules

| Rule Type | Check | Example |
|-----------|-------|---------|
| V1_ontology | Conceito existe na ontologia | NANDA 00047 must exist in nanda_diagnoses |
| V2_code_validity | Código é válido no sistema | NIC code must be 4-digit numeric |
| V3_iso_composition | Composição ISO é válida | Focus + Judgment required for diagnoses |
| V4_scope | Conceito está no escopo do NIS | Tool not in excluded_tools |

## 4. Clinical Validation Examples

| Rule | Validation |
|------|-----------|
| Braden score | 6 ≤ score ≤ 23 |
| Glasgow score | 3 ≤ score ≤ 15 |
| APGAR score | 0 ≤ score ≤ 10 |
| NANDA → NIC link | Must exist in NNN linkages with strength ≥ suggestive |
| Probability sum | All P(hypothesis) for a session should sum to ~1.0 |
| Care plan completeness | Must have ≥ 1 NANDA + ≥ 1 NIC + ≥ 1 NOC |
| Feedback loop | Every reinforcement signal must link to a verified outcome |

## 5. Validation Pipeline

```
Data Input
    ↓ Database CHECK (syntax)
    ↓ Application validation (semantics)
    ↓ Epistemic rules (V1-V4)
    ↓ Quality gate: Clinical_Validation stage
    ↓ Council Safety Agent (critical path)
    ↓ Validated ✅ or Rejected ❌
```

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-400-06 | Constraints (DB-level) |
| NIFS-400-19 | Business Rules |
| NIFS-1200-02 | Quality Validation |
