# Evolução de versões — V3 a V8

Referência: [12-clinical-intelligence-engine.md](../12-clinical-intelligence-engine.md)

---

## Linha do tempo

```
V3  Estruturado (NNN graph, threshold)
 ↓
V4  Probabilístico + conflitos
 ↓
V5.1 Temporal (tendência, aceleração)
 ↓
V5.2 Causal + counterfactual
 ↓
V5.3 Evolução contínua (forecast 24h, MPC multi-NIC)
 ↓
V5.4 Fisiologia + Bayes + tempo não-linear
 ↓
V6  State-space unificado (GLM + EKF + LQR)
 ↓
V7  EKF completo + f(S,u) não-linear + CRF diagnóstico
 ↓
V8  Belief + Particle Filter + BN + MPC/MCTS
 ↓
V8.5 Calibração + Safety + Learning (produto)
 ↓
V9  Neuro-symbolic + RL offline + LLM explicador
```

---

## V3 — SAE estruturado real

**Status:** ✅ Especificado / protótipo conceitual

| Entrega | Descrição |
|---------|-----------|
| NANDA / NIC / NOC | Objetos tipados com domínio, fatores, características |
| `NNNGraph` | Ligações formais `NNNLink` |
| `runSAE` | Ativação por threshold clínico |
| Intervenções | Vinculadas por link, sem priorização |

**Limitação:** diagnóstico binário (dentro/fora do threshold).

**Arquivos alvo:** `src/sae/nanda.ts`, `nic.ts`, `noc.ts`, `nnnGraph.ts`, `saeEngine.ts`, `sampleGraph.ts`

---

## V4 — SAE probabilístico + conflitos

**Status:** ✅ Especificado

| Entrega | Descrição |
|---------|-----------|
| Probabilidade contínua | Curva em torno do centro do threshold |
| Score composto | `probability × severityWeight × urgencyFactor` |
| `ConflictRule` | Penalização automática do diagnóstico menos prioritário |
| Top-k NIC/NOC | Intervenções filtradas pelos 2–3 diagnósticos principais |
| `clinicalSummary` | Resumo com conflitos resolvidos |

**Pendências V4 (não críticas):**

- Explicabilidade profunda (decomposição do score)
- Normalização por perfil (UTI, idoso, pediatria)
- Calibração estatística (Platt / isotonic)

---

## V5.1 — Motor temporal

**Status:** ✅ Especificado

| Entrega | Descrição |
|---------|-----------|
| `VitalHistory` / `VitalRecord` | Time-series de sinais |
| `analyzeTrend` | Slope, delta, R², direção |
| `detectAcceleration` | Alerta de piora abrupta |
| `TemporalContext` | Boost de probabilidade por tendência |
| `generateMockHistory` | Dados sintéticos para testes |

**Gap resolvido:** sistema deixa de ser “foto” e vira “vídeo”.

---

## V5.2 — Causalidade + counterfactual

**Status:** ✅ Especificado

| Entrega | Descrição |
|---------|-----------|
| `CausalEdge` | NANDA → NANDA (causes, worsens, improves, masks) |
| `InterventionEffect` | NIC → altera probabilidade de NANDA |
| `propagateCausal` | Propagação entre diagnósticos |
| `simulateCounterfactual` | “Se aplicar NIC X, o que muda?” |

**Gap resolvido:** associação → intervenção simulada.

---

## V5.3 — Evolução clínica preditiva

**Status:** ✅ Especificado

| Entrega | Descrição |
|---------|-----------|
| `simulateEvolution` | `state(t)` hora a hora |
| `propagateCausalWithDepth` | Damping + limite de profundidade |
| `applyMultiIntervention` | Várias NICs com diminishing returns |
| `calculateHybridRiskIndex` | Índice 0–100 unificado |
| Alertas preditivos | Threshold crossing (ex.: 94% em 18h) |

---

## V5.4 — Camada fisiológica + Bayes

**Status:** 📋 Especificado (research)

| Entrega | Descrição |
|---------|-----------|
| `PhysiologicalState` | Perfusão, volemia, inflamação, etc. |
| CPT | `P(NANDA \| physiology)` |
| `evolveNonLinear` | Logística + tipping points |
| `doIntervention` | do-calculus simplificado |

**Problema identificado:** três “verdades” (Bayes + logística + causal) sem reconciliação → resolvido na V6.

---

## V6 — Unified Clinical State-Space

**Status:** 📋 Especificado

| Entrega | Descrição |
|---------|-----------|
| Estado único latente | 8 dimensões fisiológicas 0–1 |
| GLM | `P(NANDA \| S)` — única fonte de probabilidade |
| Matriz A + B | Causalidade e tempo na transição |
| EKF simplificado | Propagação de covariância |
| LQR | Sugestão de NIC por erro vs estado alvo |

**Salto:** elimina dupla contagem de evidência.

---

## V7 — EKF completo + não-linearidade

**Status:** 📋 Especificado

| Entrega | Descrição |
|---------|-----------|
| `f(S, u)` não-linear | Débito = volemia × contratilidade, saturação |
| `ekfPredict` + `ekfUpdate` | Loop fechado com vitais reais |
| Jacobiano H | Modelo de observação |
| CRF-like | Interações entre diagnósticos |
| Covariância 8×8 | (simplificada na implementação de referência) |

**Formalmente:** POMDP aproximado com EKF + controle.

---

## V8 — Full Probabilistic Rewrite

**Status:** 📋 Arquitetura alvo

| Entrega | Descrição |
|---------|-----------|
| `ClinicalBelief` | Distribuição, não ponto |
| Particle Filter | Multimodalidade (choque, bifásico) |
| Likelihood | `P(vital \| estado)` |
| Bayesian Network | NANDA acoplados |
| MPC / MCTS | Intervenção com futuros simulados |
| Expected Loss | Risco calibrável |

**Pergunta central:** quais estados possíveis existem e qual ação muda a distribuição futura?

---

## Comparação rápida

| Aspecto | V4 | V6 | V7 | V8 |
|---------|----|----|----|-----|
| Estado | threshold | vetor mean | mean + cov | belief / partículas |
| Tempo | — | matriz A | f(S,u) | generativo |
| Diagnóstico | heurístico | GLM | GLM+CRF | BN |
| Intervenção | lista | LQR | LQR | MPC/MCTS |
| Incerteza | baixa | covariância | EKF | operacional |
| Observação | direta | parcial | update EKF | likelihood Bayes |

---

## Mapeamento para implementação no repo

1. **Fase MVP (produto educacional):** V4 + datasets NKOS + UI `/sae`
2. **Fase clínica simulada:** V5.1 + V5.2 + mock history
3. **Fase research:** V7 em Python (integração MIMIC-IV)
4. **Fase enterprise:** V8 + V8.5 (safety, calibração, auditoria)

Código TypeScript de referência ainda **não está** em `src/` — implementar incrementalmente ou portar para `scripts/clinical_engine/` (Python) para treino com MIMIC.
