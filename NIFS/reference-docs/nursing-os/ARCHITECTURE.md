# Nursing OS Global — Arquitetura

Sistema operacional digital da carreira de enfermagem. Combina o melhor de cada categoria em um ecossistema conectado por **Context Engine** e **Knowledge Graph**.

## Visão

```
                    Usuário + Perfil + País
                              │
                    Context Engine (CTX)
                              │
     ┌────────────┬───────────┼───────────┬────────────┐
     ▼            ▼           ▼           ▼            ▼
  Clínico    Educação    Carreira    Pesquisa      Visual
     │            │           │           │            │
     └────────────┴───────────┴───────────┴────────────┘
                              │
                    Knowledge Graph (NANDA-NIC-NOC)
                              │
                    Nursing AI Agents (NAAP)
```

## Domínios implementados

| Domínio | Código | Status | Path |
|---------|--------|--------|------|
| Visual Experience Intelligence | VEIP | MVP | `visual-intelligence/` |
| Clinical Article Factory | CAF | MVP | `clinical-articles/` |
| Nursing AI Agent Platform | NAAP | Foundation | `nursing-ai-agents/` |
| Academic Knowledge Network | NAKN | Foundation | `academic-knowledge/` |
| Context Engine | CTX | Foundation | `context-engine/` |
| Global Expansion | GEX | Partial | `global-expansion/` |

## OG Premium (VEIP)

A imagem hero institucional **não substitui** OG de compartilhamento.

- Hero: 9,5/10 · OG WhatsApp alvo: 10/10
- Spec: `visual-intelligence/og_spec_premium.json`
- Template sustentabilidade: 1200×630, 60% texto, 4 selos, sem botões

```bash
python scripts/visual_intelligence_agents/run_batch.py --generate sustentabilidade
python scripts/nursing_os/run_bootstrap.py --bootstrap
```

## APIs

| Rota | Função |
|------|--------|
| `GET /api/nursing-os/status` | Status agregado |
| `POST /api/nursing-os/context/resolve` | Context DNA → UX + Visual + IA |
| `GET /api/nursing-ai-agents/status` | Registry de agentes |
| `POST /api/nursing-ai-agents/route` | Router de intenção |
| `/api/visual-intelligence/*` | OG + VGA |
| `/api/clinical-articles/*` | Artigos problema/solução |

## Fases de implementação

Ver `datasets/master-data/nursing-os/phases.json`

1. **Fundação** (em progresso) — Master data, VEIP, artigos, context engine
2. **Valor imediato** — Calculadoras, grafo clínico, dashboard
3. **Acadêmico** — NAKN TCC, quality agent
4. **Carreira** — Marketplace, passaporte profissional
5. **Comunidade** — Fórum, mentoria
6. **IA avançada** — Simulação, digital twin

## Plataforma

Dashboard: `/nursing-os`

## Próximos passos técnicos

1. OG locales (9 idiomas)
2. UI Clinical Command Center (grafo + dashboard)
3. NAKN upload + Academic Quality Agent
4. Agent orchestrator LangGraph unificado
5. Fotos localizadas (Human Imagery System)
