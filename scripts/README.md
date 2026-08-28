# Scripts ativos

Scripts mantidos para operação contínua do repositório.

| Script | Uso |
|--------|-----|
| `build_apgar_cko.py` | Gera `apgar-edges.json` e dados CKO a partir de `NIFS/reference-datasets/` |
| `sync_cko_apgar_v3.py` | Sincroniza `CKO-APGAR-001.json` (v3) → `apgar-cko.json` (UI) |
| `sync_brand_assets.py` | Logos e favicons em `NIFS/DELIVERY/images/` |
| `package_apgar_zip.py` | ZIP portável em `artifacts/apgar-export` (não versionado) |
| `publish_delivery.py` | Publicação do site estático |
| `env_paths.py` | Caminhos de ambiente |
| `ready.sh` | Verificações de prontidão |
| `calculator_agents/` | Agentes LLM para geração de páginas (offline) |

Scripts de migração one-shot estão em `_archive/scripts-iteracao-apgar/`.
