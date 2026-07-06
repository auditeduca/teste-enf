# NIFS-400-14: Enumerations

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-400-14                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Catalogar todas as enumerações (conjuntos de valores controlados) usadas no NIS.

## 2. Core Enumerations

### 2.1 Status Enums

| Enum | Values |
|------|--------|
| `entity_status` | draft, review, active, superseded, deprecated |
| `reasoning_status` | active, completed, aborted |
| `plan_status` | proposed, active, completed, abandoned |
| `sync_status` | pending, in_progress, completed, failed |

### 2.2 Clinical Enums

| Enum | Values |
|------|--------|
| `diagnosis_type` | actual, risk, wellness, health_promotion |
| `outcome_type` | improved, unchanged, deteriorated, resolved, adverse |
| `severity` | stable, moderate, critical, terminal |
| `evidence_grade` | A, B, C, D (GRADE) |
| `nnn_strength` | strong, moderate, suggestive |

### 2.3 Cognitive Enums

| Enum | Values |
|------|--------|
| `step_type` | observation, hypothesis, evidence_for, evidence_against, selection, planning, monitoring, reassessment |
| `agent_type` | assessment, nanda, nic, noc, safety, medication, evidence, consensus |
| `attention_priority` | 1, 2, 3, 4, 5 |
| `reward_type` | positive, negative, neutral |
| `sim_type` | mcts, monte_carlo, deterministic, counterfactual |

### 2.4 Platform Enums

| Enum | Values |
|------|--------|
| `content_type` | article, calculator, tool, protocol, guide, video, infographic |
| `error_type` | js_exception, api_failure, broken_link, translation_missing, a11y_regression |
| `consent_type` | data_processing, cookies, analytics, clinical_data, marketing |

## 3. Implementation

Enums são implementados como `CHECK (field IN ('value1', 'value2', ...))` em PostgreSQL, não como ENUM types nativos, para facilitar adição de novos valores sem migration.

## 4. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-400-05 | Data Types |
| NIFS-400-06 | Constraints |
