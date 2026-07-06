# NIFS-600-05: Differential Diagnosis

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-600-05                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o processo de diagnóstico diferencial — como o NIS ranqueia hipóteses, elimina alternativas e chega ao diagnóstico mais provável.

## 2. The Differential Process

```
3+ Hypotheses (from Generation stage)
    ↓
Bayesian Update (all hypotheses updated)
    ↓
Ranking by posterior probability
    ↓
Elimination: rule out low-probability
    ↓
Conflict resolution: handle ties
    ↓
Final ranking with confidence intervals
    ↓
Output: Top-3 with P(x) and rejection reasons
```

## 3. Ranking Algorithm

```python
def rank_hypotheses(hypotheses):
    # Sort by posterior probability (descending)
    ranked = sorted(hypotheses, key=lambda h: h.posterior, reverse=True)
    
    # Assign ranks
    for i, h in enumerate(ranked):
        h.rank = i + 1
    
    # Calculate gaps
    for i in range(len(ranked) - 1):
        ranked[i].gap_to_next = ranked[i].posterior - ranked[i+1].posterior
    
    # Flag ambiguity
    if ranked[0].gap_to_next < 0.10:
        ranked[0].flag = "ambiguous_top"
    
    return ranked
```

## 4. Elimination Rules

| Rule | Threshold | Action |
|------|-----------|--------|
| Probability floor | P < 0.05 | Eliminate from differential |
| Ruled out by evidence | strong evidence_against | Eliminate + log reason |
| Mutually exclusive | actual + risk of same focus | Keep both, flag conflict |
| Population mismatch | diagnosis not relevant to population | Eliminate + log |
| Insufficient defining characteristics | < 50% met | Flag, don't eliminate |

## 5. Tie-Breaking

Quando duas hipóteses têm posterior próximo (gap < 0.10):

| Strategy | When | How |
|----------|------|-----|
| More data | Always possible | Request additional observations |
| Evidence quality | GRADE A beats GRADE B | Higher grade wins tie |
| Population fit | ICU-specific beats general | Population-specific wins |
| Council vote | When data is sufficient but tie persists | Council decides |
| Human review | When council is split | Escalate |

## 6. Output Format

```
DIFERENCIAL DIAGNÓSTICO
═══════════════════════════════════════════════════

#1  NANDA 00047: Risco de Úlcera por Pressão
    P = 74%  (IC 95%: 0.68–0.80)
    Entropia: 0.82 bits
    Evidências a favor: 4 (GRADE A, GRADE B, rule, case)
    Evidências contra: 2 (decúbito q2h, colchão alt.)
    Estado: PRINCIPAL

#2  NANDA 00046: Risco de Lesão Cutânea
    P = 18%  (IC 95%: 0.12–0.25)
    Gap para #1: 56pp
    Rejeição: menos específico para UP; 00047 é subconjunto
    Estado: ALTERNATIVA

#3  NANDA 00085: Deterioração da Integridade Tissular
    P = 6%   (IC 95%: 0.02–0.12)
    Gap para #2: 12pp
    Rejeição: exige lesão já presente; paciente sem lesão
    Estado: ELIMINADA (defining char. < 50%)

Entropia total: 0.82 bits (moderada)
Calibração: Brier = 0.12 (bom)
═══════════════════════════════════════════════════
```

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-04 | Hypothesis Generation (feeds differential) |
| NIFS-600-08 | Bayesian Network (posterior computation) |
| NIFS-600-06 | Evidence Ranking (evidence in differential) |
| NIFS-600-19 | Explainability (explains rejection) |

## 8. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — ranking + elimination + tie-breaking | Leivis Melo |
