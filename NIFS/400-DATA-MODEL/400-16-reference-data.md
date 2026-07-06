# NIFS-400-16: Reference Data

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-400-16                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir dados de referência — tabelas com valores pré-populados que servem como catálogos.

## 2. Reference Data Categories

| Category | Tables | Records | Source |
|----------|--------|---------|--------|
| Terminologies | nanda_diagnoses, nic_interventions, noc_outcomes | 244 + 575 + 550 | NANDA-I, NIC, NOC |
| Safety | safety_goals, nine_rights_medication | 6 + 9 | WHO IPSG |
| Populations | populations | 6+ | NIS defined |
| CID | cid_diagnoses, cid_nanda_map | varies | WHO ICD |
| UCUM units | ucum_units | ~50 | UCUM standard |
| Lab references | lab_reference_values | 300 | NKOS 2026 |
| Jurisdictions | jurisdictions | 28 (BR states) | NKOS 2026 |
| Legislation domains | legislation_domains | 4 | NKOS 2026 |
| Compulsory notifications | compulsory_notifications | 54 | NKOS 2026 |
| Channels | channels | 10 | NKOS 2026 |
| Audiences | audiences | 5 | NKOS 2026 |

## 3. Reference vs Transactional

| Aspect | Reference Data | Transactional Data |
|--------|---------------|-------------------|
| Volatility | Low (changes with terminology editions) | High (every session) |
| Volume | Fixed catalog (hundreds to thousands) | Grows continuously |
| Source | Standards bodies, curated | Runtime (users, agents) |
| Examples | NANDA codes, safety goals | reasoning sessions, memory episodes |

## 4. Seeding Strategy

Reference data é carregada via:
1. NKOS JSON files (canonical source)
2. Generator scripts que produzem SQL INSERTs
3. Versioned via `ni.terminology_versions`

## 5. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-400-15 | Code Systems |
| NIFS-400-17 | Master Data |
