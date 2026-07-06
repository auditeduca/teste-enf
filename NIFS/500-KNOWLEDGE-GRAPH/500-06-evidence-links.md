# NIFS-500-06: Evidence Links

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-500-06                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como evidências científicas são vinculadas a nós e arestas do grafo clínico.

## 2. Evidence Link Architecture

```
ni_mining.graded_evidence (source)
    ↓
ni_graph.edges.evidence_grade (A/B/C/D)
    ↓
ni_explain.recommendation_reasons (reason_type=literature_support)
```

## 3. GRADE System

| Grade | Quality | Description | Weight Multiplier |
|-------|---------|-------------|-------------------|
| A | High | RCTs, systematic reviews | 1.0 |
| B | Moderate | Quasi-experimental, cohort | 0.85 |
| C | Low | Observational, case-control | 0.65 |
| D | Very Low | Expert opinion, case reports | 0.40 |

## 4. Evidence Sources

| Source | Type | Records | NIS Table |
|--------|------|---------|-----------|
| PubMed | Article | varies | `ni_mining.sources` (PUBMED) |
| Cochrane | Systematic review | varies | `ni_mining.sources` (COCHRANE) |
| BDENF | Nursing article | varies | `ni_mining.sources` (BDENF) |
| WHO | Guideline | 200 | `clinical_guidelines.json` |
| MS-BR | Guideline | varies | `clinical_guidelines.json` |
| ACOG | Guideline | 1 (APGAR) | `apgar_evidence_complete.json` |

## 5. Evidence Linkage Flow

```
1. Source document mined → ni_mining.raw_sources
2. Entities extracted → ni_mining.extracted_entities
3. Evidence graded (GRADE) → ni_mining.graded_evidence
4. Graph drafts created → ni_mining.graph_drafts
5. Human review → approve/reject
6. Approved → ni_graph.edges with evidence_grade
7. Freshness tracked → ni_mining.freshness_index
```

## 6. APGAR Pilot Evidence (Template)

`apgar_evidence_complete.json` mostra o padrão:

```json
{
  "source": "Apgar V. 1953. Anesth Analg",
  "doi": "10.1213/00000539-195301000-00013",
  "evidence_grade": "A",
  "study_type": "cohort_prospective",
  "linked_tool": "APGAR"
}
```

Cada calculadora deve ter evidências com DOI e GRADE level.

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-500-05 | Confidence (evidence informs confidence) |
| NIFS-600-06 | Evidence Ranking |
| NIFS-1100-03 | Knowledge Curation (mining governance) |
