# V8 — Implementação de referência (clinical-engine)

Referência: [12-clinical-intelligence-engine.md](../12-clinical-intelligence-engine.md) · Código: [`clinical-engine/`](../../clinical-engine/)

---

## 1. Visão

A **V8** trata o paciente como **distribuição probabilística**, não como valor único:

```
Observações → Particle Filter → P(estado | dados)
           → Rede Bayesiana NANDA → P(diagnóstico | estado)
           → MPC → NIC ótima
           → Expected Clinical Loss → risco
```

**Framework:** JavaScript ESM puro (Node 18+), sem dependências externas. Compatível com integração futura em API Python (`scripts/nkp_api.py`) ou frontend Vite.

**Calculadora:** `DRIP_RATE_CAL_001` (substitui alias legado `CAL-001`).

---

## 2. Arquitetura de pastas

```
clinical-engine/
├── identifiers/          # entity_code NKOS + aliases legados
├── core/                 # tipos, distribuições
├── inference/            # Particle Filter, likelihood
├── physiology/           # modelo generativo P(S'|S,U)
├── diagnosis/            # CPTs NANDA (BN)
├── control/              # NIC + MPC
├── orchestrator.js       # runV8()
└── examples/             # demo + validação de IDs
```

---

## 3. Módulos — arquivo a arquivo

### 3.1 `identifiers/nkosEntityCodes.js`

| Export | Descrição |
|--------|-----------|
| `CAL_DRIP_RATE` | `DRIP_RATE_CAL_001` |
| `NANDA.*` | `NANDA_00046`, `NANDA_00031`, `NANDA_00033` |
| `NIC.*` | `NIC_2500`, `NIC_2510`, `NIC_2550` |
| `NANDA_DATASET_KEY` | Ponte `NANDA_00046` → `NANDA.00046` (JSON clínico) |
| `ENGINE_META` | Versão, disclaimer, schema |

### 3.2 `identifiers/legacyAliasMap.js`

Migração de protótipos V3–V7:

| Legado | entity_code |
|--------|-------------|
| `n1`, `00027`, `00046` | `NANDA_00046` |
| `n2`, `00030`, `00031` | `NANDA_00031` |
| `i3`, `4030` | `NIC_2550` |
| `CAL-001` | `DRIP_RATE_CAL_001` |

Função: `resolveEntityCode(legacyId)`.

### 3.3 `identifiers/edgeRelations.js`

Arestas demo no formato Master Data:

```json
{ "from": "DRIP_RATE_CAL_001", "to": "NANDA_00046", "relation_type": "supports_diagnosis" }
```

Tipos alinhados a `datasets/metadata/relation_dictionary.json`.

### 3.4 `core/types.js`

- `PhysiologicalState` (8 dimensões 0–1)
- `ControlInput` (fluid, diuretic, electrolyteCorrection, ventilatorSupport)
- `VitalObservation` (HR, PA, SpO2, etc.)
- `DEFAULT_STATE`, `TARGET_STATE`

### 3.5 `core/distributions.js`

- `sampleNormal`, `pdfNormal` — Box-Muller + densidade Gaussiana

### 3.6 `physiology/generativeModel.js`

- `generativeTransition(state, control)` — evolução estocástica
- Interações: débito = volemia × contratilidade; inflamação → oxigenação; etc.

### 3.7 `inference/bayesianUpdater.js`

- `computeLikelihood(vitals, state)` — produto de Gaussianas P(vital | state)

### 3.8 `inference/particleFilter.js`

| Função | Papel |
|--------|-------|
| `initializeParticles` | Prior a partir de vitais |
| `predictParticles` | Passo predict (modelo generativo) |
| `updateParticles` | Reponderação Bayesiana |
| `resampleParticles` | Reamostragem sistemática (ESS) |
| `meanState`, `stateDistribution` | Estatísticas do posterior |

### 3.9 `diagnosis/nandaGraph.js`

CPTs com **entity_code** como chave:

| entity_code | Título (demo) | Pais fisiológicos |
|-------------|---------------|-------------------|
| `NANDA_00046` | Troca de gases prejudicada | débito, perfusão |
| `NANDA_00031` | Volume excessivo | volemia, renal |
| `NANDA_00033` | Padrão de risco | renal, eletrólitos |

### 3.10 `diagnosis/bayesianDiagnosis.js`

- `inferDiagnoses(particles)` → `{ entity_code, probability, confidence, evidence[] }`

### 3.11 `control/interventionModel.js`

| entity_code | NIC (dataset) | Efeito |
|-------------|---------------|--------|
| `NIC_2500` | Fluid management | diurético / restrição |
| `NIC_2510` | Vital signs monitoring | suporte ventilatório leve |
| `NIC_2550` | Infusion-related | reposição volêmica |

### 3.12 `control/mpcController.js`

- Simula horizonte 6h por NIC
- Minimiza desvio de `TARGET_STATE` + custo da intervenção
- Retorna `entity_code` da NIC recomendada

### 3.13 `orchestrator.js`

**Entrada:** `runV8(initialVitals, vitalsSequence, { numParticles, control })`

**Saída (`V8Output`):**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `meta` | object | `engine_id`, versão, disclaimer |
| `belief` | object | mean/variance por variável fisiológica |
| `diagnoses` | array | NANDA com entity_code |
| `risk.expectedLoss` | 0–100 | Σ P(evento)×severidade |
| `recommendedIntervention` | object | NIC + rationale |
| `clinicalSummary` | string | Resumo auditável |

---

## 4. Como usar

```bash
cd clinical-engine
npm run demo
npm run test:ids
```

### Integração programática

```javascript
import { runV8 } from './clinical-engine/orchestrator.js';

const output = runV8(
  { heartRate: 110, systolicBP: 90, /* ... */ },
  vitalsSequence,
  { numParticles: 400 }
);

console.log(output.diagnoses[0].entity_code); // NANDA_00046
console.log(output.recommendedIntervention.entity_code); // NIC_2550
```

### Interpretação do risco

| Expected Loss | Nível |
|---------------|-------|
| 0–30 | Baixo |
| 31–60 | Moderado |
| 61–80 | Alto |
| 81–100 | Crítico (demo) |

---

## 5. Limitações conhecidas (referência)

1. **Sem calibração empírica** — pesos heurísticos; ver [10-evidencia-validacao-externa.md](10-evidencia-validacao-externa.md).
2. **Labels NKOS custom** — `NANDA_00046` no dataset ≠ NANDA-I oficial “00046”; ver [08-identificadores-nkos.md](08-identificadores-nkos.md).
3. **MPC simplificado** — mesma ação repetida no horizonte; não é MPC clínico certificado.
4. **Partículas fixas** — 300–500; trade-off performance vs. precisão.

---

## 6. Próximo passo

→ [09-v9-proximos-passos.md](09-v9-proximos-passos.md) (Neuro-Symbolic + LLM explicativo + calibração Grau A)
