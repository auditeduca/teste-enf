# NIFS-300-03: Relationship Catalog

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-300-03                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Catalogar todas as relações (FK → PK) entre entidades do NIS. No Excel v4.2 existem 152+ relações; no NIFS v5.0 com as 10 camadas cognitivas, este número cresce para ~280+.

## 2. Relationship Types

| Type | Pattern | Example |
|------|---------|---------|
| **N:1** | Many records → one parent | care_plans → cases |
| **N:N** | Junction table | calculator_nnn_cross (calc ↔ NANDA ↔ NIC ↔ NOC) |
| **Self-ref** | Entity → same entity | content_taxonomy.parent_term_id → content_taxonomy |
| **Graph edge** | node → node via edges | ni_graph.edges (source_node_id → target_node_id) |
| **Cognitive link** | session → step → trace | ni_reasoning cascade |

## 3. Key Relationship Clusters

### 3.1 Core Clinical Chain
```
cases → care_plans → nanda_diagnoses
                    → nic_interventions
                    → noc_outcomes
```

### 3.2 Cognitive Chain
```
reasoning.sessions → reasoning.steps → reasoning.scores
                   → reasoning.trace
                   → council.sessions → council.votes
                   → explain.explanations
```

### 3.3 Knowledge Graph
```
graph.nodes → graph.edges (source → target)
            → graph.edge_types
            → prob.bayesian_links
            → mining.freshness_index
```

### 3.4 Safety Chain
```
safety_goals → safety_goal_medication_cross → medications_anvisa
nine_rights_medication → medications_anvisa (via 9 Rights check)
```

## 4. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-300-02 | Entity Catalog |
| NIFS-400-06 | Constraints (FK enforcement) |
