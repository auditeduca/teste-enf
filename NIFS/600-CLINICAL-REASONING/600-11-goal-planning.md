# NIFS-600-11: Goal Planning

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-600-11                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o módulo de planejamento clínico — como o NIS gera, representa e executa planos de cuidado como grafos dirigidos com branches condicionais.

## 2. The Planning Problem

O enfermeiro sempre pensa em sequências condicionais:

```
Se fizer NIC A
    → NOC melhora?
        → Sim: continuar
        → Não: tentar NIC B
            → Piorou?
                → Sim: protocolo C (escalação)
                → Não: reavaliar
```

Isto não é uma lista. É um **grafo de planejamento**. O NIS modela isto explicitamente.

## 3. Plan as Directed Graph

```
[START] → [NIC 3540: Reduzir Pressão] → [EVAL: NOC 1101]
                                            │
                                   ┌────────┼────────┐
                                   │        │        │
                               improved  unchanged  deteriorated
                                   │        │        │
                              [Continue] [NIC 6540] [ESCALATE]
                                   │        │        │
                              [EVAL]   [EVAL]    [Protocol C]
                                   │        │        │
                              [Goal?]  [Goal?]   [Human Review]
```

### Node Types

| Node Type | Description | Example |
|-----------|-------------|---------|
| `action` | Intervenção a executar | NIC 3540 |
| `evaluation` | Ponto de avaliação | Medir NOC 1101 |
| `branch` | Decisão condicional | improved / unchanged / deteriorated |
| `terminal` | Fim do plano | Goal achieved |
| `escalation` | Escalar para protocolo superior | Protocol C |
| `de_escalation` | Reduzir intensidade | Diminuir frequência |

### Edge Types (Conditions)

| Condition | Description | Branch Target |
|-----------|-------------|---------------|
| `success` | NOC melhorou acima do esperado | Continue ou de-escalate |
| `failure` | NOC não mudou | Alternativa |
| `deterioration` | NOC piorou | Escalação |
| `no_change` | NOC estável sem melhora | Adicionar intervenção |
| `timeout` | Tempo limite sem melhora | Reavaliar |
| `adverse_event` | Evento adverso | Parar + escalar |
| `escalation_trigger` | Gatilho de crise | Protocolo de urgência |

## 4. Plan Generation Process

### 4.1 From Diagnosis to Plan

```
Council Decision: NANDA 00047 (74%)
    ↓
NOC Target: 1101 (Integridade Tissular)
    ↓ Current: 2, Target: 4
NIC Options: [3540, 6540, 2250, 2252]
    ↓
Graph traversal: NANDA 00047 → NIC candidates
    ↓
Rank by: evidence_grade × expected_delta × context_fit
    ↓
Select: NIC 3540 (primary) + NIC 6540 (adjunct)
    ↓
Expected outcome: NOC 1101: 2→4 in 72h
    ↓
Generate contingency branches
    ↓
Output: Plan graph
```

### 4.2 Expected Delta Calculation

```
expected_noc_delta = Σ(edge_weight(nanda→nic) × edge_weight(nic→noc) × context_modifier)

Example:
  weight(00047→3540) = 0.85
  weight(3540→1101) = 0.72
  context_modifier(ICU) = 1.1
  expected_delta = 0.85 × 0.72 × 1.1 = 0.67

  Current NOC = 2
  Expected NOC = 2 + (0.67 × 3) = 4.0  (3-point scale × delta)
```

### 4.3 Contingency Generation

Para cada plano, gerar branches automáticos:

| Primary Fails | Fallback | Escalation |
|---------------|----------|------------|
| NIC 3540 alone | Add NIC 6540 | Protocol C |
| NIC 3540 + 6540 | Add NIC 2250 | Human review |
| All NICs fail | Reassess diagnosis | Escalate to medical team |

## 5. Plan Execution Tracking

Cada nó executado é registrado:

```json
{
  "execution_id": "uuid",
  "plan_id": "uuid",
  "node_id": "uuid",
  "action_id": "uuid (→ ni_memory.actions)",
  "execution_status": "executed",
  "actual_outcome": "improved",
  "actual_noc_value": 3,
  "expected_noc_value": 3.5,
  "deviation": "slightly below expected",
  "executed_at": "2026-07-05T14:00:00Z"
}
```

## 6. Plan Adaptation

Planos não são estáticos. Adaptam-se durante execução:

| Trigger | Adaptation |
|---------|-----------|
| NOC improving faster | De-escalate (reduce frequency) |
| NOC not improving | Add adjunct intervention |
| NOC deteriorating | Escalate to protocol |
| Adverse event | Stop + escalate + human review |
| Context change (ward transfer) | Recalculate expected delta |
| New diagnosis discovered | Create new sub-plan |
| Time horizon exceeded | Reassess + possibly new plan |

## 7. Simulation Integration

Antes de executar, o plano pode ser simulado:

```
1. Digital Twin: snapshot do patient state
2. Simulation Run: MCTS com N iterations
3. Results: P(improved), P(unchanged), P(deteriorated)
4. If P(deteriorated) > 0.15: revise plan
5. If P(improved) > 0.70: approve plan
```

## 8. Schema Summary

| Table | Purpose |
|-------|---------|
| `ni_planner.plans` | Planos gerados |
| `ni_planner.plan_nodes` | Nós do grafo de plano |
| `ni_planner.plan_edges` | Transições condicionais |
| `ni_planner.plan_executions` | Execução real de cada nó |

## 9. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-02 | Reasoning Pipeline (Stage 7) |
| NIFS-600-12 | Intervention Selection (detail) |
| NIFS-600-13 | Outcome Prediction (expected delta) |
| NIFS-600-14 | Simulation (plan validation) |
| NIFS-300-17 | Goals (conceptual) |

## 10. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — plan-as-graph model | Leivis Melo |
