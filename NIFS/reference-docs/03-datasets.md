# 03 — Datasets

## Organização de pastas

```
datasets/
├── clinical/       # Terminologias, ferramentas, fármacos, segurança
├── content/        # Artigos, traduções, hubs, bindings UI
├── education/      # Cursos, trilhas, quizzes, simulados
├── metadata/       # Registros canônicos, SEO, status, CI
└── …               # Outros domínios NKOS (community, runtime, etc.)
```

Cada arquivo JSON segue o envelope NKOS: `entity`, metadados e array de registros (ou mapa `tools`, conforme o tipo).

## Datasets críticos para o site

| Arquivo | Conteúdo |
|---------|----------|
| `clinical/calculator_definitions.json` | Definições de 100 ferramentas (parâmetros, faixas) |
| `content/tool_ui_bindings.json` | Template, campos UI, engine de cálculo |
| `content/calculator_scale_options.json` | Opções `radio_grid` e `safety_blocks` (GCS, Braden, Morse) |
| `clinical/drug_monographs.json` | Bulas curadas (noradrenalina, insulina, heparina) |
| `content/institutional_hubs.json` | Páginas institucionais curadas |
| `metadata/seo_metadata.json` | Títulos e descriptions por rota |
| `content/translations.json` | Manifesto + shards de tradução (29 locales) |

## Sharding

`translations.json` e outros volumes grandes usam **sharding** via `scripts/dataset_io.py` (máx. 20 000 registros por shard). Geradores e validadores leem o envelope de forma transparente.

## Geração de datasets

Scripts numerados por fase:

- `generate_phase1_complete.py` … `generate_phase7_complete.py`
- `generate_phases_8_12.py` — fases 8–12 em lote

Após alterar datasets, **sempre** rodar os validadores antes do build do site.

## Validação

| Script | Escopo |
|--------|--------|
| `validate_phases_1_7.py` | 247 checks — referências, PKs, relações |
| `validate_phases_8_12.py` | 138 checks — entidades phases 8–12 |

Ambos devem terminar com **0 erros**.

## Próximo documento

→ [04-geracao-site.md](04-geracao-site.md)
