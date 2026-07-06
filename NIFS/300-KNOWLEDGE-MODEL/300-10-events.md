# NIFS-300-10: Events

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-300-10                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir eventos clínicos como unidades atômicas do raciocínio temporal do NIS.

## 2. Event Definition

Evento clínico é qualquer ocorrência observável e timestamped que afeta o estado do paciente.

## 3. Event Types

| Type | Example | NIS Table |
|------|---------|-----------|
| Assessment | Braden score calculated | `ni.assessment_log` + `ni_temporal.clinical_events` |
| Vital sign | PA 80x40, FC 120 | `ni_temporal.observations` |
| Medication | Noradrenaline started | `ni_memory.actions` |
| Intervention | Position change q2h | `ni_memory.actions` |
| Alert | Glasgow dropped to 7 | `ni_attention.attention_signals` |
| Transition | stable → critical | `ni_temporal.state_transitions` |
| Outcome | NOC 1101 improved 2→4 | `ni_memory.outcomes` |

## 4. Event Sequences

```
08:00  Braden=14 (event) → risk moderate
10:00  Braden=12 (event) → risk high → triggers hypothesis
11:00  NIC 3540 initiated (event) → action
13:00  Braden=16 (event) → risk improving → outcome positive
```

Cada evento alimenta `ni_temporal.event_sequences` e pode formar `ni_temporal.causal_chains`.

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-300-11 | States (events cause state transitions) |
| NIFS-600-02 | Reasoning Pipeline (events as input) |
