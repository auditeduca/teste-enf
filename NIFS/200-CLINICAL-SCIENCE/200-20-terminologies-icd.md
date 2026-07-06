# NIFS-200-20: Terminologies — ICD

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-200-20                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a integração do CID (Classificação Internacional de Doenças) no NIS como contexto médico, não como diagnóstico de enfermagem.

## 2. ICD Overview

| Aspect | Value |
|--------|-------|
| CID-10 | WHO, em uso no Brasil |
| CID-11 | WHO 2022, transição gradual |
| Purpose | Diagnósticos médicos |
| Code format | Alfanumérico (e.g., I21.9, J96.0) |
| NIS table | `ni.cid_diagnoses` |

## 3. ICD in NIS — Context, Not Diagnosis

> **Importante**: O NIS **não diagnostica** usando CID. O CID é **entrada de contexto** — o diagnóstico médico informa o raciocínio de enfermagem, mas não o substitui.

```
CID I21.9 (Infarto Agudo do Miocárdio) — diagnóstico médico
    ↓ Context
NANDA 00004 (Risco de Infecção) — diagnóstico de enfermagem
NANDA 00200 (Risco de Queda) — diagnóstico de enfermagem
```

## 4. CID ↔ NANDA Mapping

`ni.cid_nanda_map` relaciona diagnósticos médicos a diagnósticos de enfermagem prováveis:

```
CID I21.9 → NANDA 00004, 00200, 00046 (context-dependent)
CID J96.0 → NANDA 00032, 00033 (respiratory distress)
CID S72.0 → NANDA 00047, 00046 (fracture → immobility → skin risk)
```

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-14 | NANDA-I (nursing diagnoses) |
| NIFS-300-05 | Clinical Ontology (ICD as medical context) |
