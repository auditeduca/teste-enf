# NIFS-200-17: Terminologies — ICNP

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-200-17                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a integração do ICNP (International Classification for Nursing Practice) no NIS.

## 2. ICNP Overview

| Aspect | Value |
|--------|-------|
| Full name | International Classification for Nursing Practice |
| Owner | ICN (International Council of Nurses) |
| Structure | 7-axis model |
| NIS table | `ni_onto.ontology_mappings` (cross-map) |

## 3. ICNP Axes

| Axis | Description | Example |
|------|-------------|---------|
| Focus | Fenômeno de enfermagem | Pain, Skin integrity |
| Judgment | Avaliação | Impaired, Enhanced, Risk |
| Means | Método/ação | Teaching, Positioning |
| Action | Tipo de ação | Assessing, Administering |
| Time | Quando | Acute, Chronic, Intermittent |
| Location | Onde | Peripheral, Systemic |
| Client | Quem | Individual, Family, Community |

## 4. ICNP ↔ NANDA Mapping

O NIS mantém mapeamentos bidirecionais:

```
ICNP: "Focus=Skin integrity + Judgment=Risk of impaired"
    ↔
NANDA 00047: Risk of Impaired Skin Integrity
```

Mapeamento armazenado em `ni_onto.ontology_mappings` com `ni_concept_type = 'ICNP'`.

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-14 | NANDA-I |
| NIFS-200-24 | ISO 18104 (composition standard) |
| NIFS-300-05 | Clinical Ontology |
