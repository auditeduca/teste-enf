# NIFS-700-06: Memory

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-700-06                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a arquitetura de memória do Nurse-PaLM — como o sistema acumula, organiza e recupera experiências clínicas.

## 2. Memory Types

| Type | Duration | Content | Table |
|------|----------|---------|-------|
| Working | Seconds-minutes | Current reasoning session | `ni_reasoning.sessions` |
| Episodic | Days-months | Past clinical cases | `ni_memory.episodes` |
| Semantic | Permanent | General clinical knowledge | `ni_graph.nodes/edges` |
| Procedural | Permanent | How-to sequences | `ni_planner.plans` |
| Learning | Cumulative | Feedback signals | `ni_learning.reinforcement_signals` |

## 3. Episodic Memory Architecture

```
Clinical Episode (assessment → diagnosis → intervention → outcome)
    ↓
ni_memory.episodes (stored with embedding + structured data)
    ↓
Similar case retrieval via vector search + graph matching
    ↓
Applied to current reasoning as analogical evidence
```

### Episode Structure
```
{
  patient_context: { age, population, setting, comorbidities },
  observations: [ { type, value, timestamp } ],
  hypotheses: [ { nanda_code, probability, confidence } ],
  interventions: [ { nic_code, timing, outcome } ],
  outcomes: [ { noc_code, baseline, final, delta } ],
  resolution: improved | deteriorated | unchanged,
  embedding: [768-dim vector],
  tags: ["ICU", "braden", "pressure_ulcer"]
}
```

## 4. Clinical Engine V8 Reference

O `generativeModel.js` implementa um **state vector** que serve como memória de curto prazo — o particle filter mantém a distribuição de crença sobre o estado fisiológico ao longo do tempo:

```
t=0: belief = prior
t=1: belief = update(prior, observation_1)
t=2: belief = update(belief, observation_2)
...
```

Esta é a memória de trabalho (working memory) do motor.

## 5. Memory Consolidation

```
Working Memory (session)
    ↓ session ends
Episodic Memory (episode stored)
    ↓ multiple similar episodes
Pattern Extraction (semantic memory update)
    → ni_graph.edges weight adjusted
    → ni_prob.prior_beliefs updated
```

## 6. Forgetting Curve

Episódios não acessados decaem em relevância:

| Age | Access Factor |
|-----|---------------|
| < 7 days | 1.0 |
| 7-30 days | 0.8 |
| 30-90 days | 0.5 |
| > 90 days | 0.2 |

Episódios com outcome confirmado mantêm relevância maior por mais tempo.

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-16 | Clinical Memory (cognitive layer) |
| NIFS-600-17 | Learning Loop (memory → learning) |
| NIFS-700-05 | Knowledge Retrieval (uses memory) |
