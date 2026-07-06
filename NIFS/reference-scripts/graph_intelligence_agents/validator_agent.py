"""Graph validation agent — Claude for deep criteria, Groq for fast screen."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from graph_snapshot import build_inventory_stats, build_validation_snapshot, detect_structural_issues
from paths import LOGS, criteria, prompt_template


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _deterministic_baseline() -> dict:
    """Score heurístico sem LLM — garante utilidade mesmo sem API key."""
    stats = build_inventory_stats()
    structural = detect_structural_issues()
    crit = criteria()
    threshold = crit.get("pass_threshold_pct", 70)

    tools_total = stats["counts"]["clinical_tools"]
    tools_linked = stats["tools_with_relations"]
    link_pct = (tools_linked / tools_total * 100) if tools_total else 0
    isolated_pct = (stats["isolated_tools_count"] / tools_total * 100) if tools_total else 100

    scores = {
        "tool_intelligence": min(100, int(link_pct * 1.2)),
        "clinical_graph": min(100, int(stats["counts"]["relations"] / 50)),
        "reasoning_continuity": 40 if stats["counts"]["decision_trees"] > 0 else 20,
        "decision_layer": min(100, stats["counts"]["decision_trees"] * 2),
        "dose_and_global_risk": 50,
        "clinical_memory": 15,
        "patient_context": 20,
        "cross_tool_data": min(100, int(link_pct)),
        "dynamic_tool_generation": 25,
        "analytics_evolution": 10,
    }

    overall = sum(scores.values()) / max(len(scores), 1)
    passed = overall >= threshold

    return {
        "mode": "deterministic",
        "overall_score": round(overall, 1),
        "passed": passed,
        "criteria_scores": {
            cid: {"score": scores.get(cid, 0), "passed": scores.get(cid, 0) >= 60}
            for cid in scores
        },
        "stats": stats,
        "structural_issues": structural,
        "isolated_tools_sample": stats.get("isolated_tools_sample", []),
        "database_utilization": {
            "idle_entities": stats.get("isolated_tools_sample", [])[:20],
            "underconnected_tools": stats.get("isolated_tools_sample", [])[:20],
            "suggested_activations": [
                "Wire clinical_memory via context-engine",
                "Connect dose calculators to global risk scores",
                "Run P4 content enrichment for isolated tools",
            ],
        },
        "validated_at": _now(),
    }


def validate_graph(
    *,
    tool_codes: list[str] | None = None,
    use_llm: bool = True,
    provider: str | None = None,
    payload: dict | None = None,
) -> dict:
    """Valida grafo contra 10 critérios. Claude se disponível; fallback determinístico."""
    payload = payload or {}
    baseline = _deterministic_baseline()

    if not use_llm:
        return baseline

    import sys
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from llm_router import llm_enabled, route_chat_json

    if not llm_enabled(payload):
        baseline["llm_skipped"] = True
        baseline["llm_reason"] = "No API key configured (ANTHROPIC_API_KEY, DEEPSEEK_API_KEY, or GROQ_API_KEY)"
        return baseline

    snapshot = build_validation_snapshot(tool_codes=tool_codes)
    crit_json = json.dumps(criteria(), ensure_ascii=False, indent=2)
    system_tpl = prompt_template("GRAPH_VALIDATE_SYSTEM")
    system = system_tpl.replace("{criteria_json}", crit_json)

    messages = [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": (
                "Snapshot do grafo NKOS:\n"
                + json.dumps(snapshot, ensure_ascii=False, indent=2)[:120000]
                + "\n\nBaseline determinístico:\n"
                + json.dumps(
                    {
                        "overall_score": baseline["overall_score"],
                        "isolated_tools": baseline.get("isolated_tools_sample"),
                        "structural": baseline.get("structural_issues"),
                    },
                    ensure_ascii=False,
                )
            ),
        },
    ]

    try:
        result = route_chat_json(
            messages,
            task="graph_validation",
            provider=provider or "claude",
            payload=payload,
            temperature=0.15,
            max_tokens=8192,
        )
        parsed = result.get("parsed") or {}
        out = {
            "mode": "llm",
            "provider": result.get("provider"),
            "model": result.get("model"),
            "overall_score": parsed.get("overall_score", baseline["overall_score"]),
            "passed": parsed.get("overall_score", baseline["overall_score"]) >= criteria().get("pass_threshold_pct", 70),
            "criteria_scores": parsed.get("criteria_scores", baseline["criteria_scores"]),
            "isolated_nodes": parsed.get("isolated_nodes", []),
            "missing_relations": parsed.get("missing_relations", []),
            "recommendations": parsed.get("recommendations", []),
            "database_utilization": parsed.get("database_utilization", baseline["database_utilization"]),
            "stats": snapshot.get("stats", baseline["stats"]),
            "validated_at": _now(),
        }
        _persist_report(out)
        return out
    except Exception as exc:
        baseline["llm_error"] = str(exc)[:500]
        baseline["llm_skipped"] = True
        return baseline


def fast_screen(*, payload: dict | None = None) -> dict:
    """Screening rápido via Groq/Llama."""
    import sys
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    stats = build_inventory_stats()
    structural = detect_structural_issues()
    payload = payload or {}

    from llm_router import llm_enabled, route_chat_json

    if not llm_enabled(payload):
        return {"mode": "deterministic", "stats": stats, "structural": structural}

    tpl = prompt_template("FAST_GRAPH_SCREEN")
    prompt = tpl.replace("{stats_json}", json.dumps({**stats, **structural}, ensure_ascii=False))

    try:
        result = route_chat_json(
            [{"role": "user", "content": prompt}],
            task="fast_check",
            provider="groq",
            payload=payload,
            max_tokens=2048,
        )
        return {
            "mode": "llm",
            "provider": result.get("provider"),
            "parsed": result.get("parsed"),
            "stats": stats,
            "structural": structural,
        }
    except Exception as exc:
        return {"mode": "deterministic", "stats": stats, "structural": structural, "error": str(exc)[:300]}


def _persist_report(report: dict) -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    path = LOGS / "validation_report.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
