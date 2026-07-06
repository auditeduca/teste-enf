# NIFS-200-03: Assessment

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-200-03                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o conceito clínico de avaliação de enfermagem e sua implementação no NIS.

## 2. Assessment Definition

Avaliação é a **coleta sistemática, validação e comunicação de dados do paciente** — a primeira fase do ADPIE.

## 3. Assessment Types

| Type | Description | NIS Module |
|------|-------------|------------|
| Initial | Admissão, primeiro contato | `ni.assessment_log` + `ni_temporal` |
| Focused | Problema específico | Calculator trigger |
| Ongoing | Monitoramento contínuo | `ni_temporal.time_series` |
| Emergency | Situação aguda | Safety protocol + escalation |
| Discharge | Preparo de alta | `ni_planner` + `ni_content` |

## 4. Data Collection Methods

| Method | NIS Implementation |
|--------|-------------------|
| Observação | `ni_temporal.observations` |
| Entrevista | NLP → `ni_ai.named_entities` |
| Exame físico | Structured form → `ni_temporal.observations` |
| Escalas/instrumentos | Calculator engine → `ni.assessment_log` |
| Revisão de prontuário | FHIR sync → `ni_interop` |
| Monitorização contínua | Device stream → `ni_temporal.time_series` |

## 5. Assessment Quality

```
quality = completeness × timeliness × reliability × diversity

Target: > 0.80 for reliable reasoning
```

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-03 | Assessment Pipeline (implementation) |
| NIFS-200-02 | Nursing Process (parent phase) |
