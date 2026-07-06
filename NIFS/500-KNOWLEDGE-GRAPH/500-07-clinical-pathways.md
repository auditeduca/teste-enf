# NIFS-500-07: Clinical Pathways

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-500-07                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir clinical pathways como caminhos estruturados no grafo de conhecimento que representam trajetórias de cuidado recomendadas.

## 2. Pathway Structure

```
Clinical Pathway = sequência ordenada de nós no grafo

Calculator → NANDA → NIC → NOC → Reassessment
    ↓                              ↓
    └── Contingency branch ────────┘
```

## 3. Example: Braden Pathway

```
TOOL.BRADEN (score=12)
    ↓ edge: activates (weight=0.87)
NANDA:00047 (Risk of Impaired Skin Integrity)
    ↓ edge: treated_by (weight=0.85, strength=strong)
NIC:3540 (Pressure Management)
    ↓ edge: improves (weight=0.70, strength=moderate)
NOC:1101 (Tissue Integrity)
    ↓ edge: assessed_by (weight=0.90)
TOOL.BRADEN (reassessment at 24h)
    ↓
If NOC improved → continue path
If NOC unchanged → branch to NIC:2250 (Wound Care)
If NOC deteriorated → branch to escalation protocol
```

## 4. NIS Implementation

| Component | Table | Role |
|-----------|-------|------|
| Pathway definition | `ni_planner.plans` | Container do pathway |
| Pathway nodes | `ni_planner.plan_nodes` | Passos do caminho |
| Pathway branches | `ni_planner.plan_edges` | Transições condicionais |
| Graph traversal | `ni_graph.edges` | Arestas que formam o caminho |
| Protocol steps | `ni_protocol.protocol_steps` | Passos institucionais |

## 5. Pathway Types

| Type | Description | Example |
|------|-------------|---------|
| Standard | Sequência linear recomendada | Braden → NANDA → NIC → NOC |
| Contingency | Ramificações baseadas em condição | If not improving → alternative NIC |
| Escalation | Subir nível de cuidado | If deteriorating → activate protocol C |
| Preventive | Pathway proativo | High risk → preventive interventions |
| Recovery | Pathway de recuperação | Post-crisis → step-down plan |

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-11 | Goal Planning (pathway = plan with branches) |
| NIFS-300-20 | Protocols (institutional pathways) |
| NIFS-500-11 | Reasoning Graph (traversal) |
