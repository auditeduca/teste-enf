# Identificadores NKOS — clinical-engine

Schema: **Master Data v2026.2.2** · [13-master-data-banco-oficial.md](../13-master-data-banco-oficial.md)

---

## 1. Padrão canônico

| Tipo | Formato | Exemplo |
|------|---------|---------|
| Calculadora | `{CONCEITO}_{ARTEFATO}_{NNN}` | `DRIP_RATE_CAL_001` |
| NANDA | `NANDA_{NNNNN}` | `NANDA_00046` |
| NIC | `NIC_{NNNN}` | `NIC_2500` |
| Aresta | `(from, relation_type, to)` | sem entidade `REL_*` |

**Dataset JSON clínico** usa ponto: `NANDA.00046` → normalizar para underscore na API.

---

## 2. Mapeamento engine ↔ datasets

| entity_code (motor) | diagnosis_code (JSON) | Label em `nursing_diagnoses.json` |
|---------------------|----------------------|-----------------------------------|
| `NANDA_00046` | `NANDA.00046` | Impaired gas exchange |
| `NANDA_00031` | `NANDA.00031` | Excessive fluid volume |
| `NANDA_00033` | `NANDA.00033` | (padrão demo — validar label) |

| entity_code | intervention_code | Label |
|-------------|-------------------|-------|
| `NIC_2500` | `NIC.2500` | Fluid management |
| `NIC_2510` | `NIC.2510` | Vital signs monitoring |
| `NIC_2550` | `NIC.2550` | (infusão — ver dataset) |

**Calculadora:** `DRIP_RATE_CAL_001` — presente em `master_code_sequence_proposal.json`.

---

## 3. Aliases legados (migração)

Documentados em `clinical-engine/identifiers/legacyAliasMap.js`:

```
n1 → NANDA_00046
n2 → NANDA_00031
i3 → NIC_2550
CAL-001 → DRIP_RATE_CAL_001
```

**Regra:** código novo deve usar apenas `entity_code`. Aliases existem para testes de regressão da conversa V3–V7.

---

## 4. Arestas demo (edge layer)

Exemplo em `edgeRelations.js`:

| from | relation_type | to |
|------|---------------|-----|
| `DRIP_RATE_CAL_001` | `supports_diagnosis` | `NANDA_00046` |
| `DRIP_RATE_CAL_001` | `triggers` | `NANDA_00031` |
| `NANDA_00031` | `treated_by` | `NIC_2500` |

Status: **draft** — incluir na proposta Master Data após revisão clínica (`PENDING_REVIEW`).

---

## 5. Validação automática

```bash
cd clinical-engine && npm run test:ids
```

Verifica presença de cada `entity_code` em:

- `datasets/clinical/nursing_diagnoses.json`
- `datasets/clinical/nursing_interventions.json`
- `datasets/metadata/master_code_sequence_proposal.json`

---

## 6. Semântica clínica (aviso)

Os CPTs do motor V8 são **demonstração educacional**. A correspondência numérica NANDA (ex.: 00027 textbook “débito cardíaco”) **não** coincide 1:1 com labels NKOS atuais. Para produção:

1. Definir tabela `engine_concept → entity_code` aprovada por enfermeiro especialista.
2. Publicar apenas entidades com `evidence_grade: A` no Master Data.
3. Registrar divergência em `docs/14-master-data-sequencia-revisao.md`.
