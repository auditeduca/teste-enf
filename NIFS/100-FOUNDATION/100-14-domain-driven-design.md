# NIFS-100-14: Domain-Driven Design

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-100-14                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o NIS aplica Domain-Driven Design (DDD) — modelando o domínio de enfermagem como software.

## 2. Bounded Contexts

| Context | Responsibility | Schemas |
|---------|---------------|---------|
| Clinical Knowledge | Taxonomias, ontologia | `ni`, `ni_cog`, `ni_iso`, `ni_onto` |
| Reasoning | Raciocínio, inferência | `ni_reasoning`, `ni_prob` |
| Memory | Memória episódica | `ni_memory` |
| Planning | Planejamento, planos | `ni_planner`, `ni_protocol` |
| Council | Multi-agente, consenso | `ni_council` |
| Learning | Aprendizado, feedback | `ni_learning` |
| Attention | Atenção clínica | `ni_attention` |
| World | Contexto, world model | `ni_world` |
| Twin | Digital twin, simulação | `ni_twin` |
| Evidence | Mineração, evidência | `ni_mining`, `ni_epist` |
| Temporal | Eventos temporais | `ni_temporal` |
| Graph | Grafo de conhecimento | `ni_graph` |
| Interop | Interoperabilidade | `ni_interop` |
| Content | Gestão de conteúdo | `ni_content`, `ni_i18n`, `ni_design` |
| Platform | Infraestrutura, plugins | `ni_platform`, `ni_cache`, `ni_ops` |
| Quality | Quality gates, testes | `ni_qg`, `ni_test` |

## 3. Ubiquitous Language

O NIS mantém um vocabulário consistente entre spec, código e clínica:

| Term | Clinical Meaning | Code Entity |
|------|-----------------|-------------|
| Diagnóstico | NANDA-I diagnosis | `nanda_diagnoses` |
| Intervenção | NIC intervention | `nic_interventions` |
| Desfecho | NOC outcome | `noc_outcomes` |
| Hipótese | Candidate diagnosis | `reasoning.hypotheses` |
| Evidência | Scientific support | `mining.graded_evidence` |
| Episódio | Clinical case memory | `memory.episodes` |
| Conselho | Multi-agent decision | `council.sessions` |
| Atenção | Priority filtering | `attention.signals` |

## 4. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-100-13 | Modularity |
| NIFS-100-15 | Data-Driven Design |
| NIFS-300-01 | Universe Model |
