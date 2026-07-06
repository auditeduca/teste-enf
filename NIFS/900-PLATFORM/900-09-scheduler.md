# NIFS-900-09-scheduler: 900 09 scheduler

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-900-09-scheduler                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o agendador de tarefas do NIS — CI/CD, sync ANVISA, regeração de páginas.

## 2. Current State

Atual: sem scheduler ativo. NKOS tem CI (daily-platform-loop.yml, monthly-anvisa-sync.yml).

## 3. NIS v5.0 Design

Jobs: (1) daily-platform-loop — regeração de páginas + audit, (2) monthly-anvisa-sync — sync ANVISA, (3) weekly-pubmed — fetch evidência, (4) nightly-vector-index — reindex embeddings.

## 4. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-900-03 | Architecture |
| NIFS-1500-01 | Roadmap |
