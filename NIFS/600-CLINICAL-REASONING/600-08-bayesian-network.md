# NIFS-600-08: Bayesian Network

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-600-08                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o modelo probabilístico bayesiano que permeia todo o mecanismo de decisão do NIS. Um Nurse-PaLM nunca responde apenas "Diagnóstico: X" — responde com probabilidades.

## 2. The Uncertainty Principle

> "Na enfermagem clínica, a certeza é a exceção, não a regra. Cada diagnóstico é uma hipótese probabilística, não uma conclusão determinística."

O NIS trata incerteza como cidadão de primeira classe:

```
Determinístico:    "Diagnóstico: 00047"
                   ❌ Inaceitável no NIS

Probabilístico:    "NANDA 00047: 74% (IC 95%: 0.68–0.80)
                    NANDA 00046: 18% (IC 95%: 0.12–0.25)
                    NANDA 00085:  6% (IC 95%: 0.02–0.12)
                    Entropia: 0.82 bits"
                   ✅ Padrão NIS
```

## 3. Bayesian Framework

### 3.1 Core Formula

```
P(Diagnosis | Evidence) = P(Evidence | Diagnosis) × P(Diagnosis) / P(Evidence)
```

Onde:
- **P(Diagnosis)** = prior (crença antes da evidência)
- **P(Evidence | Diagnosis)** = likelihood (quão provável é a evidência se o diagnóstico for verdadeiro)
- **P(Diagnosis | Evidence)** = posterior (crença atualizada)
- **P(Evidence)** = normalização (soma sobre todas as hipóteses)

### 3.2 Sequential Update

Evidências chegam sequencialmente. Cada nova evidência atualiza o posterior:

```
Prior:          P(D) = 0.32

Evidence 1:     P(D|E1) = P(E1|D) × 0.32 / P(E1) = 0.58
                (Braden 12 suporta úlcera)

Evidence 2:     P(D|E1,E2) = P(E2|D) × 0.58 / P(E2) = 0.71
                (Imobilidade suporta úlcera)

Evidence 3:     P(D|E1,E2,E3) = P(E3|D) × 0.71 / P(E3) = 0.74
                (UTI, pós-op suporta úlcera)

Counter-evidence:
Evidence 4:     P(D|E1,E2,E3,E4) = P(E4|D) × 0.74 / P(E4) = 0.69
                (Mudança de decúbito a cada 2h reduz probabilidade)
```

Cada atualização é registrada em `ni_prob.belief_updates`.

### 3.3 Multi-Hypothesis Update

Quando há N hipóteses competindo:

```
P(D_i | E) = P(E | D_i) × P(D_i) / Σ_j [P(E | D_j) × P(D_j)]
```

A soma das posteriors é sempre 1.0 (distribuição de probabilidade sobre hipóteses).

## 4. Network Structure

### 4.1 Nodes

Nós do grafo bayesiano = nós do knowledge graph:

| Node Type | Examples | Role |
|-----------|----------|------|
| NANDA diagnosis | 00047, 00046, 00085 | Hypothesis nodes |
| Clinical finding | Hipotensão, hipoxemia | Evidence nodes |
| Assessment score | Braden=12, Glasgow=11 | Evidence nodes |
| Population | ICU, pediatrics, geriatric | Context nodes |
| Intervention | NIC 3540, NIC 6540 | Action nodes |
| Outcome | NOC 1101 | Goal nodes |

### 4.2 Edges

`ni_prob.bayesian_links` define as conexões condicionais:

| Link Type | Direction | Example |
|-----------|-----------|---------|
| Evidence → Diagnosis | E → D | Braden≤12 → 00047 |
| Diagnosis → Outcome | D → O | 00047 → NOC 1101 |
| Diagnosis → Intervention | D → I | 00047 → NIC 3540 |
| Context → Diagnosis | C → D | ICU → 00047 (prior modifier) |
| Intervention → Outcome | I → O | NIC 3540 → NOC 1101 improved |

### 4.3 Conditional Probability Tables (CPTs)

Cada nó tem uma CPT que define P(node | parents):

```
NANDA 00047:
┌─────────────┬──────────────┬────────────────┐
│ Braden ≤ 12 │ ICU = true   │ P(00047 = yes) │
├─────────────┼──────────────┼────────────────┤
│    Yes      │    Yes       │     0.87       │
│    Yes      │    No        │     0.45       │
│    No       │    Yes       │     0.12       │
│    No       │    No        │     0.03       │
└─────────────┴──────────────┴────────────────┘
```

## 5. Prior Belief System

### 5.1 Population-Specific Priors

Priors variam por população porque a prevalência varia:

| NANDA | ICU | APS | Geriatria | Pediatria | Neonatal |
|-------|-----|-----|-----------|-----------|----------|
| 00047 | 0.32 | 0.08 | 0.22 | 0.05 | 0.15 |
| 00046 | 0.18 | 0.06 | 0.15 | 0.04 | 0.08 |
| 00200 | 0.12 | 0.03 | 0.08 | 0.02 | 0.02 |

### 5.2 Prior Sources

| Source | Code | Quality | When to Use |
|--------|------|---------|-------------|
| Literature | `literature` | GRADE A/B | Quando há estudos |
| Expert | `expert_elicit` | GRADE C | Quando não há estudos |
| Empirical | `empirical` | — | Quando há dados do sistema |
| Default | `default` | — | Fallback uniforme |

### 5.3 Prior Updates

Priors não são estáticos. O sistema atualiza priors empiricamente:

```
1. Coletar episódios: SELECT * FROM ni_memory.episodes WHERE population_id = X
2. Calcular frequência: P(00047 | ICU) = count(confirmed 00047 in ICU) / total ICU episodes
3. Comparar com prior atual
4. Se divergência significativa (χ² test, p < 0.05):
   - Sugerir atualização do prior
   - Queue para validação humana
   - Se aprovado: atualizar ni_prob.prior_beliefs
```

## 6. Entropy and Ambiguity

### 6.1 Shannon Entropy

Mede a incerteza da distribuição de hipóteses:

```
H = -Σ P(D_i) × log₂(P(D_i))
```

| Entropy | Interpretation | Action |
|---------|---------------|--------|
| < 0.5 bits | Baixa incerteza (top hypothesis domina) | Propose directly |
| 0.5–1.0 bits | Moderada | Propose + explain alternatives |
| 1.0–1.5 bits | Alta (hipóteses equiprováveis) | Suggest more data |
| > 1.5 bits | Muito alta (quase uniforme) | Flag insufficient data |

### 6.2 Ambiguity Flags

`ni_prob.ambiguity_flags` registra casos de alta incerteza:

| Flag Type | Condition | Recommended Action |
|-----------|-----------|-------------------|
| `low_confidence` | top P < 0.40 | Collect more data |
| `high_entropy` | H > 1.5 bits | Collect more data |
| `conflicting_evidence` | strong evidence for & against same D | Human review |
| `insufficient_data` | < 3 observations | Continue assessment |

## 7. Confidence Intervals

Toda probabilidade reportada vem com IC:

| Method | When Used | Formula |
|--------|-----------|---------|
| Bootstrap | Quando há amostras | Percentile method, 1000 resamples |
| Analytical | Quando há distribuição fechada | Beta distribution CI |
| Bayesian posterior | Sempre que possível | 2.5% e 97.5% quantis do posterior |

```
Report format:
  NANDA 00047: P = 0.74, IC 95% [0.68, 0.80]
  NANDA 00046: P = 0.18, IC 95% [0.12, 0.25]
  NANDA 00085: P = 0.06, IC 95% [0.02, 0.12]
```

## 8. Calibration

O sistema deve ser **bem calibrado**: quando diz 74%, deve estar certo ~74% das vezes.

### 8.1 Brier Score

```
BS = (1/N) × Σ (P_i - O_i)²

Onde:
  P_i = probabilidade prevista
  O_i = desfecho real (1 = confirmado, 0 = não)
  N = número de previsões
```

| Brier Score | Quality |
|-------------|---------|
| < 0.10 | Excelente |
| 0.10–0.15 | Bom |
| 0.15–0.25 | Aceitável |
| > 0.25 | Pobre — recalibrar |

### 8.2 Calibration Curve

Plot: predicted probability (x) vs observed frequency (y). Ideal: linha 45°.

Desvios indicam:
- **Overconfident**: prevê 80% mas acerta 60% → reduz probabilidades
- **Underconfident**: prevê 40% mas acerta 70% → aumentar probabilidades

Calibração é calculada e monitorada em `ni_learning.learning_curves`.

## 9. Schema Summary

| Table | Purpose |
|-------|---------|
| `ni_prob.probability_models` | Modelos de probabilidade (definição) |
| `ni_prob.bayesian_links` | Links condicionais entre nós |
| `ni_prob.uncertainty_distributions` | Distribuições de probabilidade |
| `ni_prob.confidence_intervals` | Intervalos de confiança |
| `ni_prob.prior_beliefs` | Priors por população |
| `ni_prob.belief_updates` | Log de atualizações bayesianas |
| `ni_prob.ambiguity_flags` | Casos de alta incerteza |
| `ni_reasoning.hypotheses` | Hipóteses com prior/posterior |
| `ni_reasoning.scores` | Scores probabilísticos por etapa |

## 10. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-02 | Reasoning Pipeline (parent) |
| NIFS-600-04 | Hypothesis Generation (feeds priors) |
| NIFS-600-05 | Differential Diagnosis (uses posteriors) |
| NIFS-600-13 | Outcome Prediction (forward simulation) |
| NIFS-700-18 | Safety Layer (ambiguity → safety) |
| NIFS-APP-F | Mathematical Models (formal definitions) |

## 11. References

- Pearl, J. (2009). Causality: Models, Reasoning and Inference
- Koller, D. & Friedman, N. (2009). Probabilistic Graphical Models
- Guyatt, G.H. et al. (2008). GRADE: An emerging consensus on rating quality of evidence
- Tanner, C. (2006). Thinking Like a Nurse: A Research-Based Model of Clinical Judgment

## 12. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — full Bayesian framework | Leivis Melo |
