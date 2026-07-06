# NIFS-300-14: Assessments

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-300-14                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir assessments como a fase estruturada de coleta e interpretação que inicia o raciocínio clínico.

## 2. Assessment Structure

```
Assessment
├── Tool/Calculator (100 available)
│   ├── Parameters (inputs)
│   ├── Formula (calculation)
│   ├── Score range (min-max)
│   └── Interpretation bands (severity + action)
├── Findings (abnormal results)
├── Triggered hypotheses (NANDA candidates)
└── Tool intelligence (connections to other tools)
```

## 3. NIS Implementation

| Component | Table | Records |
|-----------|-------|---------|
| Calculator definitions | `ni_cog.calculator_mappings` + NKOS `calculator_definitions.json` | 100 |
| Assessment log | `ni.assessment_log` | runtime |
| Decision trees | `ni_cog.calculator_nnn_cross` + NKOS `clinical_decision_trees.json` | 50 trees |
| APGAR pilot (6 dimensions) | content + evidence + medication + protocol + simulation + safety | template |

## 4. Assessment → Reasoning Bridge

```
Calculator executed (Braden = 12)
    ↓ interpretation_band: "high risk" (severity=high)
    ↓ ni_attention: salience=0.85, urgency=4
    ↓ ni_reasoning: step_type=observation
    ↓ Triggers hypothesis: NANDA 00047 (P=0.87)
    ↓ Suggests tools: TOOL.MORSE (fall risk), TOOL.NUTRITION
```

## 5. Clinical Intelligence Package (APGAR Model)

Cada calculadora deve ter 6 dimensões (APGAR é o template):

| Dimension | Content |
|-----------|---------|
| Content by profile | Student, technician, nurse, academic, manager |
| Evidence | Primary sources with DOI, GRADE level |
| Medication context | Related drugs, 9 Rights |
| Protocols | Timing, actions, escalation |
| Simulation | Scenarios with probabilities |
| Safety goals | WHO IPSG customized |

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-03 | Assessment (clinical process) |
| NIFS-600-03 | Assessment Pipeline |
| NIFS-300-13 | Findings (assessment output) |
