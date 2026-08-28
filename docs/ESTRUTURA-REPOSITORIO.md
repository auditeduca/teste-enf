# Estrutura do repositório

Mapa operacional após reorganização (branch `cursor/repo-organize-plan-c848`). A especificação normativa continua em `NIFS/`.

## Princípio

| Onde editar | O que é |
|-------------|---------|
| `NIFS/DELIVERY/` | Site estático em produção (calculadoras, JS, partials, CSS) |
| `NIFS/reference-datasets/` | Dados globais canônicos (terminologia, ontologia, operações) |
| `scripts/` | Automação ativa (build CKO, sync, ZIP, publicação) |
| `i18n-pipeline/` | Tradução e injeção de idiomas no site |
| `NIFS/` (seções 000–1500) | Especificação NIFS — fonte da verdade arquitetural |
| `_archive/` | Snapshots, experimentos e scripts one-shot **não editar** |

**Não** criar duplicatas na raiz do repositório. Exportações portáveis vão para `artifacts/` (gitignored) via `scripts/package_apgar_zip.py`.

## Árvore resumida

```
/
├── docs/                          ← documentação operacional (este índice)
├── scripts/                       ← scripts ativos
│   └── calculator_agents/         ← geração offline de páginas (LLM)
├── i18n-pipeline/                 ← scanner, corpus, tradução, injetor
├── NIFS/
│   ├── 000-INTRODUCTION … 1500-ROADMAP/   ← spec NIFS (261 docs)
│   ├── DELIVERY/                  ← **runtime web atual**
│   │   ├── preview_apgar.html     ← dev Apgar
│   │   ├── apgar.html             ← produção Apgar
│   │   ├── js/                    ← motores (calc, CKO, Nurse-PaLM, i18n)
│   │   ├── partials/              ← header, footer, relatório PDF
│   │   ├── css/
│   │   ├── api/                   ← FastAPI relatório (opcional)
│   │   └── i18n/                  ← dicionários JSON por idioma (DELIVERY)
│   ├── reference-datasets/        ← **dados globais** (JSON por domínio)
│   ├── reference-clinical-engine/
│   ├── reference-docs/
│   └── reference-scripts/
├── reference-website/             ← espelho legado do site (205 páginas × idiomas)
└── _archive/                      ← backup (não canônico)
    ├── exports/apgar-completo/    ← pacote Apgar versionado (histórico)
    ├── root-snapshots/            ← HTML/DDL que estavam na raiz
    ├── delivery-experiments/      ← protótipos descartados
    └── scripts-iteracao-apgar/    ← migrações já aplicadas
```

## Caminhos canônicos (Apgar piloto)

| Artefato | Caminho |
|----------|---------|
| Página dev | `NIFS/DELIVERY/preview_apgar.html` |
| Página produção | `NIFS/DELIVERY/apgar.html` |
| CKO v3 (fonte) | `NIFS/DELIVERY/js/modules/data/cko/CKO-APGAR-001.json` |
| CKO UI (runtime) | `NIFS/DELIVERY/js/modules/data/apgar-cko.json` |
| Arestas ontologia | `NIFS/reference-datasets/ontology/apgar_edges.json` |
| Template PDF | `NIFS/DELIVERY/partials/relatorio-fiel.html` |
| Sync CKO → UI | `python3 scripts/sync_cko_apgar_v3.py` |

## Servidor local

```bash
cd NIFS/DELIVERY && python3 -m http.server 8765
# http://localhost:8765/preview_apgar.html
```

## Scripts ativos (`scripts/`)

| Script | Função |
|--------|--------|
| `build_apgar_cko.py` | Gera edges e dados CKO a partir de `reference-datasets/` |
| `sync_cko_apgar_v3.py` | CKO-APGAR-001.json → apgar-cko.json |
| `sync_brand_assets.py` | Logos e favicons |
| `package_apgar_zip.py` | ZIP em `artifacts/apgar-export` |
| `publish_delivery.py` | Publicação estática |
| `env_paths.py` | Caminhos de ambiente |
| `ready.sh` | Checagens de prontidão |

Scripts de migração one-shot: `_archive/scripts-iteracao-apgar/`.

## Dados globais (`NIFS/reference-datasets/`)

Organização por domínio (não duplicar por calculadora):

| Pasta | Exemplos |
|-------|----------|
| `global/` | `languages.json`, `locales.json`, `countries.json` |
| `clinical/` | NANDA, NIC, NOC, medicamentos, escalas, protocolos |
| `ontology/` | Arestas e relações (ex.: `apgar_edges.json`) |
| `master/` | Entidades, taxonomia, sinônimos de busca |
| `regulatory/` | Legislação BR, ANVISA |
| `education/` | Trilhas, simulados, competências |
| `operations/` | Sessões, perfis de paciente, SBAR |
| `users/` | Personalização, consentimentos |
| `metadata/` | Registro canônico, templates de prompt |

## Internacionalização

| Camada | Local | Estado |
|--------|-------|--------|
| Site legado (29 idiomas × 205 páginas) | `reference-website/{lang}/` | Gerado pelo injetor |
| Pipeline | `i18n-pipeline/` | Scanner, corpus, `translate_clinical.py` |
| Runtime DELIVERY | `NIFS/DELIVERY/i18n/*.json` + `js/i18n-loader.js` | Piloto (pt/en/es) |
| Locales canônicos | `reference-datasets/global/languages.json` | Registro de idiomas ativos |

Detalhes: [PLANO-FASEADO.md](./PLANO-FASEADO.md) (fases de i18n) e `i18n-pipeline/PENDENCIAS_I18N.md`.

## O que foi arquivado

Ver `_archive/README.md`. Em resumo: pacote `apgar-completo/`, previews na raiz, DDL na raiz, `preview_v2.html` experimental e 16 scripts de iteração Apgar.
