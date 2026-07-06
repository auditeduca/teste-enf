# NIFS-500-04: Weights

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-500-04                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como os pesos das arestas do grafo clínico são calculados, ajustados e usados no raciocínio.

## 2. Weight Semantics

O peso (0-1) representa a **força da relação clínica** entre dois conceitos:

| Weight Range | Meaning | Example |
|-------------|---------|---------|
| 0.85-1.0 | Quase certo | NANDA 00047 → NIC 3540 (strong) |
| 0.60-0.84 | Forte | NANDA 00047 → NOC 1101 (moderate) |
| 0.30-0.59 | Moderado | NANDA 00046 → NIC 2250 (suggestive) |
| 0.10-0.29 | Fraco | Correlação minerada de baixa evidência |
| 0.01-0.09 | Hipótese | Sugerido por LLM, não validado |
| 0.0 | Irrelevante | Aresta existe mas sem força |

## 3. Weight Computation

```
effective_weight = base_weight
                  × evidence_multiplier(grade)
                  × population_fit(population_id)
                  × context_adjustment(world_state)
                  × learning_delta(reinforcement_signals)
```

| Factor | Formula |
|--------|---------|
| evidence_multiplier | A=1.0, B=0.85, C=0.65, D=0.40 |
| population_fit | 1.0 if matches, 0.7 if generic, 0.3 if mismatch |
| context_adjustment | ±0.2 based on ward state, acuity, resources |
| learning_delta | cumulative reward × 0.01 (capped at ±0.15) |

## 4. NNN Strength → Weight Mapping

| NNN Strength | Base Weight | Evidence |
|-------------|-------------|----------|
| strong | 0.85 | GRADE A/B |
| moderate | 0.65 | GRADE B/C |
| suggestive | 0.40 | GRADE C/D |

## 5. Weight Updates via Learning

```
ni_learning.reinforcement_signals
    → ni_learning.weight_updates
    → ni_rules.rule_weights (validation required)
    → ni_graph.edges.weight (after human approval)
```

Pesos nunca são atualizados automaticamente sem validação humana (`validation_status = 'validated'`).

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-500-03 | Properties (weight is an edge property) |
| NIFS-500-05 | Confidence (probabilistic complement) |
| NIFS-600-17 | Learning Loop (weight adjustment) |
