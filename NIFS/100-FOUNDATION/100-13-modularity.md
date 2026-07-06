# NIFS-100-13: Modularity

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-100-13                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a estrutura modular do NIS — cada módulo é independente, testável e substituível.

## 2. Module Map

```
┌─────────────────────────────────────────────────┐
│                  NIS MODULES                     │
├──────────┬──────────┬──────────┬────────────────┤
│ Clinical │ Cognitive│  infra   │   Interface    │
│          │          │          │                │
│ NANDA    │ Reasoning│ Database │ REST API       │
│ NIC      │ Memory   │ Graph    │ FHIR           │
│ NOC      │ Attention│ Cache    │ WebSocket      │
│ ISO      │ Bayes    │ Queue    │ Web UI         │
│ CID      │ Council  │ Search   │ Mobile         │
│ Calc     │ Planner  │ Auth     │                │
│ Protocol │ Twin     │ Logging  │                │
│ Safety   │ Learning │ Monitor  │                │
│ Mining   │ Explain  │          │                │
└──────────┴──────────┴──────────┴────────────────┘
```

## 3. Module Boundaries

| Module | Input | Output | Depends On |
|--------|-------|--------|-----------|
| Attention | Observations | Filtered observations | World Model |
| Reasoning | Filtered obs + context | Hypotheses + P(x) | Attention, Memory, Graph |
| Bayesian | Hypotheses + evidence | Posterior P(x) + IC | Reasoning, Evidence |
| Council | Positions | Consensus | Reasoning, Bayesian |
| Planner | Diagnosis + context | Plan graph | Council, Graph |
| Memory | Episode data | Similar episodes | Graph, Embeddings |
| Learning | Outcome + prediction | Weight update | Memory, Reasoning |
| Twin | State + plan | Simulated outcome | Planner, Prob |

## 4. Independence Rules

- Módulos se comunicam via **interfaces definidas** (JSON contracts)
- Módulos **não** acessam tabelas de outros módulos diretamente
- Módulos podem ser **substituídos** sem afetar outros (e.g., trocar LLM)
- Módulos são **testáveis** isoladamente (unit tests + mock inputs)

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-100-12 | Extensibility |
| NIFS-100-14 | Domain-Driven Design |
| NIFS-900-04 | Modules (platform) |
| NIFS-900-05 | Services (platform) |
