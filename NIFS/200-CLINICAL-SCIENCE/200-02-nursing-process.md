# NIFS-200-02: Nursing Process

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-200-02                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir o Processo de Enfermagem (ADPIE) como o workflow clínico fundamental que o NIS modela, automatiza e enriquece com inferência cognitiva.

## 2. The ADPIE Model

O Processo de Enfermagem é um método sistemático, deliberado e intencional de resolver problemas clínicos. O NIS não substitui este processo — o **incorpora como arquitetura**.

```
A — Assessment      (Coleta de dados clínicos)
D — Diagnosis       (Diagnóstico de enfermagem NANDA-I)
P — Planning        (Plano de cuidado com NIC e NOC)
I — Implementation  (Execução de intervenções)
E — Evaluation      (Avaliação de desfechos e reavaliação)
```

## 3. ADPIE → NIS Mapping

Cada fase do ADPIE corresponde a um conjunto de módulos cognitivos do NIS:

| Fase ADPIE | Módulo NIS | Schema Principal | Output |
|------------|-----------|-----------------|--------|
| **Assessment** | Observation Ingestion + Clinical Attention | `ni_attention`, `ni_temporal` | Observações priorizadas |
| **Diagnosis** | Hypothesis Generation + Bayesian Update + Council | `ni_reasoning`, `ni_prob`, `ni_council` | Diagnóstico com P(x) e explicação |
| **Planning** | Planner + Outcome Prediction | `ni_planner`, `ni_twin` | Grafo de plano com branches |
| **Implementation** | Plan Execution + Memory | `ni_planner.plan_executions`, `ni_memory` | Registro de ações executadas |
| **Evaluation** | Outcome Comparison + Learning Loop | `ni_memory.outcomes`, `ni_learning` | Desfecho + ajuste de pesos |

## 4. Assessment Phase — Detail

### 4.1 Data Sources

| Source | Type | Examples |
|--------|------|----------|
| Sinais vitais | Automated | PA, FC, FR, SpO2, Temp |
| Escores clínicos | Calculated | Braden, Glasgow, APGAR, NEWS2, MEWS |
| Observação direta | Manual | Aspecto, comportamento, dor |
| Exames laboratoriais | External | Hemograma, gasometria, eletrólitos |
| Relato do paciente | Subjective | "Sinto dor", "Tontura ao levantar" |
| História clínica | Historical | Comorbidades, medicamentos, alergias |
| Padrões de Gordon | Structured | 11 padrões funcionais de saúde |

### 4.2 Gordon's Functional Health Patterns

O NIS suporta os 11 padrões funcionais de Gordon como framework de assessment estruturado:

| # | Pattern | Domain |
|---|---------|--------|
| 1 | Percepção-Controle de Saúde | Compliance, prevenção |
| 2 | Nutricional-Metabólico | Dieta, hidratação, pele |
| 3 | Eliminação | Urinário, intestinal |
| 4 | Atividade-Exercício | Mobilidade, ADLs |
| 5 | Sono-Repouso | Qualidade do sono |
| 6 | Cognitivo-Perceptual | Dor, orientação, sensibilidade |
| 7 | Auto-Percepção-Autoconceito | Identidade, autoestima |
| 8 | Papéis-Relacionamentos | Suporte social, família |
| 9 | Sexualidade-Reprodução | Função sexual |
| 10 | Adaptação-Tolerância ao Estresse | Coping, ansiedade |
| 11 | Valores-Crenças | Espiritualidade, cultura |

### 4.3 Attention-Weighted Assessment

O assessment não trata todas as observações igualmente. O módulo de Clinical Attention:

1. Recebe 200+ observações
2. Calcula `attention_score` para cada uma
3. Filtra as 6-10 mais críticas
4. Marca o resto como `ignored` (com motivo)
5. Passa apenas as salientes para o motor de raciocínio

## 5. Diagnosis Phase — Detail

### 5.1 From Observations to NANDA-I

```
Observations (attention-weighted)
    ↓
Graph Traversal: Observation → Finding → NANDA node
    ↓
N candidate diagnoses
    ↓
For each: P(diagnosis|observations) = prior × likelihood / evidence
    ↓
Bayesian update with evidence for/against
    ↓
Ranked differential: NANDA A 74%, NANDA B 18%, NANDA C 6%
```

### 5.2 Diagnostic Confidence Levels

| Confidence | Action |
|-----------|--------|
| > 80% | Propose diagnosis directly |
| 60–80% | Propose + request confirmation |
| 40–60% | Suggest additional assessment |
| < 40% | Flag as insufficient data |

## 6. Planning Phase — Detail

### 6.1 NNN Triad

O plano liga NANDA → NIC → NOC:

```
NANDA (Diagnosis) → NIC (Intervention) → NOC (Outcome)
     00047              3540               1101
  Úlcera por Pressão   Reduzir Pressão   Integridade Tissular
```

### 6.2 Plan as Directed Graph

O plano não é uma lista. É um **grafo dirigido** com branches condicionais:

```
[Start] → [NIC 3540: Reduzir Pressão]
              ↓
         [Evaluate NOC 1101]
          /              \
    improved            not improved
        ↓                  ↓
   [Continue]         [NIC 6540: Mudança de Posição]
                          ↓
                     [Evaluate again]
                      /          \
                  improved      deteriorated
                     ↓              ↓
                 [Continue]   [Escalate Protocol C]
```

## 7. Implementation Phase — Detail

Cada intervenção executada é registrada em `ni_memory.actions` com:
- Timestamp
- NIC code
- Dados da execução
- Sessão de raciocínio que a gerou
- Estado do World Model no momento

## 8. Evaluation Phase — Detail

### 8.1 Expected vs Actual

```
expected_noc_value = 4  (previsto pelo planner)
actual_noc_value   = 2  (observado)
surprise_score     = |4 - 2| = 2  (ALTO → forte sinal de aprendizado)
```

### 8.2 Learning Trigger

Se `surprise_score > threshold`:
1. Gerar `ni_learning.reinforcement_signal` (negativo)
2. Sugerir `ni_learning.weight_update`
3. Queue para validação humana
4. Se aprovado: atualizar peso no grafo

## 9. The ADPIE Loop

O ADPIE não é linear. É **cíclico**:

```
A → D → P → I → E → A → D → P → I → E → ...
```

Cada ciclo de reavaliação pode:
- Confirmar o diagnóstico atual
- Modificar o plano
- Gerar novo diagnóstico
- Escalar para protocolo de urgência

O NIS modela este loop explicitamente via `ni_reasoning.sessions` com status `reassessing`.

## 10. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-03 | Assessment (detail) |
| NIFS-200-14 | NANDA-I (terminology) |
| NIFS-200-15 | NIC (terminology) |
| NIFS-200-16 | NOC (terminology) |
| NIFS-600-01 | Clinical Workflow (implementation) |
| NIFS-600-02 | Reasoning Pipeline (cognitive) |

## 11. References

- Alfaro-LeFevre, R. (2010). Applying Nursing Process: A Tool for Critical Thinking
- Herdman, T.H. et al. (2024). NANDA-I Nursing Diagnoses: Definitions and Classification
- Butcher, H.K. et al. (2024). Nursing Interventions Classification (NIC)
- Moorhead, S. et al. (2024). Nursing Outcomes Classification (NOC)
- Gordon, M. (1994). Nursing Diagnosis: Process and Application

## 12. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — ADPIE → NIS mapping | Leivis Melo |
