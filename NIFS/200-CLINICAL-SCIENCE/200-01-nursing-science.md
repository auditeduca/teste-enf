# NIFS-200-01: Nursing Science

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-200-01                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Estabelecer a enfermagem como ciência e definir como o NIS a representa computacionalmente.

## 2. Nursing as Science

A enfermagem é uma ciência aplicada com:
- **Objeto de estudo**: cuidado humano na saúde e doença
- **Método**: processo de enfermagem (ADPIE)
- **Corpo de conhecimento**: taxonomias (NANDA-I, NIC, NOC), teorias, evidências
- **Produto**: cuidado seguro, eficaz e humanizado

## 3. Metaparadigm Concepts

O NIS modela os 4 conceitos do metaparadigma de enfermagem (`ni_cog.metaparadigm_concepts`):

| Concept | Definition | NIS Implementation |
|---------|-----------|-------------------|
| **Pessoa** | Ser humano holístico, biopsicossocial | `ni.cases` + `ni_world.patient_states` |
| **Ambiente** | Contexto físico, social, institucional | `ni_world.hospital_states` + `ni_world.ward_states` |
| **Saúde** | Estado de bem-estar, continuum | `ni_temporal.state_transitions` |
| **Enfermagem** | Ação profissional de cuidar | `ni_memory.actions` + `ni_planner.plans` |

## 4. Nursing Theories in NIS

| Theory Type | Examples | NIS Role |
|-------------|----------|----------|
| Grand theories | Orem, Roy, Henderson | Framework, não implementado diretamente |
| Middle-range theories | Kolcaba (Conforto), Pender (Promoção saúde) | `ni_cog.middle_range_theories` — linked to NANDA |
| Practice theories | Braden, Glasgow | Implemented as calculators |

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-200-02 | Nursing Process (ADPIE) |
| NIFS-200-05 | Clinical Reasoning |
| NIFS-300-05 | Clinical Ontology |
