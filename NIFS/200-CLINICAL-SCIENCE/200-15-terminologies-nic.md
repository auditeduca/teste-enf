# NIFS-200-15: Terminologies — NIC

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-200-15                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a integração da terminologia NIC (Nursing Interventions Classification) no NIS.

## 2. NIC Overview

| Aspect | Value |
|--------|-------|
| Full name | Nursing Interventions Classification |
| Current edition | 7th Edition |
| Interventions | ~565 |
| Structure | Domain → Class → Intervention |
| Code format | 4-digit (e.g., 3540) |
| NIS table | `ni.nic_interventions` |

## 3. NIC Domains

| Domain | Description | Example Classes |
|--------|-------------|----------------|
| 1: Basic Physiological | Care físico básico | Activity, Nutrition, Elimination |
| 2: Complex Physiological | Care físico complexo | Circulation, Respiratory, Neuro |
| 3: Behavioral | Comportamento | Teaching, Coping, Communication |
| 4: Safety | Proteção | Crisis, Risk, Injury |
| 5: Family | Família | Childbearing, Family dynamics |
| 6: Health System | Sistema de saúde | Information, Health system |

## 4. Intervention Structure

```
NIC 3540: Pressure Management
├── Domain: 1 (Basic Physiological)
├── Class: Activity and Exercise Management
├── Activities:
│   ├── Turn and reposition q2h
│   ├── Use pressure-relieving surfaces
│   ├── Monitor pressure points
│   └── Minimize friction/shear
├── Treats: NANDA 00047, 00046
├── Improves: NOC 1101
└── Expected time to improvement: 48-96h
```

## 5. Selection in NIS

NIC selection é feita pelo Intervention Selection module (NIFS-600-12):

```
NANDA 00047 → graph traversal → NIC candidates
    ↓
Rank by: edge_weight × evidence_grade × context_fit
    ↓
Primary (3540) + Adjunct (6540) + Contingency (2250)
```

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-14 | NANDA (diagnoses) |
| NIFS-200-16 | NOC (outcomes) |
| NIFS-300-16 | Interventions (conceptual model) |
| NIFS-600-12 | Intervention Selection |
