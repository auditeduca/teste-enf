# NIFS-500-11: Reasoning Graph

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-500-11                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o motor de raciocínio usa o grafo de conhecimento para navegar de observações a recomendações.

## 2. Reasoning as Graph Traversal

```
Input: Observações + Findings
    ↓
Step 1: Match to graph nodes (observação → node)
Step 2: Traverse edges (activates, implies) → hypotheses
Step 3: Rank hypotheses by weight × confidence
Step 4: Gather evidence (for/against) via edge traversal
Step 5: Bayesian update → posterior probabilities
Step 6: Select top hypothesis → traverse (treated_by) → interventions
Step 7: Traverse (improves) → expected outcomes
Step 8: Generate plan (contingency branches)
```

## 3. Traversal Patterns

| Pattern | Query | Purpose |
|---------|-------|---------|
| Forward | NANDA → treats → NIC | What interventions treat this? |
| Backward | NIC ← treated_by ← NANDA | What diagnoses does this treat? |
| Multi-hop | Calc → activates → NANDA → treated_by → NIC → improves → NOC | Full pathway |
| Best-path | Max(weight × confidence) path | Optimal recommendation |
| Contrastive | NANDA A vs NANDA B evidence paths | Differential diagnosis |

## 4. NIS Implementation

| Component | Table | Role |
|-----------|-------|------|
| Reasoning session | `ni_reasoning.sessions` | Container da traversal |
| Reasoning steps | `ni_reasoning.steps` | Cada hop do traversal |
| Reasoning trace | `ni_reasoning.trace` | Log legível do caminho |
| Reasoning scores | `ni_reasoning.scores` | Probabilidades por hipótese |
| Graph nodes | `ni_graph.nodes` | Nós visitados |
| Graph edges | `ni_graph.edges` | Arestas traversadas |

## 5. Example Traversal

```
Session start: Braden=12, ICU patient
    ↓
Step 1 (observation): Match CALC:BRADEN → node found
Step 2 (hypothesis): Traverse activates → NANDA:00047 (w=0.87)
Step 3 (hypothesis): Traverse activates → NANDA:00046 (w=0.23)
Step 4 (evidence_for): NANDA:00047 ← Braden ≤12 (w=0.91, GRADE B)
Step 5 (selection): NANDA:00047 P=0.91 (winner)
Step 6 (planning): NANDA:00047 → treats → NIC:3540 (w=0.85)
Step 7 (goal): NIC:3540 → improves → NOC:1101 (w=0.70)
Step 8 (contingency): If NOC unchanged → NIC:2250 (w=0.40)
```

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-02 | Reasoning Pipeline (full process) |
| NIFS-500-07 | Clinical Pathways (structured traversal) |
| NIFS-600-19 | Explainability (trace visualization) |
