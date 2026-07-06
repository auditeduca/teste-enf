# NIFS-700-04: Vector Search

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-700-04                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o NIS realiza busca vetorial para recuperar conhecimento clinicamente relevante.

## 2. Vector Search Architecture

```
Query: "Paciente ICU com Braden 12, risco de úlcera"
    ↓ embed
Query Vector (768-dim)
    ↓ cosine similarity
Vector Store (ni_ai.rag_chunks)
    ↓ top-k=10
Results: NANDA 00047 (0.91), NIC 3540 (0.87), NOC 1101 (0.82)...
    ↓ rerank
Top 5 with clinical context
```

## 3. Vector Store

O NIS suporta múltiplos backends:

| Backend | Type | Use Case |
|---------|------|----------|
| pgvector | PostgreSQL extension | Default, integrated with ni_ai schema |
| Pinecone | Managed vector DB | Scale > 1M vectors |
| In-memory | JS Map | Development, < 10K vectors |

## 4. Search Types

| Type | Query | Method |
|------|-------|--------|
| Semantic | "risco de úlcera" | Cosine similarity on embeddings |
| Hybrid | "NANDA 00047" + semantic | Keyword + vector fusion |
| Graph-aware | "tratar NANDA 00047" | Vector + graph traversal |
| Temporal | "úlcera em paciente ICU 48h" | Vector + temporal filter |

## 5. Relevance Scoring

```
final_score = vector_similarity × 0.5
            + graph_proximity × 0.3
            + evidence_grade_weight × 0.2
```

| Evidence Grade | Weight |
|---------------|--------|
| A | 1.0 |
| B | 0.85 |
| C | 0.65 |
| D | 0.40 |

## 6. NKOS Reference

`datasets/ai/rag_chunks.json` contém a estrutura de chunks prontos para indexação vetorial. `datasets/ai/search_documents.json` tem documentos pré-indexados para busca.

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-700-03 | Embeddings (input for search) |
| NIFS-700-05 | Knowledge Retrieval (search + reasoning) |
| NIFS-500-11 | Reasoning Graph (graph-aware search) |
