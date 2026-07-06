# 11 — APGAR + MCTS + User Context (V9 demo)

Status: **implementado (referência)** · Base: [doc 14](../14-master-data-sequencia-revisao.md) · [doc 15](../15-master-data-grafo-inferencia.md)

Motor educacional que conecta escala APGAR, regras determinísticas, grafo NANDA–NIC–NOC e **Monte Carlo Tree Search** modulado por perfil de uso (emergência, educação, mobile, flashcard).

---

## 1. Arquitetura em camadas

```
APGAR_SCL_001  →  observação (score 0–10)
APGAR_RULE_001 →  interpretação determinística (threshold)
Edge layer     →  NANDA → NIC → NOC (sem entidade REL)
MCTS           →  seleção de NIC (probabilística + contexto)
User Context   →  profundidade, reward, render de conteúdo
Content Router →  clinical | flashcard | emergency
```

| Camada | Entity code | Papel |
|--------|-------------|-------|
| SCL | `APGAR_SCL_001` | Mede — não decide |
| RULE | `APGAR_RULE_001` | Mapeia score → estado clínico + boost NANDA |
| EDGE | `datasets/ontology/apgar_edges.json` | Arestas tipadas (`supports_diagnosis`, `triggers`, `treated_by`, …) |
| MCTS | runtime | Simula NIC e otimiza reward |
| FLA | `APGAR_FLA_001` | Deck adaptativo via `contentRouter` |

**Nota:** `RULE` é artefato lógico proposto (v2026.2.3) — ainda fora do catálogo Master Data `artifact_types`.

---

## 2. Grafo APGAR (datasets reais)

Arquivo: [`datasets/ontology/apgar_edges.json`](../../datasets/ontology/apgar_edges.json)

| De | Relação | Para | Fonte |
|----|---------|------|-------|
| `APGAR_SCL_001` | `supports_diagnosis` | `NANDA_00162` | Ineffective breathing pattern |
| `APGAR_RULE_001` | `triggers` | `NANDA_00162` | Threshold score ≤6 |
| `APGAR_SCL_001` | `supports_diagnosis` | `NANDA_00046` | Proxy troca gasosa (demo) |
| `NANDA_00162` | `treated_by` | `NIC_2380` | Airway management — `nnn_linkages` |
| `NANDA_00162` | `maps_to` | `NIC_2300` | Vital signs monitoring |
| `NANDA_00162` | `maps_to` | `NIC_1120` | Positioning |
| `NIC_*` | `impacts` | `NOC_0405` / `NOC_1100` | Desfechos demo |

Códigos NANDA/NIC/NOC validados contra `datasets/clinical/` e `nnn_linkages.json`.

---

## 3. User Context Layer

Campos suportados (`clinical-engine/apgar/userContext.js`):

| Campo | Valores | Efeito no motor |
|-------|---------|-----------------|
| `mode` | standard, education, emergency, exam | Profundidade MCTS, pesos de reward |
| `scale_mode` | low_detail, standard, deep_clinical | `graphDepth`, explainability |
| `urgency` | low → critical | `time_pressure`, penalidade de risco |
| `device` | mobile, desktop | Reduz profundidade em mobile |
| `content_type` | clinical, flashcard, quiz, simulation | Roteador de UI |
| `expertise_level` | student, nurse, specialist | Reservado para calibração futura |
| `interaction_goal` | learn, decide, revise, train | Peso `user_comprehension` |

### Reward function (normalizada)

```
reward = w_clinical · Δscore
       - w_risk · P(NANDA)
       - w_cost · custo_NIC
       + w_comprehension · bônus_educação
```

Pesos derivados automaticamente de `mode` + `urgency`.

---

## 4. API

```javascript
import { runApgarMCTS } from './apgar/orchestratorApgar.js';

const output = runApgarMCTS(
  { appearance: 1, pulse: 1, grimace: 0, activity: 1, respiration: 1 },
  {
    mode: 'emergency',
    device: 'mobile',
    urgency: 'critical',
    content_type: 'clinical',
  }
);
```

### Saída (CDO unificado)

| Bloco | Conteúdo |
|-------|----------|
| `observation` | Score APGAR + breakdown |
| `rule_layer` | Estado clínico + probabilidades NANDA |
| `probabilistic_layer` | Diagnósticos ranqueados |
| `intervention_layer` | NIC MCTS + rollout table |
| `outcomes` | NOC previsto + counterfactual |
| `explainability` | Drivers + causal path (omitido em emergency) |
| `safety_layer` | Regras bloqueantes (ex.: observação com score ≤6) |
| `content` | Payload adaptativo (flashcard / emergency / clinical) |

---

## 5. Execução

```bash
cd clinical-engine
npm run demo:apgar
```

Cenários no demo:

1. Clínico padrão — score ~4, desktop  
2. Emergência mobile — score ~3, grafo reduzido  
3. Educação flashcard — deck `APGAR_FLA_001`  
4. Exame / simulação — deep clinical  

---

## 6. Módulos

| Arquivo | Função |
|---------|--------|
| `apgar/apgarScale.js` | Cálculo score 0–10 |
| `apgar/apgarRules.js` | `APGAR_RULE_001` threshold |
| `apgar/apgarGraph.js` | Carrega edges + candidatos NIC |
| `apgar/mctsClinical.js` | MCTS UCB1 + rollout |
| `apgar/userContext.js` | Contexto + modificadores |
| `apgar/contentRouter.js` | Flashcard / emergency / clinical |
| `apgar/orchestratorApgar.js` | `runApgarMCTS()` |
| `identifiers/apgarEntityCodes.js` | Entity codes APGAR |

---

## 7. Limitações (Grau C)

- Efeitos NIC no rollout são **heurísticos** — não calibrados em cohort neonatal  
- `NANDA_00046` é proxy educacional; título no dataset difere do uso clínico clássico  
- MCTS simplificado (sem particle filter V8) — integração futura na V9 completa  
- Master Data `PENDING_REVIEW` — não migrar arestas para produção até aprovação doc 14  

---

## 8. Próximos passos

- [ ] Registrar `RULE` em `artifact_types` do Master Data  
- [ ] Calibrar CPTs APGAR com literatura neonatal (Grau A)  
- [ ] Unificar `runApgarMCTS` + `runV8` sob orchestrator V9  
- [ ] UI mobile/emergency consumindo `content` JSON  
- [ ] Validador CI: arestas APGAR vs. `relation_dictionary.json`  

Ver também: [09-v9-proximos-passos.md](09-v9-proximos-passos.md) · [10-evidencia-validacao-externa.md](10-evidencia-validacao-externa.md)
