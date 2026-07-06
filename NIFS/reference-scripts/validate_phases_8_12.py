"""Referential integrity validator for NKOS Phases 8-12.

Checks, per entity:
  - JSON validity + envelope count == len(records)
  - Primary-key presence and uniqueness
  - Cross-entity foreign-key resolution against source datasets
  - Light enum / range constraints from the plan validators
Writes a report to datasets/metadata/validation_phases_8_12_report.json and
exits non-zero when any error is found.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from dataset_io import read_envelope

ROOT = Path(__file__).resolve().parent.parent / "datasets"
NOW_ISO = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load(rel: str) -> dict:
    return read_envelope(rel)


def pk_set(rel: str, field: str) -> set[str]:
    try:
        return {r[field] for r in load(rel)["records"] if r.get(field)}
    except FileNotFoundError:
        return set()


# entity -> (file, primary_key)
PHASE_FILES = {
    "Workflow": ("ai/workflows.json", "workflow_code"),
    "AIJob": ("ai/ai_jobs.json", "job_id"),
    "AIExecutionLog": ("ai/ai_execution_logs.json", "log_id"),
    "RAGChunk": ("ai/rag_chunks.json", "rag_chunk_code"),
    "KnowledgeNode": ("ai/knowledge_nodes.json", "knowledge_node_code"),
    "Explanation": ("ai/explanations.json", "explanation_id"),
    "RecommendationFeedback": ("ai/recommendation_feedback.json", "feedback_id"),
    "Channel": ("publishing/channels.json", "channel_code"),
    "Publication": ("publishing/publications.json", "publication_id"),
    "ComponentInstance": ("publishing/component_instances.json", "instance_id"),
    "PatientProfile": ("operations/patient_profiles.json", "patient_profile_code"),
    "NursingCarePlan": ("operations/nursing_care_plans.json", "care_plan_code"),
    "CalculatorSession": ("operations/calculator_sessions.json", "session_id"),
    "DualCheckSession": ("operations/dual_check_sessions.json", "session_id"),
    "SBARMessage": ("operations/sbar_messages.json", "message_id"),
    "ReassessmentRule": ("operations/reassessment_rules.json", "reassessment_rule_code"),
    "NursingIndicator": ("operations/nursing_indicators.json", "nursing_indicator_code"),
    "AssessmentResult": ("operations/assessment_results.json", "result_id"),
    "AnalyticsEvent": ("analytics/analytics_events.json", "event_id"),
    "AnalyticsAggregate": ("analytics/analytics_aggregates.json", "aggregate_id"),
    "SearchDocument": ("analytics/search_documents.json", "search_document_code"),
    "SearchQueryLog": ("analytics/search_query_logs.json", "query_id"),
    "WorkflowMetric": ("analytics/workflow_metrics.json", "metric_id"),
    "SystemEvent": ("analytics/system_events.json", "event_id"),
    "CarbonMetric": ("analytics/carbon_metrics.json", "metric_id"),
    "AuditLog": ("analytics/audit_logs.json", "audit_id"),
    "SecurityAuditLog": ("analytics/security_audit_logs.json", "security_event_id"),
    "ComplianceEvidence": ("analytics/compliance_evidence.json", "evidence_id"),
    "AnonymizationJob": ("analytics/anonymization_jobs.json", "job_id"),
    "DataAnonymizationRule": ("analytics/data_anonymization_rules.json", "anonymization_rule_code"),
    "ForumTopic": ("community/forum_topics.json", "forum_topic_code"),
    "ForumPost": ("community/forum_posts.json", "forum_post_code"),
    "JobListing": ("community/job_listings.json", "job_listing_code"),
    "CourseListing": ("community/course_listings.json", "course_listing_code"),
    "CareerPath": ("community/career_paths.json", "career_path_code"),
    "FederatedModelManifest": ("community/federated_model_manifests.json", "federated_model_code"),
    "FederatedUpdate": ("community/federated_updates.json", "update_id"),
    "CachePolicy": ("community/cache_policies.json", "cache_policy_code"),
    "FhirEndpointConfiguration": ("community/fhir_endpoint_configurations.json", "fhir_endpoint_code"),
    "WebhookSubscription": ("community/webhook_subscriptions.json", "subscription_id"),
    "FeatureFlag": ("community/feature_flags.json", "feature_flag_code"),
}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.checks = 0

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def ok(self) -> None:
        self.checks += 1


def validate_envelopes_and_pks(rep: Report) -> dict[str, list[dict]]:
    records_by_entity: dict[str, list[dict]] = {}
    for entity, (rel, pk) in PHASE_FILES.items():
        try:
            data = load(rel)
        except FileNotFoundError:
            rep.err(f"{entity}: arquivo ausente ({rel})")
            continue
        except json.JSONDecodeError as e:
            rep.err(f"{entity}: JSON inválido ({rel}): {e}")
            continue
        recs = data.get("records", [])
        records_by_entity[entity] = recs
        if data.get("count") != len(recs):
            rep.err(f"{entity}: envelope count={data.get('count')} difere de len(records)={len(recs)}")
        else:
            rep.ok()
        seen: set[str] = set()
        for i, r in enumerate(recs):
            key = r.get(pk)
            if key is None:
                rep.err(f"{entity}: registro #{i} sem PK '{pk}'")
                continue
            if key in seen:
                rep.err(f"{entity}: PK duplicada '{key}'")
            seen.add(key)
        rep.ok()
    return records_by_entity


def validate_fks(rep: Report, rbe: dict[str, list[dict]]) -> None:
    content_codes = pk_set("content/nkos/contents.json", "content_code")
    fragment_codes = pk_set("content/nkos/content_fragments.json", "fragment_code")
    tool_codes = pk_set("clinical/clinical_tools_catalog.json", "tool_code")
    diagnosis_codes = pk_set("clinical/nursing_diagnoses.json", "diagnosis_code")
    guideline_codes = pk_set("clinical/clinical_guidelines.json", "guideline_code")
    linkage_codes = pk_set("clinical/nnn_linkages.json", "linkage_code")

    def check_fk(entity: str, field: str, valid: set[str], *, node_filter=None) -> None:
        missing = 0
        for r in rbe.get(entity, []):
            if node_filter and not node_filter(r):
                continue
            val = r.get(field)
            if val and val not in valid:
                missing += 1
                if missing <= 3:
                    rep.err(f"{entity}.{field}='{val}' não resolve em entidade-fonte")
        if missing == 0:
            rep.ok()
        elif missing > 3:
            rep.err(f"{entity}.{field}: +{missing - 3} referências quebradas adicionais")

    check_fk("RAGChunk", "content_code", content_codes)
    check_fk("RAGChunk", "fragment_code", fragment_codes)
    check_fk("KnowledgeNode", "source_code", diagnosis_codes,
             node_filter=lambda r: r.get("node_type") == "nursing_diagnosis")
    check_fk("KnowledgeNode", "source_code", tool_codes,
             node_filter=lambda r: r.get("node_type") == "clinical_tool")
    check_fk("KnowledgeNode", "source_code", guideline_codes,
             node_filter=lambda r: r.get("node_type") == "guideline")
    check_fk("NursingCarePlan", "diagnosis_code", diagnosis_codes)
    check_fk("NursingCarePlan", "linkage_code", linkage_codes)
    check_fk("ReassessmentRule", "tool_code", tool_codes)
    check_fk("SearchDocument", "source_code", content_codes,
             node_filter=lambda r: r.get("source_entity") == "Content")
    check_fk("SearchDocument", "source_code", tool_codes,
             node_filter=lambda r: r.get("source_entity") == "ClinicalTool")

    topic_codes = {r["forum_topic_code"] for r in rbe.get("ForumTopic", []) if r.get("forum_topic_code")}
    check_fk("ForumPost", "forum_topic_code", topic_codes)

    for entity in ("ForumTopic", "CareerPath"):
        bad = 0
        for r in rbe.get(entity, []):
            for tc in r.get("linked_tool_codes") or []:
                if tc not in tool_codes:
                    bad += 1
                    if bad <= 3:
                        rep.err(f"{entity}.linked_tool_codes='{tc}' não resolve em ClinicalTool")
        if bad == 0:
            rep.ok()


def validate_constraints(rep: Report, rbe: dict[str, list[dict]]) -> None:
    for r in rbe.get("FeatureFlag", []):
        pct = r.get("rollout_percentage")
        if not isinstance(pct, int) or not (0 <= pct <= 100):
            rep.err(f"FeatureFlag {r.get('feature_flag_code')}: rollout_percentage fora de 0-100 ({pct})")
    rep.ok()
    for r in rbe.get("RAGChunk", []):
        tok = r.get("token_estimate", 0)
        if tok > 512:
            rep.err(f"RAGChunk {r.get('rag_chunk_code')}: token_estimate>{512} ({tok})")
    rep.ok()
    for r in rbe.get("FederatedModelManifest", []):
        if r.get("privacy_epsilon") is None or r.get("privacy_delta") is None:
            rep.err(f"FederatedModelManifest {r.get('federated_model_code')}: parâmetros de privacidade ausentes")
    rep.ok()
    valid_dim = {768}
    for entity in ("RAGChunk", "KnowledgeNode"):
        for r in rbe.get(entity, []):
            if r.get("embedding_dim") not in valid_dim:
                rep.err(f"{entity} {r.get('uuid')}: embedding_dim inconsistente ({r.get('embedding_dim')})")
    rep.ok()


def validate_registry(rep: Report, rbe: dict[str, list[dict]]) -> None:
    registry = load("metadata/canonical_registry.json")
    reg_map = {e["entity"]: e for e in registry["entities"]}
    for entity, recs in rbe.items():
        reg = reg_map.get(entity)
        if not reg:
            rep.err(f"{entity}: ausente em canonical_registry.json")
            continue
        if reg.get("records") != len(recs):
            rep.err(f"{entity}: registry records={reg.get('records')} difere do arquivo={len(recs)}")
        else:
            rep.ok()


def main() -> int:
    rep = Report()
    rbe = validate_envelopes_and_pks(rep)
    validate_fks(rep, rbe)
    validate_constraints(rep, rbe)
    validate_registry(rep, rbe)

    report = {
        "validated_at": NOW_ISO,
        "scope": "NKOS Phases 8-12",
        "entities_checked": len(rbe),
        "checks_passed": rep.checks,
        "error_count": len(rep.errors),
        "warning_count": len(rep.warnings),
        "errors": rep.errors,
        "warnings": rep.warnings,
        "passed": not rep.errors,
    }
    out = ROOT / "metadata" / "validation_phases_8_12_report.json"
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("NKOS Phases 8-12 — referential integrity")
    print(f"  Entities checked: {len(rbe)}/{len(PHASE_FILES)}")
    print(f"  Checks passed:    {rep.checks}")
    print(f"  Errors:           {len(rep.errors)}")
    print(f"  Warnings:         {len(rep.warnings)}")
    for e in rep.errors[:20]:
        print(f"    ERROR: {e}")
    print(f"  Report: {out}")
    print(f"  Result: {'PASS' if report['passed'] else 'FAIL'}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
