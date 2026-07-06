# Master Data APGAR — piloto de validação

> **Escopo exclusivo:** ferramenta **Apgar** como referência ouro antes de replicar para Braden, Morse, etc.  
> Status: **`REVIEW_READY`** · Completion piloto: **100%** (ver `modules.json`)

---

## Objetivo

Construir **do zero ao 100%** todos os módulos da ferramenta APGAR com:

1. Documentação escrita por campo (why, fonte, exemplo, validação)
2. Fonte canônica única (`canonical.json`)
3. Validador determinístico (`validate_apgar.py`)
4. Pipeline de agentes **LangGraph + DeepSeek**: buscar → gerar → revisar → validar

---

## Artefatos

| Arquivo | Função |
|---------|--------|
| [`datasets/master-data/apgar/canonical.json`](../../datasets/master-data/apgar/canonical.json) | Verdade clínica APGAR (Grau A) |
| [`datasets/master-data/apgar/field_documentation.json`](../../datasets/master-data/apgar/field_documentation.json) | Catálogo de campos + agent_roles |
| [`datasets/master-data/apgar/modules.json`](../../datasets/master-data/apgar/modules.json) | 10 módulos 0→100% |
| [`datasets/ontology/apgar_edges.json`](../../datasets/ontology/apgar_edges.json) | Grafo NNN |
| [`scripts/apgar/validate_apgar.py`](../../scripts/apgar/validate_apgar.py) | Validador CI piloto |
| [`scripts/apgar_agents/run_field_pipeline.py`](../../scripts/apgar_agents/run_field_pipeline.py) | Pipeline agentes |

---

## Documentação

| Doc | Conteúdo |
|-----|----------|
| [00-fases-0-100.md](00-fases-0-100.md) | Fases e critérios de conclusão |
| [01-modulos-e-campos.md](01-modulos-e-campos.md) | Matriz módulo × campo |
| [02-fontes-oficiais.md](02-fontes-oficiais.md) | Apgar 1953, ACOG, WHO |
| [03-pipeline-agentes.md](03-pipeline-agentes.md) | Search / Generate / Review / Validate |
| [05-agentes-micro-fases.md](05-agentes-micro-fases.md) | Agentes M1–M11 + tradução |

Relacionado: [doc 14](../14-master-data-sequencia-revisao.md) · [doc 15](../15-master-data-grafo-inferencia.md) · [clinical-engine/11](../clinical-engine/11-apgar-mcts-user-context.md)

---

## Comandos

```bash
# Validacao
python scripts/apgar/validate_apgar.py --json

# Agentes LangGraph + DeepSeek (requer DEEPSEEK_API_KEY)
python scripts/apgar_agents/run_field_pipeline.py --validate-only
python scripts/apgar_agents/run_field_pipeline.py --all --no-llm --json
```

Ver [05-agentes-micro-fases.md](05-agentes-micro-fases.md).

---

## Gate de aceite (100% piloto APGAR)

- [x] `validate_apgar.py` → **0 errors**
- [x] `score_max=10`, faixas 0-3 / 4-6 / 7-10
- [x] UI com 5 componentes Apgar
- [x] Evidência Grau A com citation + DOI
- [x] `i18n.json` — **30 idiomas**
- [x] Agentes M1–M11 PASS
- [ ] Aprovação humana doc 14 → migrar produção
