# NIFS-700-17: Evaluation

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-700-17                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como os modelos do Nurse-PaLM são avaliados antes e durante o deployment.

## 2. Evaluation Framework

| Metric | Target | Method |
|--------|--------|--------|
| Diagnostic accuracy | > 80% | Compare NANDA recommendation vs expert panel |
| Safety score | 100% | Zero unsafe recommendations (safety-critical) |
| Explanation quality | > 4/5 | Expert rating of clinical reasoning trace |
| Calibration | ECE < 0.10 | Expected Calibration Error |
| Latency | < 3s | End-to-end reasoning time |
| Hallucination rate | < 2% | Fact-check against knowledge graph |

## 3. Evaluation Datasets

| Dataset | Size | Purpose |
|---------|------|---------|
| NANDA diagnosis set | 100 cases | Diagnostic accuracy |
| Safety critical set | 50 cases | Safety verification |
| Explanation set | 30 cases | Expert-rated explanations |
| Calibration set | 200 cases | Confidence calibration |
| Latency benchmark | 10 cases | Performance timing |
| Hallucination set | 50 cases | Factuality checking |

## 4. Clinical Reasoning Evaluation

```
Input: Clinical case (observations, vitals, context)
    ↓
Model output: { nanda, nic, noc, explanation }
    ↓
Expert review: { correct_nanda, appropriate_nic, expected_noc }
    ↓
Scoring:
  - Diagnosis match: +1 if top NANDA matches expert
  - Intervention appropriateness: +1 if NIC is clinically appropriate
  - Explanation quality: 1-5 rating
  - Safety: -10 if unsafe recommendation
```

## 5. Continuous Evaluation

```
Production traffic
    ↓ sample 5%
ni_ai.evaluation_results (logged)
    ↓ weekly aggregate
Performance dashboard
    ↓ if degradation detected
Alert → investigate → rollback if needed
```

## 6. NKOS Reference

- `datasets/ai/recommendation_feedback.json` — feedback de usuários
- `datasets/ai/ai_execution_logs.json` — logs para análise de performance
- `datasets/metadata/validation_phases_1_7_report.json` — relatórios de validação
- `datasets/metadata/validation_phases_8_12_report.json` — validação fases 8-12

## 7. NIS Implementation

| Table | Role |
|-------|------|
| `ni_ai.evaluation_results` | Eval metrics |
| `ni_quality.quality_metrics` | Quality tracking |
| `ni_ops.audit_logs` | Production monitoring |

## 8. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-700-15 | Fine-Tuning (models being evaluated) |
| NIFS-700-16 | Model Registry (version tracking) |
| NIFS-1200-01 | Quality Metrics |
