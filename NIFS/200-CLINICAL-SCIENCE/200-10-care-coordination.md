# NIFS-200-10: Care Coordination

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-200-10                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir coordenação do cuidado como parte do escopo clínico do NIS.

## 2. Definition

Coordenação do cuidado é a **organização deliberada de atividades entre profissionais** para garantir cuidado contínuo, seguro e eficaz.

## 3. NIS Coordination Features

| Feature | Implementation |
|---------|---------------|
| Handoff estruturado | `ni_temporal.clinical_events` + FHIR Encounter |
| Multi-professional | `ni_council.agents` (specialist agents) |
| Continuity of care | `ni_memory.episodes` (longitudinal) |
| Transfer tracking | `ni_temporal.state_transitions` |
| Discharge planning | `ni_planner.plans` (discharge type) |
| Follow-up scheduling | `ni_platform` scheduler |

## 4. Care Transitions

| Transition | NIS Action |
|------------|-----------|
| Admission → Ward | Initial assessment + baseline |
| Ward → ICU | Escalation protocol + acuity recalc |
| ICU → Ward | De-escalation + adjusted plan |
| Hospital → Home | Discharge plan + education content |
| Home → Readmission | Memory retrieval of prior episode |

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-600-01 | Clinical Workflow |
| NIFS-800-01 | FHIR (care coordination via Encounter) |
