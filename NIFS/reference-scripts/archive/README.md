# Arquivo morto — scripts geradores one-shot

Scripts de **bootstrap NKOS fases 1–12** usados para gerar a base inicial. **Não fazem parte do CI** (`scripts/run_ci.py`).

## CI ativo (manter na raiz de `scripts/`)

- `generate_website_pt.py` — build do site
- `validate_phases_1_7.py`, `validate_phases_8_12.py`
- `audit_website_pt.py`, `run_ci.py`
- `generate_phase7_complete.py` — único regen do layer Content (`contents.json`)

## Geradores arquivados (`generators/`)

Movidos por serem idempotentes one-shot já executados (ver `datasets/metadata/generation_manifest.json`):

- `generate_phase1_complete.py`, `generate_phase1_finish.py`
- `generate_phase2_scaffold.py` (superseded por `generate_phase2_complete.py`)
- `generate_phase2_complete.py`
- `generate_phase3_complete.py`, `generate_phase4_complete.py`
- `generate_phase5_complete.py`, `generate_phase5_education_complete.py`
- `generate_phase6_complete.py`
- `generate_phases_234_finish.py`
- `generate_phases_8_12.py`
- `integrate_nkos_v44.py`
- `enrich_database_fill_nulls.py`
- `update_home_page_database.py`, `update_institutional_pages_database.py`

## Scripts de manutenção ativos (não arquivar)

- `migrate_community_tool_links.py` — FKs fórum (100) + carreira (10)
- `generate_phase7_complete.py --skip-translations` — regen Content sem 160k traduções
- `build_hub_templates.py` — consolida hub JSON
- `hub_config_lib.py` — loader unificado
- `audit_ecosystem_coverage.py` — auditoria hub vs datasets

## Uso

Para regerar Content após alterar fontes clínicas/educação:

```bash
python scripts/generate_phase7_complete.py
python scripts/generate_website_pt.py --pt-only --no-zip
```
