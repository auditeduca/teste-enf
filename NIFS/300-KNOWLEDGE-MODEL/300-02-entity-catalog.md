# NIFS-300-02: Entity Catalog

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-300-02                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Catalogar todas as entidades do universo NIS com suas propriedades, schemas e relações.

## 2. Entity Classification

| Category | Entities | NIS Schemas |
|----------|----------|-------------|
| **Terminology** | NANDA, NIC, NOC, CID, ISO Terms | `ni`, `ni_iso` |
| **Clinical Process** | Cases, Care Plans, Assessments, Outcomes | `ni`, `ni_temporal` |
| **Cognitive** | Reasoning Sessions, Hypotheses, Traces | `ni_reasoning`, `ni_memory` |
| **Graph** | Nodes, Edges, Edge Types | `ni_graph` |
| **Safety** | Safety Goals, 9 Rights, Medications | `ni` |
| **Protocols** | Protocols, Steps, Rules, Versions | `ni_protocol` |
| **Rules** | Decision Rules, Conditions, Actions, Weights | `ni_rules` |
| **Evidence** | Sources, Raw Sources, Extracted Entities, GRADE | `ni_mining` |
| **Council** | Sessions, Votes, Vetoes, Decisions, Agents | `ni_council` |
| **Explanation** | Explanations, Reasons, Traces | `ni_explain` |
| **Learning** | Feedback, Adjustments, Reinforcement | `ni_learning` |
| **Temporal** | Events, Time Series, State Transitions | `ni_temporal` |
| **Twin** | Patient States, Trajectories, Simulations | `ni_twin` |
| **Probabilistic** | Probability Models, Bayesian Links, Priors | `ni_prob` |
| **World** | Patient/Hospital/Ward/Resource/Staff States | `ni_world` |
| **Attention** | Attention Signals, Weights | `ni_attention` |
| **Planner** | Plans, Plan Nodes, Plan Edges | `ni_planner` |
| **Content** | Items, Metadata, Taxonomy | `ni_content` |
| **I18n** | Locales, Translations, Cultural Adaptations | `ni_i18n` |
| **Design** | Components, Variants | `ni_design` |
| **AI** | Embeddings, Named Entities, Annotations | `ni_ai` |
| **Interop** | Profiles, Mappings, Sync History | `ni_interop` |
| **Pharma** | Drug References, Dictionary, Monographs | `ni_pharm` (novo) |
| **Legislation** | Jurisdictions, Instruments, Provisions, Notifications | `ni_legis` (novo) |
| **User** | Profiles, Paths, Questionnaires, Consents | `ni_user` (novo) |

## 3. Canonical Registry Mapping

O `canonical_registry.json` do NKOS 2026 lista 50+ entidades com PK, FK e contagem de registros. Este catálogo é o NIFS equivalente — a visão de engenharia.

## 4. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-300-01 | Universe Model (parent) |
| NIFS-300-03 | Relationship Catalog (FK map) |
| NIFS-400-03 | Tables (physical implementation) |
