# NIFS-200-16: Terminologies — NOC

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-200-16                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a integração da terminologia NOC (Nursing Outcomes Classification) no NIS.

## 2. NOC Overview

| Aspect | Value |
|--------|-------|
| Full name | Nursing Outcomes Classification |
| Current edition | 6th Edition |
| Outcomes | ~540 |
| Structure | Domain → Class → Outcome |
| Code format | 4-digit (e.g., 1101) |
| NIS table | `ni.noc_outcomes` |

## 3. NOC Domains

| Domain | Description | Example Outcomes |
|--------|-------------|-----------------|
| 1: Functional Health | Função física | Ambulation, Self-care |
| 2: Physiologic Health | Fisiologia | Tissue integrity, Vital signs |
| 3: Psychosocial Health | Psicossocial | Anxiety, Depression |
| 4: Health Knowledge | Conhecimento | Knowledge: disease, medication |
| 5: Perceived Health | Percepção | Quality of life, Satisfaction |

## 4. Outcome Measurement

NOC outcomes têm **escalas** com pontos (typically 1-5):

```
NOC 1101: Tissue Integrity: Skin & Mucous Membranes
Scale: 1 (severely compromised) to 5 (not compromised)

Current: 2 (substantially compromised)
Target:  4 (mildly compromised)
Delta:   +2 points
Horizon: 72h
```

## 5. Outcome in NIS Pipeline

```
Diagnosis → Intervention → Expected Outcome → Actual Outcome → Learning

NANDA 00047 → NIC 3540 → NOC 1101 (2→4) → measured 4 → success
```

## 6. Outcome Prediction

`ni_reasoning.scores` e `ni_planner.plan_nodes` armazenam:
- `expected_noc_delta`: quanto se espera melhorar
- `current_noc_value`: valor atual
- `target_noc_value`: objetivo
- `time_horizon`: prazo

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-14 | NANDA (diagnoses) |
| NIFS-200-15 | NIC (interventions) |
| NIFS-300-18 | Outcomes (conceptual model) |
| NIFS-600-13 | Outcome Prediction |
