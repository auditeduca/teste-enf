# NIFS-900-07-monolith: 900 07 monolith

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-900-07-monolith                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Documentar a arquitetura monolítica atual do website (SSG + JS) e quando migrar para microserviços.

## 2. Current State

Atual: website é um monolito estático (HTML+CSS+JS). NKOS v4.4 tem backend Firebase. NIS v5.0 será híbrido.

## 3. NIS v5.0 Design

O monolito SSG permanece para conteúdo estático (SEO). O NIS adiciona camada de microserviços para reasoning dinâmico. Migração gradual, não big-bang.

## 4. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-900-03 | Architecture |
| NIFS-1500-01 | Roadmap |
