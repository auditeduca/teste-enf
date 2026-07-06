# NIFS-900-01: Backend (Static Site Generator)

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-900-01                        |
| Status        | Validated                          |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Documentar o backend do website — um pipeline SSG (Static Site Generator) em Python que gera páginas HTML estáticas a partir de JSON.

## 2. SSG Architecture

O site NÃO tem backend runtime. Todo HTML é gerado estaticamente:

```
data/tools/apgar.json
        ↓
generate_tool_page.py (698 linhas, 42KB)
        ↓
apgar.html (60KB, 546 linhas)
```

### Pipeline:
1. **Input**: `data/tools/{slug}.json` (segue `tool.schema.json`)
2. **Process**: Python lê JSON, gera HTML com todas as seções "assadas"
3. **Output**: `{slug}.html` com:
   - SEO meta tags (title, description, canonical, OG, Twitter)
   - Breadcrumb navigation
   - 5 painéis de perfil (Padrão/Estudante/Urgência/Acadêmico/Gestor)
   - JSON embutido em `<script id="tool-config">`
   - Referências a CSS (main.css, calc-tool.css, site-styles.css)
   - Referências a JS (calc-engine.js, partials-loader.js, lang-selector.js)

## 3. Python Scripts

| Script | Tamanho | Função |
|--------|---------|--------|
| `generate_tool_page.py` | 42KB (698 linhas) | Gera HTML de calculadora a partir de JSON |
| `generate_i18n.py` | 8KB | Gera dicionários i18n para 30 idiomas |
| `generate_country_locale_map.py` | 12KB | Mapeia 196 países → idiomas |
| `audit_pendencias.py` | — | Auditoria de pendências do site |
| `build_resource_modules.py` | — | Constrói módulos de recursos (biblioteca, NANDA, etc) |

## 4. generate_tool_page.py — Detalhes

O SSG gera cada página com:

### SEO (server-side):
- `<title>` otimizado
- `<meta name="description">` 
- `<link rel="canonical">`
- Open Graph tags
- Twitter Card tags
- Structured data (JSON-LD)

### HTML estruturado:
- Header com breadcrumbs
- Tool header (ícone, categoria, rating, actions)
- 5 painéis de perfil com tabs ARIA
- Formulário de calculadora (inputs sincronizados)
- Interpretação com faixas coloridas
- SAE (NANDA/NIC/NOC)
- Evidência (foundation + references)
- Aprendizado (tips + examples + quiz)
- FAQ
- About (HTML rich text)

### JSON embutido:
```html
<script type="application/json" id="tool-config">
  { ... mesmo conteúdo do data/tools/{slug}.json ... }
</script>
```
O `calc-engine.js` lê este JSON no runtime para funcionalidade interativa.

## 5. Data Pipeline

```
ESPECIFICAÇÃO (NIFS)
    ↓
tool.schema.json (Draft-07)
    ↓
data/tools/*.json (97 ferramentas)
    ↓
generate_tool_page.py
    ↓
*.html (120 páginas)
    ↓
Deploy estático (CDN/hosting)
```

## 6. NKOS Integration

O CALENF-NKD (codebase NKOS v4.4) tem um pipeline mais robusto:
- `scripts/generators/` — geradores SSG avançados
- `scripts/ai_factory_agents/` — AI factory com catalog e batch runner
- `scripts/anvisa_open_data_agents/` — agentes ANVISA (monthly sync)
- CI/CD: `daily-platform-loop.yml` + `monthly-anvisa-sync.yml`

O website atual (`Pagina inicial/`) é uma versão simplificada deste pipeline.

## 7. Future: NIS Backend

O NIS v5.0 adicionará:
- API REST (NIFS-800-05) — servindo dados das ferramentas
- FHIR endpoints (NIFS-800-01) — interoperabilidade EHR
- Clinical Engine V8 — raciocínio bayesiano em tempo real
- Vector search — recuperação de evidência por similaridade

O SSG continuará para conteúdo estático (SEO), mas o NIS adicionará camada dinâmica.

## 8. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-900-03 | Architecture (overview) |
| NIFS-900-02 | Frontend (calc-engine) |
| NIFS-1300-01 | Developer Guide: How to add a calculator |
