# 04 — Geração do site

Ver também: [09-paginas-site-traducao.md](09-paginas-site-traducao.md) — mapa de arquivos da home, institucionais, modulares, mega-menu e tradução.

## Comando principal

```bash
python scripts/generate_website_pt.py
```

Saída: `website/pt/` (e subpastas de locale `en/`, `es/`, …).

## Flags

| Flag | Efeito |
|------|--------|
| `--pt-only` | Gera só pt-BR; pula locales e zip (build ~3× mais rápido) |
| `--no-zip` | Não cria `website/nkos-site-build.zip` |

## Pipeline interno

1. **Carregar datasets** — ferramentas, protocolos, SEO, hubs, medicamentos, NNN.
2. **Emitir HTML pt-BR** — ~222 rotas (home, ferramentas, artigos, institucional, …).
3. **Locales (paralelo)** — `seo_lib.localize_html()` deriva 6 variantes do HTML pt-BR (lang, dir, canonical, paths de asset).
4. **SEO pós-build** (`post_build_seo.py`):
   - Varre HTML → `search-index.json`
   - `sitemap.xml` por locale com `xhtml:link` hreflang
   - `sitemap-index.xml`, `robots.txt`, `feed.xml`
5. **Relatório** (`build_lib.py`) — `build-report.txt/json`, amostra JSON-LD e a11y.
6. **Zip** — `nkos-site-build.zip` (build completo).
7. **Manifest** — `website/pt/generation_manifest.json`.

## Tipos de página

| Rota exemplo | Lib / mecanismo |
|--------------|-----------------|
| `/ferramentas/glasgow` | `tool_lib.render_tool_page` |
| `/medicamentos/noradrenalina` | `medication_lib` |
| `/nanda`, `/nic`, `/noc` | `templates_lib` (client-side) |
| `/protocolos/…` | `protocol_lib` |
| `/sobre`, `/blog`, … | `institutional_lib` / `hub_lib` |

## Ferramentas clínicas (UX)

Escalas principais (GCS, Braden, Morse) usam:

- **`radio_grid`** — opções descritivas em grade (HTML + CSS em `tools.css`)
- **`safety_blocks`** — alertas hard/soft avaliados em tempo real (`site.js`)

Configuração em `datasets/content/calculator_scale_options.json`; merge em `tool_lib._merge_scale_options()`.

## Artefatos gerados na raiz `website/`

```
website/
├── build-report.json
├── build-report.txt
├── nkos-site-build.zip      # omitido com --pt-only ou --no-zip
└── pt/
    ├── sitemap.xml
    ├── sitemap-index.xml
    ├── robots.txt
    ├── feed.xml
    ├── assets/data/search-index.json  # symlink lógico via path
    └── generation_manifest.json
```

## Próximo documento

→ [05-ci-validacao.md](05-ci-validacao.md)
