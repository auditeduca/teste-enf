# NIFS-800-09: Import

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-800-09                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o NIS importa dados de fontes externas — NKOS datasets, EHRs, ANVISA, PubMed.

## 2. Import Sources

| Source | Format | Method | Frequency |
|--------|--------|--------|-----------|
| NKOS datasets | JSON | Batch import pipeline | On release |
| ANVISA | JSON/CSV | `anvisa_open_data_agents/` | Monthly (CI) |
| PubMed | XML/JSON | PubMed API | Weekly |
| EHR (FHIR) | FHIR/JSON | SMART on FHIR | Real-time |
| EHR (HL7) | HL7 v2 | MLLP listener | Real-time |
| Excel (legacy) | XLSX | `datasets/` migration tool | One-time |
| Cochrane | JSON | Manual + automated | Quarterly |

## 3. Import Pipeline

```
Source data
    ↓
1. Fetch (API, file, message)
    ↓
2. Validate (schema check, code validation)
    ↓
3. Transform (map to NIS schema)
    ↓
4. Deduplicate (match existing records)
    ↓
5. Load (insert/update ni_* tables)
    ↓
6. Index (update graph + vector store)
    ↓
7. Audit (log to ni_interop.import_logs)
```

## 4. NKOS Import

O CALENF-NKD já tem scripts de importação:
- `scripts/anvisa_open_data_agents/` — agentes ANVISA (discover, extract, validate)
- `scripts/ai_factory_agents/` — AI factory com catalog e batch runner
- `scripts/generators/` — geradores que produzem datasets a partir de fontes

## 5. NIS Implementation

| Table | Role |
|-------|------|
| `ni_interop.import_logs` | Import audit trail |
| `ni_interop.import_sources` | Source registry |
| `ni_interop.import_errors` | Import failures |

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-800-10 | Export (reverse direction) |
| NIFS-800-14 | Synchronization |
| NIFS-1100-03 | Knowledge Curation (governance) |
