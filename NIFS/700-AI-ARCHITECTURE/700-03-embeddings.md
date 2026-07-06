# NIFS-700-03: Embeddings

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-700-03                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como conceitos clínicos do NIS são convertidos em embeddings vetoriais para busca semântica e RAG.

## 2. Embedding Strategy

O NIS usa uma estratégia multi-modal de embeddings:

| Content Type | Embedding Model | Dimensions | Purpose |
|-------------|-----------------|------------|---------|
| NANDA diagnoses | text-embedding-004 | 768 | Semantic similarity between diagnoses |
| NIC interventions | text-embedding-004 | 768 | Intervention matching |
| Clinical evidence | text-embedding-004 | 768 | Evidence retrieval |
| Patient context | Custom clinical encoder | 512 | Patient state representation |
| Clinical pathways | Graph embedding (Node2Vec) | 256 | Pathway similarity |

## 3. Clinical Text Embedding

```python
# Text to embed: NANDA diagnosis with full context
text = """
NANDA 00047: Risk of Impaired Skin Integrity
Domain 11: Safety/Protection
Class 2: Physical Injury
Definition: Vulnerable to alteration in skin integrity
Risk factors: Immobility, Braden ≤12, ICU stay
"""

embedding = embed(text)  # → 768-dim vector
```

## 4. NKOS Data for Embeddings

| Dataset | Records | Embedding Source |
|---------|---------|-----------------|
| `nursing_diagnoses.json` | 244 NANDA | definition + defining_characteristics |
| `nursing_interventions.json` | 575 NIC | definition + activities |
| `nnn_linkages.json` | 1500 linkages | NANDA→NIC→NOC context |
| `clinical_concepts.json` | 2000 concepts | taxonomy + SNOMED CT |
| `clinical_guidelines.json` | 200 guidelines | title + recommendation |
| `evidence.json` | 27 GRADE | claim + study_type |

## 5. NIS Implementation

| Table | Role |
|-------|------|
| `ni_ai.rag_chunks` | Text chunks with embedding vectors |
| `ni_ai.knowledge_nodes` | Graph nodes with embeddings |
| `ni_ai.embeddings_metadata` | Model version, dimensions, timestamp |

## 6. Reference Implementation

O CALENF-NKD já tem `datasets/ai/rag_chunks.json` e `datasets/ai/knowledge_nodes.json` — a infraestrutura de embeddings já está esboçada no NKOS v4.4.

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-700-02 | RAG (embeddings feed RAG) |
| NIFS-700-04 | Vector Search (retrieval) |
| NIFS-700-05 | Knowledge Retrieval |
