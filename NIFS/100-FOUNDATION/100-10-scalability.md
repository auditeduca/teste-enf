# NIFS-100-10: Scalability

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-100-10                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir os requisitos de escalabilidade do NIS — suportar crescimento de dados, usuários e complexidade sem degradação.

## 2. Scale Targets

| Dimension | v5.0 Target | v7.0 Target |
|-----------|------------|------------|
| Patients | 10K | 1M |
| Episodes | 100K | 10M |
| Graph nodes | 20K | 100K |
| Graph edges | 30K | 500K |
| Concurrent sessions | 100 | 1K |
| Inference latency (P95) | < 5s | < 3s |
| Retrieval latency | < 200ms | < 100ms |

## 3. Scaling Strategies

| Layer | Strategy |
|-------|---------|
| Database | Read replicas + partitioning by patient_identifier |
| Vector search | ivfflat indexes, tune lists parameter |
| Graph | Neo4j cluster ou Cypher-on-PostgreSQL |
| Reasoning | Stateless sessions, horizontal scale |
| Council | Parallel agent execution |
| Cache | Redis para inference_cache e recommendation_cache |
| Queue | Message broker para assessment pipeline |

## 4. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-900-06 | Microservices |
| NIFS-900-11 | Caching |
| NIFS-1400-06 | Scaling (deployment) |
