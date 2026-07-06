# NIFS-300-08: Composition

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-300-08                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como conceitos complexos são compostos a partir de elementos mais simples, seguindo o modelo ISO 18104.

## 2. Compositional Model

```
Nursing Diagnosis = Focus + Judgment (+ Modifier)

NANDA 00047 "Risk of Impaired Skin Integrity"
  = Focus: "Skin integrity" (ni_iso.axis_terms)
  + Judgment: "Risk of impaired" (ni_iso.axis_terms)
```

```
Nursing Action = Focus + Action (+ Target)

NIC 3540 "Pressure Management"
  = Focus: "Skin integrity"
  + Action: "Managing" (ni_iso.action_compositions)
```

## 3. NIS Implementation

| Table | Role |
|-------|------|
| `ni_iso.axis_terms` | Armazena termos individuais dos eixos |
| `ni_iso.compositions` | Combina Focus + Judgment → diagnóstico |
| `ni_iso.action_compositions` | Combina Composition + Action → intervenção |

## 4. Composition Validation (Epistemic)

`ni_epist.epistemology_rules` tipo V3 valida:
- Todo NANDA deve ter composição ISO válida (Focus + Judgment)
- Toda NIC deve ter action_composition válida
- Termos devem existir em `axis_terms`

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-24 | ISO 18104 (standard) |
| NIFS-300-07 | Inheritance |
| NIFS-600-02 | Reasoning Pipeline (decomposes via ISO) |
