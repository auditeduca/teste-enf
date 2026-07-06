# NIFS-600-03: Assessment Pipeline

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-600-03                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o pipeline de avaliação clínica — como observações brutas são coletadas, normalizadas, validadas e transformadas em dados estruturados que alimentam o raciocínio.

## 2. Assessment Sources

| Source | Type | Input Format | Frequency |
|--------|------|-------------|-----------|
| Manual entry | Nurse input | Form/structured | On demand |
| Vital signs monitor | Device | HL7/FHIR Observation | Continuous |
| Assessment scales | Calculator | Score (Braden, Glasgow, etc.) | Scheduled |
| Lab results | LIS | FHIR Observation | On result |
| EHR sync | External | FHIR Bundle | Real-time |
| Patient report | Interview | Free text → NLP | On assessment |
| Protocol checklist | Protocol engine | Structured form | Per protocol |

## 3. Pipeline Stages

```
Raw Input
    ↓
Stage 1: Ingest — receive data in any format
    ↓
Stage 2: Normalize — convert to NIS canonical format
    ↓
Stage 3: Validate — check plausibility and completeness
    ↓
Stage 4: Score — run calculators if applicable
    ↓
Stage 5: Attention — filter critical from noise
    ↓
Stage 6: Store — persist to temporal graph + memory
    ↓
Stage 7: Trigger — fire reasoning if threshold met
```

### 3.1 Ingest

```
Accepts: JSON, FHIR Observation, HL7 v2, manual form, device stream
Output: Raw observation record (unvalidated)
Table: ni_temporal.observations (status=pending)
```

### 3.2 Normalize

Convert everything to canonical NIS format:

```json
{
  "observation_id": "uuid",
  "patient_identifier": "hash_xxx",
  "observation_type": "vital_sign | assessment_score | lab_result | clinical_finding",
  "observation_code": "LOINC:8867-4 | CALC:BRADEN | CUSTOM",
  "value": 12,
  "unit": "score | mmHg | bpm | °C",
  "ucum_unit": "1 | mm[Hg] | /min | Cel",
  "observed_at": "2026-07-05T10:00:00Z",
  "source": "manual | monitor | lab | ehr",
  "reliability": "verified | unverified | device"
}
```

### 3.3 Validate

| Check | Rule | Action if Fail |
|-------|------|---------------|
| Range check | PA: 20-300 mmHg, HR: 20-250 bpm, etc. | Flag implausible, request correction |
| Completeness | Required fields present | Flag missing, request data |
| Temporal order | observed_at not in future | Correct or flag |
| Duplicate check | Same observation within 60s | Merge or discard duplicate |
| Unit consistency | UCUM unit valid for code | Flag, attempt conversion |

### 3.4 Score

If observation is a calculator input, run the calculator:

```
Input: Braden subscores (sensory, moisture, activity, mobility, nutrition, friction)
    ↓ Calculator engine
Output: Braden total = 12
    ↓
ni_cog.calculator_mappings: Braden → NANDA 00047 (risk)
    ↓
ni_temporal.observations: score = 12
    ↓
Trigger reasoning if score crosses threshold
```

### 3.5 Attention

Feed normalized observations to Clinical Attention module (NIFS-600-10):

```
All validated observations
    ↓ Clinical Attention
6 critical (attention_score > threshold)
194 filtered
    ↓
Only critical observations enter reasoning pipeline
```

### 3.6 Store

Persist to multiple stores:

| Store | What | Table |
|-------|------|-------|
| Temporal graph | Time series of observations | `ni_temporal.observations` |
| Clinical events | Significant events | `ni_temporal.clinical_events` |
| Episode memory | If in active episode | `ni_memory.observations` |
| Assessment log | Calculator results | `ni.assessment_log` |

### 3.7 Trigger

Fire reasoning pipeline if any condition met:

| Condition | Threshold | Action |
|-----------|-----------|--------|
| New critical observation | attention_score > 0.80 | Start reasoning session |
| Calculator crossing risk threshold | Braden ≤ 12, Glasgow ≤ 8, NEWS2 ≥ 7 | Start reasoning + alert |
| Deterioration trend | 2+ declining values in sequence | Start reasoning + alert |
| Scheduled reassessment | Timer fires | Start assessment cycle |
| Manual request | Nurse requests | Start reasoning session |

## 4. Assessment Quality Score

Each assessment receives a quality score:

```
quality = completeness × timeliness × reliability × diversity

completeness: % of expected observations present (0-1)
timeliness: 1.0 if < 1h old, 0.5 if < 6h, 0.2 if > 6h
reliability: 1.0 verified, 0.7 device, 0.5 unverified
diversity: coverage of clinical domains (0-1)
```

| Quality | Interpretation | Action |
|---------|---------------|--------|
| > 0.80 | High quality | Proceed with reasoning |
| 0.50–0.80 | Moderate | Proceed with caution flag |
| < 0.50 | Low quality | Request more data before reasoning |

## 5. Gordon's Functional Health Patterns

O NIS usa os 11 padrões funcionais de Gordon como framework de avaliação:

| # | Pattern | What It Assesses | NIS Mapping |
|---|---------|-----------------|-------------|
| 1 | Health Perception-Management | How patient perceives health | `ni_cog.gordon_patterns` |
| 2 | Nutritional-Metabolic | Nutrition, hydration, skin | Braden, BMI |
| 3 | Elimination | Bowel, bladder | Output tracking |
| 4 | Activity-Exercise | Mobility, ADLs | Braden mobility |
| 5 | Sleep-Rest | Sleep quality, rest | Sleep assessment |
| 6 | Cognitive-Perceptual | Mental status, pain | Glasgow, pain scale |
| 7 | Self-Perception-Self-Concept | Body image, self-esteem | Psychosocial |
| 8 | Role-Relationship | Family, social roles | Social assessment |
| 9 | Sexuality-Reproductive | Sexual health | Reproductive history |
| 10 | Coping-Stress Tolerance | Stress, coping mechanisms | Psychosocial |
| 11 | Value-Belief | Spiritual, cultural values | Cultural assessment |

Assessment completeness = % of applicable Gordon patterns assessed.

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-03 | Assessment (clinical science) |
| NIFS-600-01 | Clinical Workflow (parent) |
| NIFS-600-02 | Reasoning Pipeline (Stage 1) |
| NIFS-600-10 | Clinical Attention (Stage 5) |
| NIFS-200-14 | NANDA (diagnoses from assessment) |

## 7. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — 7-stage pipeline + Gordon patterns | Leivis Melo |
