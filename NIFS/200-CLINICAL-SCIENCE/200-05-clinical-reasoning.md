# NIFS-200-05: Clinical Reasoning

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-200-05                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o modelo de raciocínio clínico de enfermagem que o NIS modela computacionalmente — como o enfermeiro pensa, não apenas o que ele sabe.

## 2. The Core Gap

> "O banco representa muito bem o **conhecimento** da enfermagem, mas ainda representa pouco o **processo cognitivo** da enfermagem. Essa diferença é o que separa um excelente sistema de apoio à decisão de um verdadeiro Nurse-PaLM."

## 3. Tanner's Clinical Judgment Model

O NIS adota o modelo de Christine Tanner (2006) como base teórica do raciocínio clínico:

```
┌──────────────────────────────────────────────┐
│         TANNER'S CLINICAL JUDGMENT MODEL      │
├──────────────────────────────────────────────┤
│                                              │
│  1. NOTICING                                 │
│     ↑                                        │
│     ├─ Experiência prévia (Memory)           │
│     ├─ Expectativas do contexto (World Model)│
│     └─ Estilo cognitivo (Attention)          │
│                                              │
│  2. INTERPRETING                             │
│     ├─ Análise analítica (Bayesian)          │
│     ├─ Intuição (Pattern matching)           │
│     └─ Reconhecimento de similaridade (Memory)│
│                                              │
│  3. RESPONDING                               │
│     ├─ Intervenção (Planner + NIC)           │
│     ├─ Protocolo (Protocol Engine)           │
│     └─ Escalação (Safety Layer)              │
│                                              │
│  4. REFLECTING                               │
│     ├─ Em ação (Monitoring)                  │
│     └─ Pós ação (Learning Loop)              │
│                                              │
└──────────────────────────────────────────────┘
```

## 4. Tanner → NIS Mapping

| Tanner Phase | Cognitive Process | NIS Module | Schema |
|-------------|-------------------|------------|--------|
| **Noticing** | Coleta e filtragem perceptiva | Clinical Attention | `ni_attention.*` |
| **Interpreting** | Geração de significado | Hypothesis + Bayesian | `ni_reasoning.hypotheses`, `ni_prob.*` |
| **Responding** | Ação clínica | Planner + Council | `ni_planner.*`, `ni_council.*` |
| **Reflecting-in-action** | Monitoramento contínuo | Temporal Graph + Monitoring | `ni_temporal.*` |
| **Reflecting-on-action** | Aprendizado retrospectivo | Learning Loop + Memory | `ni_learning.*`, `ni_memory.*` |

## 5. Reasoning Modalities

O enfermeiro não usa apenas um tipo de raciocínio. O NIS modela três:

### 5.1 Analytic Reasoning

Raciocínio lógico, passo a passo, quando o caso é complexo ou pouco familiar:

```
Observação → Análise → Hipótese → Teste → Conclusão
   Braden 12    Imobilidade   00047?   Evidência   00047 (74%)
```

- **Quando**: caso atípico, enfermeiro inexperiente, múltiplas comorbidades
- **NIS módulo**: Reasoning Pipeline completo (Stage 1-10)
- **Custo cognitivo**: alto (latência ~3s)
- **Explicabilidade**: máxima (rastro completo)

### 5.2 Intuitive Reasoning

Reconhecimento de padrão, quando o caso é familiar:

```
Pattern match: "Já vi isto antes → 00047"
   Braden 12 + UTI + pós-op → reconhecimento imediato
```

- **Quando**: caso típico, enfermeiro experiente, padrão claro
- **NIS módulo**: Memory Retrieval com alta similaridade (> 0.90)
- **Custo cognitivo**: baixo (latência < 500ms)
- **Explicabilidade**: média (pattern match + caso similar)
- **Guardrail**: sempre validar com analytic se houver qualquer ambiguidade

### 5.3 Narrative Reasoning

Compreensão holística da história do paciente:

```
"Este paciente tem 67a, viúvo, mora sozinho, foi admitido 
pós-fratura fêmur, não tem cuidador em casa, medo de cair..."
→ Contexto muda a decisão (discharge planning diferente)
```

- **Quando**: planejamento de alta, cuidado longitudinal, contexto psicossocial
- **NIS módulo**: World Model + Memory (episódios longitudinais)
- **Custo cognitivo**: médio
- **Explicabilidade**: narrativa + dados estruturados

## 6. Reasoning Mode Selection

O NIS seleciona automaticamente o modo de raciocínio:

```
┌─────────────────────────────────────┐
│ Caso típico? (memory similarity>0.9)│
│   → Sim: Intuitive (fast path)      │
│   → Não: Continuar                  │
├─────────────────────────────────────┤
│ Caso complexo? (entropy > 1.0 bit)  │
│   → Sim: Analytic (full pipeline)   │
│   → Não: Continuar                  │
├─────────────────────────────────────┤
│ Contexto psicossocial relevante?    │
│   → Sim: Narrative (enrich context) │
│   → Não: Analytic standard          │
└─────────────────────────────────────┘
```

| Mode | Trigger | Latency | Explanation Depth |
|------|---------|---------|------------------|
| Intuitive | similarity > 0.90 + low entropy | < 500ms | Medium |
| Analytic | default / high entropy / atypical | ~3s | Full |
| Narrative | psychosocial factors significant | ~3s | Full + narrative |
| Hybrid | intuitive flag → analytic verify | ~3.5s | Full |

## 7. Clinical Reasoning vs. Clinical Knowledge

| Aspect | Knowledge (v4.2) | Reasoning (v5.0) |
|--------|-----------------|------------------|
| Question | "O que é NANDA 00047?" | "Este paciente tem 00047?" |
| Output | Definição, fatores de risco | P(00047) = 74% + explicação |
| Process | Lookup | Pipeline cognitivo |
| Memory | None | Episódica (casos similares) |
| Uncertainty | None | Bayesiana com IC |
| Context | None | World Model |
| Learning | None | Feedback loop |
| Explanation | None | Trace completo |

## 8. The Reasoning Trap

### 8.1 Anchoring Bias

O enfermeiro (ou a IA) fixa no primeiro diagnóstico e ignora evidência contrária.

**Mitigação NIS**: Bayesian update sempre considera contra-evidência. Se P(D) cai abaixo de 0.20 após contra-evidência, o sistema reabre hipóteses.

### 8.2 Confirmation Bias

Buscar apenas evidência que confirma a hipótese inicial.

**Mitigação NIS**: Evidence Gathering (Stage 3) sempre busca `evidence_for` E `evidence_against` em paralelo.

### 8.3 Availability Bias

Diagnósticos recentes ou memoráveis são superponderados.

**Mitigação NIS**: Memory retrieval tem decay temporal. Episódios recentes têm peso maior, mas o grafo de conhecimento (estável) equilibra.

### 8.4 Premature Closure

Aceitar o primeiro diagnóstico plausível sem considerar alternativas.

**Mitigação NIS**: Quality gate exige ≥ 3 hipóteses antes de seleção. Differential ranking sempre mostra top-3 com probabilidades.

## 9. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-04 | Clinical Judgment (Tanner model detail) |
| NIFS-600-02 | Reasoning Pipeline (implementation) |
| NIFS-600-04 | Hypothesis Generation (interpreting) |
| NIFS-600-10 | Clinical Attention (noticing) |
| NIFS-600-17 | Learning Loop (reflecting) |
| NIFS-600-16 | Clinical Memory (experience-based) |

## 10. References

- Tanner, C.A. (2006). Thinking Like a Nurse: A Research-Based Model of Clinical Judgment in Nursing. Journal of Nursing Education, 45(6), 204-211.
- Benner, P. (1984). From Novice to Expert: Excellence and Power in Clinical Nursing Practice.
- Simmons, B. (2010). Clinical Reasoning: Concept Analysis. Journal of Advanced Nursing, 66(5), 1151-1158.
- Pesut, D.J. & Herman, J. (1999). Outcome-Present State-Test (OPT) Model of Clinical Reasoning.

## 11. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — Tanner model + reasoning modalities | Leivis Melo |
