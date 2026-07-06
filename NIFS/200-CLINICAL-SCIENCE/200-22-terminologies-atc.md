# NIFS-200-22: Terminologies — ATC

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-200-22                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a integração do ATC (Anatomical Therapeutic Chemical Classification) no NIS.

## 2. ATC Overview

| Aspect | Value |
|--------|-------|
| Full name | Anatomical Therapeutic Chemical Classification System |
| Owner | WHO Collaborating Centre (Oslo) |
| Structure | 5 levels: anatomical → therapeutic → pharmacological → chemical → substance |
| Code format | Alfanumérico (e.g., C01CA03) |
| NIS table | `ni.medications_anvisa` (cross-mapped via `drug_references.atc_code`) |

## 3. ATC Hierarchy Example

```
C (Cardiovascular system)
└── C01 (Cardiac therapy)
    └── C01C (Cardiac stimulants)
        └── C01CA (Adrenergic and dopaminergic)
            └── C01CA03 (Norepinephrine / Noradrenalina)
```

## 4. ATC in NIS

| Use | Implementation |
|-----|---------------|
| Drug classification | Classificar medicamentos ANVISA por classe ATC |
| High-alert identification | ATC classes de alto risco → enhanced monitoring |
| Interaction checking | Mesma classe ATC → potential interaction |
| Safety goals | Cross com `ni.safety_goal_medication_cross` |

## 5. High-Alert ATC Classes

| ATC Class | Risk Level | NIS Action |
|-----------|-----------|------------|
| V (Antineoplastic) | Critical | Double check mandatory |
| N (Nervous system opioids) | High | Double check + dose validation |
| J05 (Antivirals) | Moderate | Standard monitoring |
| C01CA (Adrenergics) | High | Continuous monitoring |

## 6. NKOS Data

`drug_references.json` contem 500 medicamentos com campo `atc_code` populado. `drug_monographs.json` tem 3 monografias curadas com ATC e nursing monitoring. `medication_dictionary.json` tem 500 entries com ATC e `high_alert_medication` flag.

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-21 | RxNorm (drug nomenclature) |
| NIFS-100-06 | Clinical Safety (medication safety) |
