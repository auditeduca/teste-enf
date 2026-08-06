# CKO Page Shell — módulos compartilhados

Evita duplicar breadcrumb, nav de bibliotecas, hero e aviso/copyright em cada HTML.

**Alinhado a:** `docs-internos/PADRAO_PAGINAS_SAUDE_EXCELENCIA.md` §0 — **um único cluster** (header, a11y, breadcrumb, hero, módulos A–F, footer). Variação de fundo/texto ok; grid diferente = fora do padrão.

## Como usar numa página

No `<head>`:

```html
<link href="/css/pages/cart-emergencia.css" rel="stylesheet">
<link href="/css/pages/cko-page-shell.css" rel="stylesheet">
<link href="/css/pages/cko-content-modules.css" rel="stylesheet">
<script src="/js/cko-page-shell.js" defer></script>
<script src="/js/cko-content-engine.js" defer></script>
```

No `<main>` (só mounts — sem markup de breadcrumb/hero):

```html
<div data-cko-page="cirurgica" data-cko-slot="chrome"></div>
<div data-cko-page="cirurgica" data-cko-slot="hero"></div>
<div class="cko-layout">
  <div class="cko-layout__main">
    <!-- conteúdo editorial B -->
    <div data-cko-content="cirurgica" data-cko-modules="tools,faq,related,references,media"></div>
  </div>
  <aside class="cko-layout__side" data-cko-page="cirurgica" data-cko-slot="sidebar"></aside>
</div>
<div data-cko-page="cirurgica" data-cko-slot="aside"></div>
```

Módulos A–F e validador: `docs-internos/CKO-CONTENT-ENGINE.md`.

## Slots

| Slot | Renderiza |
|------|-----------|
| `chrome` | breadcrumb + navSet + actions |
| `hero` | hero navy padronizado |
| `sidebar` | TOC + recursos úteis + feedback + imprimir |
| `aside` | aviso + copyright |
| `breadcrumb` / `nav` / `actions` | peças isoladas |
| `full` | chrome + hero |

## Onde editar conteúdo

Arquivo único: `data/cko-shell-pages.json`

- `navSets.materiais` — barra compartilhada entre bibliotecas
- `pages.<id>` — breadcrumb, hero, actions, aside da página
- `defaults` — texto padrão de aviso/copyright

Nova página de biblioteca: acrescente entrada em `pages` + dois/três mounts no HTML. Sem copiar HTML de hero/breadcrumb.

## Páginas já ligadas

`carinho`, `carinho-artigo`, `cirurgica`, `curativo`, `seringa`, `provas`, `trr`

Nav sets: `materiais` e `protocolos` (TRR / NEWS / SAV / 5 Hs / Carrinho).

Hero do carrinho continua no `cart-renderer.js` (manifesto); o shell cuida do chrome/aside.
