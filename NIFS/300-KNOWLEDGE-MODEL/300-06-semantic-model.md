# NIFS-300-06: Semantic Model

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-300-06                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o modelo semântico que dá significado aos dados clínicos do NIS — como conceitos se relacionam semanticamente, não apenas estruturalmente.

## 2. Semantic Layers

| Layer | Description | NIS Implementation |
|-------|-------------|-------------------|
| **Lexical** | Sinônimos, termos de busca | `ni_mining.judgment_tokens`, `SearchSynonym` (10K) |
| **Conceptual** | Conceitos e suas hierarquias | `ni.concepts`, `ni_graph.nodes` |
| **Relational** | Como conceitos se relacionam | `ni_graph.edges` (activates, treats, implies, contradicts) |
| **Assertional** | Instâncias específicas (caso X tem NANDA Y) | `ni.care_plans`, `ni_memory.episodes` |
| **Probabilistic** | P(concept_B \| concept_A) | `ni_prob.probability_models`, `ni_prob.bayesian_links` |

## 3. Semantic Relations in NIS Graph

| Relation | Meaning | Example |
|----------|---------|---------|
| `activates` | Calculator triggers hypothesis | BRADEN → NANDA 00047 |
| `treats` | Intervention addresses diagnosis | NIC 3540 → NANDA 00047 |
| `assesses` | Tool measures outcome | BRADEN → NOC 1101 |
| `implies` | If A then likely B | NANDA 00047 → NANDA 00046 |
| `contradicts` | A and B are mutually exclusive | NANDA risk vs NANDA actual |
| `part_of` | Hierarchical containment | NIC activity → NIC intervention |
| `maps_to` | Cross-terminology mapping | NANDA 00047 → SNOMED 420324007 |
| `precedes` | Temporal ordering | Assessment → Diagnosis → Planning |
| `co_occurs` | Frequently together | NANDA 00047 + NANDA 00004 |
| `causes` | Causal link | Immobility → Skin breakdown |

## 4. Semantic Inference

```
Observation: Braden = 12 (high risk)
    ↓ Semantic relation: activates
Hypothesis: NANDA 00047 (Risk of Impaired Skin Integrity)
    ↓ Semantic relation: treats
Intervention: NIC 3540 (Pressure Management)
    ↓ Semantic relation: assesses
Outcome: NOC 1101 (Tissue Integrity) — target: 4/5
    ↓ Probabilistic: P(achieve | NIC 3540) = 0.82
```

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-300-05 | Clinical Ontology |
| NIFS-500-02 | Edge Types (relation semantics) |
| NIFS-600-02 | Reasoning Pipeline (uses semantic inference) |
