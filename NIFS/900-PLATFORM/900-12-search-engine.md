# NIFS-900-12-search-engine: 900 12 search engine

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-900-12-search-engine                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o motor de busca do NIS — busca textual + busca semântica (vector).

## 2. Current State

Atual: busca via redirect (busca.html?q=). Futuro: Elasticsearch + vector search (embeddings).

## 3. NIS v5.0 Design

Busca híbrida: (1) Textual — Elasticsearch sobre tool names/descriptions, (2) Semântica — vector search sobre NANDA/NIC/NOC definitions, (3) Graph — traversals no knowledge graph.

## 4. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-900-03 | Architecture |
| NIFS-1500-01 | Roadmap |
