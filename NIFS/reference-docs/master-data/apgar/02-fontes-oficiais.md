# APGAR — Fontes oficiais

---

## APGAR_1953 (Grau A — primária)

| Atributo | Valor |
|----------|-------|
| DOI | [10.1213/00000539-195322000-00002](https://doi.org/10.1213/00000539-195322000-00002) |
| Campos | components, score_range (0–10), formula |

**Valores:** 5 sinais 0–2 · total 0–10 · minutos 1 e 5.

---

## ACOG / WHO

| Fonte | Campos |
|-------|--------|
| ACOG | interpretation_bands, conduta |
| WHO | timing_minutes, clinical_purpose |

---

## Mapeamento

| field_id | source_id |
|----------|-----------|
| APGAR.scl.score_max | APGAR_1953 |
| APGAR.scl.components | APGAR_1953 |
| APGAR.scl.interpretation_bands | ACOG_NEONATAL |
| APGAR.scl.timing_minutes | WHO_NEONATAL |

Prompt Search Agent: `scripts/apgar_agents/prompts/search.md`
