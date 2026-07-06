# NIFS-200-07: Critical Thinking

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-200-07                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir pensamento crítico como habilidade cognitiva modelada no NIS.

## 2. Definition

Pensamento crítico é a **análise, avaliação e síntese deliberada** de informações para formar julgamentos fundamentados.

## 3. Critical Thinking in NIS

| Skill | NIS Implementation |
|-------|-------------------|
| Interpretation | `ni_attention` — filtrar observações relevantes |
| Analysis | `ni_reasoning` — decompor em hipóteses |
| Evaluation | `ni_prob` — avaliar P(x) e evidência |
| Inference | `ni_prob.belief_updates` — Bayesian inference |
| Explanation | `ni_explain` — justificar conclusão |
| Self-regulation | `ni_learning` — aprender com erros |

## 4. Anti-Patterns (Cognitive Biases)

| Bias | NIS Mitigation |
|------|---------------|
| Anchoring | Reabrir hipóteses se P cai abaixo de 0.20 |
| Confirmation | evidence_for E evidence_against em paralelo |
| Availability | Memory decay temporal |
| Premature closure | Quality gate: ≥ 3 hipóteses |
| Overconfidence | Calibration monitoring (Brier score) |

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-04 | Clinical Judgment |
| NIFS-200-05 | Clinical Reasoning |
| NIFS-100-07 | Trustworthy AI (bias mitigation) |
