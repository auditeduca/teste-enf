# NIFS-100-17: Knowledge-Driven Design

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-100-17                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o princípio fundamental do NIS: conhecimento é a matéria-prima de tudo. Toda decisão é guiada pelo grafo de conhecimento, não por código hard-coded.

## 2. The Knowledge Principle

> "O código é commodity. O conhecimento é o diferencial."

```
Knowledge Graph (nodes + edges + weights + evidence)
    ↓
Reasoning Engine (traverses graph)
    ↓
Recommendation (grounded in graph)
    ↓
Explanation (cites graph elements)
```

Se não está no grafo, o sistema **não sabe**. Não há conhecimento implícito no código.

## 3. Knowledge Representation Layers

| Layer | What | Schema |
|-------|------|--------|
| Taxonomic | NANDA domains, NIC classes | `ni`, `ni_cog` |
| Ontological | ISO axes, metaparadigm | `ni_iso`, `ni_cog` |
| Relational | Graph edges (treats, implies, etc.) | `ni_graph` |
| Probabilistic | P(x\|y), priors, posteriors | `ni_prob` |
| Evidential | GRADE evidence per claim | `ni_mining` |
| Epistemic | Validation rules (V1-V4) | `ni_epist` |
| Temporal | Event sequences, trajectories | `ni_temporal` |
| Experiential | Episodic memory | `ni_memory` |

## 4. Knowledge vs. Code

| Aspect | Knowledge | Code |
|--------|-----------|------|
| Changes | Frequent (new evidence, new NANDA) | Rare |
| Source | Clinical experts, literature | Engineers |
| Validation | Clinical governance | Unit tests |
| Storage | Graph + tables | Source files |
| Versioning | `ni_knowledge.versions` | Git |

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-500-01 | Node Types (knowledge structure) |
| NIFS-500-02 | Edge Types (knowledge relations) |
| NIFS-300-05 | Clinical Ontology (formal model) |
| NIFS-1100-01 | Knowledge Governance |
