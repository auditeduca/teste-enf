"""LangGraph v2: Read → Plan → Review ⇄ RevisePlan → Validate → Deviations → Execute → Eval → Report.

Guardrails anti-alucinação + DeepSeek documenta desvios (somente fatos).
"""
from __future__ import annotations

import json
import operator
import sys
from pathlib import Path
from typing import Annotated, Literal, TypedDict

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
if str(SCRIPTS / "database_sync_agents") not in sys.path:
    sys.path.insert(0, str(SCRIPTS / "database_sync_agents"))

from backup import create_security_backup  # noqa: E402
from deviation_agent import document_deviations  # noqa: E402
from eval_report import build_eval_report  # noqa: E402
from executor_agent import execute_step  # noqa: E402
from guardrails import llm_payload_limits, merge_plan_safe, merge_review_safe  # noqa: E402
from paths import MD, append_log, resolve_prompt  # noqa: E402
from planner_agent import _default_plan, _ensure_backup_first, plan_finalize  # noqa: E402
from reader import build_context_snapshot  # noqa: E402
from validate_program import run_validation  # noqa: E402

try:
    from langgraph.graph import END, START, StateGraph
except ImportError:
    StateGraph = None  # type: ignore

DEFAULT_MIN_SCORE = 95.0
MAX_REVISE = 2
MAX_REPLAN = 1
GRAPH_VERSION = "langgraph_finalize_v2"


class FinalizeState(TypedDict):
    tiers: list[str]
    target: str
    api_key: str
    model: str
    use_llm: bool
    live: bool
    force: bool
    min_score: float
    replan_count: int
    revise_count: int
    run_id: str
    backup: dict
    context: dict
    plan: dict
    review: dict
    validation: dict
    execution: dict
    agents_run: dict
    deviation_report: dict
    eval_report: dict
    precision_score: float
    upload_allowed: bool
    trace: Annotated[list[str], operator.add]
    error: str
    skip_agents: bool


def _deterministic_review(plan: dict, context: dict, min_score: float) -> dict:
    errors = context.get("validation_errors") or []
    warnings = context.get("validation_warnings") or []
    steps = plan.get("steps") or []
    has_backup = any(s.get("action") == "security_backup" for s in steps)
    score = 100.0 if context.get("validation_ok") else 85.0
    blockers: list[str] = []
    if errors:
        score -= min(len(errors) * 8, 40)
        blockers.extend(errors[:5])
    if warnings and not context.get("validation_ok"):
        score -= min(len(warnings) * 2, 10)
    if not has_backup:
        score -= 20
        blockers.append("missing_security_backup_step")
    score = round(max(0, min(100, score)), 1)
    decision: Literal["approve", "revise", "reject"] = "approve"
    if score < min_score:
        decision = "revise" if score >= min_score - 10 else "reject"
    if errors:
        decision = "reject" if score < min_score - 10 else "revise"
    return {
        "decision": decision,
        "precision_score": score,
        "blockers": blockers,
        "notes": f"Score {score}% vs mínimo {min_score}%",
        "mode": "deterministic",
    }


def _deterministic_validation(context: dict, review: dict, min_score: float) -> dict:
    tier_keys = []
    for t in context.get("tiers", []):
        from config import ENTITY_TIERS
        tier_keys.extend(e["entity_key"] for e in ENTITY_TIERS.get(t, []))
    rep = run_validation(tier_keys or None)
    precision = review.get("precision_score", 0)
    if rep.errors:
        precision = min(precision, max(0, 100 - len(rep.errors) * 10))
    passed = len(rep.errors) == 0 and precision >= min_score
    return {
        "validation_passed": passed,
        "precision_score": round(precision, 1),
        "min_score_required": min_score,
        "deterministic_ok": rep.ok,
        "error_count": len(rep.errors),
        "warning_count": len(rep.warnings),
        "errors": rep.errors[:10],
        "warnings": rep.warnings[:10],
        "upload_allowed": passed,
        "mode": "deterministic",
    }


def _deterministic_revise_plan(plan: dict, review: dict, context: dict, *, target: str, live: bool) -> dict:
    """Correção determinística do plano (Generate node)."""
    blockers = review.get("blockers") or []
    revised = _default_plan(context, target=target)
    revised["interpretation"] = f"Plano revisado após review:{review.get('decision')} — {review.get('notes', '')}"
    revised["revised_from"] = plan.get("mode")
    revised["revision_blockers"] = blockers[:10]
    steps = revised.get("steps") or []
    for s in steps:
        if s.get("action") == "sync_upload":
            params = s.setdefault("params", {})
            if not live:
                params["dry_run"] = True
    revised["steps"] = _ensure_backup_first(steps, context.get("tiers", []))
    return revised


def read_node(state: FinalizeState) -> dict:
    return {"context": build_context_snapshot(tiers=state["tiers"]), "trace": ["read:context_snapshot"]}


def backup_node(state: FinalizeState) -> dict:
    backup = create_security_backup(tiers=state["tiers"], label=f"langgraph_{state['run_id']}")
    return {"backup": backup, "trace": [f"backup:{backup.get('backup_id')}"]}


def run_agents_node(state: FinalizeState) -> dict:
    """Executa agentes reais antes do plano (medicamentos, conteúdo, ANVISA…)."""
    if state.get("skip_agents"):
        return {"agents_run": {"ok": True, "skipped": True}, "trace": ["run_agents:skipped"]}

    from agent_executor import run_task_center_batch  # noqa: WPS433

    result = run_task_center_batch(
        status="pending",
        use_llm=state.get("use_llm", False),
        limit=15,
    )
    context = build_context_snapshot(tiers=state["tiers"])
    return {
        "agents_run": result,
        "context": context,
        "trace": [f"run_agents:{result.get('succeeded', 0)}/{result.get('total', 0)}"],
    }


def plan_node(state: FinalizeState) -> dict:
    payload = {"api_key": state.get("api_key"), "live": state.get("live"), "force": state.get("force")}
    plan = plan_finalize(
        tiers=state["tiers"],
        target=state["target"],
        use_llm=state.get("use_llm", True),
        payload=payload,
    )
    plan.pop("context", None)
    return {"plan": plan, "trace": [f"plan:{plan.get('mode', '?')}"]}


def review_node(state: FinalizeState) -> dict:
    plan = state.get("plan") or {}
    context = state.get("context") or {}
    min_score = state.get("min_score", DEFAULT_MIN_SCORE)
    baseline = _deterministic_review(plan, context, min_score)
    ceiling = baseline["precision_score"]

    if state.get("use_llm") and state.get("api_key"):
        try:
            from llm_router import route_chat_json  # noqa: WPS433
            system = resolve_prompt("FINALIZE_REVIEW_SYSTEM")
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps({
                    "plan": {"steps": plan.get("steps"), "interpretation": plan.get("interpretation")},
                    "context_summary": {
                        "validation_ok": context.get("validation_ok"),
                        "errors": context.get("validation_errors", [])[:8],
                        "warnings": context.get("validation_warnings", [])[:8],
                        "deterministic_score_ceiling": ceiling,
                        "min_score_required": min_score,
                    },
                }, ensure_ascii=False)[:12000]},
            ]
            llm = route_chat_json(
                messages,
                task="database_validation",
                payload={"api_key": state["api_key"], **llm_payload_limits()},
            )
            parsed = llm.get("parsed") or {}
            if isinstance(parsed, dict) and parsed.get("decision"):
                review = merge_review_safe(baseline, parsed, deterministic_ceiling=ceiling)
                review["mode"] = "deepseek_langgraph"
            else:
                review = baseline
        except Exception as exc:
            review = {**baseline, "llm_error": str(exc)[:200]}
    else:
        review = baseline

    return {
        "review": review,
        "precision_score": float(review.get("precision_score", 0)),
        "trace": [f"review:{review.get('decision')}:{review.get('precision_score')}%"],
    }


def revise_plan_node(state: FinalizeState) -> dict:
    """Generate — corrige plano com base no review (loop SOTA)."""
    plan = state.get("plan") or {}
    review = state.get("review") or {}
    context = state.get("context") or {}
    baseline = _deterministic_revise_plan(plan, review, context, target=state["target"], live=state.get("live", False))

    if state.get("use_llm") and state.get("api_key"):
        try:
            from llm_router import route_chat_json  # noqa: WPS433
            system = resolve_prompt("FINALIZE_REVISE_SYSTEM")
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps({
                    "current_plan_steps": plan.get("steps"),
                    "blockers": review.get("blockers"),
                    "revision_hints": review.get("revision_hints", []),
                    "notes": review.get("notes"),
                    "live_upload": state.get("live"),
                }, ensure_ascii=False)[:8000]},
            ]
            llm = route_chat_json(
                messages,
                task="database_validation",
                payload={"api_key": state["api_key"], **llm_payload_limits()},
            )
            parsed = llm.get("parsed") or {}
            revised = merge_plan_safe(baseline, parsed if isinstance(parsed, dict) else None)
            revised["steps"] = _ensure_backup_first(revised.get("steps") or [], context.get("tiers", []))
            revised["mode"] = "deepseek_revised"
        except Exception as exc:
            revised = {**baseline, "llm_error": str(exc)[:200]}
    else:
        revised = baseline

    return {
        "plan": revised,
        "revise_count": state.get("revise_count", 0) + 1,
        "trace": [f"revise_plan:{state.get('revise_count', 0) + 1}"],
    }


def validate_node(state: FinalizeState) -> dict:
    context = state.get("context") or {}
    review = state.get("review") or {}
    min_score = state.get("min_score", DEFAULT_MIN_SCORE)
    validation = _deterministic_validation(context, review, min_score)
    return {
        "validation": validation,
        "precision_score": validation["precision_score"],
        "upload_allowed": validation["upload_allowed"],
        "trace": [f"validate:{'pass' if validation['validation_passed'] else 'fail'}:{validation['precision_score']}%"],
    }


def deviations_node(state: FinalizeState) -> dict:
    validation = state.get("validation") or {}
    if not validation and state.get("context"):
        validation = {
            "errors": state["context"].get("validation_errors", []),
            "warnings": state["context"].get("validation_warnings", []),
            "precision_score": state.get("precision_score"),
            "validation_passed": False,
        }
    doc = document_deviations(
        run_id=state["run_id"],
        context=state.get("context") or {},
        validation=validation,
        review=state.get("review"),
        plan=state.get("plan"),
        use_llm=state.get("use_llm", True),
        api_key=state.get("api_key") or None,
    )
    return {"deviation_report": doc, "trace": [f"deviations:{doc.get('deviation_count', 0)}"]}


def execute_node(state: FinalizeState) -> dict:
    plan = state.get("plan") or {}
    payload = {"live": state.get("live"), "force": state.get("force"), "use_llm": state.get("use_llm")}
    agents_done = (state.get("agents_run") or {}).get("ok")
    steps_out = []
    for step in plan.get("steps", []):
        if step.get("action") == "security_backup":
            continue
        if step.get("action") == "run_agents" and agents_done:
            steps_out.append({
                "step": step.get("step"),
                "action": "run_agents",
                "ok": True,
                "skipped": "already_ran_in_graph",
            })
            continue
        result = execute_step(step, run_id=state["run_id"], payload=payload)
        steps_out.append(result)
        if not result.get("ok") and not state.get("force"):
            break
    return {
        "execution": {"ok": all(s.get("ok") for s in steps_out) if steps_out else False, "steps": steps_out},
        "trace": [f"execute:{len(steps_out)}_steps"],
    }


def eval_node(state: FinalizeState) -> dict:
    state_copy = dict(state)
    state_copy["graph"] = GRAPH_VERSION
    report = build_eval_report(state_copy)
    return {"eval_report": report, "trace": [f"eval:{'pass' if report.get('passed') else 'fail'}"]}


def report_node(state: FinalizeState) -> dict:
    report = {
        "run_id": state["run_id"],
        "graph": GRAPH_VERSION,
        "precision_score": state.get("precision_score"),
        "upload_allowed": state.get("upload_allowed"),
        "backup_id": (state.get("backup") or {}).get("backup_id"),
        "review_decision": (state.get("review") or {}).get("decision"),
        "validation_passed": (state.get("validation") or {}).get("validation_passed"),
        "execution_ok": (state.get("execution") or {}).get("ok"),
        "eval_passed": (state.get("eval_report") or {}).get("passed"),
        "confidence_score": (state.get("eval_report") or {}).get("confidence_score"),
        "deviation_report_path": (state.get("deviation_report") or {}).get("report_path"),
        "eval_report_path": (state.get("eval_report") or {}).get("report_path"),
        "trace": state.get("trace", []),
    }
    (MD / "last_finalize_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    append_log(state["run_id"], report)
    return {"trace": ["report:saved"]}


def report_fail_node(state: FinalizeState) -> dict:
    return {"upload_allowed": False, "trace": ["report_fail:gate_blocked"]}


def replan_node(state: FinalizeState) -> dict:
    context = state.get("context") or {}
    plan = _default_plan(context, target=state["target"])
    plan["replan_reason"] = (state.get("review") or {}).get("blockers", [])
    return {"plan": plan, "replan_count": state.get("replan_count", 0) + 1, "trace": [f"replan:{state.get('replan_count', 0) + 1}"]}


def _route_after_review(state: FinalizeState) -> str:
    review = state.get("review") or {}
    decision = review.get("decision", "reject")
    if decision == "approve":
        return "validate"
    if decision == "revise":
        if state.get("revise_count", 0) < MAX_REVISE:
            return "revise_plan"
        if state.get("replan_count", 0) < MAX_REPLAN:
            return "replan"
    return "deviations_fail"


def _route_after_validate(state: FinalizeState) -> str:
    return "deviations"


def build_graph(*, execute_enabled: bool = True):
    return _build_graph_inner(execute_enabled)


def _build_graph_inner(execute_enabled: bool):
    if StateGraph is None:
        raise ImportError("langgraph não instalado — pip install -r requirements-nkp.txt")

    g = StateGraph(FinalizeState)
    for name, fn in [
        ("read", read_node), ("backup", backup_node), ("run_agents", run_agents_node),
        ("plan", plan_node),
        ("review", review_node), ("revise_plan", revise_plan_node),
        ("validate", validate_node), ("deviations", deviations_node),
        ("execute", execute_node), ("eval", eval_node), ("report", report_node),
        ("replan", replan_node),
    ]:
        g.add_node(name, fn)

    g.add_edge(START, "read")
    g.add_edge("read", "backup")
    g.add_edge("backup", "run_agents")
    g.add_edge("run_agents", "plan")
    g.add_edge("plan", "review")
    g.add_conditional_edges("review", _route_after_review, {
        "validate": "validate",
        "revise_plan": "revise_plan",
        "replan": "replan",
        "deviations_fail": "deviations",
    })
    g.add_edge("revise_plan", "review")
    g.add_edge("replan", "review")
    g.add_edge("validate", "deviations")

    if execute_enabled:
        g.add_conditional_edges(
            "deviations",
            lambda s: "execute" if s.get("upload_allowed") else "eval",
            {"execute": "execute", "eval": "eval"},
        )
        g.add_edge("execute", "eval")
    else:
        g.add_edge("deviations", "eval")

    g.add_edge("eval", "report")
    g.add_edge("report", END)
    return g.compile()


def run_finalize_graph(
    *,
    tiers: list[str] | None = None,
    target: str = "supabase",
    api_key: str | None = None,
    use_llm: bool = True,
    live: bool = False,
    force: bool = False,
    min_score: float = DEFAULT_MIN_SCORE,
    execute_enabled: bool = True,
    validate_only: bool = False,
    skip_agents: bool = False,
) -> dict:
    from uuid import uuid4
    import os

    if validate_only:
        execute_enabled = False

    key = (api_key or os.environ.get("DEEPSEEK_API_KEY") or "").strip()
    run_id = f"FIN.{uuid4().hex[:10].upper()}"
    tier_list = tiers or ["tier1_core", "tier2_clinical", "tier3_content"]

    graph = _build_graph_inner(execute_enabled=execute_enabled and not validate_only)
    initial: FinalizeState = {
        "tiers": tier_list,
        "target": target,
        "api_key": key,
        "model": "",
        "use_llm": bool(use_llm and key),
        "live": live,
        "force": force,
        "min_score": min_score,
        "replan_count": 0,
        "revise_count": 0,
        "run_id": run_id,
        "backup": {},
        "context": {},
        "plan": {},
        "review": {},
        "validation": {},
        "execution": {},
        "agents_run": {},
        "deviation_report": {},
        "eval_report": {},
        "precision_score": 0.0,
        "upload_allowed": False,
        "trace": [],
        "error": "",
        "skip_agents": skip_agents,
    }
    result = graph.invoke(initial)

    eval_passed = (result.get("eval_report") or {}).get("passed")

    if validate_only:
        ok = bool((result.get("validation") or {}).get("validation_passed"))
    elif force:
        ok = True
    else:
        ok = bool(eval_passed)

    result["ok"] = ok
    result["graph"] = GRAPH_VERSION
    result["min_score"] = min_score
    result["llm_enabled"] = initial["use_llm"]

    try:
        from agent_common.sanitize import sanitize_agent_result  # noqa: WPS433
        return sanitize_agent_result(result)
    except ImportError:
        return result
