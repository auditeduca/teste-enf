# NIFS-400-07: Indexes

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-400-07                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir estratégia de indexação para performance de consulta no NIS.

## 2. Index Strategy

| Index Type | Use Case | Examples |
|-----------|----------|---------|
| **B-tree** | Default, equality + range | All PKs, FKs, codes |
| **GIN** | JSONB, arrays | `input_data`, `defining_characteristics` |
| **GiST** | Range, geometric | temporal overlap queries |
| **Partial** | Conditional | `WHERE status = 'active'` |
| **Composite** | Multi-column | `(session_id, step_order)` |

## 3. Critical Indexes

| Table | Index | Reason |
|-------|-------|--------|
| `ni_graph.edges` | (source_node_id, target_node_id) | Graph traversal |
| `ni_temporal.observations` | (patient_identifier, observed_at DESC) | Timeline queries |
| `ni_reasoning.steps` | (session_id, step_order) | Pipeline replay |
| `ni_memory.episodes` | (patient_identifier, started_at DESC) | Memory retrieval |
| `ni_attention.attention_signals` | (reasoning_session_id, attention_score DESC) | Top-N attention |
| `ni_prob.bayesian_links` | (model_id, source_node_id) | Belief propagation |

## 4. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-400-03 | Tables |
| NIFS-100-10 | Scalability |
