# NIFS-300-12: Observations

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-300-12                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir observações clínicas como a entrada primária do pipeline de raciocínio.

## 2. Observation Types

| Type | Source | Example | Coding |
|------|--------|---------|--------|
| Vital sign | Monitor/manual | PA, FC, FR, SpO2, Temp | LOINC |
| Lab result | Laboratory | Glicemia, Creatinina, K+ | LOINC |
| Assessment score | Calculator | Braden, Glasgow, NEWS2 | Tool code |
| Clinical finding | Nurse observation | "Skin breakdown on sacrum" | SNOMED CT |
| Patient report | Interview | "Pain 8/10" | LOINC/NOC |
| Device data | Continuous monitor | ECG, capnography | LOINC/proprietary |

## 3. NIS Implementation

| Table | Role |
|-------|------|
| `ni_temporal.observations` | Single observation records |
| `ni_temporal.time_series` | Aggregated metrics over time |
| `ni.assessment_log` | Calculator results |
| `ni_memory.observations` | Episodic memory of observations |
| `ni_attention.attention_signals` | Filtered/weighted observations |

## 4. Observation → Attention → Reasoning

```
200 raw observations
    ↓ Clinical Attention filter (salience, urgency, priority)
6 critical observations
    ↓ Reasoning pipeline
Hypotheses generated
```

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-03 | Assessment (clinical process) |
| NIFS-600-10 | Clinical Attention (filtering) |
| NIFS-600-02 | Reasoning Pipeline (observations as input) |
