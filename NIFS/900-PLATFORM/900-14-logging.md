# NIFS-900-14-logging: 900 14 logging

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-900-14-logging                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a estratégia de logging do NIS — access logs, clinical reasoning logs, error logs.

## 2. Current State

Atual: sem logging estruturado. Futuro: structured logging com correlation IDs.

## 3. NIS v5.0 Design

Níveis: (1) Access logs — IP, rota, tempo, (2) Clinical logs — reasoning trace, hipóteses, confidence, (3) Error logs — stack trace + contexto, (4) Audit logs — quem acessou o quê.

## 4. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-900-03 | Architecture |
| NIFS-1500-01 | Roadmap |
