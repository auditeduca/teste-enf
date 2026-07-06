# NIFS-100-16: Event-Driven Design

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-100-16                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a arquitetura event-driven do NIS — eventos disparam raciocínio, não polling.

## 2. Event Catalog

| Event | Producer | Consumer(s) | Action |
|-------|----------|------------|--------|
| `observation.received` | Assessment Pipeline | Attention, Temporal | Filter + store |
| `attention.critical` | Attention | Reasoning | Start session |
| `calculator.threshold_crossed` | Calculator | Reasoning, Safety | Alert + reason |
| `reasoning.completed` | Reasoning | Council, Explain | Deliberate + explain |
| `council.consensus_reached` | Council | Planner, Explain | Generate plan |
| `plan.approved` | Planner/Human | Memory, Twin | Execute + simulate |
| `outcome.measured` | Memory | Learning | Generate signal |
| `learning.weight_proposed` | Learning | Human Reviewer | Queue validation |
| `safety.veto_triggered` | Safety Agent | Council, Human | Block + alert |
| `deterioration.detected` | Temporal | Reasoning, Safety | Escalate |
| `episode.closed` | Memory | Learning, Mining | Consolidate |

## 3. Event Structure

```json
{
  "event_id": "uuid",
  "event_type": "observation.received",
  "timestamp": "2026-07-05T10:00:00Z",
  "source": "assessment_pipeline",
  "payload": {
    "patient_identifier": "hash_xxx",
    "observation_type": "assessment_score",
    "value": 12,
    "code": "BRADEN"
  },
  "correlation_id": "session_uuid"
}
```

## 4. Event Bus

| Implementation | Use |
|----------------|-----|
| PostgreSQL LISTEN/NOTIFY | In-process events |
| Redis Pub/Sub | Cross-service events |
| Message queue (RabbitMQ/Kafka) | Durable, high-volume |

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-01 | Clinical Workflow (state transitions) |
| NIFS-900-10 | Queues (infrastructure) |
| NIFS-800-08 | Webhooks (external events) |
