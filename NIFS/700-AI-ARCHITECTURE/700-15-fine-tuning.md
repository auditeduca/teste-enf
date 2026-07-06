# NIFS-700-15: Fine-Tuning

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-700-15                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a estratégia de fine-tuning de modelos para o domínio de enfermagem clínica.

## 2. Fine-Tuning Strategy

| Phase | Method | Data | Goal |
|-------|--------|------|------|
| 1. Domain-Adapt | Continued pre-training | Nursing literature, NANDA/NIC/NOC texts | Vocabulary + domain knowledge |
| 2. Instruction-Tune | Supervised fine-tuning | Clinical Q&A pairs from NKOS | Task-specific performance |
| 3. Align | RLHF / DPO | Feedback from `recommendation_feedback.json` | Safety + clinical accuracy |
| 4. Evaluate | Benchmark | NIS clinical eval set | Validation before deployment |

## 3. Training Data Sources

| Source | Records | Use |
|--------|---------|-----|
| `nursing_diagnoses.json` | 244 NANDA | Domain adaptation |
| `nursing_interventions.json` | 575 NIC | Domain adaptation |
| `nnn_linkages.json` | 1500 linkages | Instruction tuning (NANDA→NIC mapping) |
| `clinical_guidelines.json` | 200 guidelines | Instruction tuning (guideline Q&A) |
| `evidence.json` | 27 GRADE entries | Evidence reasoning training |
| `recommendation_feedback.json` | runtime | RLHF / DPO alignment |
| `ai_execution_logs.json` | runtime | Preference learning |
| 577 master-data files | per-calculator | Tool-specific reasoning |

## 4. NKOS Data for Training

O CALENF-NKD já tem infraestrutura de AI:
- `datasets/ai/ai_jobs.json` — job queue para training/inference
- `datasets/ai/ai_execution_logs.json` — logs de execução
- `datasets/ai/recommendation_feedback.json` — feedback loop
- `datasets/ai/workflows.json` — AI workflows
- `datasets/ai/explanations.json` — explanations geradas
- `scripts/ai_factory_agents/` — agentes de factory para AI

## 5. NIS Implementation

| Table | Role |
|-------|------|
| `ni_ai.model_versions` | Model registry |
| `ni_ai.training_datasets` | Training data references |
| `ni_ai.evaluation_results` | Benchmark results |
| `ni_learning.reinforcement_signals` | RLHF signals |

## 6. Model Registry

```
Nurse-PaLM-Base (domain-adapted)
    ├── Nurse-PaLM-Dx (diagnosis specialist)
    ├── Nurse-PaLM-Plan (care planning)
    ├── Nurse-PaLM-Explain (explanation generation)
    └── Nurse-PaLM-Safety (safety verification)
```

Cada variante tem: version, base_model, training_data hash, evaluation metrics, deployment status.

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-700-01 | Foundation Model (base architecture) |
| NIFS-700-16 | Model Registry (versioning) |
| NIFS-700-17 | Evaluation (benchmarking) |
| NIFS-600-17 | Learning Loop (feedback → training) |
