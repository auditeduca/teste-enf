# NIFS-700-07: Planning

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-700-07                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o Nurse-PaLM planeja intervenções clínicas — do diagnóstico à execução ao reavaliamento.

## 2. Planning Architecture

```
Diagnosis (NANDA with P > threshold)
    ↓
Goal Setting (NOC target)
    ↓
Intervention Selection (NIC candidates)
    ↓
Plan Optimization (MPC / MCTS)
    ↓
Execution Plan (ordered steps)
    ↓
Contingency Branches (if-then rules)
    ↓
Reassessment Schedule
```

## 3. Clinical Engine V8 Reference

O `mpcController.js` implementa **Model Predictive Control**:

```javascript
// For each candidate NIC:
//   1. Simulate horizon=6 steps ahead with particle filter
//   2. Compute expected cost (deviation from target state)
//   3. Select NIC that minimizes cost + intervention_cost
//
// Result: optimal NIC recommendation with expected outcome %

const result = mpcController(particles, horizon=6);
// → { entity_code: "NIC_2500", expectedOutcome: "Melhora ~42% vs observação" }
```

O `mctsClinical.js` implementa **Monte Carlo Tree Search** para APGAR:

```javascript
// APGAR MCTS with 4 candidate NICs:
//   AIRWAY_MANAGEMENT: { scoreDelta: +2.8, riskReduction: 0.35, cost: 0.15 }
//   VITAL_SIGNS_MONITORING: { scoreDelta: +1.2, riskReduction: 0.18, cost: 0.08 }
//   POSITIONING: { scoreDelta: +0.9, riskReduction: 0.12, cost: 0.05 }
//   OBSERVE: { scoreDelta: -0.5, riskReduction: -0.25, cost: 0.02 }
//
// Reward = clinical_outcome - risk_penalty - intervention_cost + user_comprehension
```

## 4. Plan Structure

```json
{
  "plan_id": "uuid",
  "session_id": "uuid",
  "diagnosis": "NANDA_00047",
  "goal": { "noc_code": "NOC_1101", "target_delta": "+1", "timeframe": "48h" },
  "steps": [
    { "order": 1, "nic_code": "NIC_3540", "timing": "immediate", "priority": "high" },
    { "order": 2, "nic_code": "NIC_2250", "timing": "q2h", "priority": "medium" }
  ],
  "contingencies": [
    { "condition": "NOC unchanged at 24h", "action": "escalate to NIC_2250" },
    { "condition": "NOC deteriorated", "action": "activate protocol C" }
  ],
  "reassessment": { "tool": "BRADEN", "frequency": "q24h" },
  "optimizer": "MPC",
  "confidence": 0.77
}
```

## 5. NIS Implementation

| Table | Role |
|-------|------|
| `ni_planner.plans` | Plan container |
| `ni_planner.plan_nodes` | Steps |
| `ni_planner.plan_edges` | Transitions/contingencies |
| `ni_planner.plan_simulations` | MPC/MCTS results |
| `ni_ops.nursing_care_plans` | Executed plans |

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-11 | Goal Planning (cognitive layer) |
| NIFS-600-12 | Intervention Selection |
| NIFS-600-14 | Simulation (MCTS) |
| NIFS-500-07 | Clinical Pathways (plan = pathway + branches) |
