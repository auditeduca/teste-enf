# NIFS-600-16: Clinical Memory

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-600-16                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir a arquitetura de memória episódica do NIS — o mecanismo que permite ao sistema "lembrar" de casos anteriores e usar essas experiências para melhorar o raciocínio futuro.

## 2. The Memory Gap

LLMs modernos trabalham com memória. O banco v4.2 possui **conhecimento** mas não possui **memória**.

```
Conhecimento (estático):     Memória (experiencial):
  NANDA 00047 = código        Paciente A, UTI, Braden 12
  NIC 3540 = intervenção      → NIC 3540 executado
  NOC 1101 = desfecho         → NOC 1101 melhorou de 2→4
                               → Funcionou! Armazenar.
```

Sem memória, o sistema apenas **consulta**. Com memória, o sistema **aprende**.

## 3. Memory Architecture

### 3.1 Three Memory Types

| Type | Scope | Retention | Schema |
|------|-------|-----------|--------|
| **Episódica** | Casos individuais | Permanente | `ni_memory.*` |
| **Semântica** | Conhecimento geral | Permanente (atualizável) | `ni_graph.*` |
| **Trabalho** | Sessão atual | Efêmera (durante raciocínio) | `ni_reasoning.steps` |

### 3.2 Episodic Memory Structure

```
Episode (caso clínico completo)
    ↓ has
Observation (o que foi observado)
    ↓ triggers
Action (o que foi feito)
    ↓ produces
Outcome (o que aconteceu)
    ↓ generates
Learning (o que se aprendeu)
```

## 4. Episode Lifecycle

### 4.1 Creation

Um episódio é criado quando:
- Nova sessão de raciocínio inicia (`ni_reasoning.sessions`)
- Paciente é admitido (`ni.cases`)
- Intervenção significativa é executada

### 4.2 Accumulation

Durante o episódio, observações, ações e desfechos são acumulados:

```
Episode: paciente_X, UTI, 5 dias
  Day 1: Braden 12, Glasgow 11 → NIC 3540 started
  Day 2: Braden 11, no change → NIC 6540 added
  Day 3: Braden 13, improving → continue
  Day 4: Braden 15, NOC 1101 = 3 → reduce frequency
  Day 5: Braden 18, NOC 1101 = 4 → discharge prep
```

### 4.3 Closure

Episódio é fechado quando:
- Paciente recebe alta
- Caso é resolvido
- Transferência de unidade

No fechamento:
- Calcular `success_score` (desfecho vs objetivo)
- Gerar `learnings`
- Calcular embedding para retrieval futuro
- Atualizar priors empíricos se divergente

## 5. Case Similarity & Retrieval

### 5.1 Embedding-Based Retrieval

Cada episódio tem um embedding (`similarity_embedding`) que captura:
- Observações principais (attention-weighted)
- Diagnóstico confirmado
- População
- Intervenção executada
- Desfecho

```sql
-- Find similar cases
SELECT episode_id, similarity_score
FROM ni_memory.episodes
ORDER BY similarity_embedding <=> query_embedding
LIMIT 10;
```

### 5.2 Similarity Score

```
similarity_score = cosine(episode_embedding, query_embedding)
```

| Score | Interpretation | Use |
|-------|---------------|-----|
| > 0.85 | Muito similar | High-weight evidence |
| 0.70–0.85 | Similar | Medium-weight |
| 0.60–0.70 | Moderadamente similar | Low-weight |
| < 0.60 | Pouco similar | Ignored |

### 5.3 What is Retrieved

Ao recuperar um caso similar, o sistema obtém:

```
"Para um paciente similar (Braden 11, UTI, 70a):
 - Diagnóstico confirmado: 00047
 - Intervenção eficaz: NIC 3540 + NIC 6540
 - Desfecho: NOC 1101 melhorou 2→4 em 72h
 - Intervenção ineficaz: NIC 2250 (mudança de colchão sozinha)
 - Tempo para melhora: 3 dias
 - Sucesso: 0.82"
```

Esta informação **alimenta a geração de hipóteses** (estratégia de Memory Retrieval no NIFS-600-04).

## 6. Memory → Learning → Weight Update

```
Episode closed
    ↓
Success score calculated
    ↓
If surprise_score > threshold:
    ↓
Generate learning (ni_memory.learnings)
    ↓
Generate reinforcement signal (ni_learning.reinforcement_signals)
    ↓
Suggest weight update (ni_learning.weight_updates)
    ↓
Human validation (mandatory)
    ↓
If approved: apply to graph (ni_graph.edges.weight)
    ↓
Update priors (ni_prob.prior_beliefs)
    ↓
Update attention weights (ni_attention.weights)
```

## 7. Memory Consolidation

Periodicamente, memórias episódicas são consolidadas em conhecimento semântico:

| Pattern Found | Consolidation |
|---------------|---------------|
| NIC 3540 worked in 47/50 similar episodes | Increase edge weight: NANDA 00047 → NIC 3540 |
| NIC 2250 alone failed in 30/30 cases | Decrease edge weight |
| Braden ≤ 12 → 00047 in 87% of ICU cases | Update population prior |
| Morning shift has better outcomes | Update staff_context attention weight |

Consolidação é **sempre** validada por humano antes de aplicar.

## 8. Memory Decay

Memórias antigas podem perder relevância:

| Age | Status | Treatment |
|-----|--------|-----------|
| < 6 months | Fresh | Full weight |
| 6-12 months | Recent | 0.8× weight |
| 1-2 years | Aging | 0.5× weight |
| > 2 years | Historical | 0.2× weight (unless unique) |

**Exceção:** episódios com `outcome_type = 'adverse'` nunca decaem (sempre lembrar de erros).

## 9. Schema Summary

| Table | Purpose |
|-------|---------|
| `ni_memory.episodes` | Episódios clínicos completos |
| `ni_memory.observations` | Observações dentro do episódio |
| `ni_memory.actions` | Ações executadas |
| `ni_memory.outcomes` | Desfechos observados |
| `ni_memory.learnings` | Aprendizados extraídos |
| `ni_memory.case_similarity` | Pares de casos similares |

## 10. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-04 | Hypothesis Generation (uses memory retrieval) |
| NIFS-600-17 | Learning Loop (memory → learning) |
| NIFS-700-06 | Memory (AI implementation) |
| NIFS-300-10 | Events (temporal model) |

## 11. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — full episodic memory model | Leivis Melo |
