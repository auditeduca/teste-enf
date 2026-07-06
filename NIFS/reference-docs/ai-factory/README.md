# Nursing AI Factory (NAIF)

Fábrica interna de IA para **construir, manter e evoluir** a plataforma. Agentes internos primeiro; quando maduros, viram produtos para milhões de profissionais.

## Pipeline

```
Ideia → Pesquisa → Conteúdo → Design → Código → Testes → Auditoria → Publicação → Monitoramento → Atualização
```

## 20 agentes (6 na Fase 1)

| Fase 1 ⭐⭐⭐⭐⭐ | Agente | Integração |
|----------------|--------|------------|
| ✅ | Clinical Content | CAF |
| ✅ | Developer | design system + nkp_api |
| ✅ | Code Reviewer | code_review_report |
| ✅ | SEO | schema + meta |
| ✅ | Visual Governance | VEIP |
| ✅ | Regulatory | NPIH |

Demais 14 agentes: registry com status `foundation` ou `planned`.

## Workflow — nova ferramenta

Exemplo: `"Nova calculadora MEWS"`

Fase 1 executa 6 agentes em sequência e persiste task + log.

```powershell
python scripts/ai_factory_agents/run_batch.py --status
python scripts/ai_factory_agents/run_batch.py --run "Nova calculadora MEWS"
python scripts/ai_factory_agents/run_batch.py --run "Nova calculadora APGAR" --full
```

## API

```
GET  /api/ai-factory/status
GET  /api/ai-factory/agents
GET  /api/ai-factory/workflows
POST /api/ai-factory/run          { "brief": "Nova calculadora MEWS", "phase1_only": true }
POST /api/ai-factory/evaluate     { "agent_id": "code_reviewer", "scores": {...} }
```

## Entidades (schema lógico)

`ai_agents`, `ai_tasks`, `ai_workflows`, `ai_prompts`, `ai_rules`, `ai_evaluations`, `ai_knowledge_sources`, `ai_versions`

Definidas em `database_schema.json`; tasks em `ai_tasks.json`.

## Resultado esperado

| Antes | Depois (Fase 1 + revisão humana) |
|-------|----------------------------------|
| ~2 semanas / ferramenta | ~1–2 dias |

## Visão futura

Mesma infraestrutura → NursingAI Clinical, Career Coach, Academic, Research, Wellbeing.

## Estrutura física

Ver também [`ai-platform/README.md`](../../ai-platform/README.md).
