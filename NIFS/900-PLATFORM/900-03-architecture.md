# NIFS-900-03: Architecture

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-900-03                        |
| Status        | Validated                          |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Documentar a arquitetura técnica real do website calculadorasdeenfermagem.com.br, baseada na análise do codebase extraído (685 arquivos, 97 calculadoras).

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    PIPELINE DE GERAÇÃO                     │
│                                                           │
│  data/tools/*.json ──→ generate_tool_page.py ──→ *.html  │
│  (97 ferramentas)       (SSG Python, 698 linhas)  (120)  │
│       ↑                        ↑                          │
│  tool.schema.json         calc-tool.css                    │
│  (Draft-07)              main.css + site-styles.css       │
└───────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                    RUNTIME DO NAVEGADOR                     │
│                                                           │
│  partials-loader.js ──→ header.html + footer.html        │
│         ↓                                                 │
│  calc-engine.js ──→ #tool-config JSON ──→ Recalcular     │
│  lang-selector.js ──→ i18n/{code}.json ──→ 30 idiomas    │
│  mega-menu.js ──→ Navegação + Busca                      │
│  modules/sae-engine.js ──→ Wizard SAE (NANDA/NIC/NOC)    │
│  modules/sbar-engine.js ──→ Wizard SBAR                   │
│  modules/cv-engine.js ──→ Gerador de Currículo            │
│  modules/catalog-page.js ──→ Catálogo com filtros         │
└───────────────────────────────────────────────────────────┘
```

## 3. Camadas

| Camada | Tecnologia | Arquivo Principal | Função |
|--------|-----------|-------------------|--------|
| Dados | JSON (Draft-07) | `data/schemas/tool.schema.json` | Schema de cada calculadora |
| Geração | Python SSG | `scripts/generate_tool_page.py` (42KB) | Gera HTML estático SEO-otimizado |
| Estilo | CSS | `css/main.css` + `calc-tool.css` + `site-styles.css` | 107KB total de estilos |
| Partials | HTML + JS | `partials/*.html` + `partials-loader.js` | Header, footer, a11y, cookie |
| Runtime | JavaScript | `js/calc-engine.js` (19KB) | Motor interativo genérico |
| i18n | JSON + JS | `i18n/{code}.json` + `lang-selector.js` | 30 idiomas, 345 chaves |
| Módulos | JavaScript | `js/modules/*.js` | SAE, SBAR, CV, Catálogo |
| Imagens | WebP/PNG/SVG | `images/flags/` (382) + `images/icons/` | Bandeiras + ícones |

## 4. Tool Schema (tool.schema.json)

Cada calculadora segue o JSON Schema Draft-07 com 14 seções obrigatórias:

```json
{
  "id": "UUID v4",
  "code": "SCALE-APGAR-001",
  "slug": "apgar",
  "version": "1.0.0",
  "status": "published",
  "seo": { "title", "description", "canonical" },
  "breadcrumb": { "category", "categoryHref" },
  "overview": { "name", "acronym", "objective", "indication", "targetPopulation", "specialty", "evidenceLevel", "originalAuthors", "complexity", "rating" },
  "calculator": { "inputs[]", "formula" },
  "interpretation": { "ranges[]": { "min", "max", "label", "riskLevel", "color", "clinicalImplications", "recommendations" } },
  "sae": { "nanda[]", "noc[]", "nic[]" },
  "evidence": { "foundation", "history", "validation", "limitations", "references[]" },
  "learning": { "tips[]", "examples[]", "quiz[]" },
  "faq": [{ "q", "a" }],
  "about": { "title", "html" }
}
```

**Este schema É o Clinical Intelligence Package** com 6 dimensões:
1. **Conteúdo** → overview + calculator + interpretation
2. **SAE** → nanda + noc + nic (NANDA-I/NIC/NOC integrados)
3. **Evidência** → foundation + references (com GRADE)
4. **Aprendizado** → tips + examples + quiz
5. **FAQ** → perguntas frequentes
6. **Sobre** → explicação detalhada (HTML)

## 5. Perfis de Visualização

O calc-engine.js suporta 5 perfis por calculadora:

| Perfil | Foco | Features |
|--------|------|----------|
| Padrão | Uso clínico | Calculadora + interpretação + SAE |
| Estudante | Aprendizado | Passo-a-passo + quiz + dicas |
| Modo Urgência | Emergência | Inputs mínimos + resultado ampliado + alarme |
| Acadêmico | Pesquisa | Cálculo detalhado + evidência + referências |
| Gestor | Gestão | Indicadores + benchmarks + métricas |

## 6. i18n Architecture

```
pt-BR (nativo, embutido no HTML)
    ↓ fallback
en (i18n/en.json — 345 chaves)
    ↓ fallback
es, fr, de, it, ... (i18n/{code}.json)
    ↓ fallback
pt-BR (texto original do HTML)
```

- 30 idiomas no seletor (`lang-selector.js`)
- 196 países mapeados (`i18n/country-locale-map.json`)
- Cada idioma tem 345 chaves UI (nav, footer, a11y, cookie, tool cards)
- Conteúdo clínico (overview, interpretation, SAE) em pt-BR — fase de tradução clínica pendente

## 7. SSG Pipeline

```
1. Escrever data/tools/{slug}.json (seguindo tool.schema.json)
2. Executar: python3 scripts/generate_tool_page.py data/tools/{slug}.json > {slug}.html
3. HTML gerado com:
   - Todo texto "assado" para SEO (server-side)
   - JSON embutido em <script id="tool-config"> para o calc-engine.js
   - 5 painéis de perfil (padrão/estudante/urgência/acadêmico/gestor)
   - Partials carregados via partials-loader.js
4. Deploy: upload estático para hosting
```

## 8. File Inventory

| Categoria | Quantidade | Tamanho Total |
|-----------|-----------|---------------|
| HTML pages | 120 | ~8MB |
| Tool JSONs | 97 | ~2MB |
| i18n files | 31 | ~620KB |
| JS modules | 11 | ~130KB |
| CSS files | 3 | ~107KB |
| Python scripts | 5 | ~50KB |
| HTML partials | 4 | ~32KB |
| Images | 140 | ~33MB |
| **Total** | **421** | **~43MB** |

## 9. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-900-01 | Backend (SSG details) |
| NIFS-900-02 | Frontend (calc-engine details) |
| NIFS-900-04 | Modules (SAE, SBAR, CV) |
| NIFS-1300-01 | Developer Guide: Adding a calculator |
