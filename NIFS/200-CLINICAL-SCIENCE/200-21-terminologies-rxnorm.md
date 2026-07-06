# NIFS-200-21: Terminologies — RxNorm

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-200-21                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a integração do RxNorm no NIS para normalização de nomenclatura de medicamentos.

## 2. RxNorm Overview

| Aspect | Value |
|--------|-------|
| Full name | RxNorm |
| Owner | US NLM (National Library of Medicine) |
| Purpose | Padronizar nomenclatura de medicamentos |
| Code format | Numeric (CUI) |
| NIS table | `ni.medications_anvisa` (cross-mapped) |

## 3. RxNorm in NIS

| Use | Implementation |
|-----|---------------|
| Normalização | Cross-map ANVISA → RxNorm para padrão internacional |
| Drug interactions | RxNorm enables interaction checking across drug classes |
| FHIR Medication | FHIR usa RxNorm como CodeSystem |
| Medication Agent | Council Medication Agent usa RxNorm para validação |
| High-alert identification | RxNorm terms mapeados para high_alert flag |

## 4. ANVISA ↔ RxNorm Mapping

```
ANVISA: Noradrenalina 4mg/mL → RxNorm CUI: 7388 → Standardized
ANVISA: Dipirona 500mg      → RxNorm CUI: 3236 → Standardized
ANVISA: Insulina regular    → RxNorm CUI: 2532 → Standardized
```

O NIS mantém cross-mapping bidirecional: dados ANVISA (nacional) ↔ RxNorm (internacional).

## 5. NKOS Data Integration

`drug_references.json` tem 500 medicamentos com `snomed_ct_code` que serve como bridge para RxNorm. `medication_dictionary.json` tem 500 entries nursing-specific. `drug_monographs.json` tem 3 monografias curadas com referências cruzadas.

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-22 | ATC (drug classification) |
| NIFS-800-01 | FHIR (RxNorm as Medication code) |
| NIFS-200-18 | SNOMED CT (bridge terminology) |
