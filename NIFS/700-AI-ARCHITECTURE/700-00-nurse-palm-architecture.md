# NIFS-700-00: Nurse-PaLM — Arquitetura Cognitiva de Referência

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-700-00                        |
| Status        | Active                             |
| Version       | 2.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05 (v4.0 — UI integration + fluxo cognitivo vertical) |

## 1. Purpose

Este documento define a arquitetura cognitiva do Nurse-PaLM — o modelo de IA composto que transforma observações clínicas em diagnósticos probabilísticos, planos de intervenção e explicações rastreáveis. Ele mapeia as **10 camadas cognitivas** contra a implementação existente na Clinical Engine V8 (NKOS v4.4), identifica gaps e define o caminho evolutivo para v7.0+.

## 2. O que é Nurse-PaLM?

Nurse-PaLM não é um único modelo neural. É uma **arquitetura de IA composta** que orquestra múltiplos motores de inferência sobre um grafo de conhecimento estruturado. Cada camada resolve um problema cognitivo específico que um LLM puro não consegue resolver sozinho.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Nurse-PaLM Cognitive Stack                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Layer 10: Multi-Agent Council ─────────── nifs-700-09          │
│     Deliberação multi-perspectiva com dissidências              │
│                                                                 │
│  Layer 9:  Simulation Engine ────────────── nifs-600-14         │
│     MCTS para planejamento de intervenções                      │
│                                                                 │
│  Layer 8:  Feedback Learning ────────────── nifs-600-17         │
│     Atualização de CPTs e pesos com outcomes reais              │
│                                                                 │
│  Layer 7:  Planner ──────────────────────── nifs-600-11         │
│     MPC para sequenciamento de NICs                             │
│                                                                 │
│  Layer 6:  Uncertainty Model ────────────── nifs-600-08         │
│     Bayesian CPTs + particle filter distribution                │
│                                                                 │
│  Layer 5:  Clinical Attention ───────────── nifs-600-10         │
│     Filtro de observações críticas                              │
│                                                                 │
│  Layer 4:  World Model ──────────────────── nifs-600-15         │
│     Modelo fisiológico generativo (8 estados latentes)          │
│                                                                 │
│  Layer 3:  Temporal Graph ───────────────── nifs-500-09         │
│     Evolução temporal de estados e evidências                   │
│                                                                 │
│  Layer 2:  Episodic Memory ──────────────── nifs-600-16         │
│     Casos clínicos passados recuperáveis                        │
│                                                                 │
│  Layer 1:  Clinical Reasoning ───────────── nifs-600-02         │
│     Pipeline de inferência: obs → hipótese → diagnóstico        │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  Foundation: Knowledge Graph (NANDA/NIC/NOC) + Evidence (GRADE) │
│  Infrastructure: RAG + Vector Search + LLM + Safety Layer       │
└─────────────────────────────────────────────────────────────────┘
```

## 3. Mapeamento: 10 Camadas × Clinical Engine V8

### 3.1 Layer 1 — Clinical Reasoning (Raciocínio Clínico)

| Aspecto | Detalhe |
|---------|---------|
| **NIFS** | NIFS-600-02 (Reasoning Pipeline) |
| **Código V8** | `orchestrator.js` — função `runV8()` |
| **Status** | ✅ Implementado |
| **O que faz** | Pipeline completo: recebe vitais → inicializa partículas → predict/update loop → inferência bayesiana NANDA → cálculo de risco → MPC → sumário clínico |
| **Fluxo** | `vitalsToPrior()` → `initializeParticles()` → `predictParticles()` → `updateParticles()` → `resampleParticles()` (se ESS < 50%) → `inferDiagnoses()` → `computeRisk()` → `mpcController()` |
| **Output** | `{ belief, meanState, diagnoses[], risk, recommendedIntervention, clinicalSummary }` |
| **Gap v5.0** | Sem RAG/LLM no pipeline — inferência é puramente bayesiana. Precisa de camada de linguagem para explicar em PT-BR. |
| **Target v7.0** | Pipeline híbrido: Bayesian + LLM com RAG, onde o LLM recebe P(x) do motor bayesiano como prior obrigatório. |

### 3.2 Layer 2 — Episodic Memory (Memória Episódica)

| Aspecto | Detalhe |
|---------|---------|
| **NIFS** | NIFS-600-16 (Clinical Memory) |
| **Código V9** | `memory/episodicMemory.js` — storeEpisode, recallSimilar, extractLearnings |
| **Status** | ✅ Implementado (v5.0) |
| **O que deveria fazer** | Armazenar episódios clínicos (observações + diagnóstico + intervenção + outcome) em `ni_memory.episodes`, recuperar por similaridade semântica (vector search) |
| **Especificação** | Tabela `ni_memory.episodes` no DDL v5.0 com campos: episode_id, patient_context, observations, diagnoses, interventions, outcome, outcome_score, embedding |
| **Target v5.0** | Implementar `episodicMemory.js`: `storeEpisode()`, `retrieveSimilar()`, `updateOutcome()` — usa pgvector para similaridade |

### 3.3 Layer 3 — Temporal Graph (Grafo Temporal)

| Aspecto | Detalhe |
|---------|---------|
| **NIFS** | NIFS-500-09 (Temporal Graph) |
| **Código V9** | `temporal/temporalGraph.js` — recordEvent, buildSequence, detectCausalChain, queryEvolution, detectDeterioration |
| **Status** | ✅ Implementado (v5.0) |
| **O que faz** | O particle filter (predict/update loop) rastreia a evolução de estados latentes ao longo do tempo. Cada `predictParticles()` é um passo temporal. |
| **Gap** | Não persiste a evolução temporal como grafo explícito. Não há arestas temporais (state_t → state_t+1) materializadas. |
| **Target v5.0** | Materializar `ni_graph.temporal_edges` com snapshots de estado por timestep, permitindo query "como evoluiu a volemia do paciente X nas últimas 6h" |

### 3.4 Layer 4 — World Model (Modelo Fisiológico Generativo)

| Aspecto | Detalhe |
|---------|---------|
| **NIFS** | NIFS-600-15 (Digital Twin) |
| **Código V8** | `physiology/generativeModel.js` — `generativeTransition()` + `deterministicEvolve()` |
| **Status** | ✅ Implementado |
| **O que faz** | Modelo fisiológico com 8 estados latentes: volemia, contractilidade, resistenciaVascular, oxigenacao, ventilacao, funcaoRenal, inflamacao, eletrolitos. Cada estado evolui com base em equações determinísticas + ruído gaussiano. |
| **Dinâmica** | `cardiacOutput = volemia × contractilidade`; inflamação decai 5%/step; oxigenação depende de ventilação e inflamação; função renal depende de débito cardíaco |
| **Controles** | fluid, diuretic, electrolyteCorrection, ventilatorSupport |
| **Gap** | Modelo é 1:1 (mesmas equações para todos). Precisa de personalização por perfil de paciente (pediatria, geriatra, crônico). |
| **Target v6.0** | World Model parametrizável por população, com CPTs aprendidas de dados reais |

### 3.5 Layer 5 — Clinical Attention (Atenção Clínica)

| Aspecto | Detalhe |
|---------|---------|
| **NIFS** | NIFS-600-10 (Clinical Attention) |
| **Código V9** | `attention/clinicalAttention.js` — evaluate, persistSignals, updateWeights |
| **Status** | ✅ Implementado (v5.0) |
| **O que faz** | `vitalsToPrior()` converte sinais vitais em priors para os estados latentes. É uma função de atenção determinística (não aprendida). |
| **Mapeamento atual** | volemia ← systolicBP; contractilidade ← heartRate; oxigenação ← SpO₂; funcaoRenal ← urineOutput; inflamacao ← temperature |
| **Gap** | Não pondera por criticalidade. Não diferencia observações ruidosas de confiáveis. Não tem mecanismo de saliência (quais vitais merecem mais atenção neste contexto). |
| **Target v5.0** | `clinicalAttention.js` com mecanismo de saliência baseado em desvio de baseline + taxa de mudança + severidade NANDA associada |

### 3.6 Layer 6 — Uncertainty Model (Incerteza Probabilística)

| Aspecto | Detalhe |
|---------|---------|
| **NIFS** | NIFS-600-08 (Bayesian Network) |
| **Código V8** | `inference/particleFilter.js` + `diagnosis/bayesianDiagnosis.js` + `inference/bayesianUpdater.js` |
| **Status** | ✅ Implementado |
| **O que faz** | Inferência probabilística completa via particle filter (300 partículas). Cada partícula representa uma hipótese de estado latente. Diagnósticos NANDA via CPTs condicionais com P(hypothesis), variance e confidence. |
| **Calibração** | `confidence = 1 - min(1, sqrt(variance) / 0.3)` — medida de certeza baseada na dispersão das partículas |
| **Evidence tracking** | Cada diagnóstico tem array de evidence: `"volemia ↓ (28%), oxigenacao ↑ (91%)"` |
| **Resampling** | Resample sistemático quando ESS < 50% de N (evita degeneração) |
| **Gap** | CPTs são hardcoded, não aprendidas. Sem Brier score ou calibração formal. |
| **Target v6.0** | CPTs aprendidas via feedback learning; calibração isotônica; Brier score < 0.15 |

### 3.7 Layer 7 — Planner (Planejamento de Intervenções)

| Aspecto | Detalhe |
|---------|---------|
| **NIFS** | NIFS-600-11 (Goal Planning) + NIFS-600-12 (Intervention Selection) |
| **Código V8** | `control/mpcController.js` + `control/interventionModel.js` |
| **Status** | ✅ Implementado |
| **O que faz** | Model Predictive Control (MPC): simula cada intervenção NIC disponível por um horizonte de 6 timesteps, calcula custo esperado (desvio do estado alvo), seleciona a de menor custo. |
| **Função custo** | `|volemia - target| × 2 + |contractilidade - target| × 2 + |oxigenacao - target| × 1.5 + |funcaoRenal - target| × 2 + |inflamacao - target| × 3 + |eletrolitos - target| × 1.5` |
| **Output** | `{ entity_code, name, expectedOutcome, rationale, control }` — NIC recomendada com justificativa |
| **Gap** | Horizonte fixo (6h). Sem planejamento multi-objetivo. Sem restrições (ex: dose máxima, contraindicações). |
| **Target v5.0** | MPC com horizonte variável, restrições clínicas, multi-objetivo (segurança × eficácia × custo) |

### 3.8 Layer 8 — Feedback Learning (Aprendizado por Feedback)

| Aspecto | Detalhe |
|---------|---------|
| **NIFS** | NIFS-600-17 (Learning Loop) |
| **Código V9** | `memory/episodicMemory.js` — storeEpisode, recallSimilar, extractLearnings |
| **Status** | ✅ Implementado (v5.0) |
| **O que deveria fazer** | Quando um episódio clínico termina (outcome conhecido), atualizar CPTs do motor bayesiano para melhorar previsões futuras. Usa `ni_memory.episodes.outcome_score` como sinal de aprendizado. |
| **Mecanismo** | Bayesian update de CPTs: `P(NANDA|evidence) ← P(NANDA|evidence) × P(outcome|NANDA) / P(outcome)` |
| **Target v5.0** | `feedbackLearning.js`: `updateCpts(episode, outcome)`, `calibrateProbabilities()`, `exportLearnedCpts()` |

### 3.9 Layer 9 — Simulation Engine (Motor de Simulação)

| Aspecto | Detalhe |
|---------|---------|
| **NIFS** | NIFS-600-14 (Simulation) |
| **Código V8** | `apgar/mctsClinical.js` — `runClinicalMcts()` |
| **Status** | ✅ Implementado (APGAR pilot) |
| **O que faz** | Monte Carlo Tree Search (MCTS) clínico: explora sequências de intervenções NIC, simula rollouts com efeitos heurísticos, seleciona melhor caminho via UCB1. |
| **Estrutura** | 4 fases MCTS: Selection (UCB1) → Expansion → Rollout (simulação heurística) → Backpropagation |
| **Reward** | `clinical_outcome × w1 - risk_penalty × w2 - intervention_cost × w3 + user_comprehension × w4` — pesos adaptados por perfil (student, nurse, manager) |
| **Configuração** | `mctsIterations` e `mctsDepth` derivados do perfil do usuário via `userContext.js` |
| **Gap** | Só implementado para APGAR. NIC effects são hardcoded. Precisa generalizar para outras calculadoras. |
| **Target v5.0** | Generalizar MCTS para qualquer calculadora via Clinical Intelligence Package (6 dimensões). NIC effects lidos de `ni_sim.simulation_models`. |

### 3.10 Layer 10 — Multi-Agent Council (Conselho Multiagente)

| Aspecto | Detalhe |
|---------|---------|
| **NIFS** | NIFS-600-18 (Consensus Engine) + NIFS-700-09 (Multi-Agent) |
| **Código V9** | `memory/episodicMemory.js` — storeEpisode, recallSimilar, extractLearnings |
| **Status** | ✅ Implementado (v5.0) |
| **O que deveria fazer** | Múltiplos agentes especializados (Diagnostician, Interventionist, Safety Officer, Patient Advocate) deliberam sobre o caso, cada um com perspectiva diferente. Consenso ou dissidência explícita. |
| **Mecanismo** | Cada agente propõe diagnóstico/plano → votação ponderada → se dissidência > threshold → human review |
| **Target v5.0** | `multiAgentCouncil.js`: `conveneCouncil(case)`, `agentDeliberation(agent, case)`, `consensusVote()`, `dissentReport()` |

## 4. Matriz de Cobertura

| # | Camada | Código V8 | NIFS Spec | DDL Table | Gap |
|---|--------|-----------|-----------|-----------|-----|
| 1 | Clinical Reasoning | ✅ `orchestrator.js` | ✅ 600-02 | `ni_reasoning.*` | Sem LLM |
| 2 | Episodic Memory | ❌ | ✅ 600-16 | `ni_memory.episodes` | Sem código |
| 3 | Temporal Graph | ⚡ Implícito | ✅ 500-09 | `ni_graph.temporal_edges` | Não materializado |
| 4 | World Model | ✅ `generativeModel.js` | ✅ 600-15 | `ni_sim.physiological_states` | Não parametrizável |
| 5 | Clinical Attention | ⚡ `vitalsToPrior()` | ✅ 600-10 | `ni_reasoning.attention_weights` | Heurístico |
| 6 | Uncertainty | ✅ `particleFilter.js` | ✅ 600-08 | `ni_prob.*` | CPTs hardcoded |
| 7 | Planner | ✅ `mpcController.js` | ✅ 600-11 | `ni_plan.*` | Sem restrições |
| 8 | Feedback Learning | ❌ | ✅ 600-17 | `ni_memory.feedback_events` | Sem código |
| 9 | Simulation | ✅ `mctsClinical.js` | ✅ 600-14 | `ni_sim.*` | Só APGAR |
| 10 | Multi-Agent Council | ❌ | ✅ 600-18 | `ni_council.*` | Sem código |

**Resumo:** 5 camadas implementadas, 2 parciais, 3 sem código. Especificação NIFS cobre 100%.

## 5. Pipeline de Inferência End-to-End (Target v5.0)

```
Input: { patient_context, observations[], user_profile, query }
  │
  ├─ (1) Clinical Attention
  │     Filtra observações críticas, pondera por saliência
  │     Output: weighted_observations[]
  │
  ├─ (2) Episodic Memory
  │     Recupera N casos similares (vector search)
  │     Output: similar_episodes[]
  │
  ├─ (3) World Model + Temporal Graph
  │     Inicializa estados latentes a partir de observações + episódios
  │     Output: initial_state, temporal_context
  │
  ├─ (4) Uncertainty (Particle Filter + Bayesian)
  │     Propaga partículas, atualiza com observações, infer P(NANDA|evidence)
  │     Output: diagnoses[] with P(x), CI, evidence
  │
  ├─ (5) RAG + LLM
  │     Retrieve knowledge chunks, inject as context
  │     LLM gera explicação em PT-BR usando P(x) como prior obrigatório
  │     Output: narrated_diagnosis with trace
  │
  ├─ (6) Planner (MPC)
  │     Simula intervenções NIC, seleciona melhor sequência
  │     Output: intervention_plan[]
  │
  ├─ (7) Simulation Engine (MCTS)
  │     Simula outcomes do plano, estima risco/benefício
  │     Output: predicted_outcomes, confidence_intervals
  │
  ├─ (8) Multi-Agent Council
  │     Agentes deliberam, votam, reportam dissidências
  │     Output: consensus_report, dissent_flags
  │
  ├─ (9) Safety Layer
  │     Verifica against safety rules, drug interactions, contraindications
  │     Output: safety_check, veto_events[]
  │
  └─ (10) Output
        { diagnosis, P(x), plan, simulation, council, explanation, trace }
        Target latency: < 3.5s
```

## 6. Roadmap de Implementação

### Phase 1: v5.0 — Bayesian + RAG (Q3 2026)

| Prioridade | Camada | Ação | Artefato |
|------------|--------|------|----------|
| P0 | Episodic Memory | Implementar `episodicMemory.js` | `ni_memory.episodes` + pgvector |
| P0 | Clinical Attention | Implementar `clinicalAttention.js` | `ni_reasoning.attention_weights` |
| P0 | RAG Integration | Conectar LLM ao pipeline bayesiano | `700-02-rag.md` → código |
| P1 | Temporal Graph | Materializar evolução temporal | `ni_graph.temporal_edges` |
| P1 | Planner v2 | MPC com restrições clínicas | `mpcController.js` v2 |

### Phase 2: v6.0 — Domain Adaptation (Q1 2027)

| Prioridade | Camada | Ação | Artefato |
|------------|--------|------|----------|
| P0 | Feedback Learning | Implementar `feedbackLearning.js` | CPTs aprendidas |
| P0 | World Model v2 | Parametrização por população | `generativeModel.js` v2 |
| P0 | Simulation v2 | Generalizar MCTS para qualquer calculator | `mctsClinical.js` genérico |
| P1 | Uncertainty v2 | CPTs aprendidas + calibração | Brier score < 0.15 |

### Phase 3: v7.0+ — Native Model (2027+)

| Prioridade | Camada | Ação | Artefato |
|------------|--------|------|----------|
| P0 | Multi-Agent Council | Implementar `multiAgentCouncil.js` | `ni_council.*` |
| P0 | Fine-tuning | Treinar com episódios + feedback | `nurse-palm-ft-v1` |
| P1 | Native Model | Transformer + GNN from scratch | `nurse-palm-native-v1` |

## 7. Identificadores Canônicos (NKOS Entity Codes)

O Nurse-PaLM usa o sistema de códigos canônicos definido em `nkosEntityCodes.js`:

| Prefixo | Tipo | Exemplo | Entidade |
|---------|------|---------|----------|
| `NANDA_` | Diagnóstico | `NANDA_00046` | Risco de Lesão |
| `NIC_` | Intervenção | `NIC_2500` | Manejo da Via Aérea |
| `NOC_` | Desfecho | `NOC_1101` | Integridade Tissular |
| `PHYS.` | Estado Fisiológico | `PHYS.VOLEMIA` | Estado de Volemia |
| `CTRL.` | Controle | `CTRL.FLUID` | Administração de Fluidos |
| `EV_` | Evidência | `EV_APGAR_1953` | Apgar 1953 (DOI) |
| `DX_` | Decisão | `DX_HIGH_ALERT` | Drug High-Alert Flag |

Estes códigos são a **única moeda** do Nurse-PaLM — o LLM é forçado a outputar apenas códigos do grafo, eliminando alucinação.

## 8. Evidence Disclaimer

Todo output clínico do Nurse-PaLM inclui o disclaimer definido em `ENGINE_META.evidence_disclaimer`:

> "Este sistema é uma ferramenta de apoio à decisão. Toda inferência é probabilística e deve ser validada por profissional habilitado."

## 9. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-02 | Reasoning Pipeline (Layer 1 detail) |
| NIFS-600-08 | Bayesian Network (Layer 6 detail) |
| NIFS-600-10 | Clinical Attention (Layer 5 detail) |
| NIFS-600-11 | Goal Planning (Layer 7 detail) |
| NIFS-600-14 | Simulation (Layer 9 detail) |
| NIFS-600-15 | Digital Twin (Layer 4 detail) |
| NIFS-600-16 | Clinical Memory (Layer 2 detail) |
| NIFS-600-17 | Learning Loop (Layer 8 detail) |
| NIFS-600-18 | Consensus Engine (Layer 10 detail) |
| NIFS-700-01 | Foundation Model (LLM strategy) |
| NIFS-700-02 | RAG (retrieval) |
| NIFS-700-09 | Multi-Agent (council detail) |
| NIFS-700-18 | Safety Layer (guardrails) |

## 11. Integração UI — Nurse-PaLM como Lógica, Não como Painel

### Princípio Fundamental (v2.0.0)

Nurse-PaLM **NÃO é um painel separado** nem uma seção isolada na interface. É a **lógica integrada às ferramentas**. Cada campo, cada card, cada step do fluxo da calculadora reflete o pensamento cognitivo do enfermeiro.

### O que foi removido (v2.0.0):
- ~~Painel "Análise Cognitiva Nurse-PaLM"~~ — era um painel separado com tabs (Diagnóstico, Atenção, Conselho, Simulação, Trace)
- ~~Seção "Clinical Intelligence Package"~~ — era um placeholder vazio (#cipContainer)
- ~~Seção "Recursos Conectados"~~ (Knowledge Graph Links) — substituída por hashtags + related tools
- ~~JS `nurse-palm.js`~~ — bundle separado do motor cognitivo
- ~~JS `cognitive-ui.js`~~ — painel visual separado
- ~~JS `knowledge-graph.js`~~ — seção de links

### O que substituiu (v2.0.0):

O raciocínio cognitivo do Nurse-PaLM agora se manifesta como **fluxo cognitivo vertical integrado** à página da calculadora (ver NIFS-900-02 §3):

| Step | Camada Nurse-PaLM | Manifestação UI |
|------|-------------------|-----------------|
| 1 — Parâmetros | Clinical Attention (L5) | Inputs da calculadora com dicas contextuais |
| 2 — Resultado | Uncertainty Model (L6) | Score + banner de status + faixa de interpretação |
| 3 — NANDA · NIC · NOC | Clinical Reasoning (L1) | Grid 3 colunas com diagnóstico, intervenção, resultado |
| 4 — Plano de Ação | Planner (L7) | Lista de ações baseadas no resultado |
| 5 — Avaliação NOC | Clinical Reasoning (L1) | Texto descritivo do monitoramento esperado |
| 6 — Segurança do Paciente | Safety Layer | 9 Certos + Metas IPSG (parte do perfil Profissional) |

### Ferramentas que consomem Nurse-PaLM:
- **Simulados** — cenários clínicos com feedback NANDA/NIC/NOC (ver NIFS-900-04 §3)
- **Flashcards** — repetição espaçada de NANDA/NIC/NOC/interpretação/segurança (ver NIFS-900-04 §4)

### Design System:
- O Nurse-PaLM não tem CSS próprio — usa o mesmo `site-styles.css` que toda a plataforma
- Ícones SVG inline (sprite compartilhado) — não usa Font Awesome para elementos cognitivos
- Paleta azul para componentes de decisão (igual ao restante do site)
- Sem dark mode separado — segue o tema da página

## 10. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial — mapeamento 10 camadas × Clinical Engine V8 | Leivis Melo |
| 2.0.0 | 2026-07-05 | UI integration — Nurse-PaLM como lógica integrada, não painel separado. Fluxo cognitivo vertical (6 steps). Remoção de CIP/cognitive-ui/knowledge-graph. | Leivis Melo |
