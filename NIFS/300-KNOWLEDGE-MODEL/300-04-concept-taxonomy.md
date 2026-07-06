# NIFS-300-04: Concept Taxonomy

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-300-04                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a taxonomia de conceitos clínicos do NIS — a hierarquia que organiza o conhecimento.

## 2. Taxonomy Structure

```
Clinical Domain (Cardiologia, Neurologia, Pneumologia, ...)
└── Clinical Concept (2000 conceitos)
    ├── NANDA Diagnosis (244)
    │   └── Domain → Class → Diagnosis
    ├── NIC Intervention (575)
    │   └── Domain → Class → Intervention
    ├── NOC Outcome (550)
    │   └── Domain → Class → Outcome
    ├── ISO Term (eixos foco/julgamento/ação)
    ├── Safety Goal (6 metas WHO)
    └── Calculator (100 ferramentas clínicas)
```

## 3. Cross-Taxonomy Mapping

```
NANDA Domain 1: Health Promotion
    ↕ (via NNN Linkages)
NIC Domain 1: Basic Physiological
    ↕ (via NNN Linkages)
NOC Domain 1: Functional Health

NANDA 00047 → NIC 3540 → NOC 1101
  (strength: strong, evidence: GRADE B)
```

## 4. NIS Implementation

| Component | Table | Records |
|-----------|-------|---------|
| Clinical Concepts | `ni.concepts` + `ni_graph.nodes` | 2,000 |
| NANDA Domains | `nursing_diagnoses.domain_code` | 13 domains |
| NIC Domains | `nursing_interventions.domain` | 6 domains |
| NNN Linkages | `ni_cog.calculator_nnn_cross` (estendido) | 1,500 |
| Content Taxonomy | `ni_content.taxonomy` | 113 terms |

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-300-05 | Clinical Ontology |
| NIFS-500-01 | Node Types (graph taxonomy) |
