# Clinical Article Factory

Agente que gera **artigos editoriais** no formato `datasets/content/editorial/articles.json`:

- **Problema** — dores reais por região (BR, LatAm, US, UK, IN), erros comuns, impacto clínico, soft skills
- **Solução** — mitigação de risco, técnicas, checklist, apoio digital, soft skills aplicadas

## Master Data

```
datasets/master-data/clinical-articles/
├── canonical.json
├── article_template.json       # Estrutura problema vs solução
├── tool_pain_registry.json     # Dores detalhadas (gotejamento, Capurro, etc.)
├── category_pain_defaults.json # Fallback por categoria de ferramenta
└── soft_skills_registry.json   # 10 soft skills clínicas
```

## Ferramentas piloto (dores detalhadas)

| Código | Tema |
|--------|------|
| TOOL.INFUSION | Calculadora de gotejamento |
| TOOL.CAPURRO | Método de Capurro (neonatal) |
| TOOL.APGAR | Escala de Apgar |
| TOOL.BRADEN | Escala de Braden |
| TOOL.GCS | Glasgow |
| TOOL.BMI | IMC |
| TOOL.MCG_KG_MIN | mcg/kg/min (vasopressores) |
| TOOL.INSULIN | Insulina |

## CLI

```bash
# Piloto: 16 artigos (8 ferramentas × 2)
python scripts/clinical_article_agents/run_batch.py --pilot --apply

# Uma ferramenta
python scripts/clinical_article_agents/run_batch.py --tool TOOL.INFUSION --apply

# Catálogo completo (~200 artigos)
python scripts/clinical_article_agents/run_batch.py --all --apply

# Status
python scripts/clinical_article_agents/run_batch.py --status
```

## API

| Método | Rota | Body |
|--------|------|------|
| GET | `/api/clinical-articles/status` | — |
| POST | `/api/clinical-articles/generate` | `{ "tool": "TOOL.INFUSION" }` ou `{ "all": true, "apply": true }` |

## Integração website

Após `--apply`, regenere o site:

```bash
python scripts/generate_website_pt.py
```

Artigos aparecem em `/artigos/` com layout científico (TOC, callouts, cards, checklist).

## Evolução

- Fase 2: LLM para enriquecer storytelling por locale
- Fase 3: Vincular artigos ao grafo NANDA-NIC-NOC por ferramenta
- Fase 4: Artigos em en-US, es-ES via locale overrides
