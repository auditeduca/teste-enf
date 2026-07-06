# NIFS-700-01: Foundation Model

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-700-01                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a estratégia de modelo de fundação para o Nurse-PaLM — a camada de IA que opera sobre o conhecimento estruturado para produzir inferência clínica cognitiva.

## 2. What is Nurse-PaLM?

Nurse-PaLM não é um único modelo. É uma **arquitetura de IA composta** que combina:

```
┌──────────────────────────────────────────────┐
│              Nurse-PaLM Stack                 │
├──────────────────────────────────────────────┤
│  LLM (Clinical Reasoning)                    │
│  ↓                                           │
│  RAG (Knowledge Retrieval)                   │
│  ↓                                           │
│  Knowledge Graph (Structured Knowledge)       │
│  ↓                                           │
│  Bayesian Engine (Probabilistic Inference)   │
│  ↓                                           │
│  Multi-Agent Council (Consensus)             │
│  ↓                                           │
│  Memory (Episodic Retrieval)                 │
│  ↓                                           │
│  Planner (Intervention Sequencing)           │
│  ↓                                           │
│  Simulator (Outcome Prediction)              │
└──────────────────────────────────────────────┘
```

## 3. Why Not Just an LLM?

Um LLM puro tem problemas fundamentais em clínica:

| Problem | LLM-only | Nurse-PaLM |
|---------|----------|------------|
| Alucinação | inventa NANDA, NIC, NOC | só usa códigos do grafo |
| Rastreabilidade | caixa preta | cada inferência tem trace |
| Probabilidade | texto sem P(x) | P(x) com IC e calibração |
| Conhecimento estático | frozen no treino | knowledge graph atualizável |
| Segurança | sem guardrails | safety layer + veto + human review |
| Memória | janela de contexto limitada | memória episódica persistente |
| Multagente | resposta única | conselho com dissidências |

## 4. Foundation Model Strategy

### 4.1 Phase 1: RAG-Augmented LLM (v5.0)

```
User Query → Embed → Vector Search → Top-K → Context → LLM → Response
                                                ↑
                                        Knowledge Graph
                                        + Bayesian Priors
```

- Base LLM: GPT-4 / Claude / Llama 3 (escolha por custo/latência)
- RAG sobre: NANDA, NIC, NOC, ISO, protocolos, evidências
- Guardrails: códigos só do grafo, sempre com P(x)

### 4.2 Phase 2: Domain-Adapted Model (v6.0)

- Fine-tuning com casos clínicos rotulados
- Dados de treino: `ni_memory.episodes` + `ni_council.human_decisions`
- Objetivo: reduzir alucinação e melhorar raciocínio clínico
- Avaliação: F1 > 0.90 em diagnóstico NANDA

### 4.3 Phase 3: Nurse-PaLM Native (v7.0+)

- Modelo treinado from scratch em:
  - Literatura de enfermagem (BDENF, PubMed Nursing)
  - Taxonomias completas (NANDA, NIC, NOC, ISO)
  - Casos clínicos anonimizados
  - Protocolos e guidelines
- Arquitetura: Transformer + Graph Neural Network híbrido
- Capacidade: raciocínio multi-passo, explicação, probabilidade

## 5. Model Registry

Todos os modelos são versionados em `ni_ai.model_registry`:

| Model ID | Version | Type | Status | F1 | Latency |
|----------|---------|------|--------|-----|---------|
| nurse-palm-rag-v1 | 1.0.0 | RAG+LLM | production | 0.87 | 2.1s |
| nurse-palm-rag-v2 | 2.0.0 | RAG+LLM | staging | 0.89 | 1.8s |
| nurse-palm-ft-v1 | 1.0.0 | Fine-tuned | experiment | 0.91 | 2.5s |
| nurse-palm-native-v1 | 0.1.0 | Native | research | — | — |

## 6. RAG Architecture

### 6.1 Knowledge Chunks

```
Knowledge Graph Nodes → Text Descriptions → Chunks → Embeddings → Vector DB
```

Cada nó do grafo é convertido em texto:

```
Node: NANDA:00047
Chunk: "NANDA-I 00047: Risco de Úlcera por Pressão. 
        Domínio: Segurança/Proteção. Classe: Lesão Física.
        Fatores de risco: imobilidade, fricção, cisalhamento, 
        umidade, nutrição inadequada.
        POPULAÇÕES DE RISCO: UTI (P=0.32), Geriatria (P=0.22).
        INTERVENÇÕES: NIC 3540, NIC 6540.
        DESFECHOS: NOC 1101 (Integridade Tissular)."
```

### 6.2 Retrieval Pipeline

```
Query: "Paciente UTI, Braden 12, imóvel"
    ↓ Embed query
    ↓ Vector search (top-20)
    ↓ Re-rank by: clinical relevance + evidence grade
    ↓ Filter by: population match + context fit
    ↓ Top-5 chunks
    ↓ Inject as context to LLM
```

### 6.3 Hallucination Prevention

| Guardrail | Mechanism |
|-----------|-----------|
| Code-only output | LLM forced to output from graph node IDs |
| Probability mandatory | Template: "NANDA {code}: P={value}, IC={interval}" |
| Evidence citation | Every claim must reference `graded_evidence` |
| Safety check | Post-generation filter against `ni_council.veto_events` |
| Human review | Low confidence or high ambiguity → human queue |

## 7. Embedding Strategy

| Content Type | Model | Dimension | Notes |
|-------------|-------|-----------|-------|
| NANDA/NIC/NOC descriptions | text-embedding-3-large | 1536 | PT-BR + EN |
| Clinical cases (episodes) | text-embedding-3-large | 1536 | Symptom + diagnosis |
| Evidence (papers) | PubMedBERT | 768 | Domain-specific |
| Patient observations | BiomedNLP-PubMedBERT | 768 | Clinical language |

Embeddings vivem em `ni_ai.content_embeddings` com suporte a pgvector.

## 8. Inference Pipeline

```
1. Receive: observations + context + query
2. Attention: filter to critical observations
3. RAG: retrieve relevant knowledge
4. Graph: traverse for hypotheses
5. Bayesian: compute P(diagnosis|evidence)
6. Council: multi-agent deliberation
7. Planner: generate intervention plan
8. Explain: compile decision trace
9. Safety: verify no red flags
10. Output: diagnosis + P(x) + plan + explanation
```

Target latency: < 3.5s end-to-end.

## 9. Evaluation Framework

| Metric | Target | Method |
|--------|--------|--------|
| Diagnostic F1 | > 0.90 | Validation cases (`ni_test.validation_cases`) |
| Brier Score | < 0.15 | Calibration on historical cases |
| Explanation quality | > 4/5 | Expert review score |
| Hallucination rate | < 2% | Code verification against graph |
| Safety violation | 0% | Safety check pass rate |
| Latency P95 | < 5s | Production monitoring |

## 10. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-700-02 | RAG (retrieval detail) |
| NIFS-700-03 | Embeddings (vector detail) |
| NIFS-700-15 | Fine-Tuning (domain adaptation) |
| NIFS-700-18 | Safety Layer (guardrails) |
| NIFS-700-19 | Hallucination Prevention |
| NIFS-600-02 | Reasoning Pipeline (cognitive orchestration) |

## 11. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — Nurse-PaLM 3-phase strategy | Leivis Melo |
