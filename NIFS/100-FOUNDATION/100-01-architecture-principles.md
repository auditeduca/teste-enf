# NIFS-100-01: Architecture Principles

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-100-01                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir os princípios arquiteturais fundamentais que governam todas as decisões de design no Nursing Intelligence System.

## 2. The 10 Commandments of NIS Architecture

### P1. Specification-First

A especificação (NIFS) precede implementação. Todo artefato — SQL, API, IA, UI — é derivado da especificação, nunca o contrário.

```
NIFS → Generators → Artifacts → Runtime
```

### P2. Knowledge is Graph, Not Table

O conhecimento clínico é fundamentalmente relacional. Tabelas são uma projeção do grafo de conhecimento, não o contrário. O grafo (Neo4j ou equivalente) é a representação canônica; o PostgreSQL é a projeção operacional.

### P3. Reasoning is First-Class

Raciocínio não é uma query. É um pipeline cognitivo com hipóteses, evidências, probabilidades, explicações e rastro. O motor de raciocínio é o coração do sistema, não um módulo periférico.

### P4. Uncertainty is Explicit

Nenhuma recomendação clínica é determinística. Toda saída carrega probabilidade, intervalo de confiança e nível de incerteza. "Diagnóstico: X" é inaceitável; "NANDA A 74% (IC 95%: 0.68–0.80)" é o padrão.

### P5. Explainability is Non-Negotiable

Cada inferência tem um rastro completo: quais observações, quais regras, quais evidências, qual peso, qual probabilidade. Sem explicação, não há recomendação.

### P6. Memory Enables Learning

O sistema lembra de casos. Compara com casos similares. Aprende com desfechos. Atualiza pesos. Sem memória episódica, o sistema apenas consulta — não aprende.

### P7. Context Changes Decisions

Paciente grave + UTI lotada + sem bomba = decisão diferente. O World Model fornece contexto que modifica o raciocínio. Decisões que ignoram contexto são incompletas.

### P8. Attention is Selective

200 observações não têm o mesmo peso. O sistema identifica as 6 críticas e prioriza. Attention é um mecanismo de primeira classe, não um filtro secundário.

### P9. Consensus, Not Dictatorship

Nenhuma decisão clínica complexa é tomada por um único agente. O Conselho Multiagente vota, delibera, e produz consenso com dissidências registradas.

### P10. Human is Final Authority

A IA propõe. O enfermeiro decide. Toda recomendação pode ser aceita, modificada, rejeitada ou escalada. O feedback humano alimenta o aprendizado.

## 3. Architectural Patterns

### 3.1 Layered Architecture

```
Layer 0: Philosophy         (NIFS-000)
Layer 1: Clinical Science   (NIFS-200)
Layer 2: Knowledge Model    (NIFS-300)
Layer 3: Data Model         (NIFS-400)
Layer 4: Knowledge Graph    (NIFS-500)
Layer 5: Clinical Reasoning (NIFS-600)
Layer 6: AI Architecture    (NIFS-700)
Layer 7: Interoperability   (NIFS-800)
Layer 8: Platform           (NIFS-900)
Layer 9: Security           (NIFS-1000)
Layer 10: Governance        (NIFS-1100)
Layer 11: Quality           (NIFS-1200)
```

### 3.2 Cognitive Flow

```
World Model → Attention → Reasoning → Hypotheses → Probability →
Council → Planner → Execution → Memory → Outcome → Learning →
Simulation → (loop back to Attention)
```

### 3.3 Event-Driven Clinical Events

Mudanças clínicas são eventos. Eventos disparados por observações, scores, alertas. O sistema reage a eventos, não apenas responde a queries.

### 3.4 CQRS for Clinical Data

- **Write side**: structured clinical input (assessments, observations, interventions)
- **Read side**: projections for reasoning, graph traversal, search, analytics

## 4. Anti-Patterns to Avoid

| Anti-Pattern | Why It's Wrong | Correct Approach |
|-------------|----------------|-----------------|
| Excel → Banco direto | Acoplamento frágil | Excel → SPEC → Generators → Banco |
| Resposta sem probabilidade | Falsa certeza | Sempre com P(x) e IC |
| Recomendação sem explicação | Caixa preta | Rastro completo obrigatório |
| Conhecimento sem versionamento | Mudanças sem rastreabilidade | Semantic versioning em tudo |
| Agente único decidindo | Viés, sem dissidência | Conselho multiagente |
| Ignorar contexto | Decisão descontextualizada | World Model sempre ativo |
| Aprendizado sem validação | Drift, erros se amplificam | Human-in-the-loop obrigatório |

## 5. Decision Framework

Quando houver conflito entre princípios, a precedência é:

1. **Segurança clínica** > tudo
2. **Explicabilidade** > performance
3. **Incerteza explícita** > simplicidade
4. **Especificação** > implementação
5. **Grafo** > tabela
6. **Consenso** > velocidade
7. **Contexto** > abstração

## 6. References

- Domain-Driven Design (Eric Evans)
- Clean Architecture (Robert C. Martin)
- Building Evolutionary Architectures (Neal Ford)
- Clinical Judgment Model (Christine Tanner)
- Evidence-Based Practice in Nursing

## 7. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft | Leivis Melo |
