# NIFS-900-10-queues: 900 10 queues

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-900-10-queues                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o sistema de filas do NIS para processamento assíncrono — bulk export, reasoning, indexing.

## 2. Current State

Atual: sem filas. Futuro: Redis/RabbitMQ para bulk export, reasoning async, vector indexing.

## 3. NIS v5.0 Design

Filas: (1) reasoning-queue — inferência assíncrona, (2) export-queue — bulk data export, (3) indexing-queue — vector indexing, (4) notification-queue — alertas clínicos.

## 4. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-900-03 | Architecture |
| NIFS-1500-01 | Roadmap |
