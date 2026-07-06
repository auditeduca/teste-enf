# NIFS-300-07: Inheritance

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-300-07                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como a herança conceitual funciona no modelo de conhecimento do NIS.

## 2. Inheritance Patterns

### 2.1 Taxonomic Inheritance (is-a)

```
NursingDiagnosis (abstract)
└── RiskDiagnosis (type=risk)
    └── NANDA 00047 "Risk of Impaired Skin Integrity"
└── ActualDiagnosis (type=actual)
    └── NANDA 00046 "Impaired Skin Integrity"
```

Um `RiskDiagnosis` herda propriedades de `NursingDiagnosis` mas adiciona `risk_factors` em vez de `defining_characteristics`.

### 2.2 Population Inheritance

```
Population: ICU
└── inherits priors from → Population: Adult Critical Care
    └── inherits priors from → Population: Adult

P(NANDA 00047 | ICU) inherits base P(NANDA 00047 | Adult) and adjusts
```

### 2.3 Protocol Inheritance

```
Protocol: ICU Sepsis Bundle
└── extends → Protocol: Sepsis Management (base)
    └── extends → Protocol: Infection Control (foundation)
```

## 3. NIS Implementation

Inheritance is implemented via:
- `ni_graph.edges` with `relation_type = 'part_of'` or `'is_a'`
- `ni_prob.prior_beliefs` with population hierarchy
- `ni_protocol.protocols` with version chains

## 4. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-300-08 | Composition |
| NIFS-300-09 | Aggregation |
| NIFS-500-01 | Node Types |
