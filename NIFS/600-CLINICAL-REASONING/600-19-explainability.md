# NIFS-600-19: Explainability

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-600-19                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o framework de explicabilidade do NIS — toda recomendação clínica deve ter um rastro completo, legível e auditável.

## 2. The Explainability Mandate

> "Sem explicação, não há recomendação. Ponto."

Cada inferência produzida pelo NIS deve responder:

1. **Por quê** este diagnóstico?
2. **Quais evidências** suportam e contradizem?
3. **Qual a probabilidade** e a incerteza?
4. **Quais alternativas** foram consideradas e rejeitadas?
5. **Qual o rastro** passo a passo do raciocínio?
6. **Quem votou** no conselho e quem discordou?
7. **Que regras** foram disparadas?
8. **Que casos similares** foram lembrados?

## 3. Explanation Structure

### 3.1 Clinical Explanation Card

```
┌─────────────────────────────────────────────────────────┐
│  DIAGNÓSTICO RECOMENDADO                                │
│  NANDA 00047: Risco de Úlcera por Pressão              │
│  Probabilidade: 74% (IC 95%: 0.68–0.80)                │
│  Entropia: 0.82 bits | Calibração: Brier 0.12          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  POR QUÊ                                                │
│  ┌─────────────────────────────────────────────┐       │
│  │ Observações críticas (Attention-filtered):  │       │
│  │  • Braden = 12 (attention: 0.92)            │       │
│  │  • Imobilidade total (attention: 0.88)      │       │
│  │  • UTI, pós-operatório (attention: 0.75)    │       │
│  │  • Umidade local (attention: 0.70)          │       │
│  └─────────────────────────────────────────────┘       │
│                                                         │
│  EVIDÊNCIAS A FAVOR                                     │
│  • GRADE A: Braden ≤12 → UP risco (87%) [Cochrane 2023]│
│  • GRADE B: Imobilidade + ICU → UP (74%) [Rev Lat-Am]  │
│  • Regra disparada: "Braden≤12 AND ICU → 00047"        │
│  • Caso similar: Episódio #4823 (sim=0.89, sucesso)    │
│                                                         │
│  EVIDÊNCIAS CONTRA                                      │
│  • Mudança de decúbito q2h (reduz P em 15%)            │
│  • Colchão de pressão alternativa em uso               │
│                                                         │
│  ALTERNATIVAS REJEITADAS                                │
│  • NANDA 00046 (18%): menos específico para UP         │
│  • NANDA 00085 (6%): exige lesão já presente           │
│                                                         │
│  CONSELHO                                               │
│  • Acordo: 0.87 (7/8 agentes)                          │
│  • Safety Agent: ressalva (quer protocol C backup)     │
│  • Rodadas: 2                                           │
│                                                         │
│  PLANO RECOMENDADO                                      │
│  • NIC 3540 (primário) + NIC 6540 (adjunto)            │
│  • NOC 1101: esperar 2→4 em 72h                        │
│  • Contingência: se sem melhora → NIC 2250             │
│  • Escalação: se piorar → Protocolo C                  │
│                                                         │
│  RASTRO                                                 │
│  [Ver rastro completo →]                                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Decision Trace (Machine-Readable)

```json
{
  "explanation_id": "uuid",
  "session_id": "uuid",
  "final_diagnosis": {
    "nanda_code": "00047",
    "probability": 0.74,
    "confidence_interval": [0.68, 0.80],
    "entropy": 0.82
  },
  "observations_used": [
    {"ref": "obs_uuid_1", "label": "Braden = 12", "attention": 0.92},
    {"ref": "obs_uuid_2", "label": "Imobilidade total", "attention": 0.88}
  ],
  "observations_filtered": [
    {"ref": "obs_uuid_3", "label": "Temp 37.2°C", "attention": 0.18, "reason": "below_threshold"}
  ],
  "evidence_for": [
    {"grade": "A", "source": "Cochrane 2023", "description": "Braden ≤12 → UP risco 87%"},
    {"rule": "rule_uuid_1", "description": "Braden≤12 AND ICU → 00047"}
  ],
  "evidence_against": [
    {"description": "Mudança de decúbito q2h reduz P em 15%"}
  ],
  "alternatives": [
    {"nanda_code": "00046", "probability": 0.18, "rejection_reason": "menos específico"},
    {"nanda_code": "00085", "probability": 0.06, "rejection_reason": "exige lesão presente"}
  ],
  "council": {
    "agreement_score": 0.87,
    "rounds": 2,
    "dissent": [
      {"agent": "COUNCIL.SAFETY.001", "concern": "quer protocol C backup"}
    ]
  },
  "plan": {
    "primary_nic": "3540",
    "adjunct_nic": "6540",
    "expected_noc": {"code": "1101", "from": 2, "to": 4, "horizon": "72h"},
    "contingency": "NIC 2250 if no improvement",
    "escalation": "Protocol C if deterioration"
  },
  "trace_steps": [
    {"order": 1, "type": "observation", "summary": "8 observations ingested"},
    {"order": 2, "type": "attention", "summary": "4 critical, 4 filtered"},
    {"order": 3, "type": "hypothesis", "summary": "3 hypotheses generated"},
    {"order": 4, "type": "bayesian", "summary": "Prior 0.32 → Posterior 0.74"},
    {"order": 5, "type": "council", "summary": "7/8 agree, 1 partial"},
    {"order": 6, "type": "planning", "summary": "Plan graph with 3 branches"},
    {"order": 7, "type": "safety", "summary": "No vetoes, 1 ressalva"}
  ]
}
```

## 4. Explanation Levels

Diferentes usuários precisam de diferentes níveis de explicação:

| Level | Audience | Content |
|-------|----------|---------|
| `summary` | Enfermeiro à beira do leito | Card resumido (diagnóstico + P + por quê) |
| `detailed` | Enfermeiro revisor | Card + evidências + alternativas + plano |
| `full_trace` | Auditor / pesquisador | Tudo + rastro passo a passo + logs |
| `machine` | Sistema / API | JSON completo |

## 5. Explanation Generation

### 5.1 Template-Based

Cada componente do raciocínio preenche um template:

```
[ATTENTION]
"Das {total} observações, {critical} foram identificadas como críticas 
(attention_score > {threshold}). As {critical} observações críticas são: 
{list}. As {filtered} observações filtradas foram ignoradas porque 
{reason}."

[HYPOTHESIS]
"Foram geradas {n} hipóteses diagnósticas usando {strategies}. 
A hipótese principal é {nanda_code} ({label}) com probabilidade prévia 
de {prior}%."

[BAYESIAN]
"Após atualização bayesiana com {n_evidence} evidências, a probabilidade 
posterior é {posterior}% (IC 95%: {lower}–{upper}). 
Entropia: {entropy} bits ({uncertainty_level})."

[COUNCIL]
"O conselho deliberou em {rounds} rodadas. 
Acordo: {agreement}%. 
{dissent_summary}."
```

### 5.2 Natural Language (LLM)

Para explicações mais fluidas, o LLM (RAG-augmented) recebe:
- Os dados estruturados do trace
- Os templates preenchidos
- Contexto do paciente

E gera uma explicação em linguagem natural, sempre grounded nos dados estruturados (não inventa).

## 6. Audit Trail

Toda explicação é armazenada permanentemente:

| What | Where | Retention |
|------|-------|-----------|
| Explanation card | `ni_explain.explanations` | Permanente |
| Reasoning trace | `ni_explain.decision_traces` | Permanente |
| Recommendation reasons | `ni_explain.recommendation_reasons` | Permanente |
| Council deliberation | `ni_council.deliberation_log` | Permanente |
| Weight updates | `ni_learning.weight_updates` | Permanente |

Permite auditoria retrospectiva: "Por que o sistema recomendou X para o paciente Y em 2026-07-05?"

## 7. Schema Summary

| Table | Purpose |
|-------|---------|
| `ni_explain.explanations` | Explicação completa de cada decisão |
| `ni_explain.recommendation_reasons` | Razões estruturadas (why_diagnosis, why_intervention, etc.) |
| `ni_explain.decision_traces` | Rastro passo a passo |
| `ni_reasoning.trace` | Rastro de inferência (baixo nível) |

## 8. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-100-08 | Explainability (principle) |
| NIFS-600-02 | Reasoning Pipeline (Stage 8) |
| NIFS-600-20 | Reasoning Trace (format detail) |
| NIFS-700-18 | Safety Layer (guardrails) |
| NIFS-1000-06 | Audit (compliance) |

## 9. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — full explainability framework | Leivis Melo |
