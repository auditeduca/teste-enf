# NIFS-1200-02: Clinical Validation

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-1200-02                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o NIS valida clinicamente cada recomendação — garantindo que o sistema produz resultados corretos, seguros e calibrados antes de chegar ao enfermeiro.

## 2. Validation Layers

```
┌─────────────────────────────────────────────────────┐
│              VALIDATION PYRAMID                      │
│                                                     │
│  Layer 4: Clinical Outcome Validation               │
│  (desfecho real vs predito — pós execução)          │
│                                                     │
│  Layer 3: Expert Review Validation                  │
│  (enfermeiros especialistas avaliam recomendações)  │
│                                                     │
│  Layer 2: Test Case Validation                      │
│  (casos clínicos rotulados — pré produção)          │
│                                                     │
│  Layer 1: Structural Validation                     │
│  (códigos existem, relações válidas, P(x) presente) │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## 3. Layer 1: Structural Validation

Automática, em toda recomendação:

| Check | Rule | Action if Fail |
|-------|------|---------------|
| Code exists | NANDA/NIC/NOC in graph | Block output |
| Relationship exists | Edge in graph | Flag warning |
| Probability present | P(x) in [0,1] | Block output |
| Confidence interval | IC present and valid | Block output |
| Explanation present | Trace exists | Block output |
| Disclaimer present | "IA propõe, enfermeiro decide" | Append |
| No hallucinated codes | All codes validated against DB | Block + log |

## 4. Layer 2: Test Case Validation

Casos clínicos rotulados em `ni_test.validation_cases`:

### 4.1 Test Case Structure

```json
{
  "case_id": "uuid",
  "case_name": "Braden 12 → NANDA 00047",
  "calc_id": "BRADEN",
  "input": {
    "braden_score": 12,
    "population": "ICU",
    "mobility": "bedridden",
    "postop": true
  },
  "expected": {
    "primary_diagnosis": "00047",
    "min_probability": 0.60,
    "expected_interventions": ["3540", "6540"],
    "expected_outcome": "1101"
  }
}
```

### 4.2 Test Execution

```python
def run_validation_case(case):
    session = start_reasoning_session(case.input)
    results = {
        "predicted_diagnosis": session.final_nanda_code,
        "predicted_probability": session.final_confidence,
        "predicted_interventions": extract_nics(session.plan),
        "pass": True
    }
    
    # Check diagnosis
    if results.predicted_diagnosis != case.expected.primary_diagnosis:
        results.pass = False
        results.fail_reason = "wrong_diagnosis"
    
    # Check probability
    if results.predicted_probability < case.expected.min_probability:
        results.pass = False
        results.fail_reason = "low_confidence"
    
    # Check interventions
    for expected_nic in case.expected.expected_interventions:
        if expected_nic not in results.predicted_interventions:
            results.pass = False
            results.fail_reason = "missing_intervention"
    
    return results
```

### 4.3 Test Suite Categories

| Category | Count | What It Tests |
|----------|-------|--------------|
| `braden_to_nanda` | 20 | Braden scores → correct NANDA |
| `glasgow_to_nanda` | 15 | Glasgow scores → correct NANDA |
| `news2_to_escalation` | 10 | NEWS2 → correct escalation |
| `medication_safety` | 25 | Medication interactions detected |
| `council_consensus` | 10 | Multi-agent consensus correct |
| `edge_cases` | 15 | Atypical presentations |
| `adverse_events` | 10 | Adverse event detection |
| **Total** | **105** | Full suite |

### 4.4 Regression Testing

Toda mudança de peso, regra ou evidência dispara regression tests:

```
Weight update applied
    ↓
Run full test suite (105 cases)
    ↓
If any case that previously passed now fails:
    ↓
ALERT: regression detected
    ↓
Rollback weight update
    ↓
Notify clinical governance
```

## 5. Layer 3: Expert Review

### 5.1 Blind Review

Enfermeiros especialistas avaliam recomendações sem saber se vieram da IA ou de humano:

```
10 recomendações (5 AI + 5 human)
    ↓
Expert rates each: correct? safe? useful? explained?
    ↓
If AI scores ≥ human scores: system is viable
If AI scores < human: identify gaps
```

### 5.2 Review Metrics

| Metric | Target | Scale |
|--------|--------|-------|
| Diagnostic accuracy | > 90% | % correct diagnosis |
| Safety | 100% | % with no safety issues |
| Usefulness | > 4/5 | Expert rating |
| Explanation quality | > 4/5 | Expert rating |
| Trust calibration | 60-80% acceptance | Not too high, not too low |

## 6. Layer 4: Outcome Validation

Pós-execução, compara predito com real:

```
Predicted: NANDA 00047, P=0.74, NOC 2→4 in 72h
    ↓
Actual: NANDA 00047 confirmed, NOC reached 4 in 68h
    ↓
Prediction accuracy: ✓
Calibration: P=0.74, actual=yes → well calibrated

If actual != predicted:
    ↓
Root cause analysis
    ↓
Was it: wrong data? wrong reasoning? wrong weight? atypical case?
    ↓
Feed into Learning Loop
```

## 7. Continuous Monitoring

| Metric | Frequency | Alert Threshold |
|--------|-----------|----------------|
| Diagnostic F1 | Daily | < 0.85 |
| Brier score | Weekly | > 0.15 |
| Hallucination rate | Daily | > 2% |
| Safety veto rate | Daily | > 5% |
| Human reject rate | Weekly | > 40% or < 10% |
| Adverse event rate | Real-time | > 0% |
| Calibration drift | Monthly | |predicted - actual| > 0.10 |

## 8. Schema Summary

| Table | Purpose |
|-------|---------|
| `ni_test.validation_cases` | Casos de teste rotulados |
| `ni_test.expected_results` | Resultados esperados |
| `ni_test.regression_tests` | Execuções de regressão |
| `ni_obs.error_logs` | Erros em produção |
| `ni_ops.inference_metrics` | Métricas de inferência |

## 9. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-1200-01 | Testing (technical testing) |
| NIFS-1200-03 | Benchmark (performance benchmarks) |
| NIFS-1200-08 | Evidence Quality (evidence validation) |
| NIFS-100-06 | Clinical Safety (safety validation) |
| NIFS-600-17 | Learning Loop (validation feeds learning) |

## 10. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — 4-layer validation + 105 test cases | Leivis Melo |
