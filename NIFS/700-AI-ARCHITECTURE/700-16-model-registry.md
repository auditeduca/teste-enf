# NIFS-700-16: Model Registry

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-700-16                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o registry de modelos de IA do Nurse-PaLM — versionamento, deployment e rollback.

## 2. Model Hierarchy

```
Nurse-PaLM (family)
├── Nurse-PaLM-Base v1.0.0 (domain-adapted, production)
│   ├── embedding_model: text-embedding-004
│   ├── reasoning_model: Llama-3.1-70B (Groq)
│   └── safety_model: Llama-3-8B (local)
├── Nurse-PaLM-Dx v1.0.0 (diagnosis specialist)
├── Nurse-PaLM-Plan v0.9.0 (care planning, beta)
├── Nurse-PaLM-Explain v1.0.0 (explanation)
└── Nurse-PaLM-Safety v1.0.0 (safety verification)
```

## 3. Registry Schema

| Field | Type | Description |
|-------|------|-------------|
| `model_id` | UUID | Unique model identifier |
| `name` | VARCHAR | Model name |
| `version` | SemVer | Semantic version |
| `base_model` | VARCHAR | Base LLM (e.g., Llama-3.1-70B) |
| `provider` | VARCHAR | groq, openai, local |
| `training_data_hash` | VARCHAR | Hash of training dataset |
| `evaluation_metrics` | JSONB | { accuracy, f1, safety_score } |
| `deployment_status` | ENUM | staging, production, archived |
| `created_date` | TIMESTAMPTZ | |
| `retired_date` | TIMESTAMPTZ | nullable |

## 4. Deployment Lifecycle

```
Training → Evaluation → Staging → Canary (10% traffic) → Production
                                                    ↓
                                              Monitoring
                                                    ↓
                                          Issues? → Rollback
                                          OK? → Full deployment
```

## 5. NKOS Reference

- `datasets/ai/ai_jobs.json` — job queue que orquestra training/inference
- `datasets/ai/workflows.json` — workflows de AI
- `datasets/metadata/ai_prompt_templates.json` — templates por modelo

## 6. NIS Implementation

| Table | Role |
|-------|------|
| `ni_ai.model_versions` | Model registry |
| `ni_ai.model_deployments` | Deployment tracking |
| `ni_ai.evaluation_results` | Eval metrics per version |

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-700-15 | Fine-Tuning (produces models) |
| NIFS-700-17 | Evaluation (validates models) |
| NIFS-1100-02 | Model Governance (oversight) |
