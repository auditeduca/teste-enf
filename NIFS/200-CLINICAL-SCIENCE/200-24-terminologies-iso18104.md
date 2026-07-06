# NIFS-200-24: Terminologies — ISO 18104

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-200-24                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a integração da ISO 18104 (Health informatics — Integration of a reference terminology for nursing) no NIS como framework composicional.

## 2. ISO 18104 Overview

| Aspect | Value |
|--------|-------|
| Full name | ISO 18104:2023 Health informatics — Integration of a reference terminology for nursing |
| Owner | ISO/TC 215 (Health Informatics) |
| Purpose | Padronizar terminologias de enfermagem via modelo composicional |
| NIS schema | `ni_iso` (axis_terms, compositions, action_compositions) |

## 3. The Compositional Model

ISO 18104 define que qualquer diagnóstico ou intervenção de enfermagem pode ser **composto** a partir de eixos terminológicos:

### 3.1 Nursing Diagnosis Reference Model

```
Diagnosis = Focus + Judgment (+ Modifier)

Ex: "Risco de Úlcera por Pressão"
  Focus: "Skin integrity" (Tissue integrity)
  Judgment: "Risk of impaired"
```

### 3.2 Nursing Action Reference Model

```
Action = Focus + Action (+ Target)

Ex: "Monitorar pressão arterial"
  Focus: "Blood pressure"
  Action: "Monitoring"
```

## 4. ISO Axes in NIS (`ni_iso.axis_terms`)

| Axis | Description | Example Terms |
|------|-------------|---------------|
| Focus | Fenômeno de enfermagem | Skin integrity, Pain, Nutrition |
| Judgment | Avaliação | Impaired, Enhanced, Risk of, Effective |
| Action | Tipo de ação | Assessing, Administering, Teaching, Monitoring |
| Means | Método | Positioning, Teaching, Massage |
| Time | Quando | Acute, Chronic, Intermittent |
| Location | Onde | Peripheral, Systemic |
| Client | Quem | Individual, Family, Community |

## 5. ISO ↔ NANDA Composition

`ni_iso.compositions` armazena a decomposição de diagnósticos NANDA em eixos ISO:

```
NANDA 00047 "Risk of Impaired Skin Integrity"
  → focus_term_id: "Skin integrity"
  → judgment_term_id: "Risk of impaired"
```

`ni_iso.action_compositions` decompose NIC interventions:

```
NIC 3540 "Pressure Management"
  → composition_id: "Skin integrity + Managing"
  → action_term: "Managing"
```

## 6. Why ISO 18104 Matters for NIS

| Benefit | Explanation |
|---------|-------------|
| **Composability** | Criar novos diagnósticos que não existem em NANDA |
| **Cross-mapping** | Mapear NANDA ↔ ICNP via eixos comuns |
| **Precision** | Decompor um diagnóstico em seus componentes semânticos |
| **Extensibility** | Adicionar novos focos/julgamentos sem criar novas taxonomias |
| **Interoperabilidade** | ISO 18104 é padrão internacional para terminologia de enfermagem |

## 7. Epistemological Validation

A `ni_epist.epistemology_rules` inclui regras V3 (ISO composition validation):

| Rule | Check |
|------|-------|
| V3_iso_composition | Todo diagnóstico NANDA deve ter composição ISO válida |
| V3_axis_coverage | Focus + Judgment são obrigatórios; Action é obrigatório para intervenções |
| V3_term_existence | Termos usados devem existir em `ni_iso.axis_terms` |

## 8. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-14 | NANDA-I (diagnoses) |
| NIFS-200-15 | NIC (interventions) |
| NIFS-200-17 | ICNP (alternative compositional system) |
| NIFS-300-05 | Clinical Ontology |
| NIFS-600-02 | Reasoning Pipeline (uses ISO decomposition) |
