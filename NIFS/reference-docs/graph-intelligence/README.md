# Graph Intelligence — Validação e enriquecimento do grafo clínico

Programa para revisar **100% do grafo NKOS** contra 10 critérios de inteligência clínica, usando **Claude** para validação profunda e **Groq/Llama** para screening rápido.

## Critérios (10)

1. **Inteligência entre ferramentas** — cross-links, feeds, complements
2. **Grafo clínico** — NANDA-NIC-NOC + ferramentas + taxonomia
3. **Continuidade de raciocínio** — observação → decisão → intervenção → desfecho
4. **Camada de decisão** — árvores, protocolos, safety rules
5. **Dose e risco global** — calculadoras + scores agregados
6. **Memória clínica** — context-engine / MCTS
7. **Contexto do paciente** — persona, país, estado
8. **Conexão de dados entre ferramentas** — outputs como inputs
9. **Geração dinâmica de ferramentas** — lacunas → AI Factory
10. **Evolução por analytics** — pesos de arestas por uso real

Definição completa: [`datasets/master-data/graph-intelligence/validation_criteria.json`](../datasets/master-data/graph-intelligence/validation_criteria.json)

## Plano de revisão (6 fases)

| Fase | Nome | Provedor |
|------|------|----------|
| P1 | Inventário e baseline | Groq |
| P2 | Validação estrutural | Groq |
| P3 | Critérios clínicos | Claude |
| P4 | Conteúdo denso | Claude |
| P5 | Inteligência entre ferramentas | Claude |
| P6 | Evolução por analytics | Groq |

Plano: [`review_plan.json`](../datasets/master-data/graph-intelligence/review_plan.json)

## APIs

| Método | Rota | Função |
|--------|------|--------|
| GET | `/api/graph-intelligence/status` | Status + stats + LLM |
| GET | `/api/graph-intelligence/inventory` | Contagens, órfãos |
| GET | `/api/graph-intelligence/criteria` | 10 critérios |
| GET | `/api/graph-intelligence/review-plan` | Plano 6 fases |
| POST | `/api/graph-intelligence/validate` | Validação Claude |
| POST | `/api/graph-intelligence/fast-screen` | Screening Groq |
| POST | `/api/graph-intelligence/generate-content` | Conteúdo decisão clínica |
| POST | `/api/graph-intelligence/cross-tool` | Inteligência cruzada |

## Base de dados não ociosa

O agente Claude identifica:

- `idle_entities` — nós sem relações
- `underconnected_tools` — ferramentas isoladas
- `suggested_activations` — ações para conectar dados

Relatórios persistidos em `datasets/master-data/graph-intelligence/logs/`.

## Próximos passos (auditoria anterior)

- Design System + tokens unificados
- i18n funcional (geração por locale)
- Hub com taxonomia completa
- Apps quiz/simulado/trilha
- Analytics loop (P6) para evolução automática

Ver também: [llm-providers.md](../llm-providers.md)
