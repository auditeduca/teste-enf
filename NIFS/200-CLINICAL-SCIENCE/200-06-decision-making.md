# NIFS-200-06: Decision Making

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-200-06                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir tomada de decisão clínica de enfermagem no contexto do NIS.

## 2. Definition

Tomada de decisão é a **escolha entre alternativas** baseada em evidência, contexto e julgamento profissional.

## 3. Decision Types

| Type | Description | NIS Module | Example |
|------|-------------|------------|---------|
| Diagnostic | Qual diagnóstico? | `ni_reasoning.hypotheses` | "00047 vs 00046?" |
| Therapeutic | Qual intervenção? | `ni_planner` | "NIC 3540 vs 2250?" |
| Prioritization | O que é mais urgente? | `ni_attention` | "Airway before skin" |
| Escalation | Quando escalar? | Safety layer | "Glasgow < 8 → notify" |
| Ethical | Dilema moral | Human review | "Restraint vs autonomy" |

## 4. Decision Models

| Model | NIS Use |
|-------|---------|
| Analytic (expected utility) | Bayesian + NOC delta |
| Recognition-primed | Memory retrieval (fast path) |
| Intuitive | Pattern match (similarity > 0.90) |
| Shared decision | Human + AI deliberation |

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-04 | Clinical Judgment |
| NIFS-200-05 | Clinical Reasoning |
| NIFS-600-05 | Differential Diagnosis |
