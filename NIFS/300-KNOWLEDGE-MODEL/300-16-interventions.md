# NIFS-300-16: Interventions

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-300-16                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir intervenções de enfermagem como ações terapêuticas selecionadas pelo processo de raciocínio.

## 2. Intervention Model

```
NursingIntervention
├── nic_code (PK, e.g., "3540")
├── domain (6 NIC domains)
├── definition
├── activities[] (specific actions)
├── snomed_ct_code
├── related_tool_codes[]
├── ISO action composition: focus + action
└── NNN linkages → treats NANDA X, improves NOC Y
```

## 3. Intervention Selection

```
NANDA 00047 selected (P=0.91)
    ↓ Graph traversal: edges where relation_type='treats'
NIC candidates: 3540 (strong), 6540 (moderate), 2250 (suggestive)
    ↓ Rank by: edge_weight × evidence_grade × context_fit
Primary: NIC 3540 (Pressure Management)
Adjunct: NIC 6540 (Skin Surveillance)
Contingency: NIC 2250 (Wound Care) if deteriorates
```

## 4. NIS Data (NKOS 2026)

| Data | Count | Source |
|------|-------|--------|
| NIC interventions | 575 | `nursing_interventions.json` |
| NIC domains | 6 | NIC 7th edition |
| NNN linkages | 1,500 | `nnn_linkages.json` |
| Related tools | per NIC | `related_tool_codes[]` |

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-15 | NIC (terminology) |
| NIFS-600-12 | Intervention Selection |
| NIFS-300-17 | Goals (intervention targets) |
