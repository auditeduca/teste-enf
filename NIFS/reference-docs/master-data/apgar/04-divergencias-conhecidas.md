# APGAR — Divergências conhecidas

Gerado pelo validador piloto. Rodar:

```bash
python scripts/apgar/validate_apgar.py
```

---

## Críticas (bloqueiam 100%)

### 1. score_max = 30 (esperado 10)

| Onde | Valor atual | Esperado |
|------|-------------|----------|
| `calculator_definitions.json` → `CALC.TOOL.APGAR` | 30 | 10 |

**Causa:** placeholder genérico de fase geradora.  
**Agente:** `APGAR.scl.score_max`  
**Fonte:** Apgar 1953

---

### 2. Faixas de interpretação invertidas/erradas

| Faixa atual | Faixa correta |
|-------------|---------------|
| 0–9 baixo | 0–3 crítico |
| 10–19 moderado | 4–6 moderado |
| 20–30 alto | 7–10 normal |

**Agente:** `APGAR.scl.interpretation_bands`

---

### 3. UI com input_a / input_b

| Onde | Problema |
|------|----------|
| `field_configurations.json` → `FIELD.TOOL.APGAR.STANDARD` | Campos genéricos |

**Esperado:** appearance, pulse, grimace, activity, respiration (0–2 cada).

**Agente:** `APGAR.scl.components`

---

### 4. i18n.pt-BR.name null

| Onde | Esperado |
|------|----------|
| `master_code_sequence_proposal.json` → APGAR_SCL_001 | "Escore de Apgar" |

---

## Avisos (não bloqueiam piloto imediato)

| Issue | Detalhe |
|-------|---------|
| NANDA no catálogo | `NANDA.00198` vs grafo `NANDA.00162` |
| Evidência | `citation` null — pending_official_source |
| Grafo | edges status `draft`, grade MODERATE |

---

## O que já está correto

- UUID e URL canônica
- Motor `clinical-engine/apgar` (score 0–10)
- Grafo `apgar_edges.json` (FK resolve)
- Entity codes no master proposal

---

## Próximo passo

Corrigir M2 + M3 → re-rodar validador → 0 errors → aprovar doc 14.
