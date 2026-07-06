# NIFS-900-06-microservices: 900 06 microservices

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-900-06-microservices                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a arquitetura de microserviços do NIS v5.0 — separação entre Clinical Engine, Knowledge Graph, API e Frontend.

## 2. Current State

Atual: monolito SSG + JS. Futuro: 4 microserviços (Clinical Engine, Knowledge Graph, API Gateway, Auth).

## 3. NIS v5.0 Design

Serviços: (1) Clinical Engine (V8 + Bayes + MCTS), (2) Knowledge Graph (Neo4j + Postgres), (3) API Gateway (REST + FHIR), (4) Auth (JWT + OAuth2). Comunicação via gRPC interno + REST externo.

## 4. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-900-03 | Architecture |
| NIFS-1500-01 | Roadmap |
