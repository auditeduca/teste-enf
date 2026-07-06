# NIFS-700-11: Reflection

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-700-11                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o Nurse-PaLM reflete sobre suas próprias recomendações — auto-avaliação antes de emitir output clínico.

## 2. Reflection Loop

```
Draft Recommendation (from reasoning)
    ↓
Reflection Questions:
  - "Esta recomendação é consistente com todas as evidências?"
  - "Existem contraindicações não verificadas?"
  - "O paciente tem alergias ou condições que afetam esta recomendação?"
  - "Esta recomendação está alinhada com o protocolo institucional?"
  - "O nível de confiança justifica a ação recomendada?"
    ↓
If issues found → revise recommendation
If no issues → finalize with confidence
```

## 3. Reflection Checks

| Check | Type | Action on Fail |
|-------|------|---------------|
| Evidence consistency | All evidence supports recommendation? | Downgrade confidence |
| Safety verification | No contraindications? | Block or add alert |
| Protocol alignment | Matches institutional protocol? | Add deviation note |
| Completeness | All relevant NANDAs considered? | Add differential |
| Calibration | Confidence matches historical accuracy? | Adjust confidence |
| Bias check | Population-specific bias? | Add caveat |

## 4. Clinical Engine V8 Reference

O `bayesianDiagnosis.js` já implementa uma forma de reflexão — calcula **variance** e **confidence**:

```javascript
const variance = vals.reduce((a, b) => a + (b - probability) ** 2, 0) / vals.length;
const confidence = 1 - Math.min(1, Math.sqrt(variance) / 0.3);
```

Alta variance → baixa confidence → reflexão detecta incerteza.

## 5. NIS Implementation

| Table | Role |
|-------|------|
| `ni_reasoning.steps` (type=reflection) | Reflection checkpoints |
| `ni_reasoning.trace` | Reflection reasoning trace |
| `ni_explain.recommendation_reasons` | Reflection output |
| `ni_epist.verification_log` | Epistemic verification |

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-19 | Explainability (reflection feeds explanation) |
| NIFS-700-12 | Verification (post-reflection check) |
| NIFS-700-18 | Safety Layer (reflection includes safety) |
