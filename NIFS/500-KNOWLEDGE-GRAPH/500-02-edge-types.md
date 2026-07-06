# NIFS-500-02: Edge Types

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-500-02                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir todos os tipos de arestas (relações) do grafo de conhecimento clínico. As arestas carregam o **significado** das conexões entre conceitos.

## 2. Edge Type Catalog

### 2.1 Clinical Relationship Types

| Edge Type | Direction | Description | Example |
|-----------|-----------|-------------|---------|
| `activates` | Observation → NANDA | Observação ativa/gatilha hipótese diagnóstica | Braden=12 → 00047 |
| `treats` | NIC → NANDA | Intervenção trata diagnóstico | NIC 3540 → 00047 |
| `assesses` | CALC → NANDA | Calculadora avalia risco para diagnóstico | BRADEN → 00047 |
| `implies` | NANDA → NANDA | Diagnóstico implica outro (co-morbidade) | 00047 → 00046 |
| `contradicts` | NANDA → NANDA | Diagnósticos mutuamente exclusivos | Actual → Risk (mesmo focus) |
| `part_of` | NANDA → Domain | Conceito é parte de uma hierarquia | 00047 → Safety/Protection |
| `maps_to` | NANDA → SNOMED | Equivalência cross-terminology | 00047 → SNOMED 420324007 |
| `precedes` | Event → Event | Sequência temporal causal | Hipotensão → Taquicardia |
| `co_occurs` | NANDA → NANDA | Diagnósticos frequentemente co-ocorrem | 00047 → 00004 (Risco Infecção) |
| `causes` | Factor → NANDA | Fator causal | Imobilidade → 00047 |

### 2.2 NNN Link Types (NANDA-NIC-NOC)

| Edge Type | Direction | Description |
|-----------|-----------|-------------|
| `nanda_to_nic` | NANDA → NIC | Diagnóstico tratado por intervenção |
| `nanda_to_noc` | NANDA → NOC | Diagnóstico medido por desfecho |
| `nic_to_noc` | NIC → NOC | Intervenção melhora desfecho |
| `calc_to_nanda` | CALC → NANDA | Calculadora prevê diagnóstico |
| `calc_to_nic` | CALC → NIC | Score da calculadora indica intervenção |
| `nanda_to_safety` | NANDA → SAFETY | Diagnóstico relacionado a meta de segurança |

### 2.3 Evidence Links

| Edge Type | Direction | Description |
|-----------|-----------|-------------|
| `evidenced_by` | NANDA → Evidence | Diagnóstico suportado por evidência |
| `graded_by` | Evidence → GRADE | Nível de evidência GRADE |
| `published_in` | Evidence → Source | Fonte da evidência |

### 2.4 Cognitive Edges (v5.0)

| Edge Type | Direction | Description |
|-----------|-----------|-------------|
| `hypothesis_of` | HYP → NANDA | Hipótese sobre diagnóstico |
| `plan_step_of` | PLAN → Plan | Nó pertence a plano |
| `plan_transition` | PLAN → PLAN | Transição condicional entre nós |
| `similar_to` | EP → EP | Episódios similares (memória) |
| `learned_from` | Weight → EP | Peso aprendido de episódio |
| `voted_on` | Agent → HYP | Agente votou em hipótese |

### 2.5 Context Edges

| Edge Type | Direction | Description |
|-----------|-----------|-------------|
| `located_in` | Patient → Ward | Paciente em enfermaria |
| `part_of` | Ward → Hospital | Enfermaria pertence a hospital |
| `assigned_to` | Staff → Ward | Profissional alocado |
| `available_in` | Resource → Ward | Recurso disponível |
| `modifies` | Context → Decision | Contexto modifica decisão |
| `applies_to` | Protocol → Population | Protocolo aplicável a população |

## 3. Edge Properties

### 3.1 Mandatory Properties

| Property | Type | Description |
|----------|------|-------------|
| `edge_id` | UUID | Identificador único |
| `source_node_id` | VARCHAR(64) | Nó de origem |
| `target_node_id` | VARCHAR(64) | Nó de destino |
| `edge_type` | VARCHAR(64) | Tipo de relação |
| `weight` | NUMERIC | Peso da relação (0.0–1.0) |
| `confidence` | NUMERIC | Confiança na relação (0.0–1.0) |

### 3.2 Optional Properties

| Property | Type | Description |
|----------|------|-------------|
| `evidence_ref` | UUID → graded_evidence | Evidência que suporta a relação |
| `population_id` | UUID → populations | Restrito a população |
| `temporal_validity` | JSONB | {start: date, end: date} |
| `source` | VARCHAR | literature, expert, empirical, default |
| `grade_level` | CHAR(1) | GRADE A/B/C/D |
| `reversible` | BOOLEAN | Relação pode ser invertida por aprendizado |

## 4. Weight System

### 4.1 Weight Semantics

O peso de uma aresta representa a **força da relação clínica**:

```
weight(NANDA:00047 → NIC:3540) = 0.85
→ "Para 00047, NIC 3540 é fortemente recomendada (85%)"

weight(NANDA:00047 → NIC:2250) = 0.45
→ "Para 00047, NIC 2250 é moderadamente recomendada (45%)"
```

### 4.2 Weight Sources

| Source | Initial Weight | Adjustability |
|--------|---------------|---------------|
| Literature (GRADE A) | 0.80–0.95 | Low (strong evidence) |
| Literature (GRADE B) | 0.60–0.80 | Medium |
| Literature (GRADE C) | 0.40–0.60 | High |
| Expert consensus | 0.50–0.70 | High |
| Empirical (from memory) | calculated | Very high (learned) |
| Default | 0.50 | Very high |

### 4.3 Weight Updates

Pesos são atualizados pelo Learning Loop:

```
Initial: weight(00047 → 3540) = 0.85
Episode: 00047 treated with 3540 → NOC improved 2→4 (success)
Reinforcement signal: +0.08
Proposed new weight: 0.93 (capped at 0.95)
Human validation: approved
Applied: weight(00047 → 3540) = 0.93
```

## 5. Edge Direction Rules

### 5.1 Directed Edges

A maioria das arestas são dirigidas (têm sentido clínico):

```
NIC 3540 →treats→ NANDA 00047  ✓ (intervenção trata diagnóstico)
NANDA 00047 →treats→ NIC 3540  ✗ (não faz sentido clínico)
```

### 5.2 Bidirectional Edges

Algumas relações são bidirecionais:

| Edge Type | Bidirectional? | Rationale |
|-----------|---------------|-----------|
| `co_occurs` | Yes | A co-ocorre com B ↔ B co-ocorre com A |
| `similar_to` | Yes | Similaridade é simétrica |
| `maps_to` | Yes | Equivalência é simétrica |
| `contradicts` | Yes | Contradição é simétrica |

## 6. Edge Statistics (Current v4.2)

| Edge Type | Count | Source |
|-----------|-------|--------|
| nanda_to_nic | ~1,200 | NNN links |
| nanda_to_noc | ~800 | NNN links |
| nic_to_noc | ~600 | NNN links |
| calc_to_nanda | ~80 | Calculator mappings |
| calc_to_nic | ~40 | Calculator mappings |
| nanda_to_safety | ~30 | Safety cross |
| maps_to (SNOMED) | ~200 | SNOMED mapping |
| maps_to (LOINC) | ~100 | LOINC mapping |
| maps_to (ICNP) | ~150 | ICNP mapping |
| part_of (hierarchy) | ~3,000 | Taxonomy |
| evidenced_by | ~500 | Evidence links |

**Total: ~6,700 edges (v4.2) → projetado ~20,000+ (v5.0)**

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-500-01 | Node Types (what connects) |
| NIFS-500-04 | Weights (weight system detail) |
| NIFS-500-05 | Confidence (confidence scoring) |
| NIFS-500-06 | Evidence Links (evidence attachment) |
| NIFS-600-04 | Hypothesis Generation (uses edges for traversal) |
| NIFS-600-17 | Learning Loop (updates edge weights) |

## 8. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — complete edge type catalog | Leivis Melo |
