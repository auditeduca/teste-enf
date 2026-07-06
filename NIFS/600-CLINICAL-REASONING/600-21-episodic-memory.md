# NIFS-600-21 — Episodic Memory Engine

**Seção:** 600 (Clinical Reasoning)
**Camada cognitiva:** 2 — Episodic Memory
**Status:** ✅ Implementado (v5.0)
**Arquivo de código:** `reference-clinical-engine/memory/episodicMemory.js`
**Schema DDL:** `ni_memory` (5 tabelas)

## 1. Propósito

A camada de Memória Episódica armazena e recupera episódios clínicos completos (admissão → intervenção → desfecho) para suportar raciocínio baseado em casos (case-based reasoning). Quando o sistema enfrenta um novo paciente, a memória episódica permite recall de casos similares, fornecendo evidência empírica complementar à inferência bayesiana.

Esta camada foi identificada como **gap crítico** no mapeamento NIFS-700-00: a Clinical Engine V8 não possuía persistência de episódios, limitando o aprendizado à sessão atual.

## 2. Arquitetura

```
┌─────────────────────────────────────────────────────┐
│              Episodic Memory Engine                  │
│                                                      │
│  storeEpisode()          recallSimilar()            │
│       │                        │                     │
│       ▼                        ▼                     │
│  ┌─────────┐  pgvector   ┌──────────┐               │
│  │episodes │  cosine     │ vector   │               │
│  │obs      │  similarity │ search   │               │
│  │actions  │             │ top-k    │               │
│  │outcomes │             └──────────┘               │
│  │learnings│                                         │
│  └─────────┘           extractLearnings()            │
│                              │                       │
│                              ▼                       │
│                    effective/ineffective/            │
│                    adverse/time/context              │
└─────────────────────────────────────────────────────┘
```

## 3. Tabelas (ni_memory schema)

| Tabela | PK | Função |
|--------|-----|--------|
| `episodes` | episode_id (UUID) | Registro do episódio com embedding vetorial |
| `observations` | observation_id (UUID) | Sinais clínicos observados no episódio |
| `actions` | action_id (UUID) | Intervenções NIC executadas |
| `outcomes` | outcome_id (UUID) | Desfechos NOC medidos |
| `learnings` | learning_id (UUID) | Aprendizados extraídos (auto-gerados) |

## 4. API

### storeEpisode(episode)
Persiste um episódio completo: observações, ações, desfechos e metadados. Gera embedding automaticamente se não fornecido.

### recallSimilar(query, k)
Retorna os top-k episódios mais similares usando similaridade vetorial cosine (pgvector). Fallback: filtro por tipo + success_score.

### extractLearnings(episodeId)
Compara ações vs desfechos para extrair aprendizados estruturados:
- `effective_intervention`: NIC → improved/resolved (weight +0.05)
- `ineffective_intervention`: NIC → deteriorated (weight -0.05)
- `adverse_reaction`: NIC → adverse (weight -0.10)
- `time_pattern`: padrões temporais entre episódios
- `context_pattern`: padrões contextuais compartilhados

### generateEmbedding(episode)
Placeholder: hash determinístico → 1536-dim. Produção: `text-embedding-3-small`.

## 5. Integração com o Pipeline

A memória episódica é chamada no **Step 2** do orquestrador cognitivo, após a filtragem de atenção e antes do raciocínio bayesiano. Os episódios recuperados servem como:
- **Priors informados** para a inferência bayesiana (em vez de priors uniformes)
- **Evidência empírica** para o conselho multiagente
- **Base de casos** para a simulação (digital twin)

## 6. Dependências

- PostgreSQL 15+ com extensão `pgvector`
- Supabase client (ou cliente PostgreSQL compatível)
- Schema `ni_memory` (DDL v5.0)
- Função RPC `match_episodes` (para busca vetorial)

## 7. Roadmap

| Versão | Feature |
|--------|---------|
| v5.0 (atual) | Store, recall, extract learnings |
| v5.1 | Embedding model real (OpenAI/local) |
| v5.2 | Time pattern detection entre episódios |
| v6.0 | Context pattern clustering |
| v7.0 | Fine-tuning de embeddings por domínio clínico |
