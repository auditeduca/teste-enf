# 12 — Clinical Intelligence Engine (CAL-001)

**Clinical Intelligence Engine V8** — plataforma probabilística de raciocínio clínico baseada em estado fisiológico latente, inferência Bayesiana, grafo causal NANDA–NIC–NOC e planejamento de intervenções.

Relacionado: [clinical-engine/README.md](clinical-engine/README.md) · [03-datasets.md](03-datasets.md)

---

## 1. Visão geral

### 1.1 O que é

O **CAL-001** transforma dados clínicos (vitais, laboratório, histórico temporal, intervenções) em:

- estimativa do **estado fisiológico oculto** do paciente;
- **diagnósticos NANDA** com probabilidade, confiança e explicabilidade;
- **intervenções NIC** sugeridas ou simuladas (contrafactual);
- **desfechos NOC** previstos;
- **risco clínico** e alertas de deterioração;
- **trilha de auditoria** para governança.

### 1.2 Filosofia V8

Sistemas tradicionais:

```
Vitais → Regras → Score → Alerta
```

CAL-001 V8:

```
Observações incompletas
        ↓
Bel(S) — distribuição sobre estados fisiológicos
        ↓
Modelo generativo + grafo causal
        ↓
P(NANDA | evidência, tempo, contexto)
        ↓
Planejamento (MPC / MCTS)
        ↓
Intervenção → nova distribuição futura
```

O sistema pergunta: *quais estados são possíveis, qual o risco de cada um, e qual ação altera a distribuição futura?*

### 1.3 Posicionamento no CALENF-NKD

| Camada NKOS | Papel no CAL-001 |
|-------------|------------------|
| `datasets/clinical/nursing_diagnoses.json` | Catálogo NANDA-I 2026 (244) |
| `datasets/clinical/nursing_interventions.json` | Catálogo NIC |
| `datasets/clinical/nursing_outcomes.json` | Catálogo NOC |
| `datasets/clinical/nnn_linkages.json` | 1500 ligações formais NNN (`strength`, evidência) |
| `datasets/clinical/clinical_decision_trees.json` | Árvores de decisão (50) — referência para regras |
| `datasets/clinical/safety_rules.json` | Base para **Clinical Safety Layer** |
| `datasets/master/entity_relations.json` | Relações clínico ↔ ferramenta |
| Site `/sae` | UX educacional (`template_pages.json`) |

O motor computacional (V3–V8) é a **especificação de runtime**; os datasets NKOS são a **fonte canônica de taxonomia e ligações**.

---

## 2. Pipeline clínico completo

```
INPUT
  Paciente + Vitais + Labs + Sintomas + Histórico + Intervenções
        ↓
Bayesian State Estimator (Particle Filter / EKF)
        ↓
Latent Physiological State Bel(S)
        ↓
Causal Clinical Graph (DAG fisiológico + NNN)
        ↓
NANDA Probability Engine
        ↓
NIC Optimization (MPC / MCTS / LQR)
        ↓
NOC Prediction (horizonte 6h / 12h / 24h)
        ↓
Clinical Explanation + Audit Log
```

### 2.1 Modos de operação

| Modo | Público | Comportamento |
|------|---------|---------------|
| **Estudante** | Graduação | Explicação passo a passo, simulação, quizzes |
| **Profissional** | Enfermagem clínica | SAE completo, priorização, NIC filtradas |
| **Emergência** | UTI / PS | ABCDE, alertas, ações de alto impacto |
| **Gestor** | Qualidade | KPIs, tendências, benchmarks |

---

## 3. Modelo matemático central

### 3.1 Estado latente

Não se estima apenas `PA = 85/50`. Estima-se:

```typescript
interface LatentClinicalState {
  cardiovascular: { preload; contractility; afterload; cardiacOutput };
  respiratory:      { oxygenation; ventilation; compliance };
  renal:            { perfusion; filtration; clearance };
  inflammatory:     { cytokineLoad; systemicResponse };
  metabolic:        { electrolytes; acidBase };
}
```

Na V8, cada variável é uma **distribuição**:

```typescript
interface RandomVariable {
  mean: number;
  variance: number;
  // distribution: "normal" | "beta" | "logNormal"
}
```

### 3.2 Inferência Bayesiana

```
P(S_t | O_t) ∝ P(O_t | S_t) · P(S_t)
```

- **Prior** — estado anterior / belief
- **Likelihood** — compatibilidade dos vitais com o estado
- **Posterior** — belief atualizado

### 3.3 Transição e controle

```
S_{t+1} = f(S_t, u_t) + w_t
```

- `u_t` — intervenções NIC (controle)
- `w_t` — ruído de processo

### 3.4 Diagnóstico

```
P(NANDA | evidência) via rede Bayesiana + GLM sobre S
```

### 3.5 Risco (V8)

**Expected Clinical Loss:**

```
Risk = Σ P(evento) × Impacto × Peso_temporal
```

Substitui scores heurísticos isolados (NEWS2, probabilidade bruta).

---

## 4. Arquitetura de software (V8 alvo)

```
src/
└── clinical-engine/          # ou v8/
    ├── core/
    │   ├── beliefState.ts
    │   ├── probability.ts
    │   └── distributions.ts
    ├── inference/
    │   ├── particleFilter.ts
    │   ├── bayesianUpdater.ts
    │   └── likelihood.ts
    ├── physiology/
    │   ├── generativeModel.ts
    │   └── causalGraph.ts
    ├── diagnosis/
    │   ├── bayesianNanda.ts
    │   └── dependencyGraph.ts
    ├── intervention/
    │   ├── mpcController.ts
    │   ├── mctsController.ts
    │   └── nicEffectModel.ts
    ├── outcome/
    │   └── nocPredictor.ts
    ├── safety/
    │   ├── contraindications.ts
    │   └── clinicalRules.ts
    ├── validation/
    │   ├── calibration.ts
    │   └── metrics.ts
    ├── explainability/
    │   └── reasoning.ts
    └── orchestrator.ts
```

### 4.1 Módulos por versão (implementação incremental)

| Versão | Módulos | Pasta sugerida |
|--------|---------|----------------|
| V3 | NANDA, NIC, NOC, `nnnGraph`, `saeEngine` (threshold) | `sae/` |
| V4 | Probabilidade, conflitos, score composto | `sae/saeEngine.ts` |
| V5.1 | Temporal: `trendEngine`, `mockHistory` | `temporal/` |
| V5.2 | Causal: `causalGraph`, counterfactual | `causal/` |
| V5.3 | Evolução: `evolutionEngine`, MPC híbrido | `evolution/` |
| V6 | State-space + GLM + EKF + LQR | `stateSpace/` |
| V7 | EKF completo (predict+update), f(S,u) não-linear | `v7/` |
| V8 | Particle filter, BN, MPC/MCTS, belief | `v8/` |

---

## 5. Grafo NNN e causalidade

### 5.1 Ligação formal (V3)

```typescript
interface NNNLink {
  nandaId: string;
  nicIds: string[];
  nocIds: string[];
  strength: number; // 0–1
}
```

No NKOS: `NNNLinkage` em `datasets/clinical/nnn_linkages.json` com `diagnosis_code`, `intervention_code`, `outcome_code`, `strength`, `evidence_code`.

### 5.2 Conflitos clínicos (V4)

```typescript
interface ConflictRule {
  nandaIdA: string;
  nandaIdB: string;
  penalty: number;
  rationale: string;
}
```

Ex.: débito cardíaco diminuído (hipovolemia) vs risco de sobrecarga volêmica — condutas opostas.

### 5.3 Grafo causal (V5.2+)

```typescript
interface CausalEdge {
  from: string;
  to: string;
  type: "causes" | "worsens" | "improves" | "masks";
  weight: number;
  timeLagHours?: number;
}
```

Causalidade embutida na **dinâmica de estado** (V6+), não como delta pós-processamento.

---

## 6. Saída clínica (contrato API)

```json
{
  "patient_id": "P001",
  "timestamp": "2026-06-20T12:00:00Z",
  "belief": {
    "cardiovascular": { "volemia": { "mean": 0.42, "variance": 0.08, "confidence": 0.76 } }
  },
  "diagnoses": [
    {
      "code": "00027",
      "title": "Débito cardíaco diminuído",
      "probability": 0.87,
      "variance": 0.05,
      "priority_rank": 1,
      "drivers": [
        { "feature": "hipotensão", "impact": 0.32 },
        { "feature": "oligúria", "impact": 0.21 }
      ],
      "conflicts_applied": ["n2"],
      "temporal_boost": 0.30
    }
  ],
  "interventions": [
    {
      "code": "4120",
      "title": "Controle de líquidos",
      "linked_to": ["n2"],
      "expected_gain": 0.32
    }
  ],
  "outcomes": [
    { "code": "0401", "title": "Estado hemodinâmico", "target_value": 80, "predicted_24h": 72 }
  ],
  "risk": {
    "hybrid_index": 74,
    "alert_level": "orange",
    "events": [
      { "name": "choque", "probability": 0.35, "severity": 5, "horizon_hours": 6 }
    ]
  },
  "recommended_action": {
    "nic_ids": ["i3", "i1"],
    "rationale": "Reduzir erro fisiológico vs estado alvo",
    "counterfactual": {
      "without_intervention_risk_6h": 0.78,
      "with_intervention_risk_6h": 0.42
    }
  },
  "clinical_summary": "Prioridade 1: 00027 (Score 5.12) | Ajuste temporal +30% | Aceleração em heart_rate",
  "audit": {
    "engine_version": "8.0.0",
    "model_weights_version": "2026.1",
    "reasoning_trace_id": "uuid"
  }
}
```

---

## 7. Segurança clínica e limites

### 7.1 O que o sistema NÃO faz

- Não substitui julgamento clínico do enfermeiro.
- Não prescreve medicamentos ou doses.
- Não decide sozinho em modo autônomo (produto).

### 7.2 Clinical Safety Layer (V8.5)

```
Motor probabilístico → Safety Gate → Recomendação
```

- Contraindicações (ex.: reposição volêmica com risco de edema pulmonar).
- Regras de `datasets/clinical/safety_rules.json`.
- Modos de decisão: **suggest** | **alert** | **block** (crítico).

### 7.3 Auditoria

Cada execução registra: timestamp, belief, evidências, reasoning, intervenção sugerida, outcome esperado, versão do modelo.

---

## 8. Explainability (XAI)

| Nível | V4 | V8 |
|-------|----|----|
| Resumo textual | ✅ `clinicalSummary` | ✅ |
| Conflitos aplicados | ✅ | ✅ |
| Boost temporal | ✅ V5.1 | ✅ |
| Drivers por feature | 📋 | ✅ `drivers[]` |
| Contrafactual | 📋 V5.2 | ✅ |
| Cadeia causal | ❌ | ✅ DAG + propagação |
| Incerteza operacional | decorativa | ✅ variância no risco |

---

## 9. Integração com calculadora (CAL-001 gotejamento)

Orquestrador histórico (`runFullCalculatorV5` / `runV7Engine`):

1. `calculateDrip(volume, time, factor)` → valor clínico (ex.: gtt/min).
2. Valor alimenta threshold / GLM / estado fisiológico.
3. Se cálculo **blocked** (fora de limites), SAE retorna `null` + motivo.

Exemplo: gotejamento 333 gtt/min → ativa NANDAs de sobrecarga / débito conforme grafo e tendência.

---

## 10. Referências cruzadas NKOS

| Entidade NKOS | Arquivo | Uso no CAL-001 |
|---------------|---------|----------------|
| `NursingDiagnosis` | `clinical/nursing_diagnoses.json` | Nós NANDA |
| `NursingIntervention` | `clinical/nursing_interventions.json` | NIC |
| `NursingOutcome` | `clinical/nursing_outcomes.json` | NOC |
| `NNNLinkage` | `clinical/nnn_linkages.json` | Arestas NNN + evidência |
| `ClinicalDecisionTree` | `clinical/clinical_decision_trees.json` | Regras derivadas |
| `SafetyRule` | `clinical/safety_rules.json` | Safety layer |
| `EntityRelation` | `master/entity_relations.json` | Ferramenta ↔ diagnóstico |
| `ClinicalToolCatalog` | `clinical/clinical_tools_catalog.json` | Entrada numérica |

Loader futuro: importar de `scripts/dataset_io.py` / API `nkp_api.py` em vez de JSON duplicado no TypeScript.

---

## 11. Resumo executivo

O **Clinical Intelligence Engine** é um motor probabilístico causal de raciocínio clínico que unifica:

- **Estado fisiológico latente** (não só vitais observados)
- **Taxonomia NANDA–NIC–NOC** (grafo formal + datasets NKOS)
- **Tempo** (tendência, aceleração, projeção 24h)
- **Causalidade e contrafactual** (simulação de NIC)
- **Controle ótimo** (LQR → MPC/MCTS)
- **Incerteza** (belief, particle filter, expected loss)

Transforma **dados → conhecimento → decisão explicável** em ciclo contínuo auditável.

---

## 12. Próximos documentos

| Doc | Tema |
|-----|------|
| [02-evolucao-versoes.md](clinical-engine/02-evolucao-versoes.md) | V3–V8 detalhado |
| [03-pendencias-roadmap.md](clinical-engine/03-pendencias-roadmap.md) | Pendências e V8.5 |
| [04-validacao-datasets.md](clinical-engine/04-validacao-datasets.md) | MIMIC-IV, métricas |
| [05-agentes-documentacao-tecnica.md](clinical-engine/05-agentes-documentacao-tecnica.md) | Agentes + docs obrigatórias |
| [06-avaliacao-mercado.md](clinical-engine/06-avaliacao-mercado.md) | Notas e concorrentes |
| [07-v8-implementacao-referencia.md](clinical-engine/07-v8-implementacao-referencia.md) | **Código V8** — módulos, API `runV8`, uso |
| [08-identificadores-nkos.md](clinical-engine/08-identificadores-nkos.md) | `entity_code`, aliases, arestas Master Data |
| [09-v9-proximos-passos.md](clinical-engine/09-v9-proximos-passos.md) | **Passo 9** — Neuro-Symbolic + LLM + calibração |
| [10-evidencia-validacao-externa.md](clinical-engine/10-evidencia-validacao-externa.md) | Grau A, MIMIC, model card, protocolo |

**Código de referência:** [`clinical-engine/`](../../clinical-engine/) · Validação: `npm run test:ids` ou `python scripts/clinical_engine/validate_entity_codes.py`
