# Pendências, roadmap V8.5 e V9

Referência: [12-clinical-intelligence-engine.md](../12-clinical-intelligence-engine.md)

---

## Mapa de pendências por versão

### V4 — lacunas menores

| ID | Item | Prioridade |
|----|------|------------|
| 4.1 | XAI profunda — decomposição do score por variável | Média |
| 4.2 | Normalização por perfil (UTI, idoso, pós-op) | Média |
| 4.3 | Calibração Platt / isotonic + validação externa | Alta |

### V5 — evoluções grandes

| ID | Item | Prioridade |
|----|------|------------|
| 5.1 | ✅ Fase 1 temporal | Concluída (spec) |
| 5.2 | ✅ Fase 2 causal + counterfactual | Concluída (spec) |
| 5.3 | ✅ Fase 3 forecast 24h + hybrid risk | Concluída (spec) |
| 5.4 | Motor de evolução com **projeção contrafactual temporal** (NIC ao longo de 1h/6h/12h) | Alta |

### Infraestrutura global

| ID | Item | Prioridade |
|----|------|------------|
| I.1 | Persistência multi-paciente + versionamento clínico | Alta |
| I.2 | Validação vs guidelines NANDA/NIC/NOC oficiais | Alta |
| I.3 | Test harness — UTI, cenários extremos, regressão SAE | Alta |
| I.4 | Observabilidade — logs estruturados, trace por diagnóstico | Média |
| I.5 | Performance — batch, cache inferência, stream eventos | Média |
| I.6 | Modo clínico formal (suggest / alert / block) | Alta |

---

## Três pilares até V5 “hospital real”

| Pilar | Status spec | Falta |
|-------|-------------|-------|
| **Tempo** | V5.1 ✅ | Integrar slopes reais do EHR |
| **Causalidade** | V5.2 ✅ | DAG calibrado + do-calculus formal |
| **Probabilidade real** | V8 📋 | Particle filter + calibração |

---

## V8.5 — Caminho para produto confiável

Objetivo: transformar motor “inteligente” em motor **clinicamente confiável**.

```
V8.5
├── Bayesian Calibration      # Brier, calibration curve
├── Clinical Safety Layer     # contraindicações, block
├── Counterfactual Engine     # explicar “e se não fizer?”
├── Learning Module           # ajuste de pesos (offline)
├── Evidence Graph            # guidelines + literatura
├── Temporal Forecast         # NANDA em 6h/12h/24h
└── Digital Twin Simulator    # cenários sintéticos + MIMIC
```

### Melhorias por nota baixa

| Área | Nota atual | Ação V8.5 | Nota alvo |
|------|------------|-----------|-----------|
| Validação clínica | 5 | MIMIC + métricas + model card | 8.5 |
| Segurança | 6 | Safety layer + audit | 9 |
| Modelo fisiológico | 8.5 | Híbrido physics + NN residual | 9.5 |
| Aprendizado | 7 | Pipeline offline + federated (opcional) | 9 |
| Regulatório | 5 | AI safety file, limitações explícitas | 8 |

---

## V9 — Neuro-Symbolic Clinical Engine

| Componente | Descrição |
|------------|-----------|
| Ontologia NKOS | NANDA/NIC/NOC como grafo simbólico |
| GNN / CRF | Dependência estruturada entre diagnósticos |
| Offline RL | NIC aprendidas de desfechos (com guardrails) |
| LLM explicador | Camada de linguagem — **não** decisor |
| FHIR + auditoria | Integração hospitalar |

---

## Roadmap executável (ordenado por impacto)

### Fase A — MVP NKOS (4–8 semanas)

- [ ] Loader Python: `nnn_linkages.json` → grafo runtime
- [ ] API `POST /api/sae/run` (V4 mínimo)
- [ ] UI SAE consumindo API + explicação básica
- [ ] Testes com `clinical_decision_trees.json` (casos GCS, etc.)

### Fase B — Temporal + Safety (4–6 semanas)

- [ ] V5.1 trend engine
- [ ] Safety rules de `safety_rules.json`
- [ ] Audit log JSON por sessão

### Fase C — Validação (8–12 semanas)

- [ ] Credenciamento PhysioNet (MIMIC-IV)
- [ ] ETL vitais → estado latente
- [ ] Calibration report (Brier, ECE)
- [ ] Model card + dataset card

### Fase D — Research V7/V8 (contínuo)

- [ ] Particle filter protótipo
- [ ] MPC para combinação NIC
- [ ] Publicação / parceria acadêmica

---

## Erros a evitar

1. **Big bang V8** — implementar tudo de uma vez quebra estabilidade.
2. **Dupla contagem** — manter uma única fonte de `P(NANDA)` (estado latente).
3. **LLM como decisor** — usar apenas para explicação e documentação.
4. **Deploy clínico sem calibração** — probabilidade não calibrada gera falsa confiança.
5. **Ignorar NKOS** — duplicar NANDA em JSON paralelo; sempre usar `datasets/clinical/`.

---

## Critérios de “done” por milestone

| Milestone | Critério |
|-----------|----------|
| V4 MVP | 3 NANDAs demo + conflito + API + teste unitário |
| V5.1 | Mock history + boost temporal visível no summary |
| V5.2 | Counterfactual NIC com delta > 5% documentado |
| V8.5 | Brier < 0.15 em holdout MIMIC (meta ilustrativa) |
| Produto hospital | Safety layer + auditoria + validação prospectiva |
