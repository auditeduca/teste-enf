# NIFS-600-22 — Feedback Learning Engine

**Seção:** 600 (Clinical Reasoning)
**Camada cognitiva:** 8 — Feedback Learning
**Status:** ✅ Implementado (v5.0)
**Arquivo de código:** `reference-clinical-engine/learning/feedbackLearning.js`
**Schema DDL:** `ni_learning` (3 tabelas)

## 1. Propósito

Fecha o loop de aprendizado: **desfecho observado → sinal de recompensa → ajuste de peso**. O sistema compara o que aconteceu com o que era esperado, calcula uma recompensa (positiva/negativa/neutra) e propaga ajustes para os pesos das arestas do grafo de conhecimento, regras clínicas, priors probabilísticos e scores de atenção.

Sem esta camada, o sistema repete os mesmos erros: uma intervenção NIC que sistematicamente falha para um perfil específico de paciente nunca teria seu peso reduzido.

## 2. Arquitetura

```
┌──────────────────────────────────────────────────┐
│            Feedback Learning Engine               │
│                                                   │
│  processOutcome(episodeId)                        │
│       │                                           │
│       ├──► _computeReward(outcome)                │
│       │     improved → +0.6    adverse → -0.9     │
│       │     + surprise modulation                 │
│       │                                           │
│       ├──► insert reinforcement_signals           │
│       │                                           │
│       ├──► fetch related graph edges              │
│       │     (NANDA → NIC aresta)                  │
│       │                                           │
│       ├──► compute weight_updates                 │
│       │     delta = reward × 0.05                 │
│       │     capped at ±0.15 (safety)              │
│       │                                           │
│       └──► record learning_curves                 │
│                                                   │
│  applyWeightUpdates()                             │
│       │                                           │
│       ├──► safety check (|delta| ≤ 0.15)          │
│       ├──► UPDATE edges SET weight = new_value    │
│       └──► mark validated / rejected              │
└──────────────────────────────────────────────────┘
```

## 3. Tabelas (ni_learning schema)

| Tabela | PK | Função |
|--------|-----|--------|
| `reinforcement_signals` | signal_id (UUID) | Sinal de recompensa por desfecho |
| `weight_updates` | update_id (UUID) | Delta de peso proposto (validação obrigatória) |
| `learning_curves` | curve_id (UUID) | Métricas de aprendizado ao longo do tempo |

## 4. Modelo de Recompensa

```
reward ∈ [-1, +1]

Base:
  improved    → +0.6
  resolved    → +0.8
  unchanged   →  0.0
  deteriorated → -0.5
  adverse     → -0.9

Modulações:
  + surprise_score × 0.1 (max ±0.3)
  + (outcome_value - expected_value) × 0.1 (max ±0.2)

Clamp final: [-1, +1]
```

## 5. Safety Constraints

- **Delta máximo por update:** ±0.15 (hard cap no DDL)
- **Validação obrigatória:** todo weight_update nasce como `pending` e precisa ser `validated` antes de aplicado ao grafo
- **Rollback:** updates podem ser revertidos para `rolled_back`
- **Rejection reason:** updates rejeitados devem ter motivo registrado

Em produção, a validação é feita por:
1. **Safety agent** (no conselho multiagente) — veto automático se delta > threshold
2. **Human reviewer** — para deltas significativos (> 0.10)
3. **Automated validator** — para deltas pequenos (< 0.05)

## 6. Integração com o Pipeline

O feedback learning é executado **após** o desfecho ser observado (assíncrono ao pipeline principal):

1. Orquestrador processa paciente → gera plano → executa
2. Desfecho é medido e registrado em `ni_memory.outcomes`
3. `processOutcome(episodeId)` é chamado:
   - Gera sinais de recompensa
   - Propõe ajustes de peso (pending)
   - Registra métricas de aprendizado
4. Periodicamente, `applyWeightUpdates()` valida e aplica os ajustes

## 7. Métricas de Aprendizado (learning_curves)

| Componente | Métrica | Descrição |
|------------|---------|-----------|
| feedback_learning | avg_reward | Recompensa média por episódio |
| feedback_learning | signal_count | Sinais gerados por episódio |
| feedback_learning | update_count | Updates propostos por episódio |
| feedback_learning | updates_applied | Updates validados e aplicados |
| feedback_learning | updates_rejected | Updates rejeitados por safety |

## 8. Roadmap

| Versão | Feature |
|--------|---------|
| v5.0 (atual) | Reward signals, weight updates, validation gate |
| v5.1 | TD-learning (temporal difference) para sequências |
| v6.0 | Bayesian weight updates (em vez de delta fixo) |
| v7.0 | Fine-tuning de modelo baseado em feedback acumulado |
