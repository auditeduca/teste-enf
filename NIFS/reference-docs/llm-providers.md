# Provedores LLM — Estratégia combinada NKOS

O roteador unificado (`scripts/llm_router/`) direciona cada tarefa ao provedor mais adequado.

## Variáveis de ambiente

**Use `.env` na raiz** (nunca chaves reais em `.env.example`):

```powershell
copy .env.example .env
# Edite .env e preencha as chaves
```

O carregamento é automático via `scripts/agent_common/env_loader.py` ao iniciar:
- `python scripts/nkp_api.py`
- `python scripts/graph_intelligence_agents/run_batch.py`
- qualquer import de `llm_router`

Verifique: `GET /api/llm/status` → `env.env_file_exists` e `providers.*.configured`.

| Variável | Provedor | Uso principal |
|----------|----------|---------------|
| `ANTHROPIC_API_KEY` | Claude | Validação de grafo, decisão clínica densa, raciocínio |
| `ANTHROPIC_MODEL` | Claude | Default: `claude-sonnet-4-20250514` |
| `DEEPSEEK_API_KEY` | DeepSeek | Tradução, code review, conteúdo em volume |
| `DEEPSEEK_MODEL` | DeepSeek | Default: `deepseek-v4-flash` |
| `GROQ_API_KEY` | Groq (Llama) | Screening rápido, classificação, sumarização |
| `GROQ_MODEL` | Groq | Default: `llama-3.3-70b-versatile` |
| `CURSOR_API_KEY` | Cursor | Code review alternativo (opcional) |

## Roteamento por tarefa

| Task | Provedor | Agente |
|------|----------|--------|
| `graph_validation` | Claude | graph_validator_claude |
| `clinical_decision_content` | Claude | clinical_content_claude |
| `reasoning_chain` | Claude | cross_tool_agent |
| `translation` | DeepSeek | localization |
| `code_review` | DeepSeek | code_reviewer |
| `bulk_content` | DeepSeek | clinical_content |
| `fast_check` | Groq | graph_inventory |
| `classification` | Groq | graph_validator |
| `summarize` | Groq | analytics_evolution |

## APIs

```bash
# Status de todos os provedores
GET /api/llm/status

# Chat com roteamento automático
POST /api/llm/route
{ "task": "graph_validation", "json": true, "messages": [...] }

# Proxy genérico (inclui claude)
POST /api/ai/complete
{ "provider": "claude", "messages": [...] }
```

## CLI

```bash
# Inventário do grafo (sem LLM)
python scripts/graph_intelligence_agents/run_batch.py --inventory

# Validação completa (Claude se ANTHROPIC_API_KEY configurada)
python scripts/graph_intelligence_agents/run_batch.py --validate

# Screening rápido (Groq)
python scripts/graph_intelligence_agents/run_batch.py --fast-screen

# Conteúdo clínico denso para ferramenta
python scripts/graph_intelligence_agents/run_batch.py --tool TOOL.GCS --content
```

## Integração em agentes existentes

Agentes APGAR (`scripts/apgar_agents/llm.py`) aceitam `task` ou `llm_task` no payload para rotear via `llm_router` quando a tarefa não é volume/review padrão.
