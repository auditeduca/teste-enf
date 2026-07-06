# NIFS-200-04: Clinical Judgment

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-200-04                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir julgamento clínico de enfermagem e como o NIS o modela computacionalmente.

## 2. Definition

Julgamento clínico é o **processo de interpretar dados, formar conclusões e tomar decisões** sobre o cuidado do paciente.

## 3. Tanner's Model (NIS Implementation)

| Phase | Cognitive Process | NIS Module |
|-------|------------------|------------|
| Noticing | Perceber o que importa | `ni_attention` |
| Interpreting | Dar significado aos dados | `ni_reasoning` + `ni_prob` |
| Responding | Agir clinicamente | `ni_planner` + `ni_council` |
| Reflecting | Avaliar a ação | `ni_learning` + `ni_memory` |

## 4. Judgment Quality Factors

| Factor | NIS Metric |
|--------|-----------|
| Experience | Episode count in memory |
| Knowledge | Graph coverage per diagnosis |
| Critical thinking | Hypothesis count (≥ 3) |
| Ethical reasoning | Safety check pass rate |

## 5. Novice vs. Expert

| Level | Characteristic | NIS Mode |
|-------|---------------|---------|
| Novice | Analytic, rule-based | Full reasoning pipeline |
| Competent | Pattern recognition + analysis | Hybrid mode |
| Expert | Intuitive recognition | Memory retrieval (similarity > 0.90) |

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-05 | Clinical Reasoning (process) |
| NIFS-600-02 | Reasoning Pipeline (implementation) |
