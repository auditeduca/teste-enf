# NIFS-100-04: Human-Centered AI

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-100-04                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o princípio fundamental de que a IA do NIS **augmenta** o julgamento do enfermeiro — nunca substitui.

## 2. The Core Principle

> "A IA propõe. O enfermeiro decide. Sempre."

O NIS é um sistema de **apoio** à decisão, não um sistema de **tomada** de decisão. Esta distinção é não-negociável e permeia toda a arquitetura.

## 3. The Spectrum of AI Autonomy

```
┌─────────────────────────────────────────────────────────────┐
│              NÍVEL DE AUTONOMIA DA IA                        │
│                                                             │
│  Nível 0: Sem IA           [────]                           │
│  Nível 1: Informação       [██──] ← NIS está aqui           │
│  Nível 2: Sugestão         [████] ← NIS máximo aqui         │
│  Nível 3: Recomendação     [████] ← Com validação humana    │
│  Nível 4: Ação automática  [────] ← NÃO PERMITIDO           │
│  Nível 5: Autonomia total  [────] ← NÃO PERMITIDO           │
└─────────────────────────────────────────────────────────────┘
```

| Level | NIS Behavior | Human Role |
|-------|-------------|------------|
| Informação | "Braden=12, Glasgow=11" | Enfermeiro interpreta |
| Sugestão | "Possível 00047 (74%)" | Enfermeiro decide |
| Recomendação | "Recomendo NIC 3540 + 6540" | Enfermeiro aceita/modifica/rejeita |
| Ação automática | **NUNCA** | — |

## 4. Human-in-the-Loop Architecture

```
┌──────────────────────────────────────────────┐
│              HUMAN-IN-THE-LOOP                │
│                                              │
│  AI Engine                                    │
│  ├─ Reasoning Pipeline                        │
│  ├─ Council Deliberation                      │
│  └─ Output: Recommendation + P(x) + Trace    │
│       ↓                                      │
│  ┌─────────────────┐                         │
│  │  Human Gateway   │                         │
│  │  (Mandatory)     │                         │
│  └────────┬────────┘                         │
│           │                                  │
│     ┌─────┼─────┐                            │
│     │     │     │                            │
│  Accept  Modify  Reject                       │
│     │     │     │                            │
│     ↓     ↓     ↓                            │
│  Apply  Apply   Discard                       │
│  +log   +log   +log                          │
│     │     │     │                            │
│     └─────┴─────┘                            │
│           │                                  │
│  Learning Loop                                │
│  ├─ Accept → positive signal                  │
│  ├─ Modify → partial signal + correction      │
│  └─ Reject → negative signal + reason         │
│                                              │
└──────────────────────────────────────────────┘
```

## 5. Override Mechanism

O enfermeiro **sempre** pode:

| Action | What Happens | Learning Signal |
|--------|-------------|-----------------|
| Accept | Aplicar como recomendado | Positive (reinforce) |
| Modify | Aplicar com alterações | Partial (correct + learn) |
| Reject | Descartar recomendação | Negative (learn what NOT to recommend) |
| Escalate | Pedir segunda opinião humana | Neutral (flag for review) |
| Ignore | Não responder | No signal (but logged) |

Cada ação é registrada em `ni_council.human_decisions` e alimenta `ni_learning.feedback`.

## 6. Interface Principles

### 6.1 Presentation

| Principle | Implementation |
|-----------|---------------|
| Probabilidade sempre visível | "NANDA 00047: 74%" não "NANDA 00047" |
| Incerteza sempre visível | "Entropia: 0.82 bits (moderada)" |
| Alternativas sempre visíveis | Top-3 hipóteses mostradas |
| Explicação sempre acessível | "Ver rastro" em toda recomendação |
| Disclaimer sempre presente | "IA propõe, enfermeiro decide" |
| Override sempre disponível | Botão "Modificar" / "Rejeitar" |

### 6.2 Cognitive Load

| Scenario | UI Behavior |
|----------|------------|
| Stable patient, routine | Minimal alerts, quiet UI |
| Deteriorating patient | Escalated alerts, priority排序 |
| High uncertainty | Yellow warning, "collect more data" |
| Critical event | Red alert, emergency protocol |
| Multiple recommendations | Ranked list with probabilities |

## 7. Trust Calibration

O sistema deve calibrar a confiança do enfermeiro:

| Trust Level | Problem | NIS Response |
|-------------|---------|--------------|
| Too high (blind trust) | Nurse always accepts | Add more uncertainty cues, require confirmation |
| Too low (always rejects) | Nurse ignores system | Improve accuracy, show evidence, build track record |
| Calibrated | Nurse accepts good, rejects bad | Ideal state |

Métrica: **AI acceptance rate** deve estar entre 60-80% (nem muito alto = confiança cega, nem muito baixo = descrença).

## 8. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-100-06 | Clinical Safety (safety guardrails) |
| NIFS-100-08 | Explainability (principle) |
| NIFS-600-17 | Learning Loop (feedback mechanism) |
| NIFS-600-18 | Consensus Engine (human override) |
| NIFS-700-18 | Safety Layer (AI guardrails) |

## 9. References

- Amershi, S. et al. (2019). Guidelines for Human-AI Interaction. CHI 2019.
- Parasad, A. et al. (2019). Clinical Decision Support Systems: A Review.
& Ward, J. (1995). Automation Bias: The Human Factor in Decision Support

## 10. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — autonomy levels + human gateway | Leivis Melo |
