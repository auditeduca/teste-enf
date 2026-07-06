# NIFS-800-13: Bulk Data

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-800-13                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o NIS exporta grandes volumes de dados (bulk data) para analytics, research e backup.

## 2. Bulk Export Formats

| Format | Use Case | Size |
|--------|----------|------|
| FHIR Bulk ($export) | Research, population health | GB-TB |
| NDJSON | Streaming analytics | MB-GB |
| Parquet | Data warehouse | GB |
| CSV | Excel/analytics | MB |
| SQL Dump | Backup/migration | GB |

## 3. FHIR Bulk Data Export

```
POST /fhir/$export?_type=Condition,Observation
    ↓
202 Accepted + Content-Location header
    ↓
Async processing (batch export)
    ↓
GET /fhir/$export-status/{job_id}
    ↓
200 Complete → download URLs (signed)
```

## 4. NIS Bulk Data

| Dataset | Records | Export Size (est.) |
|---------|---------|-------------------|
| NANDA diagnoses | 244 | ~500KB |
| NIC interventions | 575 | ~1MB |
| NOC outcomes | 550 | ~800KB |
| NNN linkages | 1500 | ~2MB |
| Clinical concepts | 2000 | ~3MB |
| Calculator definitions | 100 | ~200KB |
| Master-data (all) | 52K+ | ~60MB |
| Full NKOS dataset | ~52K | ~60MB |

## 5. NIS Implementation

| Table | Role |
|-------|------|
| `ni_interop.bulk_jobs` | Export job tracking |
| `ni_interop.bulk_artifacts` | Generated files |

## 6. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-800-10 | Export (general) |
| NIFS-800-01 | FHIR (FHIR bulk format) |
| NIFS-1400-04 | Backup Strategy |
