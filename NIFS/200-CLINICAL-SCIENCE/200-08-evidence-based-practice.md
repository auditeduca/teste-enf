# NIFS-200-08: Evidence-Based Practice

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-200-08                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir Prática Baseada em Evidência (PBE) como fundação clínica do NIS.

## 2. The PBE Triad

```
    Best Research Evidence
              ↑
              │
     ┌────────┴────────┐
     │       NIS       │ → Clinical Decision
     └────────┬────────┘
              │
  Clinical Expertise + Patient Values/Preferences
```

## 3. The 5 Steps of EBP (ASK Model)

| Step | Description | NIS Module |
|------|-------------|------------|
| Ask | Formular pergunta PICO | Reasoning session input |
| Search | Buscar evidência | `ni_mining.sources` + RAG |
| Appraise | Avaliar qualidade (GRADE) | `ni_mining.graded_evidence` |
| Apply | Aplicar ao paciente | `ni_reasoning` + `ni_prob` |
| Assess | Avaliar resultado | `ni_memory.outcomes` + `ni_learning` |

## 4. PICO Format

```
P — Population: ICU adult patients
I — Intervention: Position change q2h (NIC 3540)
C — Comparison: Standard care without schedule
O — Outcome: Pressure ulcer incidence (NOC 1101)
```

O NIS estruturar todas as perguntas em formato PICO antes de buscar evidência.

## 5. GRADE Integration

| GRADE | Weight in NIS | Use |
|-------|--------------|-----|
| A | 0.95 | Strong recommendation |
| B | 0.70 | Moderate recommendation |
| C | 0.50 | Weak recommendation |
| D | 0.25 | Expert opinion only |

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-100-05 | Evidence-Based Nursing (principle) |
| NIFS-300-19 | Evidence (model) |
| NIFS-600-06 | Evidence Ranking (in reasoning) |
| NIFS-1200-08 | Evidence Quality (metrics) |
