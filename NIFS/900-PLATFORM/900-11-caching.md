# NIFS-900-11-caching: 900 11 caching

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-900-11-caching                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a estratégia de cache do NIS — CDN para estáticos, Redis para API, cache de browser.

## 2. Current State

Atual: cache de browser (localStorage para SAE/SBAR/CV). Futuro: CDN + Redis + cache de embeddings.

## 3. NIS v5.0 Design

Camadas: (1) CDN (Cloudflare) para HTML/CSS/JS, (2) Redis para API responses + terminology lookups, (3) Browser localStorage para preferências, (4) Embedding cache para vector search.

## 4. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-900-03 | Architecture |
| NIFS-1500-01 | Roadmap |
