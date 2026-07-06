# NIFS-200-14: Terminologies — NANDA-I

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-200-14                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a integração da terminologia NANDA-I no NIS.

## 2. NANDA-I Overview

| Aspect | Value |
|--------|-------|
| Full name | North American Nursing Diagnosis Association International |
| Current edition | 2024-2026 |
| Diagnoses | ~267 |
| Structure | Domain → Class → Diagnosis |
| Code format | 5-digit (e.g., 00047) |
| NIS table | `ni.nanda_diagnoses` |

## 3. Diagnosis Types

| Type | Code Pattern | Example | NIS Use |
|------|-------------|---------|---------|
| Actual | 00XXX | 00047 (actual) | Confirmed diagnosis |
| Risk | 00XXX | 00200 (risk) | Predictive diagnosis |
| Wellness | 00XXX | 001XX | Health promotion |
| Health promotion | 00XXX | 00XXX | Education target |

## 4. NANDA Structure in NIS

```
Domain 11: Safety/Protection
└── Class 2: Physical Injury
    └── 00047: Risk of Impaired Skin Integrity
        ├── Defining characteristics: (for actual)
        ├── Risk factors: immobility, friction, moisture (for risk)
        ├── Related factors: (for actual)
        ├── NIC links: 3540, 6540, 2250
        ├── NOC links: 1101
        └── Population priors: ICU=0.32, Geriatric=0.22
```

## 5. Graph Representation

```
Node: NANDA:00047
  node_type: NANDA
  label: "Risco de Úlcera por Pressão"
  properties:
    domain: "Safety/Protection"
    class: "Physical Injury"
    diagnosis_type: "risk"
    risk_factors: ["immobility", "friction", "shear", "moisture"]
```

## 6. Versioning

NANDA-I atualiza a cada 3 anos. NIS rastreia em `ni.terminology_versions`:

| Field | Value |
|-------|-------|
| terminology_name | NANDA |
| edition | 2024-2026 |
| code_count | 267 |
| status | active |

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-15 | NIC (paired terminology) |
| NIFS-200-16 | NOC (paired terminology) |
| NIFS-200-24 | ISO 18104 (composition standard) |
| NIFS-300-15 | Diagnoses (conceptual model) |
