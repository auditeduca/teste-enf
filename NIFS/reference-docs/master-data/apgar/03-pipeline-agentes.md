# APGAR — Pipeline de agentes (campo a campo)

Quatro agentes por campo — **somente dados APGAR**.

```
┌─────────┐   ┌──────────┐   ┌────────┐   ┌──────────┐
│ Search  │ → │ Generate │ → │ Review │ → │ Validate │
└─────────┘   └──────────┘   └────────┘   └──────────┘
     │              │             │              │
  fonte A      proposed      approve/       validate_
  + dataset      value         reject         apgar.py
```

---

## 1. Search Agent

- **Input:** `field_id`, `field_documentation.json`, `canonical.json`
- **Output:** valor canônico, fontes, valores atuais no dataset
- **Prompt:** `scripts/apgar_agents/prompts/search.md`
- **LLM:** opcional — modo determinístico usa canonical direto

---

## 2. Generate Agent

- **Input:** search result + divergência
- **Output:** `proposed_value`, `target_dataset`, `rationale_pt`
- **Prompt:** `scripts/apgar_agents/prompts/generate.md`
- **Regra:** nunca score_max=30; sempre 5 componentes Apgar

---

## 3. Review Agent

- **Input:** proposal + evidência
- **Output:** `decision`: approve | reject | revise
- **Prompt:** `scripts/apgar_agents/prompts/review.md`
- **Bloqueia:** faixas erradas, uuid alterado, Grau A ausente

---

## 4. Validate Agent

- **Input:** proposal (ou estado atual)
- **Output:** pass/fail via `validate_apgar.py`
- **Prompt:** `scripts/apgar_agents/prompts/validate.md`
- **Determinístico:** sempre roda — não depende de LLM

---

## Implementação

| Arquivo | Papel |
|---------|-------|
| `scripts/apgar_agents/graph.py` | LangGraph 4 nós |
| `scripts/apgar_agents/validators.py` | Wrapper validate_apgar |
| `scripts/apgar_agents/run_field_pipeline.py` | CLI |

---

## Comandos

```bash
# Só validação (recomendado primeiro)
python scripts/apgar_agents/run_field_pipeline.py --validate-only

# Um campo
python scripts/apgar_agents/run_field_pipeline.py --field APGAR.scl.score_max --json

# Todos
python scripts/apgar_agents/run_field_pipeline.py --all --json
```

Runs salvos em `datasets/master-data/apgar/agent_runs/`.

---

## Segurança

- Agentes **não alteram datasets automaticamente** neste piloto — só propõem
- Aplicação manual ou script futuro `apply_apgar_field.py`
- Prompts versionados em `prompts/`
- Reutiliza padrão `scripts/review/` (LangGraph + DeepSeek)
