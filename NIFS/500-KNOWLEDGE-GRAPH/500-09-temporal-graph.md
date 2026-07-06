# NIFS-500-09: Temporal Graph

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-500-09                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a camada temporal do grafo de conhecimento — como eventos clínicos formam sequências e causalidades ao longo do tempo.

## 2. Static vs Temporal Graph

| Aspect | Static Graph | Temporal Graph |
|--------|-------------|----------------|
| Nodes | Conceitos clínicos (NANDA, NIC, NOC) | Eventos clínicos (observações, ações) |
| Edges | Relações semânticas (treats, assesses) | Sequência temporal + causalidade |
| Time | Imutável | Sempre presente |
| Queries | "O que está relacionado?" | "O que aconteceu depois?" |

## 3. Temporal Event Chain

```
08:00  Braden=14 (event)
  → edge: precedes (delta=2h)
10:00  Braden=12 (event)
  → edge: triggers (delta=0)
10:00  NANDA 00047 activated (event)
  → edge: causes (delta=0)
10:00  NIC 3540 initiated (event)
  → edge: precedes (delta=3h)
13:00  Braden=16 (event)
  → edge: results_from (delta=3h)
13:00  NOC 1101 improved (event)
```

## 4. NIS Implementation

| Table | Role |
|-------|------|
| `ni_temporal.clinical_events` | Eventos individuais com timestamp |
| `ni_temporal.event_sequences` | Agrupamento de eventos em sequência |
| `ni_temporal.event_sequence_items` | Ordenação dentro de sequência |
| `ni_temporal.causal_chains` | Links causais entre eventos |
| `ni_temporal.state_transitions` | Mudanças de estado do paciente |
| `ni_temporal.time_series` | Métricas agregadas ao longo do tempo |

## 5. Causal Inference

```
Cause event: NIC 3540 initiated at 10:00
Effect event: Braden improved at 13:00
Causality type: direct (confidence=0.82, evidence_grade=B)
    → Reinforcement signal: +0.8
    → Weight update: edge NIC:3540 → NOC:1101 += 0.02
```

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-300-10 | Events (conceptual) |
| NIFS-600-14 | Simulation (temporal projection) |
| NIFS-600-16 | Clinical Memory (episodic recall) |
