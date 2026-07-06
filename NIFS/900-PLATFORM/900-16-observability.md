# NIFS-900-16-observability: 900 16 observability

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-900-16-observability                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir observabilidade end-to-end do NIS — traces, metrics, logs centralizados.

## 2. Current State

Atual: sem observabilidade. Futuro: OpenTelemetry + Jaeger + centralized logs.

## 3. NIS v5.0 Design

Stack: OpenTelemetry (instrumentação) + Jaeger (distributed tracing) + Prometheus (metrics) + Loki (logs). Correlation ID em cada request → trace end-to-end.

## 4. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-900-03 | Architecture |
| NIFS-1500-01 | Roadmap |
