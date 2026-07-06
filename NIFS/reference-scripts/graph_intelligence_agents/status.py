"""Status for Graph Intelligence program."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from graph_snapshot import build_inventory_stats, detect_structural_issues
from paths import LOGS, MD, agents_registry, criteria, review_plan


def _llm_status() -> dict:
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        from llm_router import llm_status
        return llm_status()
    except ImportError:
        return {"providers": {}, "any_configured": False}


def collect_status() -> dict:
    stats = build_inventory_stats()
    structural = detect_structural_issues()
    crit = criteria()
    plan = review_plan()
    agents = agents_registry()

    report_path = LOGS / "validation_report.json"
    last_validation = None
    if report_path.is_file():
        try:
            last_validation = json.loads(report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass

    proposals = 0
    prop_path = LOGS / "content_proposals.jsonl"
    if prop_path.is_file():
        proposals = sum(1 for _ in prop_path.open(encoding="utf-8"))

    return {
        "program": "GRAPH_INTELLIGENCE",
        "name": "Clinical Graph Intelligence",
        "master_data_path": str(MD),
        "criteria_count": crit.get("count", 0),
        "review_phases": len(plan.get("phases", [])),
        "agents": len(agents.get("agents", [])),
        "graph_stats": stats,
        "structural_issues_summary": {
            "duplicates": len(structural.get("duplicate_relations", [])),
            "orphan_tool_refs": len(structural.get("orphan_tool_refs", [])),
        },
        "last_validation_score": last_validation.get("overall_score") if last_validation else None,
        "content_proposals_count": proposals,
        "llm": _llm_status(),
        "capabilities": [
            "tool_intelligence",
            "clinical_graph",
            "reasoning_continuity",
            "decision_layer",
            "dose_and_global_risk",
            "clinical_memory",
            "patient_context",
            "cross_tool_data",
            "dynamic_tool_generation",
            "analytics_evolution",
        ],
    }
