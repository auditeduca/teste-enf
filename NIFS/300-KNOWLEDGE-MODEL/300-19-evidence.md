# NIFS-300-19: Evidence

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-300-19                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o modelo de evidência do NIS — como evidências científicas são estruturadas, graduadas, vinculadas ao conhecimento e usadas no raciocínio clínico.

## 2. The Evidence Principle

> "Evidence First. Nenhuma recomendação sem evidência. Nenhuma evidência sem graduação. Nenhuma graduação sem rastreabilidade."

```
Literature/Papers/Guidelines
    ↓
Mining Pipeline (extract, grade, link)
    ↓
Graded Evidence (GRADE A/B/C/D)
    ↓
Linked to Knowledge Graph nodes/edges
    ↓
Used in Reasoning (evidence_for / evidence_against)
    ↓
Cited in Explanation (audit trail)
```

## 3. GRADE Framework

O NIS adota o sistema GRADE (Grading of Recommendations Assessment, Development and Evaluation):

| Grade | Quality | Description | NIS Treatment |
|-------|---------|-------------|---------------|
| **A** | Alto | Ensaios clínicos randomizados, revisões sistemáticas | Strong weight (0.80-0.95) |
| **B** | Moderado | Estudos coorte, estudos caso-controle | Medium weight (0.60-0.80) |
| **C** | Baixo | Estudos observacionais, séries de casos | Low weight (0.40-0.60) |
| **D** | Muito baixo | Opinião de especialista, relatos | Minimal weight (0.20-0.40) |

## 4. Evidence Lifecycle

### 4.1 Acquisition

| Source | Code | Type | Pipeline |
|--------|------|------|----------|
| PubMed | PUBMED | article | Automated fetch (PubMed API) |
| Cochrane | COCHRANE | systematic_review | Manual + automated |
| BDENF | BDENF | article (nursing) | Automated fetch |
| CINAHL | CINAHL | article (nursing) | Manual import |
| Guidelines | GUIDELINE | guideline | Manual + review |
| Expert | EXPERT | expert_opinion | Elicitation protocol |
| Clinical | CLINICAL | clinical_data | From ni_memory.episodes |

### 4.2 Extraction

```
Raw Source (PDF, HTML, XML)
    ↓ NLP extraction
Extracted Entities: {phenomenon, finding, diagnosis, intervention, outcome, claim}
    ↓
ni_mining.extracted_entities
    ↓
Graph Draft: {node, edge} proposals
    ↓
ni_mining.graph_drafts
```

### 4.3 Grading

Cada evidência extraída recebe graduação GRADE:

```
Starting grade: 
  RCT → A
  Cohort → B
  Observational → C
  Expert → D

Adjustments:
  +1 if large effect size
  +1 if dose-response
  -1 if risk of bias
  -1 if inconsistency
  -1 if indirectness
  -1 if imprecision
  -1 if publication bias

Final grade: max(A), clamped to [A, D]
```

### 4.4 Linking

Evidência graduada é vinculada a elementos do grafo:

```
Evidence: "Braden ≤12 predicts pressure ulcer in ICU (87%, GRADE A)"
    ↓ links to
NANDA 00047 (supports diagnosis)
NIC 3540 (supports intervention)
CALC BRADEN (validates calculator)
POP ICU (population-specific)
```

### 4.5 Freshness

Evidências envelhecem. O `ni_mining.freshness_index` rastreia:

| Age | Status | Action |
|-----|--------|--------|
| < 2 years | Fresh | Full weight |
| 2-5 years | Current | 0.8× weight |
| 5-10 years | Aging | 0.5× weight |
| > 10 years | Stale | 0.2× weight or review |

Se nova evidência contradiz antiga → `ni_cog.conflicting_evidence` → arbitration.

## 5. Evidence in Reasoning

### 5.1 Evidence For

Evidências que **suportam** uma hipótese:

```
Hypothesis: NANDA 00047 (P = 0.32 prior)

Evidence FOR:
  E1: GRADE A — "Braden≤12 → UP risk 87%" (weight: 0.95)
  E2: GRADE B — "Immobility + ICU → UP 74%" (weight: 0.70)
  E3: Rule — "Braden≤12 AND ICU → 00047" (weight: 1.00)
  E4: Case — "Episode #4823: similar patient → 00047 confirmed" (weight: 0.89)

Combined evidence_for_weight: 0.95 × 0.70 × 1.00 × 0.89 = 0.59
```

### 5.2 Evidence Against

Evidências que **contradizem** uma hipótese:

```
Evidence AGAINST:
  E5: "Mudança de decúbito q2h reduz P(UP) em 15%" (weight: 0.60)
  E6: "Colchão pressão alternativo em uso" (weight: 0.45)

Combined evidence_against_weight: 0.60 × 0.45 = 0.27
```

### 5.3 Net Evidence

```
net_evidence = evidence_for_weight - evidence_against_weight
             = 0.59 - 0.27 = 0.32

Bayesian likelihood ratio: LR+ = evidence_for / evidence_against = 2.19

Posterior update:
  P(D|E) = P(D) × LR+ / [P(D) × LR+ + (1-P(D))]
         = 0.32 × 2.19 / [0.32 × 2.19 + 0.68]
         = 0.70 / 1.38 = 0.51 → then refined with individual updates → 0.74
```

## 6. Evidence Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| GRADE A coverage | > 60% of NANDA diagnoses | Audit |
| Evidence per node | ≥ 3 per NANDA diagnosis | Graph stats |
| Freshness | > 70% < 5 years old | Freshness index |
| Extraction F1 | > 0.85 | `ni_mining.extraction_quality_metrics` |
| Conflicts resolved | > 90% | Arbitration logs |

## 7. Schema Summary

| Table | Purpose |
|-------|---------|
| `ni_mining.sources` | Fontes de evidência |
| `ni_mining.raw_sources` | Documentos brutos |
| `ni_mining.extracted_entities` | Entidades extraídas |
| `ni_mining.graded_evidence` | Evidências graduadas (GRADE) |
| `ni_mining.graph_drafts` | Propostas de nós/arestas |
| `ni_mining.freshness_index` | Índice de atualidade |
| `ni_cog.conflicting_evidence` | Conflitos entre evidências |

## 8. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-08 | Evidence-Based Practice (clinical science) |
| NIFS-600-06 | Evidence Ranking (in reasoning pipeline) |
| NIFS-1200-08 | Evidence Quality (quality metrics) |
| NIFS-APP-E | Evidence Matrix (GRADE detail) |

## 9. References

- Guyatt, G.H. et al. (2008). GRADE: An emerging consensus on rating quality of evidence
-GRADE Working Group. (2013). GRADE guidelines 1-20
- Melnyk, B.M. & Fineout-Overholt, E. (2014). Evidence-Based Practice in Nursing & Healthcare

## 10. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — full evidence lifecycle with GRADE | Leivis Melo |
