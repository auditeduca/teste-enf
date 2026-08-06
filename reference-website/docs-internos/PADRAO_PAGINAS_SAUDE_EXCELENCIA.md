# Padrão CKO — Páginas de conteúdo em saúde (excelência)

**Status:** DECLARADO (baseline) — aplicar a todas as páginas de conteúdo PT-BR após aprovação.  
**Data:** 2026-08-05  
**Escopo:** páginas educativas/protocolos/bibliotecas (não calculadoras interativas puras).

---

## 0. Regra-mãe: um único cluster editorial/visual

**As páginas devem ser praticamente iguais em estrutura.**  
O leitor reconhece o site pela **mesma ossatura**, não por layouts inventados por página.

| Camada | Obrigatório idêntico | Variação permitida |
|--------|----------------------|--------------------|
| Skip link / a11y anti-CLS / dark-mode boot | Sim — mesmos scripts e padrões | — |
| Header global (`#global-header-container`) | Sim — `menu-global.html` | — |
| Seletor de idioma | Sim — `#language-selector-placeholder` | — |
| Largura do main | Sim — `max-w-7xl mx-auto` (cluster com sidebar) | — |
| Breadcrumb | Sim — componente shell (mesmas classes) | Só os *itens* do trail |
| Nav de cluster (materiais / protocolos) | Sim — `cko-btn` + `ce-actionbar` | Só o `navSet` ativo |
| Actions da página | Sim — mesma barra visual | Só os links |
| Banner / hero | Sim — `cko-cart-hero` (eyebrow, H1, lead, chips) | Texto, chips, tom do gradiente |
| **Grid editorial** | Sim — `.cko-layout` = **main + sidebar** (mesmo em todas) | Sem inventar outro grid |
| **Sidebar** | Sim — índice + recursos úteis + feedback (+ imprimir) | Conteúdo dos cards |
| Corpo editorial (coluna main) | Sim — módulos A→F na coluna principal | Conteúdo textual/midia |
| Aside aviso + copyright | Sim — shell (abaixo do layout) | Texto do aviso |
| Footer global | Sim — `footer.html` | — |
| Fundo da página | Preferência `bg-gray-50` / slate-50 | Tinte suave **sem** mudar grid |

### 0.1 Proibido (quebra de cluster)

- Breadcrumb com SVG/casa, classes `.breadcrumb` legadas ou markup diferente do shell  
- Hero “title-bar” / `h1` solto / card navy reinventado (`hero-card-navy`, `meem-card-navy`)  
- Grid inventado por página (sidebar só em algumas, ou 3 colunas, ou full-bleed sem shell)  
- Página de conteúdo **sem** sidebar padrão `.cko-layout__side`  
- Skip links / acessibilidade só em algumas páginas  
- Footer ou header “local” paralelo ao global  
- Recursos/feedback em posições aleatórias (devem viver na sidebar + módulos da main)

### 0.2 Permitido (variação controlada)

- Texto do hero, chips, `navSet` (`materiais` vs `protocolos`)  
- Fundo: leve variação de token (`--cko-page-tint`) **sem** alterar tipografia, largura ou ordem dos blocos  
- Dentro da coluna main: tabelas, listas, figuras — mesmas classes de seção/card  
- Produto especial (ex.: explorador do carrinho) na coluna main, mantendo sidebar de recursos/feedback  

### 0.3 Diagrama do cluster (todas as páginas)

```
┌──────────────────────────────────────────────────────┐
│ Skip → Header global → Idioma                          │
├──────────────────────────────────────────────────────┤
│ main.max-w-7xl                                         │
│  breadcrumb · navSet · actions                         │
│  hero/banner                                           │
│  ┌────────────── cko-layout ───────────────────────┐   │
│  │ MAIN                    │ SIDEBAR (sticky)       │   │
│  │ A Índice (também side)  │ Nesta página (TOC)     │   │
│  │ B Seções + midia        │ Recursos úteis         │   │
│  │ D FAQ                   │ Feedback               │   │
│  │ E Relacionados          │ Imprimir               │   │
│  │ F Refs + créditos       │                        │   │
│  └─────────────────────────┴────────────────────────┘   │
│  aviso + copyright                                       │
├──────────────────────────────────────────────────────┤
│ Footer global                                            │
└──────────────────────────────────────────────────────┘
```

**Teste de ouro:** tirando o texto e as imagens, duas páginas qualquer (TRR vs Cirúrgica vs NEWS) devem parecer o **mesmo template**.

---

## 1. Por que o desktop “parece igual”

O shell modular (breadcrumb / hero / nav / aviso) **já muda o topo**.  
O **corpo** das páginas legado (TRR, NEWS, etc.) ainda é o conteúdo antigo: parede de texto + imagens full-bleed sem índice, FAQ, midia desktop/mobile, nem bloco de ferramentas.

**Regra:** excelência = **cluster único** (seção 0) + **módulos de conteúdo obrigatórios** abaixo do hero. Trocar só o chrome não basta; inventar grid novo também é erro.

---

## 2. Referências de excelência (benchmark)

Usamos estes marcos como critério de qualidade (não como cópia visual):

| Fonte | O que adotamos |
|-------|----------------|
| [NHS — Standard for creating health content](https://service-manual.nhs.uk/content/standard-for-creating-health-content) | Conteúdo claro, acionável, atualizado, evidência, linguagem acessível |
| [NHS — Accessibility / WCAG 2.2 AA](https://digital.nhs.uk/about-nhs-digital/standards-for-web-products/accessibility-for-digital-services) | Contraste, teclado, alt text, HTML primeiro (não PDF como formato principal) |
| MedlinePlus / CDC / WHO (páginas educativas) | Sumário no topo, seções curtas, “quando procurar ajuda”, refs no rodapé |
| COFEN / MS / ANVISA / PlanificaSUS (BR) | Enquadramento normativo local; disclaimer de não substituir POP |
| Cochrane / SciELO (citação) | Links canônicos + data de acesso; não inventar evidência |

**Princípios CKO derivados**

1. **HTML primeiro** — leitura completa na página; PDF só como anexo opcional.
2. **Orientação clínica local** — sempre disclaimer POP / protocolo institucional.
3. **Evidência rastreável** — toda afirmação normativa/científica com fonte.
4. **Mídia responsável** — toda imagem com alt, fonte/origem e papel (ilustrativo vs protocolo).
5. **Navegação cognitiva** — índice da página + FAQ + relacionados antes do scroll infinito.
6. **Mobile parity** — figuras de protocolo com variante desktop **e** thumbnail/mobile.

---

## 3. Arquitetura de página (obrigatória)

```
[Header global]
[Shell chrome]   breadcrumb + navSet + actions
[Shell hero]     eyebrow · H1 · lead · chips
[Módulo A]       Índice da página (TOC)
[Módulo B]       Conteúdo por seções (H2/H3) + midia
[Módulo C]       Ferramentas úteis (links/calculadoras — não widgets de lixo)
[Módulo D]       Dúvidas frequentes (FAQ)
[Módulo E]       Relacionados
[Módulo F]       Referências + midia credits
[Shell aside]    aviso + copyright
[Footer global]
```

### 3.1 O que entra em cada módulo

| ID | Módulo | Obrigatório | Conteúdo mínimo |
|----|--------|-------------|-----------------|
| A | Índice | Sim | Âncoras para todos os H2; sticky opcional desktop |
| B | Seções | Sim | 1 ideia por H2; imagens com caption + fonte |
| C | Ferramentas úteis | Sim* | Links para calculadora/protocolo/carrinho relevantes (*omitir só se não houver ferramenta real) |
| D | FAQ | Sim | ≥ 4 Q&A específicas da página |
| E | Relacionados | Sim | 3–7 links internos tipados (protocolo/guia/calculadora) |
| F | Referências | Sim | Bibliografia + **créditos de midia** |

### 3.2 Phase 1 — recursos obrigatórios na sidebar

- Índice (TOC)
- Recursos úteis (calculadoras/protocolos irmãos)
- **Feedback** (avaliação + comentário; persistência local até backend)
- Imprimir / PDF via navegador

### 3.3 O que NÃO é padrão Phase 1 (ainda)

- Export Word/Excel genérico em página de conteúdo  
- Chat / NPS de terceiro  
- Comentários públicos  
- Paywall / lead magnet  

(CKO-CART export permanece exceção de **produto**, não de página editorial.)

---

## 4. Shell visual + templates por tipo

| Peça | Arquivo |
|------|---------|
| Catálogo | `data/cko-shell-pages.json` |
| Renderer | `js/cko-page-shell.js` |
| CSS shell | `css/pages/cko-page-shell.css` |
| Tokens produto | `css/pages/cart-emergencia.css` (`#1A3E74`, Inter, Nunito Sans) |
| Templates (home/institucional/calc/tool) | `data/cko-page-templates.json` · `js/cko-page-templates.js` · `css/pages/cko-page-templates.css` · `docs-internos/CKO-PAGE-TEMPLATES.md` |

**Regra:** páginas de conteúdo usam `cko-cart-page` + mounts `data-cko-page` / `data-cko-slot`.  
**Proibido:** breadcrumb/hero HTML duplicado por página.

---

## 5. Midia — declaração obrigatória

Toda imagem em página de conteúdo deve constar em inventário com:

| Campo | Descrição |
|-------|-----------|
| `file` | Path `/img/...` |
| `role` | `protocol-figure` \| `illustrative` \| `ui-screenshot` \| `banner` |
| `alt` | Texto alternativo factual |
| `caption` | Legenda visível (o que o usuário deve aprender) |
| `source` | Origem (produção própria CKO / órgão / URL) |
| `license` | Uso educativo / direitos reservados / etc. |
| `desktop` | Arquivo desktop (opcional se único) |
| `mobile` | Arquivo mobile/thumbnail (obrigatório para `protocol-figure`) |

**Protocol figures** (fluxogramas, escalas, critérios): sempre **par desktop + mobile**.  
**UI screenshots** (ex.: calculadora NEWS): preferir crop mobile + desktop.

Inventário TRR (estado atual — a declarar/completar fontes): ver `docs-internos/INVENTARIO_MIDIA_TRR.md`.

---

## 6. Conteúdo textual — regras rápidas

- H1 único = título do hero (não repetir H1 no artigo).
- Seções com H2 estáveis (`id` slug) para TOC.
- Tabelas com `<th>` e caption.
- Disclaimer clínico em `aside` (shell) + reforço se a página for protocolo.
- Não misturar “conteúdo educativo” com marketing de curso no primeiro viewport.
- CTAs: no máximo 2 primários (ex.: Calculadora NEWS + Carrinho).

---

## 7. Ferramentas úteis (definição)

Ferramenta útil = **leva o profissional a agir** no mesmo ecossistema:

- Calculadora (NEWS, scores)
- Checklist / conferência (carrinho)
- Protocolo irmão (SAV, 5 Hs/Ts)
- Simulado

Não conta como ferramenta útil: botão “compartilhar”, “gerar PDF”, “deixe feedback” sem fluxo clínico.

---

## 8. Content Engine (implementado)

Documentação completa: `docs-internos/CKO-CONTENT-ENGINE.md`

| Peça | Path |
|------|------|
| Contrato de identidade | `data/cko-content-identity.json` |
| Manifesto por página | `data/content/<pageId>.json` |
| Renderer | `js/cko-content-engine.js` |
| CSS módulos | `css/pages/cko-content-modules.css` |
| Schema | `schemas/cko-content-page.schema.json` |
| Validador | `tools/validate_content_identity.py` |

```html
<div data-cko-content="trr" data-cko-modules="tools,faq,related,references,media"></div>
```

Piloto: `time-de-resposta-rapida.html` + `data/content/trr.json`.

---

## 9. Ordem de rollout (após este documento)

1. **TRR** — piloto completo dos módulos A–F + midia desktop/mobile  
2. **NEWS** — protocolo com thumbs mobile + TOC + FAQ + tools  
3. Demais protocolos ligados ao nav `protocolos` (SAV, 5 Hs, 5 Ts…)  
4. Bibliotecas de materiais (já no shell; acrescentar TOC/FAQ onde couber)  
5. Varredura PT-BR de conteúdo restante

---

## 10. Critério de aceite (“página no padrão”)

- [ ] **Cluster idêntico** à seção 0 (header, a11y, breadcrumb, hero, **cko-layout main+sidebar**, aside, footer)
- [ ] Sidebar com TOC + recursos úteis + **feedback**
- [ ] Sem hero/breadcrumb legado divergente
- [ ] Shell chrome + hero + sidebar + aside via catálogo  
- [ ] FAQ ≥ 4 (coluna main)  
- [ ] Relacionados ≥ 3 (coluna main)  
- [ ] Referências com links  
- [ ] Créditos/origem de **todas** as imagens  
- [ ] Protocol figures com variante mobile  
- [ ] Desktop e mobile: sidebar empilha abaixo no mobile, mesma ordem de cards  

---

## 11. Decisões registradas (2026-08-05)

1. Documentar **antes** de massificar ajustes.  
2. Phase 1 = qualidade editorial + navegação + midia + feedback na sidebar (localStorage).  
3. NEWS e TRR são prioridade por vínculo clínico (deterioração → TRR → carrinho/PCR).  
4. Toda midia sem fonte declarada = **débito** até inventário preenchido.  
5. **Um cluster só:** `cko-layout` (main + sidebar) em todas; variação de fundo/texto ok.  
6. **Sidebar obrigatória** com TOC + recursos úteis + feedback.  
7. **Content Engine + validator** obrigatórios para novas páginas de conteúdo (ver `CKO-CONTENT-ENGINE.md`).  

