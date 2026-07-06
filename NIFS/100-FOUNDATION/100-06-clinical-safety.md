# NIFS-100-06: Clinical Safety

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-100-06                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir os requisitos de segurança clínica que governam todas as recomendações do NIS. Segurança clínica é a **prioridade máxima** — acima de performance, above de explicabilidade, above de qualquer outra consideração.

## 2. The Safety Hierarchy

```
1. Segurança do paciente          ← NÃO negociável
2. Julgamento do enfermeiro       ← A IA propõe, o humano decide
3. Explicabilidade                ← Toda recomendação é rastreável
4. Incerteza explícita            ← Nunca falsa certeza
5. Performance                    ← Importante, mas último
```

## 3. Safety Layers

### 3.1 Layer 1: Input Safety

| Guard | What It Checks | Action if Violated |
|-------|---------------|-------------------|
| Data completeness | Mínimo de observações | Refuse reasoning, request more data |
| Data plausibility | PA 300mmHg? Recusar | Flag implausible, request correction |
| Population match | Dados apropriados para população | Adjust priors, flag mismatch |
| Temporal consistency | Observações em ordem temporal | Reorder or flag |

### 3.2 Layer 2: Reasoning Safety

| Guard | What It Checks | Action if Violated |
|-------|---------------|-------------------|
| Minimum hypotheses | ≥ 3 hipóteses geradas | Expand search |
| Entropy check | Entropia < 1.5 bits | Flag high uncertainty |
| Confidence floor | P(top) > 0.40 | Flag insufficient data |
| Contraindication check | Intervenção contraindicada? | Block + suggest alternative |
| Drug interaction | Medicação + condição | Veto by Medication Agent |
| Safety goal alignment | Recomendação viola meta de segurança? | Veto by Safety Agent |

### 3.3 Layer 3: Output Safety

| Guard | What It Checks | Action if Violated |
|-------|---------------|-------------------|
| Code validation | NANDA/NIC/NOC códigos existem no grafo | Block output |
| Probability mandatory | Toda recomendação tem P(x) | Block output |
| Explanation present | Toda recomendação tem trace | Block output |
| Disclaimer present | "IA propõe, enfermeiro decide" | Append if missing |
| Escalation path | Plano tem branch de escalação | Add if missing |

### 3.4 Layer 4: Human Safety

| Guard | What It Checks | Action if Violated |
|-------|---------------|-------------------|
| Human review required | P < 0.60 OU entropia > 1.0 | Queue for human review |
| Critical case flag | Glasgow < 8, NEWS2 ≥ 7 | Force human confirmation |
| Override capability | Enfermeiro pode sempre rejeitar | Log rejection → learning |
| Veto power | Safety Agent veto | Block until resolved |

## 4. The Nine Rights of Medication

O NIS integra os 9 certos da medicação como safety checks:

| # | Right | NIS Check |
|---|-------|-----------|
| 1 | Paciente certo | Patient identifier match |
| 2 | Medicamento certo | Medication Agent validates |
| 3 | Dose certa | Dose calculator + range check |
| 4 | Via certa | Route validation |
| 5 | Horário certo | Schedule + interaction check |
| 6 | Documentação certa | Administration logged |
| 7 | Razão certa | Indication validated against NANDA |
| 8 | Resposta certa | NOC monitoring linked |
| 9 | Reação adversa certa | Allergy + ADR check |

## 5. Safety Goals (WHO/ANS)

O NIS integra as metas de segurança internacionais:

| # | Safety Goal | NIS Integration |
|---|------------|-----------------|
| 1 | Identificação do paciente | Hash único, verificação cruzada |
| 2 | Cirurgia segura | Protocol validation, checklist |
| 3 | Segurança em procedimentos | Protocol steps + time-out |
| 4 | Comunicação segura | Handoff data + structured transfer |
| 5 | Medicamentos de alta vigilância | Double check + enhanced monitoring |
| 6 | Higienização das mãos | Protocol reminders + audit |

## 6. Escalation Protocol

```
Normal Recommendation (P > 0.60, entropy < 1.0)
    ↓
Safety Check Pass
    ↓
Output to nurse

─── OR ───

High Uncertainty (P < 0.60 OR entropy > 1.0)
    ↓
Flag: needs_human_review
    ↓
Queue: ni_council.human_decisions
    ↓
Human decides: accept / modify / reject / escalate

─── OR ───

Critical Event (Glasgow < 8, NEWS2 ≥ 7, code blue)
    ↓
Override all reasoning
    ↓
Activate emergency protocol
    ↓
Notify charge nurse
    ↓
Log everything
```

## 7. Adverse Event Handling

Quando um desfecho adverso ocorre:

```
1. Detect: outcome_type = 'adverse' em ni_memory.outcomes
2. Alert: notificar enfermeiro responsável
3. Trace: recuperar reasoning_session_id → full trace
4. Analyze: o que o sistema recomendou? Por quê?
5. Root cause: erro de raciocínio? Dados insuficientes? Caso atípico?
6. Learn: gerar reinforcement signal negativo forte (reward = -1.0)
7. Prevent: atualizar pesos para reduzir probabilidade de repetição
8. Report: registro em ni_audit_log + ni_obs.error_logs
```

**Adverse events NUNCA decaem na memória** — sempre lembrar de erros.

## 8. Safety Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Safety veto rate | < 5% of recommendations | Council logs |
| Adverse event rate | 0% from AI recommendations | Outcome tracking |
| Human override rate | 10-30% (healthy range) | Human decisions |
| False positive rate | < 5% | Validation cases |
| False negative rate | < 2% (missed high-risk) | Clinical audit |
| Escalation appropriateness | > 90% | Post-escalation review |
| Explanation completeness | 100% | Audit |

## 9. Never Events

O NIS tem uma lista de eventos que **nunca** devem ocorrer:

| Never Event | Prevention |
|-------------|-----------|
| Recomendar sem probabilidade | Output guard Layer 3 |
| Recomendar sem explicação | Output guard Layer 3 |
| Aplicar peso sem validação humana | Learning guard |
| Ignorar contraindicação medicamentosa | Medication Agent veto |
| Recomendar intervenção contraindicada | Safety Agent veto |
| Output com código inexistente | Code validation |
| Falhar em escalar caso crítico | Escalation protocol |

## 10. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-100-04 | Human-Centered AI (human authority) |
| NIFS-700-18 | Safety Layer (AI implementation) |
| NIFS-200-09 | Patient Safety (clinical science) |
| NIFS-1000-06 | Audit (compliance tracking) |
| NIFS-600-18 | Consensus Engine (veto mechanism) |

## 11. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — 4-layer safety model | Leivis Melo |
