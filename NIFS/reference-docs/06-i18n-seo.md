# 06 — i18n e SEO

## Locales do site

| Prefixo | Lang | Dir |
|---------|------|-----|
| (raiz `pt/`) | pt-BR | ltr |
| `en/` | en | ltr |
| `es/` | es | ltr |
| `fr/` | fr | ltr |
| `de/` | de | ltr |
| `it/` | it | ltr |
| `ja/` | ja | ltr |

Definição central: `seo_lib.LOCALES`.

Variantes são geradas em duas camadas:

1. **Conteúdo traduzido** — quando `datasets/by-locale/{locale}/home_page.json` tem `i18n_status: "translated"` (ou hero diferente do pt-BR), a home é **re-renderizada** com `locale_content_lib` + `render_locale_ctx`.
2. **Shell i18n** — demais páginas passam por `localize_html()` (ajusta `lang`, `dir`, canonical, `og:url`, `og:locale` e prefixo de assets).

Loader: `scripts/locale_content_lib.py` · build: `generate_website_pt.py` (secção i18n).

## HEAD por página

Cada página inclui (via `seo_lib.render_document`):

- `<link rel="canonical">` absoluto
- `<link rel="alternate" hreflang="…">` — 7 locales + `x-default`
- Open Graph (`og:url`, `og:site_name`, …)
- JSON-LD `@graph`: Organization, WebSite (+ SearchAction), WebPage, BreadcrumbList
- Páginas Drug: tipo `Drug` adicional

## Artefatos SEO (pós-build)

Gerados por `post_build_seo.py` a partir do HTML escaneado:

| Artefuto | Descrição |
|----------|-----------|
| `sitemap.xml` | URLs do locale com blocos `xhtml:link` hreflang |
| `sitemap-index.xml` | Índice dos 7 sitemaps |
| `robots.txt` | Allow `/`; Disallow `/assets/data/` |
| `feed.xml` | RSS das páginas principais |
| `assets/data/search-index.json` | Índice para busca no header |

## Busca client-side

`site.js` carrega `search-index.json` sob demanda e filtra título/descrição/tipo (top 8 resultados). Entradas vêm do scan pós-build, não de montagem manual no gerador.

## hreflang e canonical

- **pt-BR** canonical na raiz: `https://…/pt/ferramentas/glasgow/`
- **en** canonical: `https://…/pt/en/ferramentas/glasgow/`
- Reciprocidade entre todos os pares + `x-default` apontando para pt-BR

## Pendência P1

Infraestrutura i18n (**R13**) concluída. Falta substituir corpo HTML por traduções do dataset `content/translations.json` (160 776 registros, 29 locales no dataset; 7 no site).

## Voltar ao índice

→ [README.md](../README.md)
