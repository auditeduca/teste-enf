# LangGraph + DeepSeek — agentes APGAR

## Pré-requisito

```bash
pip install -r requirements-nkp.txt
export DEEPSEEK_API_KEY=sk-...
```

## Pipeline por campo (Search → Generate → Review → Validate)

```bash
python scripts/apgar_agents/run_field_pipeline.py --field APGAR.scl.score_max --llm --json
python scripts/apgar_agents/run_field_pipeline.py --all --llm --model deepseek-v4-flash
python scripts/apgar_agents/run_field_pipeline.py --validate-only   # sem LLM
```

| Flag | Efeito |
|------|--------|
| `--llm` | Ativa DeepSeek nos nós generate/review |
| `--no-llm` | Força determinístico |
| `--model` | Modelo DeepSeek (default: `deepseek-v4-flash`) |
| `--api-key` | Ou variável `DEEPSEEK_API_KEY` |

Implementação: `scripts/apgar_agents/graph.py` (LangGraph) + `llm.py` (cliente DeepSeek reutiliza `review/deepseek_client.py`).

## Tradução 30 idiomas (LangGraph bateladas)

```bash
python scripts/apgar_agents/translation_agent.py --llm --write --json
python scripts/apgar_agents/translation_agent.py --llm --refresh-tier machine_from_en
```

Grafo: `search → generate (lotes 5) → merge → review → validate`  
Arquivo: `scripts/apgar_agents/translation_graph.py`

## Prompts

| Arquivo | Agente |
|---------|--------|
| `prompts/search.md` | Search |
| `prompts/generate.md` | Generate |
| `prompts/review.md` | Review |
| `prompts/validate.md` | Validate (referência) |
| `prompts/translate.md` | Tradução 30 idiomas |

## Fallback

Se `DEEPSEEK_API_KEY` ausente ou erro de API → fallback determinístico (`i18n_catalog.py` / `canonical.json`) sem falhar o pipeline.
