# NIFS-700-05: Knowledge Retrieval

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-700-05                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o Nurse-PaLM recupera conhecimento estruturado (grafo) e não-estruturado (RAG) para alimentar o raciocínio clínico.

## 2. Retrieval Pipeline

```
Clinical Context (patient state + observations)
    ↓
1. Structured Retrieval (graph)
   → Query ni_graph.nodes/edges for related NANDA/NIC/NOC
   → Query ni_clinical for patient-specific data
    ↓
2. Semantic Retrieval (RAG)
   → Vector search on ni_ai.rag_chunks
   → Retrieve guidelines, evidence, protocols
    ↓
3. Episodic Retrieval (memory)
   → Query ni_memory.episodes for similar past cases
    ↓
4. Fusion + Ranking
   → Combine all sources, rank by relevance + evidence
    ↓
Reasoning Engine (ni_reasoning)
```

## 3. Retrieval Sources

| Source | Type | Table | Content |
|--------|------|-------|---------|
| Knowledge Graph | Structured | `ni_graph.*` | NANDA, NIC, NOC, relations |
| Clinical Data | Structured | `ni_clinical.*` | Diagnoses, interventions, outcomes |
| RAG Chunks | Unstructured | `ni_ai.rag_chunks` | Guidelines, articles, evidence |
| Episodic Memory | Case-based | `ni_memory.episodes` | Past clinical episodes |
| Master Data | Reference | `ni_ref.*` | Terminologies, taxonomies |
| Legislation | Regulatory | `ni_legis.*` | Legal provisions, notifications |

## 4. Clinical Context Vector

O Clinical Engine V8 já implementa um vetor de estado fisiológico:

```javascript
// From generativeModel.js — 8 latent states
state = {
  volemia: 0.45,           // volume status
  contractilidade: 0.72,   // cardiac contractility
  resistenciaVascular: 0.38, // vascular resistance
  oxigenacao: 0.81,        // oxygenation
  ventilacao: 0.75,        // ventilation
  funcaoRenal: 0.60,       // renal function
  inflamacao: 0.22,        // inflammation
  eletrolitos: 0.88        // electrolytes
}
```

Este vetor serve como query estruturada para retrieval contextual.

## 5. Ranking Formula

```
relevance = semantic_similarity × 0.35
          + graph_proximity × 0.25
          + evidence_grade × 0.20
          + population_match × 0.10
          + temporal_freshness × 0.10
```

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-700-02 | RAG (unstructured retrieval) |
| NIFS-700-04 | Vector Search (semantic retrieval) |
| NIFS-600-02 | Reasoning Pipeline (consumer) |
| NIFS-600-16 | Clinical Memory (episodic retrieval) |
