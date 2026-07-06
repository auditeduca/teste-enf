# NIFS-1100-01: Knowledge Governance

| Field         | Value                              |
|---------------|------------------------------------|
| Document ID   | NIFS-1100-01                        |
| Status        | Draft                              |
| Version       | 1.0.0                              |
| Owner         | Leivis Melo                        |
| Reviewers     | —                                  |
| Last Updated  | 2026-07-05                         |

## 1. Purpose

Definir como o conhecimento clínico do NIS é governado — quem altera, quem aprova, quem revisa, quem publica, e como cada mudança é rastreada.

## 2. The Governance Problem

Conhecimento clínico não é estático. NANDA atualiza a cada 3 anos. NIC e NOC também. Novas evidências surgem diariamente. Protocolos mudam. Medicações são reclassificadas.

Sem governança, o conhecimento degrada. Com governança, cada mudança é:
- **Proposta** por alguém identificado
- **Revisada** por especialistas
- **Aprovada** por autoridade clínica
- **Versionada** com histórico
- **Publicada** com data efetiva
- **Auditável** permanentemente

## 3. Governance Roles

| Role | Who | Responsibility |
|------|-----|----------------|
| **Knowledge Proposer** | Enfermeiro clínico, pesquisador | Propõe nova entidade ou mudança |
| **Knowledge Reviewer** | Especialista de domínio | Revisa proposta tecnicamente |
| **Clinical approver** | Liderança clínica | Aprova mudança clinicamente |
| **Technical Approver** | Arquiteto do NIS | Aprova mudança tecnicamente |
| **Knowledge Publisher** | Release manager | Publica versão aprovada |
| **Audit Reader** | Auditor/regulador | Consulta histórico |

## 4. Change Workflow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ PROPOSE  │────→│ REVIEW   │────→│ APPROVE  │────→│ PUBLISH  │
│          │     │          │     │          │     │          │
│ Proposer │     │ Reviewer │     │ Approver │     │ Publisher│
│ creates  │     │ validates│     │ signs    │     │ releases │
│ draft    │     │ content  │     │ off      │     │ version  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                       │                │
                       ↓                ↓
                  ┌──────────┐    ┌──────────┐
                  │ REJECT   │    │ REJECT   │
                  │ return   │    │ return   │
                  │ to       │    │ to       │
                  │ proposer │    │ reviewer │
                  └──────────┘    └──────────┘
```

### 4.1 Change Types

| Type | Code | Examples | Approval Required |
|------|------|----------|-------------------|
| `add` | ADD | Novo NANDA, nova calculadora | Clinical + Technical |
| `modify` | MOD | Mudar peso de edge, atualizar label | Clinical |
| `deprecate` | DEP | Descontinuar intervenção obsoleta | Clinical + Technical |
| `realign` | RAL | Realinhar mapeamento SNOMED | Technical |
| `merge` | MRG | Fundir dois conceitos duplicados | Clinical + Technical |
| `split` | SPL | Dividir conceito em dois | Clinical + Technical |

### 4.2 Change Request Format

```json
{
  "change_request_id": "uuid",
  "proposer": "nurse_lic_12345",
  "change_type": "modify",
  "target_entity": "ni_graph.edges",
  "target_id": "edge_uuid",
  "changes": {
    "weight": {"old": 0.65, "new": 0.82, "reason": "GRADE A evidence from Cochrane 2025"},
    "evidence_ref": {"new": "grade_id_new"}
  },
  "justification": "Novo estudo Cochrane 2025 demonstra 82% efetividade de NIC 3540 para 00047 em UTI",
  "evidence_refs": ["grade_id_1", "grade_id_2"],
  "status": "pending_review"
}
```

## 5. Versioning Strategy

### 5.1 Semantic Versioning for Knowledge

```
NIFS Knowledge v5.2.1

MAJOR (5): Schema changes (new tables, breaking changes)
MINOR (2): New entities, new edges, new evidence
PATCH (1): Weight adjustments, label corrections, typo fixes
```

### 5.2 Entity-Level Versioning

Cada entidade versionável tem:

| Field | Type | Description |
|-------|------|-------------|
| `version` | VARCHAR(16) | e.g., "2024.1" |
| `status` | VARCHAR(16) | draft, review, active, deprecated |
| `effective_from` | DATE | Data de vigência |
| `effective_to` | DATE | Data de obsolescência (nullable) |
| `superseded_by` | VARCHAR(64) | ID da versão substituta |

### 5.3 Knowledge Changelog

```json
{
  "version": "5.2.1",
  "date": "2026-07-05",
  "changes": [
    {
      "change_id": "uuid",
      "type": "modify",
      "entity": "edge:NANDA:00047→NIC:3540",
      "description": "Weight updated 0.65→0.82 based on Cochrane 2025",
      "approved_by": "clinical_board",
      "approved_at": "2026-07-01"
    }
  ]
}
```

## 6. Deprecation Policy

Quando uma entidade se torna obsoleta:

```
1. Flag: status = 'deprecated'
2. Set: effective_to = deprecation_date
3. Set: superseded_by = replacement_id (if any)
4. Keep: in database (never delete — audit trail)
5. Alert: all consumers that reference deprecated entity
6. Migrate: consumers to replacement (if any)
7. Log: in knowledge changelog
```

**Conhecimento nunca é deletado. É deprecado.**

## 7. Approval Matrix

| Change | Clinical Reviewer | Clinical Approver | Technical Approver |
|--------|-------------------|-------------------|-------------------|
| New NANDA mapping | ✅ Nursing specialist | ✅ Clinical board | ✅ Architect |
| Edge weight adjustment | ✅ Domain expert | ✅ Clinical lead | — |
| New evidence link | ✅ Evidence specialist | — | ✅ Knowledge engineer |
| Schema change | — | ✅ Clinical board | ✅ Architect |
| Protocol update | ✅ Protocol owner | ✅ Clinical board | — |
| Medication update | ✅ Pharmacist | ✅ Clinical board | — |
| Prior update | ✅ Statistician | ✅ Clinical lead | — |

## 8. Audit Trail

Toda mudança de conhecimento é auditável:

```sql
SELECT 
  v.version_id, v.entity_type, v.entity_id,
  v.change_type, v.changeset_summary,
  v.proposed_by, v.reviewed_by, v.approved_by,
  v.effective_from, v.effective_to
FROM ni_knowledge.versions v
WHERE v.entity_id = 'NANDA:00047'
ORDER BY v.effective_from DESC;
```

## 9. Related Documents

| Document | Relationship |
|----------|-------------|
| NIFS-000-14 | Versioning (global strategy) |
| NIFS-1100-02 | Clinical Governance (clinical oversight) |
| NIFS-1100-05 | Approval Workflow (process detail) |
| NIFS-1100-09 | Deprecation (process detail) |
| NIFS-1000-06 | Audit (compliance) |

## 10. Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | Initial draft — full governance workflow | Leivis Melo |
