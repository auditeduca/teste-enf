# NIFS-900-08-api-gateway: 900 08 api gateway

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-900-08-api-gateway                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o API Gateway do NIS — ponto único de entrada para REST, FHIR e WebSocket.

## 2. Current State

Atual: sem API gateway (site estático). Futuro: gateway para REST/FHIR/WebSocket com rate limiting.

## 3. NIS v5.0 Design

Gateway único: /api/v1/* (REST), /fhir/* (FHIR), /ws (WebSocket para reasoning stream). Rate limiting: 100 req/min usuário, 1000 req/min serviço.

## 4. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-900-03 | Architecture |
| NIFS-1500-01 | Roadmap |
