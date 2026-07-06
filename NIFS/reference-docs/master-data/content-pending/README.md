# Master Data — Conteúdos pendentes

> **Status:** `PENDING_REVIEW` — fila editorial antes de `published`.

Pacote master-data para **6 tipos de conteúdo** com agentes **Search → Generate → Review → Validate** (LangGraph + DeepSeek).

---

## Tipos de conteúdo

| Sufixo | Tipo | Dataset alvo | Itens na fila |
|--------|------|--------------|---------------|
| **FLA** | Flashcards | `datasets/education/flashcards.json` | 40 (proposta doc 14) |
| **SIM** | Simulados | `datasets/education/simulated_exams.json` | 10 piloto |
| **MMP** | Mapas mentais | `datasets/content/editorial/mindmaps.json` | 10 piloto |
| **PRT** | Protocolos | catálogo clínico | 10 |
| **PKT** | Guias de bolso | `datasets/content/editorial/pocket_guides.json` | 10 piloto |
| **FAQ** | FAQ por página | `template_pages.json` | 10 páginas |

**Total:** 90 itens em `pending_items.json`

---

## Estrutura

```
datasets/master-data/content-pending/
├── canonical.json
├── content_types.json
├── pending_items.json      ← fila (regenerável)
├── field_documentation.json
├── modules.json
├── validation_report.json
└── agent_runs/

scripts/content/
├── pending_catalog.py      ← regenera fila
├── validate_content.py
└── field_registry.py

scripts/content_agents/
├── graph.py
├── run_field_pipeline.py
├── run_phases.py
└── phases/registry.py      ← M1–M9
```

---

## Comandos

```bash
# Regenerar fila a partir da proposta master-data
python scripts/content/pending_catalog.py

# Validar estrutura (CI gate)
python scripts/content/validate_content.py --json

# Pipeline por campo (determinístico)
python scripts/content_agents/run_field_pipeline.py --field CONTENT.FLA.deck_structure --no-llm

# Micro-fases M1–M9
python scripts/content_agents/run_phases.py

# Com DeepSeek
python scripts/content_agents/run_field_pipeline.py --field CONTENT.PRT.checklist_steps --llm
```

---

## App (plataforma)

- Rota: **`/content-pending`**
- API: `/api/content-pending/*` (mesma `deepseekApiKey` do app)
- Reinicie `python scripts/nkp_api.py` após pull

---

## Documentação

- [01-tipos-conteudo.md](01-tipos-conteudo.md)
- [02-pipeline-agentes.md](02-pipeline-agentes.md)
- [03-campos-por-tipo.md](03-campos-por-tipo.md)
- [04-workflow-aprovacao.md](04-workflow-aprovacao.md)

→ Padrão de códigos: [doc 14](../../14-master-data-sequencia-revisao.md)  
→ Piloto clínico: [master-data/apgar](../apgar/README.md)
