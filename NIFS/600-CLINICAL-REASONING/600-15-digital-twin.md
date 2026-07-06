# NIFS-600-15: Digital Twin

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-600-15                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o modelo de Digital Twin do paciente no NIS — uma representação virtual que espelha o estado clínico real e permite simular intervenções antes de executá-las.

## 2. What is a Clinical Digital Twin?

Um Digital Twin clínico é uma **cópia computacional do paciente** que:

1. **Espelha** o estado atual (sinais vitais, escores, diagnósticos, plano)
2. **Recorda** a trajetória histórica (série temporal de estados)
3. **Prevê** futuros possíveis (simulação de intervenções)
4. **Aprende** com desfechos reais (validação e calibração)

```
Paciente Real          Digital Twin
┌──────────┐          ┌──────────────┐
│ Braden 12│ ──sync──→│ Braden 12    │
│ Glasgow 11│ ──sync──→│ Glasgow 11   │
│ PA 90x60 │ ──sync──→│ PA 90x60     │
│ NIC 3540 │ ──sync──→│ NIC 3540     │
└──────────┘          └──────┬───────┘
                             │
                      ┌──────▼───────┐
                      │  Simulate    │
                      │  "What if    │
                      │   NIC 6540?" │
                      └──────┬───────┘
                             │
                      ┌──────▼───────┐
                      │  Predicted   │
                      │  NOC = 3.8   │
                      │  P(imp)=0.72 │
                      └──────────────┘
```

## 3. Patient State Model

### 3.1 State Components

```json
{
  "state_id": "uuid",
  "patient_identifier": "hash_xxx",
  "captured_at": "2026-07-05T10:00:00Z",
  "vital_signs": {
    "bp_systolic": 90,
    "bp_diastolic": 60,
    "heart_rate": 110,
    "respiratory_rate": 22,
    "spo2": 92,
    "temperature": 37.5
  },
  "assessment_scores": {
    "braden": 12,
    "glasgow": 11,
    "news2": 7,
    "pain_scale": 3
  },
  "active_diagnoses": ["00047", "00046"],
  "active_interventions": ["NIC:3540", "NIC:6540"],
  "noc_current": {
    "1101": 2,
    "0413": 3
  },
  "medications": [
    {"med_id": "uuid", "name": "Noradrenalina", "dose": "0.2mcg/kg/min"}
  ],
  "context": {
    "ward": "ICU",
    "population": "ICU",
    "day_of_admission": 3,
    "post_op_day": 2
  }
}
```

### 3.2 State Transitions

O twin registra transições de estado ao longo do tempo:

```
Day 1: Braden=14, Glasgow=13, NOC=3 → state: moderate_risk
    ↓ transition: deterioration
Day 2: Braden=12, Glasgow=11, NOC=2 → state: high_risk
    ↓ intervention: NIC 3540 started
Day 3: Braden=13, Glasgow=12, NOC=2 → state: high_risk (improving)
    ↓ transition: improvement
Day 4: Braden=15, Glasgow=14, NOC=3 → state: moderate_risk
    ↓ transition: stabilization
Day 5: Braden=18, Glasgow=15, NOC=4 → state: stable
```

Cada transição é armazenada em `ni_twin.trajectories` com:
- Estado anterior
- Estado posterior
- Evento que causou a transição (intervenção, mudança clínica, medicação)
- Tempo entre estados
- Nível de confiança na causalidade

## 4. Twin → Simulation Pipeline

```
1. Snapshot: Capture current patient state → ni_twin.patient_states
2. Clone: Create virtual copy with uncertainty distributions
3. Inject Plan: Apply proposed interventions to the twin
4. Simulate: Run Monte Carlo / MCTS over the twin
5. Predict: Generate outcome probabilities
6. Compare: If multiple plans, compare predicted outcomes
7. Recommend: Choose plan with best expected outcome + lowest risk
8. Validate: After real execution, compare actual vs predicted
```

## 5. Trajectory Learning

O twin aprende com cada paciente:

```
For each patient:
  1. Record all state transitions over time
  2. Record interventions and their outcomes
  3. Build trajectory model: "Given state X + intervention Y → state Z with P"
  4. Aggregate across patients (population-level trajectories)
  5. Use as priors for future simulations
```

### 5.1 Trajectory Patterns

| Pattern | Description | Example |
|---------|-------------|---------|
| `recovery_curve` | Melhora gradual esperada | Braden 12→14→16→18 over 5 days |
| `deterioration_curve` | Declínio esperado sem intervenção | Braden 12→10→8 without intervention |
| `crisis_threshold` | Ponto de deterioração aguda | SpO2 < 85% triggers rapid decline |
| `stabilization_plateau` | Ponto de estabilidade | Braden stabilizes at 16 |
| `oscillation_pattern` | Flutuação entre estados | Pain 3→7→3→7 (inadequate management) |

## 6. Outcome Feedback Loop

```
Simulation predicts: NOC = 3.8 ± 0.8 (72h)
    ↓
Real outcome: NOC = 4.0 at 72h
    ↓
Prediction error: |3.8 - 4.0| = 0.2 (within CI)
    ↓
Calibration: good (predicted 72% improvement, actual = improved)
    ↓
If systematic bias detected:
    ↓
Adjust distribution parameters
    ↓
Update `ni_twin.outcome_feedback`
    ↓
Feed into `ni_learning.reinforcement_signals`
    ↓
Improve future simulations
```

## 7. Population-Level Twins

Além de twins individuais, o NIS mantém **twins populacionais**:

| Population Twin | Use Case |
|----------------|----------|
| ICU adulto | Priors para pacientes UTI |
| Pediatria | Priors para pacientes pediátricos |
| Neonatal | Priors para recém-nascidos |
| Pós-operatório | Priors para pós-cirúrgicos |
| Sepse | Priors para pacientes sépticos |

Population twins fornecem:
- Trajectory templates (curvas canônicas)
- Prior distributions (parâmetros para simulação)
- Expected outcomes (baseline para comparação)
- Risk profiles (distribuição de risco por população)

## 8. Schema Summary

| Table | Purpose |
|-------|---------|
| `ni_twin.patient_states` | Snapshots de estado do paciente |
| `ni_twin.trajectories` | Sequências de transições |
| `ni_twin.outcome_feedback` | Feedback de desfechos reais |
| `ni_twin.simulation_runs` | Execuções de simulação no twin |
| `ni_twin.simulation_results` | Resultados preditos |
| `ni_twin.counterfactuals` | Cenários alternativos |
| `ni_twin.simulation_validations` | Validação predito vs real |

## 9. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-14 | Simulation (engine that runs on twin) |
| NIFS-600-13 | Outcome Prediction (prediction models) |
| NIFS-600-16 | Clinical Memory (episodes feed twin learning) |
| NIFS-300-11 | States (conceptual state model) |
| NIFS-500-09 | Temporal Graph (trajectory as graph) |

## 10. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — patient twin + trajectory + population twins | Leivis Melo |
