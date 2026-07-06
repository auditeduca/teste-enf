# NIFS-100-07: Trustworthy AI

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-100-07                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir os requisitos para que o NIS seja uma IA confiável em contexto clínico.

## 2. Trust Pillars (EU AI Act + WHO Ethics)

| Pillar | NIS Implementation |
|--------|-------------------|
| **Transparency** | Rastro completo, explicação em 4 níveis |
| **Accountability** | Toda decisão tem session_id + created_by |
| **Fairness** | Priors por população, não por gênero/raça; testes de viés |
| **Reliability** | Validação clínica, regression tests, calibration |
| **Safety** | 4-layer safety, veto, human-in-the-loop |
| **Privacy** | Hash de paciente, LGPD/HIPAA, dados anonimizados |
| **Human Agency** | Override sempre, IA propõe/humano decide |

## 3. Bias Mitigation

| Bias Type | Mitigation |
|-----------|-----------|
| Anchoring | Bayesian sempre reabre hipóteses se P cai |
| Confirmation | evidence_for E evidence_against em paralelo |
| Availability | Memory decay temporal |
| Premature closure | Quality gate: ≥ 3 hipóteses |
| Population bias | Priors por população, audit por demografia |

## 4. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-100-04 | Human-Centered AI |
| NIFS-100-06 | Clinical Safety |
| NIFS-100-08 | Explainability |
| NIFS-700-18 | Safety Layer |
| NIFS-700-19 | Hallucination Prevention |
