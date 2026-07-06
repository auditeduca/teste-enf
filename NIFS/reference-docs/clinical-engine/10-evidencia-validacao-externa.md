# Evidência externa e validação (Grau A)

Complementa [04-validacao-datasets.md](04-validacao-datasets.md) · Motor: [`clinical-engine/`](../../clinical-engine/)

---

## 1. Estado atual da evidência

| Camada | Grau | Fonte |
|--------|------|-------|
| Fórmula gotejamento | **A** | Potter & Perry; protocolos ANVISA (educacional) |
| Thresholds demo V8 | **C** | Heurístico — não calibrado |
| CPTs NANDA no motor | **C** | Especialista + demo NKOS |
| Particle Filter / MPC | **B** | Literatura (SMC, POMDP) — não validado neste repo |
| Linkages `nnn_linkages.json` | **MODERATE** | `EVID.GRADE.MODERATE` nos datasets |

**Conclusão:** o repositório tem **arquitetura research-grade** e **evidência clínica parcial**. Publicação Grau A exige calibração empírica documentada.

---

## 2. Fontes externas recomendadas

### 2.1 Bases de dados (outcomes reais)

| Base | URL | Uso |
|------|-----|-----|
| MIMIC-IV | [physionet.org/content/mimiciv](https://physionet.org/content/mimiciv/) | Vitais, fluids, mortalidade, AKI |
| eICU-CRD | [physionet.org/content/eicu-crd](https://physionet.org/content/eicu-crd/) | Generalização multicentro |
| Synthea | [github.com/synthetichealth/synthea](https://github.com/synthetichealth/synthea) | Protótipo sem credenciamento |

### 2.2 Terminologias (crosswalk)

Já presentes em `datasets/clinical/nursing_diagnoses.json`:

- `snomed`: ex. `698070010` (Impaired gas exchange)
- `icd11`: ex. `MD11.0`
- `evidence_code`: `EVID.GRADE.MODERATE`

**Ação:** validar crosswalk SNOMED/ICD11 contra [NANDA International](https://nanda.org/) antes de claim Grau A.

### 2.3 Literatura de suporte (métodos)

| Método V8 | Referência |
|-----------|------------|
| Particle Filter | Doucet & Johansen, SMC handbook |
| Dynamic BN | Murphy, Dynamic Bayesian Networks |
| MPC clínico | Drgáčová et al., MPC in critical care (survey) |
| Calibration | Platt scaling; isotonic regression (Niculescu-Mizil & Caruana) |

---

## 3. Protocolo de validação proposto

### Etapa 1 — Identificadores (✅ parcial)

```bash
cd clinical-engine && npm run test:ids
python scripts/clinical_engine/validate_entity_codes.py
python scripts/clinical_engine/validate_entity_codes.py --json   # CI
```

Garante `entity_code` ⊆ datasets ∪ master proposal.

### Etapa 2 — ETL (pendente)

Script alvo: `scripts/clinical_engine/etl/mimic_to_features.py`

Features mínimas:

```
heart_rate, bp_sys, bp_dia, spo2, urine_output, lactate, creatinine
fluid_balance, vasopressor_flag
outcome: shock_24h, mortality_30d, aki_stage
```

### Etapa 3 — Calibração CPT

1. Treinar GLM: `P(NANDA_00046 | features)` em hold-out temporal
2. Substituir funções em `nandaGraph.js` por coeficientes exportados (JSON)
3. Reportar Brier e calibration plot

### Etapa 4 — Validação externa (peer)

- [ ] Revisão por enfermeiro especialista (parecer escrito)
- [ ] Comparação baseline: NEWS2 / MEWS vs. `risk.expectedLoss`
- [ ] Registro em model card (data, versão, limitações)

---

## 4. Model card (template)

```yaml
model_id: DRIP_RATE_CAL_001
version: 8.0.0
intended_use: educação enfermagem — simulação gotejamento + SAE demo
not_intended: decisão clínica, prescrição, UTI real-time
training_data: none (heuristic v8.0.0)
evaluation_data: pending MIMIC-IV subset
metrics:
  brier_NANDA_00046: null
  brier_NANDA_00031: null
bias_risks: pesos não calibrados; labels NKOS custom
entity_codes: [DRIP_RATE_CAL_001, NANDA_00046, NANDA_00031, NIC_2500, ...]
evidence_grade: C (target A after calibration)
```

---

## 5. Checklist Grau A (publicação Master Data)

- [ ] `evidence_grade: A` só após Brier < limiar acordado
- [ ] `status: published` no Master Data (não `draft`)
- [ ] Arestas com `evidence_ref` (DOI ou guideline)
- [ ] Disclaimer visível na UI (`/sae`, calculadora)
- [ ] Audit log de execuções (V9)

---

## 6. Links internos

- [07-v8-implementacao-referencia.md](07-v8-implementacao-referencia.md)
- [08-identificadores-nkos.md](08-identificadores-nkos.md)
- [09-v9-proximos-passos.md](09-v9-proximos-passos.md)
- [13-master-data-banco-oficial.md](../13-master-data-banco-oficial.md)
