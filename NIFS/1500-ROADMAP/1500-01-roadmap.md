# NIFS-1500-01: Roadmap

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-1500-01                        |
| Status        | Validated                          |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Roadmap técnico do NIS — do website estático atual ao Nurse-PaLM completo.

## 2. Phases

### Fase 0 — Atual (Concluído)
- ✅ Website com 97 calculadoras funcionais
- ✅ SSG Python (generate_tool_page.py)
- ✅ calc-engine.js (motor interativo)
- ✅ 30 idiomas (UI traduzida)
- ✅ 196 países mapeados
- ✅ SAE/SBAR/CV wizards
- ✅ NIFS 152/261 documentos (58%)
- ✅ NKOS v4.4 extraído (Clinical Engine V8)
- ✅ DDL v5.0 (33+ tabelas)

### Fase 1 — NIFS Completion (Q3 2026)
- [ ] Completar 109 docs restantes (000, 900, 1000, 1100, 1200, 1300, 1400, 1500, Appendix)
- [ ] Validar consistência spec ↔ código
- [ ] Gerar DDL consolidado v5.1
- [ ] Gerar OpenAPI spec
- [ ] CI/CD ativo

### Fase 2 — Data Migration (Q4 2026)
- [ ] Migrar 97 tool JSONs → NIS database (ni_clinical)
- [ ] Migrar 244 NANDA → ni_clinical.nursing_diagnoses
- [ ] Migrar 575 NIC → ni_clinical.nursing_interventions
- [ ] Migrar 550 NOC → ni_clinical.nursing_outcomes
- [ ] Migrar 1500 NNN linkages → ni_graph.edges
- [ ] Migrar 54 notificações compulsórias → ni_legis
- [ ] Migrar 200 guidelines → ni_clinical.guidelines
- [ ] Migrar 196 países → ni_ref.countries

### Fase 3 — API Layer (Q1 2027)
- [ ] REST API (NIFS-800-05)
- [ ] FHIR endpoints (NIFS-800-01)
- [ ] Terminology service (NIFS-800-11)
- [ ] Code mapping (NIFS-800-12)
- [ ] Vector embeddings para NANDA/NIC/NOC

### Fase 4 — Clinical Engine Integration (Q2 2027)
- [ ] Portar Clinical Engine V8 para NIS runtime
- [ ] particleFilter.js → API endpoint
- [ ] bayesianDiagnosis.js → API endpoint
- [ ] mctsClinical.js → API endpoint
- [ ] mpcController.js → API endpoint
- [ ] Substituir NANDA hardcoded do sae-engine.js por V8
- [ ] tool.schema.json v2.0 com reasoning_trace

### Fase 5 — Multi-Agent Council (Q3 2027)
- [ ] NANDA Agent (diagnóstico bayesiano)
- [ ] Safety Agent (IPSG + contraindicações)
- [ ] Evidence Agent (GRADE + retrieval)
- [ ] Consensus engine (NIFS-600-18)
- [ ] Reasoning trace visível na UI

### Fase 6 — Nurse-PaLM Complete (Q4 2027)
- [ ] Memória episódica (RAG de casos)
- [ ] World model generativo (8 estados latentes)
- [ ] Grafo temporal de evolução
- [ ] Clinical attention (priorização)
- [ ] Feedback learning loop
- [ ] Simulation engine (MCTS completo)

### Fase 7 — Global Content (2028)
- [ ] Conteúdo clínico traduzido (5+ idiomas)
- [ ] Protocolos locais por país
- [ ] Legislação por jurisdição
- [ ] Diretrizes nacionais integradas

## 3. Milestone Summary

| Fase | Trimestre | Foco | Entregável |
|------|-----------|------|-----------|
| 0 | Concluído | Website | 97 calc + 30 idiomas |
| 1 | Q3 2026 | NIFS | 261 docs completos |
| 2 | Q4 2026 | Dados | NIS database populada |
| 3 | Q1 2027 | API | REST + FHIR + terminology |
| 4 | Q2 2027 | Engine | V8 integrado |
| 5 | Q3 2027 | Council | Multi-agent |
| 6 | Q4 2027 | Nurse-PaLM | 10 camadas cognitivas |
| 7 | 2028 | Global | Conteúdo multilíngue |

## 4. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-000-01 | Vision |
| NIFS-700-01 | AI Architecture |
| NIFS-600-02 | Reasoning Pipeline |
