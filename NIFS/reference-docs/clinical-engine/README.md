# Clinical Intelligence Engine (CAL-001)

Documentação do motor SAE estruturado NANDA–NIC–NOC e da evolução probabilística V3 → V8.

| Documento | Conteúdo |
|-----------|----------|
| [12-clinical-intelligence-engine.md](../12-clinical-intelligence-engine.md) | **Documento principal** — visão, arquitetura, pipeline, segurança |
| [02-evolucao-versoes.md](02-evolucao-versoes.md) | V3 → V8: o que cada versão entrega e status |
| [03-pendencias-roadmap.md](03-pendencias-roadmap.md) | Pendências, V8.5, V9 e checklist de melhorias |
| [04-validacao-datasets.md](04-validacao-datasets.md) | Bases públicas, ETL, métricas, calibração |
| [05-agentes-documentacao-tecnica.md](05-agentes-documentacao-tecnica.md) | Agentes, docs obrigatórias, integração NKOS |
| [06-avaliacao-mercado.md](06-avaliacao-mercado.md) | Notas 0–10, concorrentes, inovação |
| [07-v8-implementacao-referencia.md](07-v8-implementacao-referencia.md) | **V8 código** — módulos, API `runV8`, uso |
| [08-identificadores-nkos.md](08-identificadores-nkos.md) | entity_code, aliases, arestas Master Data |
| [09-v9-proximos-passos.md](09-v9-proximos-passos.md) | **Passo 9** — Neuro-Symbolic + LLM + calibração |
| [10-evidencia-validacao-externa.md](10-evidencia-validacao-externa.md) | Grau A, MIMIC, model card, protocolo |
| [11-apgar-mcts-user-context.md](11-apgar-mcts-user-context.md) | **APGAR demo** — MCTS + User Context + grafo NNN |

## Status no repositório CALENF-NKD

| Camada | Status |
|--------|--------|
| Datasets NKOS (NANDA/NIC/NOC, linkages, árvores) | ✅ `datasets/clinical/` |
| Página SAE no site (`/sae`, template) | ✅ `datasets/content/editorial/template_pages.json` |
| Motor V8 referência | ✅ [`clinical-engine/`](../../clinical-engine/) — Particle Filter + BN + MPC |
| Runtime API / Digital Twin | 📋 Roadmap V9 |

Relacionado: [01-visao-geral.md](../01-visao-geral.md) · [03-datasets.md](../03-datasets.md) · [11-excellencia-global-institutional.md](../11-excellencia-global-institutional.md)
