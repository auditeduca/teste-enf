# APGAR — Módulos e campos

Matriz **módulo × field_id** — cada campo tem documentação em `field_documentation.json`.

---

## M1 — Identidade

| field_id | Campo | Esperado | completion |
|----------|-------|----------|------------|
| `APGAR.identity.concept_code` | concept_code | APGAR | 100% |
| `APGAR.identity.legacy_uuid` | uuid | 008c226d-… | 90% |
| `APGAR.identity.canonical_url` | canonical_url | calculadoras…/apgar/ | 100% |

---

## M2 — Instrumento clínico (SCL)

| field_id | Campo | Esperado | completion |
|----------|-------|----------|------------|
| `APGAR.scl.score_max` | score_max | **10** | 0% |
| `APGAR.scl.components` | 5 componentes | A-P-G-A-R | 0% |
| `APGAR.scl.interpretation_bands` | faixas | 0-3 / 4-6 / 7-10 | 0% |
| `APGAR.scl.timing_minutes` | timing | [1, 5] | 20% |

**Datasets:** `calculator_definitions.json#CALC.TOOL.APGAR`

---

## M3 — UI

| field_id | Esperado | completion |
|----------|----------|------------|
| `APGAR.scl.components` | radio_grid 5 componentes | 0% |

**Datasets:** `field_configurations.json#FIELD.TOOL.APGAR.STANDARD`

---

## M5 — Grafo

| field_id | Destino |
|----------|---------|
| `APGAR.graph.edges` | apgar_edges.json |
| `APGAR.graph.primary_nanda` | NANDA_00162 |

---

## Agent roles

| Role | Função |
|------|--------|
| search | Valor oficial + dataset atual |
| generate | Proposta corrigida |
| review | Aprovação clínica |
| validate | Checks determinísticos |
