"""Eval report automático — métricas pós-run + detecção de alucinação."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from guardrails import clamp_score
from paths import MD


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_eval_report(state: dict) -> dict:
    """Gera relatório de avaliação a partir do estado final do LangGraph."""
    review = state.get("review") or {}
    validation = state.get("validation") or {}
    plan = state.get("plan") or {}
    deviations = state.get("deviation_report") or {}
    trace = state.get("trace") or []

    guard_review = review.get("guardrails") or {}
    guard_plan = plan.get("guardrails") or {}
    hall_flags = list(dict.fromkeys(
        (guard_review.get("hallucination_risk") or [])
        + ([f"dropped:{a}" for a in (guard_plan.get("dropped_actions") or [])])
    ))

    gate_blocked = "report_fail:gate_blocked" in trace
    precision = validation.get("precision_score") or state.get("precision_score") or 0
    min_score = state.get("min_score", 95.0)

    metrics = {
        "precision_score": precision,
        "min_score_required": min_score,
        "gate_passed": validation.get("validation_passed") and not gate_blocked,
        "upload_allowed": state.get("upload_allowed"),
        "validation_passed": validation.get("validation_passed"),
        "deterministic_errors": validation.get("error_count", 0),
        "deterministic_warnings": validation.get("warning_count", 0),
        "replan_count": state.get("replan_count", 0),
        "revise_count": state.get("revise_count", 0),
        "review_decision": review.get("decision"),
        "llm_enabled": state.get("use_llm"),
        "hallucination_flags": hall_flags,
        "hallucination_flag_count": len(hall_flags),
        "deviation_count": deviations.get("deviation_count", 0),
        "compliance_gap_pct": deviations.get("compliance_gap_pct"),
    }

    # Score composto de confiança (0-100)
    confidence = precision
    confidence -= metrics["hallucination_flag_count"] * 5
    confidence -= metrics["deterministic_errors"] * 8
    confidence -= metrics["replan_count"] * 3
    confidence -= metrics["revise_count"] * 2
    if gate_blocked:
        confidence -= 15
    confidence = clamp_score(confidence)

    passed = (
        metrics["gate_passed"]
        and precision >= min_score
        and metrics["deterministic_errors"] == 0
        and metrics["hallucination_flag_count"] == 0
    )

    report = {
        "run_id": state.get("run_id"),
        "evaluated_at": _now(),
        "graph": state.get("graph", "langgraph_finalize_v1"),
        "passed": passed,
        "confidence_score": confidence,
        "metrics": metrics,
        "trace_summary": trace,
        "backup_id": (state.get("backup") or {}).get("backup_id"),
        "execution_ok": (state.get("execution") or {}).get("ok"),
        "recommendations": _recommendations(metrics, passed),
    }
    return _persist_eval_report(report)


def _recommendations(metrics: dict, passed: bool) -> list[str]:
    recs: list[str] = []
    if not passed:
        recs.append("Corrigir erros determinísticos antes de --live")
    if metrics["hallucination_flag_count"]:
        recs.append("Revisar flags anti-alucinação — LLM tentou inflar score ou aprovar cedo")
    if metrics["precision_score"] < metrics["min_score_required"]:
        recs.append(f"Precisão {metrics['precision_score']}% abaixo do mínimo {metrics['min_score_required']}%")
    if metrics["deviation_count"]:
        recs.append(f"Consultar deviation_report ({metrics['deviation_count']} desvios documentados)")
    if passed:
        recs.append("Gate OK — pode prosseguir com upload dry-run e depois --live")
    return recs


def _persist_eval_report(report: dict) -> dict:
    out_dir = MD / "eval_reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    run_id = report.get("run_id", "UNKNOWN")
    path = out_dir / f"{run_id}_eval.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    latest = MD / "last_eval_report.json"
    latest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["report_path"] = str(path)
    return report
