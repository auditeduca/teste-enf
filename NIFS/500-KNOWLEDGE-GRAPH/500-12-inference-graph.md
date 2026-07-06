# NIFS-500-12: Inference Graph

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-500-12                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o NIS deriva novo conhecimento a partir do grafo existente — inferência transitiva, composicional e abdutiva.

## 2. Inference Types

### 2.1 Transitive Inference
```
Known: CALC:BRADEN → activates → NANDA:00047
Known: NANDA:00047 → treated_by → NIC:3540
Inferred: CALC:BRADEN → ultimately_suggests → NIC:3540
```

### 2.2 Compositional Inference
```
Known: NANDA:00047 has ISO composition: focus=skin_integrity + judgment=risk
Known: NIC:3540 has ISO action: focus=skin_integrity + action=managing
Inferred: NANDA:00047 and NIC:3540 share focus → treatment alignment confirmed
```

### 2.3 Abductive Inference
```
Known: NOC:1101 deteriorated
Known: NANDA:00047 → improves → NOC:1101
Inferred: NANDA:00047 likely active (abductive: effect → cause)
    → Verify with assessment
```

### 2.4 Analogical Inference
```
Known: NANDA:00047 (skin integrity) in ICU population → NIC:3540 (w=0.85)
Inferred: NANDA:00047 in LTC population → NIC:3540 (w=0.65, lower confidence)
    → Requires validation before clinical use
```

## 3. NIS Implementation

| Component | Role |
|-----------|------|
| `ni_graph.edges` | Arestas explícitas (known) |
| `ni_mining.graph_drafts` | Arestas inferidas (pending validation) |
| `ni_epist.verification_log` | Validação epistêmica V1-V4 |
| `ni_council.arbitration_decisions` | Resolução de conflitos de inferência |
| `ni_prob.bayesian_links` | Inferência probabilística |

## 4. Inference Pipeline

```
1. Existing graph edges (validated)
2. Apply inference rules (transitive, compositional, abductive)
3. Generate draft edges → ni_mining.graph_drafts (status=pending)
4. Evidence mining finds supporting evidence
5. Council review (Evidence Agent + NANDA Agent vote)
6. Human review → approve/reject
7. Approved → ni_graph.edges (new knowledge)
```

## 5. Inference Rules (Epistemic)

| Rule | Type | Check |
|------|------|-------|
| Transitivity | V1_ontology | If A→B and B→C, infer A→C |
| Symmetry check | V1_ontology | treats ≠ treated_by (directional) |
| Composition | V3_iso_composition | Focus alignment validates relation |
| Scope | V4_scope | Inferred edge must be in NIS scope |
| Conflict | V2_code_validity | Contradictory edges → arbitration |

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-500-11 | Reasoning Graph (uses inferences) |
| NIFS-200-05 | Clinical Reasoning (inference process) |
| NIFS-600-18 | Consensus Engine (inference validation) |
