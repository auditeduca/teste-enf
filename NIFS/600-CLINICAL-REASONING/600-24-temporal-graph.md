# NIFS-600-24 — Temporal Graph Engine

**Seção:** 600 (Clinical Reasoning)
**Camada cognitiva:** 3 — Temporal Graph
**Status:** ✅ Implementado (v5.0)
**Arquivo de código:** `reference-clinical-engine/temporal/temporalGraph.js`
**Schema DDL:** `ni_temporal` (3 tabelas + clinical_events)

## 1. Propósito

Materializa a evolução temporal de estados clínicos como um grafo explícito. O particle filter do V8 já rastreava estados implicitamente — este módulo persiste snapshots de estado como nós e transições como arestas temporais, permitindo queries como "como evoluiu a volemia do paciente X nas últimas 6h?" e detecção de padrões de deterioração.

## 2. API

- `recordEvent(event)` — persiste evento clínico com snapshot de estado
- `buildSequence(patientId, type)` — agrupa eventos em sequência nomeada
- `detectCausalChain(patientId)` — infere relações causais entre eventos
- `queryEvolution(patientId, state, window)` — série temporal de um estado
- `detectDeterioration(patientId)` — alerta de declínio multi-variável

## 3. Tipos de Sequência

deterioration, recovery, crisis, stabilization, oscillation

## 4. Tipos de Causalidade

direct (intervenção → mudança de estado), contributing, temporal_correlation, confounded

## 5. Janelas Temporais

1h, 6h, 24h, 7d, 30d

## 6. Detecção de Deterioração

Monitora 4 variáveis de estado (volemia, contractilidade, oxigenacao, funcaoRenal) em janela de 6h. Se ≥2 variáveis declinam consistentemente nos últimos 3 snapshots, emite alerta com recomendação de escalada de avaliação.
