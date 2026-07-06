"""Inventário unificado de pendências — orienta todos os agentes."""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent

NOW = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(rel: str) -> dict:
    p = ROOT / rel.replace("/", "\\") if "\\" in str(ROOT) else ROOT / rel
    if not p.is_file():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        obj, _ = json.JSONDecoder().raw_decode(p.read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else {}


def collect() -> dict[str, Any]:
    """Retorna pendências reais + plano de ação sugerido para agentes."""
    # Content pending items
    cp = _load("datasets/master-data/content-pending/pending_items.json")
    cp_items = cp.get("items", [])
    cp_by_status = dict(Counter(i.get("status") for i in cp_items))
    cp_pending = [i for i in cp_items if i.get("status") not in ("applied", "published")]

    # Workflows
    wf_idx = _load("datasets/master-data/content-pending/workflow/index.json")
    wf_by_status = dict(Counter(w.get("status") for w in wf_idx.get("workflows", [])))
    wf_retry = [
        w for w in wf_idx.get("workflows", [])
        if w.get("status") in ("failed", "draft", "awaiting_approval")
    ]

    # Medication dictionary
    drugs = _load("datasets/clinical/drug_references.json").get("records", [])
    med = _load("datasets/clinical/medication_dictionary.json")
    med_refs = {
        r.get("drug_ref_code") or r.get("parent_entity_code")
        for r in med.get("records", [])
    } - {""}
    med_pending = max(len(drugs) - len(med_refs), 0)

    # Library assets
    lib = _load("datasets/content/library/library_visual_assets.json")
    lib_records = lib.get("records", [])
    lib_total = lib.get("total_assets", len(lib_records))
    lib_downloaded = sum(1 for r in lib_records if r.get("status") == "downloaded")
    lib_pending = max(lib_total - lib_downloaded, 0)

    # Indicators
    ind = _load("datasets/operations/nursing_indicators.json")
    ind_count = len(ind.get("records", []))
    ind_target = 100
    ind_pending = max(ind_target - ind_count, 0)

    # Resource / global expansion
    re_cov = _load("datasets/master-data/resource-expansion/coverage_report.json")
    ge_cov = _load("datasets/master-data/global-expansion/coverage_report.json")

    # Compulsory notifications queue
    cn_queue = _load("datasets/master-data/compulsory-notifications/pending_queue.json")
    cn_pending = cn_queue.get("total", len(cn_queue.get("items", [])))

    # Brazilian legislation
    bl_queue = _load("datasets/master-data/brazilian-legislation/pending_queue.json")
    bl_pending = bl_queue.get("total", len(bl_queue.get("items", [])))

    # ANVISA open data (dados.gov.br / dados.anvisa.gov.br)
    anv_discover = _load("datasets/master-data/anvisa-open-data/discover_report.json")
    anv_sources = _load("datasets/master-data/anvisa-open-data/scrape_sources.json")
    anv_meds = _load("datasets/regulatory/br/anvisa/medications_registry.json")
    anv_stale = anv_discover.get("stale", 0)
    anv_needs_catalog = not anv_sources.get("sources")
    anv_needs_data = len(anv_meds.get("records", [])) < 100
    anv_pending = anv_stale if anv_stale else (5 if anv_needs_catalog or anv_needs_data else 0)

    actions: list[dict[str, Any]] = []

    if med_pending > 0:
        actions.append({
            "agent": "medication_dictionary",
            "priority": 1,
            "pending": med_pending,
            "command": f"medication_dictionary_agents/run_batch.py --all-pending",
        })
    if wf_retry:
        actions.append({
            "agent": "content_workflows",
            "priority": 2,
            "pending": len(wf_retry),
            "statuses": wf_by_status,
            "command": "content/workflow_runner.py --retry-failed",
        })
    if cp_pending:
        actions.append({
            "agent": "content_pending",
            "priority": 3,
            "pending": len(cp_pending),
            "command": "content_agents/run_field_pipeline.py",
        })
    if lib_pending > 0:
        actions.append({
            "agent": "library_assets",
            "priority": 4,
            "pending": lib_pending,
            "command": f"resource_expansion/sync_library_assets.py --limit {min(lib_pending, 851)}",
        })
    if ind_pending > 0:
        actions.append({
            "agent": "indicators",
            "priority": 5,
            "pending": ind_pending,
            "command": "resource_expansion/build_nursing_indicators.py --target 100",
        })
    if cn_pending > 0:
        actions.append({
            "agent": "compulsory_notifications",
            "priority": 6,
            "pending": cn_pending,
            "command": "compulsory_notification_agents/run_batch.py --scrape --catalog",
        })
    if bl_pending > 0:
        actions.append({
            "agent": "brazilian_legislation",
            "priority": 7,
            "pending": bl_pending,
            "command": "brazilian_legislation_agents/run_batch.py --refresh --all-sources",
        })
    if anv_pending > 0:
        actions.append({
            "agent": "anvisa_open_data",
            "priority": 7,
            "pending": anv_pending,
            "command": "anvisa_open_data_agents/run_batch.py --monthly",
        })
    if (ge_cov.get("overall_completion_pct") or 100) < 100 or (ge_cov.get("progress_segments") or {}).get("profiles", 100) < 100:
        prof_pct = (ge_cov.get("progress_segments") or {}).get("profiles", 0)
        actions.append({
            "agent": "user_profiles",
            "priority": 8,
            "pending_pct": round(100 - prof_pct, 1),
            "command": "global_expansion/build_user_profiles.py",
        })
    if (ge_cov.get("overall_completion_pct") or 100) < 100:
        actions.append({
            "agent": "global_expansion",
            "priority": 8,
            "pending_pct": round(100 - (ge_cov.get("overall_completion_pct") or 0), 1),
            "command": "global_expansion_agents/run_global.py --all --rebuild",
        })

    actions.sort(key=lambda a: a.get("priority", 99))

    return {
        "generated_at": NOW(),
        "summary": {
            "total_action_items": len(actions),
            "critical_pending": sum(a.get("pending", 0) for a in actions if a.get("pending")),
        },
        "programs": {
            "content_pending": {
                "total": len(cp_items),
                "applied": cp_by_status.get("applied", 0),
                "pending_items": len(cp_pending),
                "by_status": cp_by_status,
            },
            "workflows": {
                "by_status": wf_by_status,
                "retry_count": len(wf_retry),
                "retry_ids": [w.get("workflow_id") for w in wf_retry[:20]],
            },
            "medication_dictionary": {
                "total_drug_references": len(drugs),
                "linked": len(med_refs),
                "pending": med_pending,
            },
            "resource_expansion": {
                "completion_pct": re_cov.get("overall_completion_pct", 0),
                "library_assets_pending": lib_pending,
                "indicators_count": ind_count,
                "indicators_target": ind_target,
                "indicators_pending": ind_pending,
            },
            "global_expansion": {
                "completion_pct": ge_cov.get("overall_completion_pct", 0),
                "segments": ge_cov.get("progress_segments", {}),
            },
            "compulsory_notifications": {"queue_pending": cn_pending},
            "brazilian_legislation": {"queue_pending": bl_pending},
            "anvisa_open_data": {
                "sources_total": anv_sources.get("sources_total", len(anv_sources.get("sources", []))),
                "stale_sources": anv_stale,
                "medications": len(anv_meds.get("records", [])),
                "pending_refresh": anv_pending,
            },
        },
        "actions": actions,
    }
