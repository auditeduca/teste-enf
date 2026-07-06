# NIFS-600-17: Learning Loop

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-600-17                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o ciclo de aprendizado contínuo do NIS — o mecanismo que transforma desfechos reais em atualizações de peso, tornando o sistema melhor a cada caso.

## 2. The Learning Principle

> "Sem aprendizado, a IA apenas consulta conhecimento. Com aprendizado, ela evolui."

```
Plano → Execução → Desfecho → Funcionou? → Atualizar pesos → (loop)
```

## 3. Learning Loop Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    LEARNING LOOP                         │
│                                                         │
│  ┌─────────┐    ┌──────────┐    ┌──────────┐           │
│  │  Plan   │───→│ Execute  │───→│ Outcome  │           │
│  │ (Planner)│   │ (Memory) │    │ (Memory) │           │
│  └─────────┘    └──────────┘    └────┬─────┘           │
│                                      │                   │
│                              ┌───────▼───────┐          │
│                              │  Compare      │          │
│                              │  expected vs  │          │
│                              │  actual       │          │
│                              └───────┬───────┘          │
│                                      │                   │
│                              ┌───────▼───────┐          │
│                              │  Surprise     │          │
│                              │  Score        │          │
│                              └───────┬───────┘          │
│                                      │                   │
│                   ┌──────────────────┼──────────────┐   │
│                   │                  │              │   │
│              ┌────▼─────┐    ┌──────▼──────┐  ┌────▼──┐│
│              │Positive  │    │Negative     │  │Neutral││
│              │Signal    │    │Signal       │  │       ││
│              │(reward)  │    │(penalty)    │  │       ││
│              └────┬─────┘    └──────┬──────┘  └───────┘│
│                   │                 │                   │
│                   └────────┬────────┘                   │
│                            │                            │
│                   ┌────────▼────────┐                   │
│                   │  Weight Update  │                   │
│                   │  Proposal       │                   │
│                   └────────┬────────┘                   │
│                            │                            │
│                   ┌────────▼────────┐                   │
│                   │  Human          │                   │
│                   │  Validation     │                   │
│                   └────────┬────────┘                   │
│                            │                            │
│              ┌─────────────┼─────────────┐             │
│              │             │             │              │
│         ┌────▼────┐  ┌─────▼─────┐  ┌────▼────┐        │
│         │Approve  │  │Modify     │  │Reject   │        │
│         │Apply    │  │Apply mod  │  │Discard  │        │
│         └────┬────┘  └─────┬─────┘  └─────────┘        │
│              │             │                            │
│              └──────┬──────┘                            │
│                     │                                   │
│              ┌──────▼──────┐                            │
│              │  Update     │                            │
│              │  Graph      │                            │
│              │  Weights    │                            │
│              │  + Priors   │                            │
│              │  + Attention│                            │
│              └─────────────┘                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 4. Surprise Score

A medida fundamental do aprendizado é o **surprise** — quão diferente o desfecho real foi do previsto:

```
surprise_score = |expected_outcome - actual_outcome| / outcome_scale
```

| Surprise | Interpretation | Learning Intensity |
|----------|---------------|-------------------|
| 0.0–0.1 | Previsto corretamente | Minimal (confirm belief) |
| 0.1–0.3 | Pequeno desvio | Low (slight adjustment) |
| 0.3–0.5 | Desvio moderado | Medium (reconsider) |
| > 0.5 | Grande surpresa | High (strong learning signal) |

## 5. Reinforcement Signals

### 5.1 Signal Types

| Type | Reward Range | When | Example |
|------|-------------|------|---------|
| Positive | +0.3 to +1.0 | Outcome better than expected | NIC 3540 worked well |
| Negative | -1.0 to -0.3 | Outcome worse than expected | NIC 3540 failed |
| Neutral | -0.1 to +0.1 | Outcome as expected | No surprise |
| Mixed | variable | Multiple outcomes | Some improved, some not |

### 5.2 Reward Calculation

```
reward = (actual_outcome - expected_outcome) / outcome_scale
       × outcome_importance
       × discount_factor(age_of_plan)
```

### 5.3 Temporal Discount

Planos recentes têm mais peso que antigos:

```
discount = γ^(days_since_episode)
γ = 0.95 (default)

Day 0: discount = 1.00
Day 30: discount = 0.21
Day 90: discount = 0.01
```

## 6. Weight Update Mechanism

### 6.1 What Gets Updated

| Component | Table | Update Method |
|-----------|-------|--------------|
| Graph edge weight | `ni_graph.edges` | Gradient-like adjustment |
| Rule weight | `ni_rules.rule_weights` | Rule adjustment |
| Bayesian prior | `ni_prob.prior_beliefs` | Bayesian update |
| Attention weight | `ni_attention.weights` | Salience reweighting |
| Probability model | `ni_prob.probability_models` | Parameter update |

### 6.2 Update Formula (Edge Weights)

```
new_weight = old_weight + α × reward × edge_relevance

Where:
  α = learning_rate (default 0.05, adjustable)
  reward = reinforcement signal value
  edge_relevance = how much this edge contributed to the outcome
```

### 6.3 Guardrails

- **Maximum change per update**: ±0.15 (prevent radical shifts)
- **Minimum evidence**: ≥ 3 consistent signals before applying
- **Cooldown**: same edge can't be updated more than once per day
- **Rollback**: if new weight causes worse predictions, revert

## 7. Human Validation (Mandatory)

**Nenhum peso é atualizado sem validação humana.**

```
Weight Update Proposal
    ↓
Queue: ni_learning.weight_updates[status=pending]
    ↓
Human Reviewer sees:
  - What changed
  - Why (reinforcement signal)
  - Evidence (episode, outcome, surprise)
  - Impact (what predictions would change)
    ↓
Decision: Approve / Modify / Reject
    ↓
If approve: apply + log
If modify: adjust + apply + log
If reject: discard + log reason
```

## 8. Experience Replay

Para treino contínuo, experiências passadas são armazenadas em buffer:

```
ni_learning.experience_replay:
  - state_snapshot (estado no momento da decisão)
  - action_taken (o que foi feito)
  - reward (resultado)
  - next_state (estado após ação)
  - priority (prioritized replay: high-surprise → high priority)
```

Permite:
- Re-treino offline sem novos casos
- Simulação de políticas alternativas
- Análise contrafactual ("e se fizéssemos X?")

## 9. Learning Curves

Cada componente tem sua curva de aprendizado rastreada:

| Component | Metric | Target | Current |
|-----------|--------|--------|---------|
| NANDA prediction | F1 | > 0.90 | 0.87 |
| NIC selection | Accuracy | > 0.85 | 0.78 |
| NOC prediction | MAE | < 0.5 | 0.7 |
| Attention filter | Precision | > 0.95 | 0.91 |
| Calibration | Brier | < 0.15 | 0.18 |
| Council consensus | Agreement | > 0.75 | 0.72 |

Curvas são monitoradas em `ni_learning.learning_curves`.

## 10. Schema Summary

| Table | Purpose |
|-------|---------|
| `ni_learning.feedback` | Feedback clínico humano |
| `ni_learning.model_adjustments` | Ajustes derivados |
| `ni_learning.reinforcement_signals` | Sinais de reforço |
| `ni_learning.weight_updates` | Atualizações de peso (com validação) |
| `ni_learning.learning_curves` | Métricas ao longo do tempo |
| `ni_learning.experience_replay` | Buffer de experiências |

## 11. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-16 | Clinical Memory (source of episodes) |
| NIFS-600-02 | Reasoning Pipeline (Stage 10) |
| NIFS-600-13 | Outcome Prediction (expected values) |
| NIFS-700-11 | Reflection (AI self-assessment) |
| NIFS-1200-02 | Clinical Validation (learning validation) |

## 12. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — complete learning loop | Leivis Melo |
