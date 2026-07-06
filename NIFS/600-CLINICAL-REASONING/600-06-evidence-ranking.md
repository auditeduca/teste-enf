# NIFS-600-06: Evidence Ranking

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-600-06                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o NIS ranqueia e pondera evidências no raciocínio clínico — separando evidência forte de fraca, e suporte de contradição.

## 2. Evidence Ranking Formula

```
evidence_weight = grade_weight × freshness_factor × relevance_factor × population_match
```

| Factor | Range | Description |
|--------|-------|-------------|
| `grade_weight` | 0.20–0.95 | GRADE A=0.95, B=0.70, C=0.50, D=0.25 |
| `freshness_factor` | 0.20–1.00 | <2y=1.0, 2-5y=0.8, 5-10y=0.5, >10y=0.2 |
| `relevance_factor` | 0.50–1.00 | Direct=1.0, indirect=0.7, tangential=0.5 |
| `population_match` | 0.60–1.00 | Exact match=1.0, partial=0.8, none=0.6 |

## 3. Evidence Categories in Reasoning

| Category | Supports | Contradicts | Use |
|----------|----------|-------------|-----|
| `literature` | ✓ | ✓ | Research papers, systematic reviews |
| `rule` | ✓ | ✓ | Decision rules (`ni_rules.decision_rules`) |
| `case` | ✓ | ✗ | Similar episodes from memory |
| `expert` | ✓ | ✓ | Expert opinion (GRADE D) |
| `calculator` | ✓ | ✗ | Calculator thresholds |

## 4. Combined Evidence Score

For each hypothesis:

```
evidence_for_score = Σ(w_i × grade_i × fresh_i × rel_i × pop_i) for all FOR evidence
evidence_against_score = Σ(w_j × grade_j × fresh_j × rel_j × pop_j) for all AGAINST evidence

net_score = evidence_for_score - evidence_against_score
likelihood_ratio = evidence_for_score / max(evidence_against_score, 0.01)
```

| Net Score | Interpretation |
|-----------|---------------|
| > 0.70 | Strong support |
| 0.40–0.70 | Moderate support |
| 0.10–0.40 | Weak support |
| < 0.10 | Insufficient or balanced |

## 5. Conflict Detection

When evidence_for and evidence_against are both strong:

```
if evidence_for_score > 0.50 AND evidence_against_score > 0.50:
    flag: conflicting_evidence
    → ni_cog.conflicting_evidence
    → Council arbitration
```

## 6. Schema Summary

| Table | Purpose |
|-------|---------|
| `ni_mining.graded_evidence` | Evidências com GRADE |
| `ni_mining.freshness_index` | Atualidade por nó |
| `ni_cog.conflicting_evidence` | Conflitos detectados |
| `ni_reasoning.trace` | Evidências usadas por sessão |

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-300-19 | Evidence (model) |
| NIFS-600-04 | Hypothesis Generation (uses evidence) |
| NIFS-600-05 | Differential Diagnosis (uses ranking) |
| NIFS-600-18 | Consensus Engine (arbitrates conflicts) |

## 8. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — ranking formula + conflict detection | Leivis Melo |
