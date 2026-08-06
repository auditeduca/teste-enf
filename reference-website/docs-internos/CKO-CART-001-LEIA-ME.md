# CKO-CART-001 — LEIA-ME / Índice de arquivos

Recurso **Carrinho de Emergência Interativo** (biblioteca + artigo educativo + ferramenta de conferência).

## Páginas públicas

| Arquivo | Função |
|---------|--------|
| `biblioteca-carinho-de-emergencia.html` | Página principal: explorador, conferência, artigo embutido, dicas/erros, referências |
| `biblioteca/artigo-carrinho-de-emergencia-enfermagem.html` | Artigo educativo completo (mesmo conteúdo do manifesto, modo `article`) |

## Dados e schema

| Arquivo | Função |
|---------|--------|
| `data/cko-cart-001.manifest.json` | Manifesto único: zonas, regras, dicas/erros, artigo (`educationalArticle`), copyright, formulários, referências |
| `schemas/cko-cart.schema.json` | JSON Schema do manifesto CKO-CART |
| `data/institutions.homolog.internal.json` | Base interna de instituições homologadas (não expor notes no HTML) |

## Front-end

| Arquivo | Função |
|---------|--------|
| `js/cart-renderer.js` | Renderer do manifesto (explorador, conferência, export PDF/Excel/Word, artigo, dicas) |
| `js/cko-page-shell.js` | Shell modular: breadcrumb, nav, hero, aside (catálogo JSON) |
| `css/pages/cart-emergencia.css` | Estilos da página / artigo / tip cards / rodapé de copyright |
| `css/pages/cko-page-shell.css` | Estilos do breadcrumb/nav/aside padronizados |
| `data/cko-shell-pages.json` | Catálogo de chrome/hero das bibliotecas (editar aqui, não no HTML) |
| `docs-internos/CKO-PAGE-SHELL.md` | Como usar mounts `data-cko-page` / `data-cko-slot` |
| `img/carrinho-emergencia-interativo.webp` | Imagem principal do explorador |
| `img/carrinho-emergencia-interativo.png` | Fallback PNG |

## Docs internos e ferramentas

| Arquivo | Função |
|---------|--------|
| `docs-internos/CKO-CART-001-LEIA-ME.md` | Este índice |
| `docs-internos/PADRAO_PAGINAS_SAUDE_EXCELENCIA.md` | **Padrão declarado** de páginas de conteúdo (TOC, FAQ, midia, Phase 1) |
| `docs-internos/INVENTARIO_MIDIA_TRR.md` | Inventário de imagens TRR + débitos de fonte/mobile |
| `docs-internos/CKO-PAGE-SHELL.md` | Shell modular breadcrumb/hero |
| `schemas/cko-content-page.schema.json` | Schema dos módulos de conteúdo |
| `docs-internos/MARCO_INSTITUICOES_HOMOLOGADAS.md` | Critérios internos de homologação de fontes |
| `tools/smoke_cart.py` | Smoke checks do delivery CKO-CART-001 |
| `tools/validate-manifest.py` | Validação do manifesto vs instituições |

## Fontes normativas de apoio (docs/)

| Arquivo | Função |
|---------|--------|
| `docs/Parecer_010_2022-Carro-de-emergencia.txt` | Texto de apoio — parecer carro de emergência |
| `docs/pop-carro-urgencia-emergencia_v3.txt` | Texto de apoio — POP carro urgência/emergência |

## Conteúdo de direitos autorais

- Classificação: **conteúdo interno de direitos autorais** (`contentCopyright` no manifesto).
- Corpo de dicas/erros e artigo: texto educativo **próprio** do site.
- Normas externas (COFEN/COREN, SBC, MS, etc.): apenas **referência legal breve**.
- Rodapé padrão:  
  `© Calculadoras de Enfermagem / Cia de Enfermagem Global Platform — direitos reservados. Uso educativo; adaptação ao POP local.`

## URLs canônicas

- Interativo: `https://www.calculadorasdeenfermagem.com.br/biblioteca-carinho-de-emergencia.html`
- Artigo: `https://www.calculadorasdeenfermagem.com.br/biblioteca/artigo-carrinho-de-emergencia-enfermagem.html`
