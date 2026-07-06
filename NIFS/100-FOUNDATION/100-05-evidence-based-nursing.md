# NIFS-100-05: Evidence-Based Nursing

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-100-05                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o compromisso do NIS com a prática baseada em evidência (PBE) como fundamento de toda recomendação.

## 2. The EBP Triad

```
    Best Evidence
         ↑
         │
    ┌────┴────┐
    │  NIS    │ → Recommendation
    └────┬────┘
         │
  Clinical Expertise + Patient Values
```

| Component | NIS Implementation |
|-----------|-------------------|
| Best Evidence | `ni_mining.graded_evidence` (GRADE A-D) |
| Clinical Expertise | `ni_council` agents + `ni_rules` (expert rules) |
| Patient Values | `ni.cases` patient context + `ni_world` context |

## 3. Evidence Hierarchy

| Level | Source | NIS Weight |
|-------|--------|-----------|
| 1 | Systematic review / meta-analysis | 0.95 (GRADE A) |
| 2 | RCT | 0.85 (GRADE A) |
| 3 | Cohort study | 0.70 (GRADE B) |
| 4 | Case-control | 0.60 (GRADE B) |
| 5 | Case series | 0.50 (GRADE C) |
| 6 | Expert opinion | 0.25 (GRADE D) |
| 7 | Clinical experience (memory) | variable (empirical) |

## 4. No Evidence, No Recommendation

```
If no evidence found for a hypothesis:
    → Do NOT recommend
    → Output: "INSUFFICIENT_EVIDENCE"
    → Suggest: collect more data or consult specialist
```

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-08 | Evidence-Based Practice (clinical science) |
| NIFS-300-19 | Evidence (model) |
| NIFS-600-06 | Evidence Ranking (in reasoning) |
