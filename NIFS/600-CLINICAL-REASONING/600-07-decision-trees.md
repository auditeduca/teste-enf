# NIFS-600-07: Decision Trees

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-600-07                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o NIS representa e executa árvores de decisão clínica — a estrutura determinística que complementa o raciocínio probabilístico.

## 2. Trees vs. Bayes

O NIS usa **ambos** raciocínio determinístico (árvores) e probabilístico (Bayes):

| Aspect | Decision Tree | Bayesian Network |
|--------|--------------|-----------------|
| Logic | If-then-else | P(D\|E) |
| Output | Yes/No + action | P(x) + IC |
| Transparency | Maximal (trivial to trace) | High (trace available) |
| Flexibility | Rigid (rules are fixed) | Flexible (weights adapt) |
| Learning | Manual update | Automatic via learning loop |
| Use case | Protocols, safety gates | Diagnosis, prediction |

**Princípio**: Árvores para **ações obrigatórias** (protocolos, safety). Bayes para **decisões incertas** (diagnóstico, predição).

## 3. Tree Structure

```
Node: Braden score
├── ≤ 9 (very high risk)
│   ├── ICU? 
│   │   ├── Yes → NIC 3540 + NIC 6540 + Protocol C
│   │   └── No  → NIC 3540 + NIC 6540 + reassess q2h
│   └── Postop?
│       ├── Yes → add NIC 2252 (wound surveillance)
│       └── No  → continue
├── 10-12 (high risk)
│   ├── ICU?
│   │   ├── Yes → NIC 3540 + NIC 6540
│   │   └── No  → NIC 3540
│   └── Mobility?
│       ├── Bedridden → add NIC 6540
│       └── Assisted  → continue
├── 13-14 (moderate risk)
│   └── NIC 3540 + reassess q4h
├── 15-18 (low risk)
│   └── NIC 2250 (skin surveillance) + reassess q shift
└── ≥ 19 (minimal risk)
    └── Routine care, no specific NIC
```

## 4. Tree Node Types

| Node Type | Description | Example |
|-----------|-------------|---------|
| `condition` | Evaluates a clinical variable | "Braden ≤ 12?" |
| `action` | Executes an intervention | "Start NIC 3540" |
| `branch` | Decision point with multiple paths | "ICU? Yes/No" |
| `terminal` | End of path, output recommendation | "NIC 3540 + 6540" |
| `alert` | Safety alert, not action | "High risk — notify charge nurse" |
| `escalation` | Escalate to higher authority | "Human review required" |

## 5. Rule-Based Decision Trees

As regras em `ni_rules.decision_rules` são a implementação das árvores:

### 5.1 Rule Structure

```
Rule: "Braden ≤ 12 AND ICU → NANDA 00047 + NIC 3540"

Conditions (ni_rules.rule_conditions):
  1. braden_score <= 12 (order: 1, operator: LTE, value: 12)
  2. population = 'ICU' (order: 2, operator: EQ, value: 'ICU')

Actions (ni_rules.rule_actions):
  1. set_diagnosis: NANDA 00047 (order: 1)
  2. recommend_intervention: NIC 3540 (order: 2)
  3. recommend_intervention: NIC 6540 (order: 3)

Weights (ni_rules.rule_weights):
  nanda_to_nic: 0.85 (00047 → 3540)
  nanda_to_nic: 0.72 (00047 → 6540)
```

### 5.2 Rule Evaluation

```python
def evaluate_rules(observations, rules):
    triggered = []
    for rule in rules:
        conditions_met = True
        for condition in rule.conditions:
            if not evaluate_condition(condition, observations):
                conditions_met = False
                break
        if conditions_met:
            triggered.append(rule)
    return triggered
```

### 5.3 Conflict Resolution

Multiple rules may fire simultaneously:

| Situation | Resolution |
|-----------|-----------|
| Two rules suggest same NANDA | Merge, use higher weight |
| Two rules suggest different NANDA | Run Bayesian to resolve |
| Rule contradicts Bayesian | Bayesian wins for diagnosis, rule wins for action |
| Safety rule fires | Always takes priority (veto power) |

## 6. Safety Decision Trees

Safety gates são árvores não-negociáveis:

```
Observation: Glasgow = 7
    ↓
Safety Tree: Glasgow < 8?
    ├── Yes → ESCALATE immediately
    │   ├── Notify charge nurse
    │   ├── Activate airway protocol
    │   ├── Block all non-urgent recommendations
    │   └── Require human confirmation for any action
    └── No → Continue normal reasoning
```

Safety trees **não produzem probabilidades** — produzem ações obrigatórias.

## 7. Protocol-as-Tree

Protocolos clínicos (`ni_protocol.protocols`) são árvores de decisão sequenciais:

```
Protocol: Sepse Bundle (3h)
    ├── Step 1: Lactate measured? 
    │   ├── Yes → continue
    │   └── No → Order lactate
    ├── Step 2: Blood cultures drawn?
    │   ├── Yes → continue
    │   └── No → Draw cultures before antibiotics
    ├── Step 3: Broad-spectrum antibiotics
    │   ├── Within 1h? → continue
    │   └── > 1h → ALERT: delayed antibiotic
    ├── Step 4: Fluid resuscitation (30mL/kg crystalloid)
    └── Step 5: Reassess lactate at 3h
```

## 8. Tree vs. Graph

| Feature | Decision Tree | Knowledge Graph |
|---------|--------------|----------------|
| Structure | Hierarchical, acyclic | Network, cyclic |
| Path | Single path from root to leaf | Multiple paths |
| Output | One recommendation | Multiple hypotheses |
| Flexibility | Fixed conditions | Weighted edges |
| Use | Protocols, safety, algorithms | Diagnosis, exploration |

## 9. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-02 | Reasoning Pipeline (uses trees for safety gates) |
| NIFS-600-08 | Bayesian Network (probabilistic complement) |
| NIFS-300-20 | Protocols (protocol-as-tree) |
| NIFS-100-06 | Clinical Safety (safety trees) |

## 10. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — trees + rules + safety gates | Leivis Melo |
