# NIFS-900-05: Services

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-900-05                        |
| Status        | Validated                          |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Documentar os serviços da plataforma — SSG, geração de páginas, i18n e scripts de automação.

## 2. Service Catalog

| Serviço | Tecnologia | Frequência | Output |
|---------|-----------|-----------|--------|
| SSG (geração de páginas) | Python | On-demand | HTML estático |
| i18n generation | Python | On-demand | 30 JSON files |
| Country locale mapping | Python | On-demand | 196 países JSON |
| Audit pendências | Python | On-demand | Relatório |
| Build resource modules | Python | On-demand | Módulos de dados |
| Deploy | Manual/CI | On-release | CDN upload |

## 3. SSG Service

### Input:
```
data/tools/{slug}.json (seguindo tool.schema.json)
```

### Command:
```bash
python3 scripts/generate_tool_page.py data/tools/apgar.json > apgar.html
```

### Output:
- HTML estático (60-110KB por página)
- SEO otimizado (title, meta, OG, canonical, JSON-LD)
- 5 perfis de visualização
- JSON embutido para runtime

### Batch generation:
```bash
for f in data/tools/*.json; do
  slug=$(basename "$f" .json)
  python3 scripts/generate_tool_page.py "$f" > "${slug}.html"
done
```

## 4. i18n Service

### Command:
```bash
python3 scripts/generate_i18n.py
```

### Output:
- 27 arquivos `i18n/{code}.json` (345 chaves cada)
- Atualiza `i18n/manifest.json` com status

### Country Mapping:
```bash
python3 scripts/generate_country_locale_map.py
```

### Output:
- `i18n/country-locale-map.json` (196 países → 30 idiomas)

## 5. NKOS CI/CD (referência)

O CALENF-NKD tem CI mais robusto:
- `daily-platform-loop.yml` — loop diário de plataforma
- `monthly-anvisa-sync.yml` — sync mensal ANVISA
- `anvisa_open_data_agents/` — agentes de descoberta/extração/validação

O website atual não tem CI ativo (gap identificado no audit).

## 6. Future Services (NIS v5.0)

| Serviço | Tecnologia | Status |
|---------|-----------|--------|
| REST API | Node.js/Deno | Planejado (NIFS-800-05) |
| FHIR API | Node.js/Deno | Planejado (NIFS-800-01) |
| Clinical Engine V8 | JS/WASM | Planejado (NIFS-600) |
| Vector Search | Embedding + cosine | Planejado (NIFS-700) |
| Multi-Agent Council | Agent framework | Planejado (NIFS-600-18) |

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-900-01 | Backend (SSG details) |
| NIFS-900-09 | Scheduler (CI/CD) |
| NIFS-800-05 | REST API |
