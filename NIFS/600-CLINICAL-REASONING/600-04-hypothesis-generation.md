# NIFS-600-04: Hypothesis Generation

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-600-04                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o motor de raciocínio gera hipóteses diagnósticas a partir de observações clínicas — o segundo estágio do pipeline cognitivo.

## 2. The Hypothesis Problem

Um enfermeiro não lê 200 observações e "sabe" o diagnóstico. Ele:
1. Identifica padrões (atenção seletiva)
2. Lembrava de casos similares (memória episódica)
3. Percorre mentalmente os diagnósticos possíveis (grafo de conhecimento)
4. Gera 3-5 hipóteses prováveis
5. Testa cada uma contra a evidência

O NIS modela este processo explicitamente.

## 3. Hypothesis Generation Pipeline

```
                    ┌──────────────────┐
                    │  Observações     │
                    │  (attention-     │
                    │   weighted)      │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
    ┌─────────▼──────┐ ┌────▼───────┐ ┌────▼───────────┐
    │ Graph Traversal│ │ Memory     │ │ Rule Matching  │
    │ (NANDA nodes)  │ │ Retrieval  │ │ (decision rules)│
    └─────────┬──────┘ └────┬───────┘ └────┬───────────┘
              │              │              │
              └──────────────┼──────────────┘
                             │
                    ┌────────▼─────────┐
                    │  Hypothesis      │
                    │  Merger &        │
                    │  Deduplication   │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  Prior           │
                    │  Assignment      │
                    │  (Bayesian priors)│
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  N Hypotheses    │
                    │  with P(x)       │
                    └──────────────────┘
```

## 4. Three Generation Strategies

### 4.1 Graph Traversal

Caminha pelo grafo de conhecimento das observações até os nós NANDA:

```
Observation: Braden = 12
    ↓ edge: indicates
Finding: Risco de integridade tissular comprometida
    ↓ edge: supports
NANDA: 00047 (Risco de Úlcera por Pressão)
    ↓ edge: co_occurs_with
NANDA: 00046 (Risco de Lesão Cutânea)
```

Cada caminho tem um **peso cumulativo** calculado pela multiplicação dos pesos das arestas.

| Path Property | Formula |
|---------------|---------|
| Path weight | Π(w_i) for each edge i in path |
| Path confidence | min(confidence_i) along path |
| Path depth | número de hops (máximo = 3) |

### 4.2 Memory Retrieval

Busca episódios passados similares e extrai diagnósticos que se confirmaram:

```
Current patient: Braden 12, UTI, 67a, pós-operatório
    ↓ similarity search (embedding cosine)
Similar episode: Braden 11, UTI, 70a, pós-op → confirmed 00047
Similar episode: Braden 13, UTI, 65a, pós-op → confirmed 00046
    ↓ extract
Hypothesis: 00047 (similarity_score = 0.89)
Hypothesis: 00046 (similarity_score = 0.72)
```

| Retrieval Parameter | Value |
|---------------------|-------|
| Similarity metric | Cosine similarity on embeddings |
| Top-K | 10 episódios mais similares |
| Minimum similarity | 0.60 |
| Weight in hypothesis | similarity_score × outcome_success |

### 4.3 Rule Matching

Avalia regras de decisão (`ni_rules.decision_rules`) contra as observações:

```
Rule: "Braden ≤ 12 AND UTI AND immobile → NANDA 00047"
Conditions:
  C1: braden_score ≤ 12     ✓ (12 ≤ 12)
  C2: population = 'ICU'     ✓ (UTI)
  C3: mobility = 'bedridden' ✓ (acentuado)
Match: 3/3 conditions met
→ Hypothesis: 00047 (match_score = 1.0)
```

## 5. Hypothesis Merging

As três estratégias podem gerar a mesma hipótese. O merger:

1. Agrupa por `nanda_code`
2. Combina scores: `combined_score = α×graph_score + β×memory_score + γ×rule_score`
3. Remove duplicatas
4. Ordena por score combinado

| Weight | Default | Rationale |
|--------|---------|-----------|
| α (graph) | 0.40 | Conhecimento estruturado |
| β (memory) | 0.35 | Experiência empírica |
| γ (rules) | 0.25 | Regras explícitas |

Pesos ajustáveis por aprendizado (`ni_attention.weights`).

## 6. Prior Assignment

Cada hipótese recebe uma probabilidade prévia (prior) antes da atualização bayesiana:

### 6.1 Prior Sources

| Source | When Used | Quality |
|--------|-----------|---------|
| Population prior | Sempre | Baseline por população |
| Empirical prior | Quando há dados | Frequência observada |
| Literature prior | Quando há evidência | Baseada em estudos |
| Uniform prior | Fallback | 1/N (não-informativo) |

### 6.2 Example

```
P(00047 | ICU, postop) = 0.32  (population prior)
P(00046 | ICU, postop) = 0.18  (population prior)
P(00200 | ICU, postop) = 0.08  (population prior)
... (normalized to sum = 1.0)
```

Estes priors vivem em `ni_prob.prior_beliefs`.

## 7. Hypothesis Quality Gates

Antes de passar hipóteses para o próximo estágio (Evidence Gathering):

| Gate | Threshold | Action if Failed |
|------|-----------|-----------------|
| Minimum hypotheses | ≥ 3 | Expand graph search depth |
| Maximum hypotheses | ≤ 15 | Filter by combined_score |
| Score spread | top - bottom ≥ 0.1 | If too uniform, flag ambiguity |
| Population coverage | ≥ 1 hypothesis relevant to population | Add population-specific NANDA |
| Safety check | All high-risk NANDAs included | Manual add if missing |

## 8. Schema Mapping

| Concept | Table | Key Fields |
|---------|-------|------------|
| Observation input | `ni_reasoning.steps` | step_type='observation', input_data |
| Generated hypothesis | `ni_reasoning.hypotheses` | nanda_code, prior_probability |
| Graph path | `ni_graph.edges` | source_node_id, target_node_id, weight |
| Memory retrieval | `ni_memory.case_similarity` | similarity_score |
| Rule match | `ni_rules.decision_rules` | rule_name, conditions |
| Prior belief | `ni_prob.prior_beliefs` | prior_value, prior_source |

## 9. Edge Cases

### 9.1 No Hypotheses Generated

Se nenhuma hipótese atinge score mínimo:
- Flag: `insufficient_data`
- Recomendar: coletar mais observações
- Não forçar diagnóstico

### 9.2 Too Many Hypotheses

Se > 15 hipóteses geradas:
- Aplicar filtro de attention score mais agressivo
- Limitar a top-15 por combined_score
- Registrar hipóteses filtradas no trace

### 9.3 Conflicting Hypotheses

Se duas hipóteses são mutuamente exclusivas (ex: "Risco de" vs "Presença de"):
- Manter ambas
- Sinalizar conflito para Evidence Gathering resolver
- Se irresolúvel: escalar para Council

## 10. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-02 | Reasoning Pipeline (parent) |
| NIFS-600-05 | Differential Diagnosis (next stage) |
| NIFS-600-08 | Bayesian Network (prior computation) |
| NIFS-600-16 | Clinical Memory (retrieval strategy) |
| NIFS-500-11 | Reasoning Graph (traversal) |

## 11. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — triple strategy generation | Leivis Melo |
