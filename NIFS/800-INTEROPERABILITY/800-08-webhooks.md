# NIFS-800-08: Webhooks

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-800-08                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o NIS envia notificações assíncronas para sistemas externos via webhooks.

## 2. Webhook Events

| Event | Trigger | Payload |
|-------|---------|---------|
| `diagnosis.created` | New NANDA diagnosis | { patient_id, nanda_code, probability } |
| `safety.alert` | Safety rule violation | { patient_id, alert_type, severity } |
| `care_plan.updated` | Care plan modified | { plan_id, changes } |
| `outcome.assessed` | NOC outcome recorded | { patient_id, noc_code, delta } |
| `evidence.updated` | New evidence graded | { evidence_id, grade } |

## 3. NKOS Reference

- `datasets/community/webhook_subscriptions.json` — inscrições de webhook já definidas no NKOS

## 4. Delivery Protocol

```
Event occurs in NIS
    ↓
ni_interop.webhook_subscriptions (find matching subscriptions)
    ↓
POST payload to subscriber URL
    ↓
Expect 200 OK within 5s
    ↓
Retry: 3 attempts with exponential backoff (1s, 5s, 30s)
    ↓
Log delivery to ni_interop.webhook_deliveries
```

## 5. Security

- **HMAC-SHA256 signature** in `X-NIS-Signature` header
- **TLS required** for all webhook URLs
- **Secret rotation** every 90 days

## 6. NIS Implementation

| Table | Role |
|-------|------|
| `ni_interop.webhook_subscriptions` | Subscriptions |
| `ni_interop.webhook_deliveries` | Delivery log |
| `ni_interop.webhook_events` | Event queue |

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-800-05 | REST (webhook payload format) |
| NIFS-1000-05 | Encryption (webhook security) |
