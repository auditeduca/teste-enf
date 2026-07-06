# NIFS-600-14: Simulation

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-600-14                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | — |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o motor de simulação clínica do NIS — o mecanismo que permite testar planos em um paciente virtual antes de executá-los no paciente real.

## 2. The Simulation Principle

> "Paciente virtual → executar plano → simular → resultado provável"

O conceito de Digital Twin, mas **integrado ao raciocínio**, não apenas armazenado como dados.

```
Plano proposto
    ↓
Digital Twin (snapshot do patient state)
    ↓
Simulation Engine
    ↓
Resultado provável: P(improved)=0.72, P(unchanged)=0.18, P(deteriorated)=0.10
    ↓
Se P(deteriorated) > 0.15 → revisar plano
Se P(improved) > 0.70 → aprovar plano
    ↓
Executar plano real
```

## 3. Simulation Types

| Type | Method | When to Use | Iterations |
|------|--------|-------------|-----------|
| `monte_carlo` | Amostragem aleatória sobre distribuições | Análise de incerteza | 1000+ |
| `mcts` | Monte Carlo Tree Search | Planejamento multi-passo | 100-500 |
| `deterministic` | Modelo fechado | Cenários simples | 1 |
| `counterfactual` | "E se fizéssemos X?" | Comparação de alternativas | 2+ |
| `stress_test` | Pior caso + casos extremos | Validação de segurança | 100+ |

## 4. Monte Carlo Simulation

### 4.1 Process

```
1. Patient State: {braden: 12, glasgow: 11, pa: 90x60, ...}
2. Plan: [NIC 3540 → evaluate → NIC 6540 if no change]
3. For each iteration (N=1000):
   a. Sample from uncertainty distributions:
      - P(NIC 3540 effective) ~ Beta(7, 3) → sample: 0.68
      - P(NOC improves by 2 points) ~ Normal(1.5, 0.5) → sample: 1.8
      - P(adverse event) ~ Bernoulli(0.05) → sample: 0 (no)
   b. Simulate forward:
      - NOC after NIC 3540: 2 + 1.8 = 3.8 → round to 4 ✓
   c. Record outcome
4. Aggregate:
   - P(improved) = 720/1000 = 0.72
   - P(unchanged) = 180/1000 = 0.18
   - P(deteriorated) = 100/1000 = 0.10
   - Mean NOC: 3.6 ± 0.8
```

### 4.2 Distributions

| Parameter | Distribution | Source |
|-----------|-------------|--------|
| NIC effectiveness | Beta(α, β) | `ni_prob.uncertainty_distributions` |
| NOC improvement | Normal(μ, σ) | `ni_prob.uncertainty_distributions` |
| Adverse event | Bernoulli(p) | Historical data + safety metrics |
| Time to improvement | Lognormal(μ, σ) | `ni_memory.episodes` |
| Context modifier | Uniform(0.8, 1.2) | World Model uncertainty |

## 5. MCTS (Monte Carlo Tree Search)

Para planejamento multi-passo, MCTS explora a árvore de decisões:

```
                    [NIC 3540]
                   /          \
            improved          not improved
              / \                / \
        [continue] [de-escalate] [NIC 6540] [NIC 2250]
                                / \
                          improved  deteriorated
                            /          \
                      [continue]    [Protocol C]

MCTS:
  1. Selection: UCB1 formula to balance exploration/exploitation
  2. Expansion: add new child nodes
  3. Simulation: random rollout to terminal
  4. Backpropagation: update visit counts and values
```

| MCTS Parameter | Default | Notes |
|----------------|---------|-------|
| Iterations | 200 | Balance speed/accuracy |
| Exploration constant | 1.414 (√2) | UCB1 standard |
| Max depth | 5 | Multi-step plans |
| Time budget | 1.5s | Hard limit |

## 6. Counterfactual Analysis

"Se fizéssemos X em vez de Y, o que teria acontecido?"

```
Base scenario (actual): NIC 3540 → NOC improved 2→4
Counterfactual: NIC 2250 (colchão alternativo) → ???

Simulation:
  Base: P(improved) = 0.72 → NOC = 3.8
  CF:   P(improved) = 0.45 → NOC = 2.9

Causal effect of NIC 3540 vs 2250:
  ΔNOC = 3.8 - 2.9 = 0.9 points
  → NIC 3540 is 0.9 NOC points better than 2250 for this patient type
```

## 7. Simulation Validation

Simulações são validadas contra desfechos reais:

```
Simulated: P(improved) = 0.72, predicted NOC = 3.8
Actual: NOC = 4 (improved)

Prediction error = |3.8 - 4.0| = 0.2 (good)
Calibration: predicted 72% improved, actual = improved ✓

If systematic over/under-prediction:
  → Adjust distribution parameters
  → Update `ni_twin.simulation_validations`
  → Feed into learning loop
```

## 8. Integration with Reasoning Pipeline

```
Reasoning Pipeline:
  Stage 7 (Planning) → generates plan
      ↓
  Simulation Engine → validates plan
      ↓
  If P(deteriorated) > threshold → revise plan (loop back to Stage 7)
  If P(improved) > threshold → approve plan
      ↓
  Stage 8 (Explainability) → includes simulation results in explanation
      ↓
  "Plano aprovado com P(melhora)=72%. Simulação executada com 1000 iterações."
```

## 9. Schema Summary

| Table | Purpose |
|-------|---------|
| `ni_twin.patient_states` | Snapshot do estado do paciente |
| `ni_twin.trajectories` | Trajetórias simuladas |
| `ni_twin.simulation_runs` | Execuções de simulação |
| `ni_twin.simulation_results` | Resultados por cenário |
| `ni_twin.counterfactuals` | Análises contrafactuais |
| `ni_twin.simulation_validations` | Validação contra realidade |
| `ni_twin.outcome_feedback` | Feedback de desfechos reais |

## 10. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-15 | Digital Twin (patient model) |
| NIFS-600-11 | Goal Planning (plan to simulate) |
| NIFS-600-13 | Outcome Prediction (prediction model) |
| NIFS-600-17 | Learning Loop (validation feeds learning) |
| NIFS-700-07 | Planning (AI planning module) |

## 11. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — MC + MCTS + counterfactual | Leivis Melo |
