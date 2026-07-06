# Validação clínica e bases de dados públicas

Referência: [12-clinical-intelligence-engine.md](../12-clinical-intelligence-engine.md)

---

## 1. Por que validação é o maior gargalo

O motor V3–V8 tem arquitetura avançada, mas **nota ~5/10 em validação** porque:

- pesos são definidos por especialista (não aprendidos);
- probabilidades não foram calibradas contra outcomes reais;
- NANDA labels não existem nativamente em bases ICU.

**Meta V8.5:** toda probabilidade reportada deve passar por calibração e métricas documentadas.

---

## 2. Bases públicas recomendadas

### 2.1 MIMIC-IV — principal para CAL-001

| Aspecto | Detalhe |
|---------|---------|
| **Site** | [PhysioNet MIMIC-IV](https://physionet.org/content/mimiciv/) |
| **Conteúdo** | UTI, vitais, labs, meds, ventilação, ICD, mortalidade |
| **Uso** | Transição temporal, calibração fisiológica, forecast |
| **Acesso** | Credenciamento CITI + termo PhysioNet |
| **Nota para V8** | 10/10 |

**Exemplo de features:**

```
heart_rate, bp_sys, bp_dia, spo2, lactate, creatinine, urine_output
```

### 2.2 eICU Collaborative Research Database

| Aspecto | Detalhe |
|---------|---------|
| **Site** | [PhysioNet eICU](https://physionet.org/content/eicu-crd/) |
| **Diferencial** | Multicentro — generalização |
| **Nota** | 9/10 |

### 2.3 PhysioNet (geral)

ECG, monitorização contínua, séries temporais de alta frequência.

### 2.4 Synthea — protótipo sem barreira ética

| Aspecto | Detalhe |
|---------|---------|
| **Site** | [Synthea GitHub](https://github.com/synthetichealth/synthea) |
| **Uso** | Gerar milhões de trajetórias antes de MIMIC |
| **Nota protótipo** | 10/10 |

### 2.5 Outras (uso secundário)

| Base | Uso | Nota |
|------|-----|------|
| UK Biobank | Epidemiologia, risco populacional | 7.5 |
| NIH Chest X-ray | Imagem → oxigenação (futuro) | 6 |
| OpenFDA | Eventos adversos, safety layer | 7 |

---

## 3. Pipeline ETL proposto

```
MIMIC-IV / eICU / Synthea
        ↓
ETL (scripts/clinical_engine/etl/)
        ↓
Clinical Feature Store
  - observations (vitais, labs)
  - interventions (fluid, vasopressor)
  - outcomes (mortality, AKI, shock)
        ↓
State Encoder
  - mapeia → PhysiologicalState (0–1)
        ↓
Label Mapper (desafio principal)
  - ICD-10 / SNOMED / NLP notas → NANDA proxy
        ↓
V8 Engine + treino / calibração
        ↓
Métricas + Model Card
```

### 3.1 Tabela intermediária (DNA da V8)

Não treinar direto em HR/BP brutos. Criar:

```json
{
  "patient_id": "mimic_12345",
  "timestamp": "2020-01-15T08:00:00Z",
  "state": {
    "volemia": 0.32,
    "contractilidade": 0.55,
    "inflamacaoSistemica": 0.85,
    "funcaoRenal": 0.40
  },
  "observation": { "heart_rate": 120, "systolic_bp": 85 },
  "nanda_proxy": ["PERFUSION_INADEQUATE"],
  "outcome_24h": { "aki": true, "mortality": false }
}
```

### 3.2 Mapeamento NANDA

NANDA/NIC/NOC **não vêm prontos** em MIMIC. Estratégias:

1. **ICD-10 → NANDA** (tabela de mapeamento curada)
2. **SNOMED CT** (onde disponível)
3. **NLP** em notas de enfermagem (research)
4. **Proxy clínico** — choque, hipovolemia, IRA como labels intermediários

Isso pode ser **diferencial científico** do CALENF-NKD.

---

## 4. Módulo de validação (a implementar)

```
src/validation/   # ou scripts/clinical_engine/validation/
├── calibration.ts      # Platt, isotonic, reliability diagram
├── metrics.ts          # Brier, log-loss, AUROC, AUPRC, ECE
├── clinicalDataset.ts  # loaders MIMIC / Synthea
└── reports.ts          # HTML/JSON report
```

### 4.1 Métricas obrigatórias

| Métrica | O que mede |
|---------|------------|
| **Brier Score** | Erro quadrático probabilístico |
| **Log Loss** | Penaliza confiança errada |
| **ECE** | Expected Calibration Error |
| **AUROC / AUPRC** | Discriminação |
| **Calibration curve** | Predito vs observado |

### 4.2 Exemplo de saída calibrada

```
Probabilidade de choque séptico: 78%
Confiança do modelo: 74%
Calibração: boa (ECE 0.04)
Base de validação: 12.500 stays (MIMIC-IV holdout)
```

---

## 5. Fases de aprendizado

| Fase | Dados | Objetivo |
|------|-------|----------|
| **1 — Fisiologia** | MIMIC/eICU | Aprender `f(S, u, t)` |
| **2 — Diagnóstico** | + labels proxy | `P(NANDA \| S)` |
| **3 — NIC** | + intervenções | `P(outcome \| NIC)` |
| **4 — Calibração** | holdout | Ajustar confiança |

---

## 6. Model Card (template)

Documento obrigatório em `docs/clinical-engine/model-card.md` (a criar na Fase C):

```markdown
## Model Card — CAL-001 State Engine

- **Nome:** Clinical Intelligence Engine V8
- **Objetivo:** Suporte à decisão SAE (não diagnóstico autônomo)
- **População:** Adultos hospitalizados / UTI (treino MIMIC)
- **Exclusões:** Pediatria, obstetrícia (v1)
- **Métricas:** Brier X, AUROC Y (holdout)
- **Limitações:** Pesos parcialmente expert; NANDA via proxy
- **Data de treino / versão:** ...
- **Contato / responsável clínico:** ...
```

### Dataset Card

- Origem, anonimização, viés, cobertura temporal, variáveis usadas.

### AI Safety File

- Riscos conhecidos, falhas esperadas, comportamento seguro, escalonamento humano.

---

## 7. Você consegue avançar com isso?

**Sim**, desde que:

1. **Protótipo imediato:** Synthea + mock + datasets NKOS (sem credenciamento).
2. **Validação séria:** credenciamento PhysioNet (2–4 semanas).
3. **Produto educacional:** não exige MIMIC — exige explicabilidade e casos simulados.
4. **Hospital real:** exige V8.5 completo + estudo prospectivo.

| Objetivo | Dados mínimos |
|----------|---------------|
| Site / educação | NKOS + Synthea |
| Paper / pesquisa | MIMIC-IV + métricas |
| Startup HealthTech | MIMIC + calibração + safety |
| Uso hospitalar | Validação prospectiva + regulatório |

---

## 8. Integração com scripts existentes

| Script repo | Extensão sugerida |
|-------------|-------------------|
| `scripts/dataset_io.py` | Loader sharded clinical |
| `scripts/nkp_api.py` | Endpoints `/api/sae/*`, `/api/clinical/validate` |
| `scripts/review/` | Revisão de código do motor clínico |
| `requirements-nkp.txt` | `pandas`, `numpy`, `scikit-learn` (calibração) |

Credenciamento MIMIC: processo manual via PhysioNet — documentar passos em `docs/clinical-engine/mimic-access.md` quando iniciar.

---

## 9. Evidência externa e Grau A (V8+)

Protocolo completo, model card e checklist de publicação no Master Data:

→ **[10-evidencia-validacao-externa.md](10-evidencia-validacao-externa.md)**

Validação rápida de `entity_code` do motor:

```bash
cd clinical-engine && npm run test:ids
```
