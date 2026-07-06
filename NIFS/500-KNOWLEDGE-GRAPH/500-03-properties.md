# NIFS-500-03: Properties

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-500-03                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir as propriedades (atributos) que nós e arestas do grafo de conhecimento clínico podem carregar.

## 2. Node Properties

| Property | Type | Applies To | Description |
|----------|------|-----------|-------------|
| `node_label` | VARCHAR(256) | All | Rótulo legível |
| `node_type` | VARCHAR(32) | All | NANDA, NIC, NOC, calculator, etc. |
| `code` | VARCHAR(32) | Terminology nodes | Código canônico |
| `snomed_ct` | VARCHAR(32) | Clinical nodes | Cross-map SNOMED CT |
| `definition` | TEXT | Concept nodes | Definição clínica |
| `domain` | VARCHAR(32) | NANDA/NIC/NOC | Domínio taxonômico |
| `population_ids` | UUID[] | All | Populações onde aplica |
| `status` | VARCHAR(16) | All | active, superseded, deprecated |
| `version` | VARCHAR(16) | All | SemVer da entidade |

## 3. Edge Properties

| Property | Type | Description |
|----------|------|-------------|
| `weight` | NUMERIC(0,1) | Força da relação (0=irrelevante, 1=certeza) |
| `edge_type` | VARCHAR(64) | activates, treats, assesses, implies, contradicts... |
| `evidence_grade` | CHAR(1) | A, B, C, D (GRADE) |
| `population_id` | UUID | População específica (null = todas) |
| `rule_id` | UUID | Regra que originou a aresta (nullable) |
| `confidence` | NUMERIC(0,1) | Confiança bayesiana (nullable) |
| `temporal_validity` | JSONB | Janela temporal de validade (nullable) |
| `source` | VARCHAR(32) | nnn_linkage, expert, mined, computed |

## 4. JSONB Extension Properties

Nós e arestas suportam propriedades extensíveis via JSONB:

```json
// Node extension
{
  "apgar_context": {"timing": "1min", "score_range": "0-3"},
  "clinical_setting": ["ICU", "NICU"],
  "priority_boost": 0.15
}

// Edge extension
{
  "conditions": {"braden_score": {"op": "<=", "value": 12}},
  "action": "activate_protocol",
  "fallback_edge_id": "uuid-here"
}
```

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-500-01 | Node Types |
| NIFS-500-02 | Edge Types |
| NIFS-500-04 | Weights |
