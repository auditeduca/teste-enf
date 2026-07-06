# NIFS-800-10: Export

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-800-10                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o NIS exporta dados para sistemas externos — relatórios, FHIR resources, datasets.

## 2. Export Formats

| Format | Use Case | Method |
|--------|----------|--------|
| FHIR Bundle | EHR integration | REST API (NIFS-800-01) |
| JSON | NKOS dataset regeneration | Batch export |
| CSV/Excel | Analytics, reporting | Query export |
| HL7 v2 | Legacy EHR | Message generation |
| Neo4j Cypher | Graph database import | Graph export script |
| OpenAPI | API documentation | Schema generation |

## 3. Export Pipeline

```
Export request (entity, format, filters)
    ↓
1. Query NIS database (ni_* tables)
    ↓
2. Transform to target format
    ↓
3. Validate output (schema compliance)
    ↓
4. Package (file, stream, API response)
    ↓
5. Deliver (download, API push, webhook)
    ↓
6. Audit (log to ni_interop.export_logs)
```

## 4. FHIR Resource Export

NIS entities → FHIR resources:

| NIS Entity | FHIR Resource |
|-----------|---------------|
| `ni_clinical.observations` | Observation |
| `ni_clinical.diagnoses` | Condition |
| `ni_planner.plans` | CarePlan |
| `ni_pharm.administrations` | MedicationAdministration |
| `ni_user.patients` | Patient |

## 5. NKOS Dataset Export

O NIS pode regenerar os datasets NKOS a partir do banco:
```
ni_graph.nodes → datasets/clinical/nursing_diagnoses.json
ni_graph.edges → datasets/master/entity_relations.json
ni_clinical.* → datasets/clinical/*.json
ni_ref.* → datasets/master/*.json
```

Isto fecha o ciclo: NIFS (spec) → DDL (schema) → Data (loaded) → NKOS (export) → Website (generated).

## 6. NIS Implementation

| Table | Role |
|-------|------|
| `ni_interop.export_logs` | Export audit |
| `ni_interop.export_templates` | Export format templates |

## 7. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-800-09 | Import (reverse direction) |
| NIFS-800-01 | FHIR (export format) |
| NIFS-800-13 | Bulk Data (large exports) |
