# Passo 9 — V9 Neuro-Symbolic Clinical Engine

Status: **planejado** · Base: V8 referência em [`clinical-engine/`](../../clinical-engine/)

---

## 1. Objetivo da V9

Transformar o motor probabilístico V8 em sistema **interpretável, calibrado e integrado ao NKOS**, sem que o LLM tome decisões clínicas.

```
V8 (probabilístico) + Ontologia NKOS + Calibração empírica + LLM (explicação)
= V9 Neuro-Symbolic
```

---

## 2. Pilares (ordem recomendada)

### Fase 9.1 — Ontologia e grafo oficial

- [ ] Migrar CPTs para nós ligados via `nnn_linkages.json` (entity_code)
- [ ] Publicar arestas `DRIP_RATE_CAL_001 → NANDA_*` no Master Data
- [ ] UI Entity Hierarchy: exibir outputs do motor por `entity_code`

### Fase 9.2 — Calibração empírica (Grau A)

- [ ] ETL MIMIC-IV → feature store ([04-validacao-datasets.md](04-validacao-datasets.md))
- [ ] Regressão logística / isotonic regression nos pesos CPT
- [ ] Métricas: Brier score, calibration curve, AUROC por NANDA
- [ ] Model card publicado (`docs/clinical-engine/model-cards/`)

### Fase 9.3 — LLM camada explicativa (não decisor)

- [ ] Input: JSON `V8Output` (probabilidades, evidence, risk)
- [ ] Output: relatório estruturado (SOAP-like, idioma do locale)
- [ ] Guardrails: proibir alteração de probabilidades; citar `entity_code`
- [ ] Agente: [05-agentes-documentacao-tecnica.md](05-agentes-documentacao-tecnica.md) — Clinical Narrator

### Fase 9.4 — Dashboard clínico

- [ ] Distribuição de partículas (volemia, oxigenação)
- [ ] Curva de risco 24h (MPC + forecast)
- [ ] Counterfactual: “sem NIC_2550” vs. “com NIC_2550”

### Fase 9.5 — API e compliance

- [ ] Endpoint `POST /v1/clinical-engine/run` em `nkp_api.py`
- [ ] Audit trail: `user_id`, inputs hash, `meta.engine_id`
- [ ] LGPD / disclaimer em toda resposta

---

## 3. O que a V9 **não** faz (escopo negativo)

- Não substitui prontuário eletrônico
- Não prescreve medicamentos
- Não diagnostica legalmente
- Não usa LLM para alterar scores ou escolher NIC sem MPC

---

## 4. Critérios de “pronto para piloto hospitalar”

| Critério | Meta |
|----------|------|
| Calibração Brier | < 0.15 nos 3 NANDA demo |
| Cobertura entity_code | 100% validados vs. Master Data |
| Evidência | ≥ 1 NANDA com Grau A documentado |
| Revisão clínica | Parecer registrado em `docs/14-*` |
| Performance | runV8 < 2s com 500 partículas (Node) |

---

## 5. Referências

- [03-pendencias-roadmap.md](03-pendencias-roadmap.md)
- [10-evidencia-validacao-externa.md](10-evidencia-validacao-externa.md)
- [07-v8-implementacao-referencia.md](07-v8-implementacao-referencia.md)
