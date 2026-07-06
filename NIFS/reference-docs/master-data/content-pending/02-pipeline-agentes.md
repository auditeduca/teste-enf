# Pipeline de agentes — conteúdos pendentes

## Grafo LangGraph (por campo)

```
Search → Generate → Review → Validate
```

| Agente | Função |
|--------|--------|
| **Search** | Busca datasets, proposta master-data, lineage SCL |
| **Generate** | Propõe rascunho estruturado (JSON) — não grava arquivos |
| **Review** | Aprova / revisa / rejeita (evidência, clínica) |
| **Validate** | `validate_content.py` + regras do campo |

## Micro-fases M1–M9

| Fase | Módulo |
|------|--------|
| M1 | Registro e fila |
| M2 | Flashcards |
| M3 | Simulados |
| M4 | Mapas mentais |
| M5 | Protocolos |
| M6 | Guias de bolso |
| M7 | FAQ |
| M8 | Pipeline agentes |
| M9 | Gate CI |

## DeepSeek

- CLI: `DEEPSEEK_API_KEY` ou `--api-key`
- App: `localStorage` → `deepseekApiKey` (body `api_key`)

Prompts: `scripts/content_agents/prompts/*.md`
