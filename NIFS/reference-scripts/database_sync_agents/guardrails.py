"""Limitadores anti-alucinação — LLM só enriquece; código decide."""
from __future__ import annotations

import copy
from typing import Any

# Ações executáveis pelo pipeline — whitelist estrita
ALLOWED_ACTIONS = frozenset({
    "security_backup",
    "run_agents",
    "run_agent",
    "validate",
    "generate_schema",
    "sync_upload",
    "write_report",
})

ALLOWED_DECISIONS = frozenset({"approve", "revise", "reject"})

# Campos que o LLM pode sobrescrever no review (resto ignorado)
REVIEW_LLM_ALLOWED_KEYS = frozenset({
    "notes",
    "recommendations",
    "revision_hints",
})

# Campos numéricos com limites
SCORE_MIN = 0.0
SCORE_MAX = 100.0


def clamp_score(value: Any, *, ceiling: float | None = None) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError):
        score = 0.0
    score = max(SCORE_MIN, min(SCORE_MAX, score))
    if ceiling is not None:
        score = min(score, ceiling)
    return round(score, 1)


def sanitize_plan_steps(steps: list[dict] | None) -> list[dict]:
    """Remove steps inventados pelo LLM; renumera."""
    if not steps:
        return []
    clean: list[dict] = []
    for raw in steps:
        action = (raw.get("action") or "").strip()
        if action not in ALLOWED_ACTIONS:
            continue
        clean.append({
            "step": len(clean) + 1,
            "action": action,
            "params": raw.get("params") if isinstance(raw.get("params"), dict) else {},
            "reason": str(raw.get("reason", ""))[:500],
        })
    # Backup → agentes → resto
    backup = [s for s in clean if s["action"] == "security_backup"]
    agents = [s for s in clean if s["action"] in ("run_agents", "run_agent")]
    rest = [s for s in clean if s["action"] not in ("security_backup", "run_agents", "run_agent")]
    ordered = backup + agents + rest
    for i, s in enumerate(ordered, 1):
        s["step"] = i
    return ordered


def merge_plan_safe(baseline: dict, llm: dict | None) -> dict:
    """Plano LLM fundido ao baseline — steps sanitizados; metadados textuais permitidos."""
    out = copy.deepcopy(baseline)
    if not llm or not isinstance(llm, dict):
        out["guardrails"] = {"llm_merged": False}
        return out

    llm_steps = sanitize_plan_steps(llm.get("steps"))
    if llm_steps:
        out["steps"] = llm_steps

    for key in ("interpretation", "recommendations", "risk_level"):
        if llm.get(key) and isinstance(llm[key], (str, list)):
            out[key] = llm[key]

    # Nunca confiar em upload_ready do LLM sem validação posterior
    out.pop("upload_ready", None)
    out["guardrails"] = {
        "llm_merged": True,
        "steps_before": len(baseline.get("steps") or []),
        "steps_after": len(out.get("steps") or []),
        "dropped_actions": _dropped_actions(baseline.get("steps"), out.get("steps")),
    }
    return out


def _dropped_actions(before: list | None, after: list | None) -> list[str]:
    before_a = {(s.get("action") or "") for s in (before or [])}
    after_a = {(s.get("action") or "") for s in (after or [])}
    return sorted(before_a - after_a - {""})


def merge_review_safe(baseline: dict, llm: dict | None, *, deterministic_ceiling: float) -> dict:
    """Review: decisão e score limitados pelo determinístico."""
    out = copy.deepcopy(baseline)
    if not llm or not isinstance(llm, dict):
        out["guardrails"] = {"llm_merged": False, "decision_source": "deterministic"}
        return out

    # Decisão: LLM só pode ser MAIS conservadora que o baseline
    llm_decision = (llm.get("decision") or "").strip().lower()
    base_decision = out.get("decision", "reject")
    out["decision"] = _conservative_decision(base_decision, llm_decision)
    out["llm_suggested_decision"] = llm_decision if llm_decision in ALLOWED_DECISIONS else None

    # Score: teto = determinístico (LLM não infla)
    llm_score = clamp_score(llm.get("precision_score"), ceiling=deterministic_ceiling)
    out["precision_score"] = min(out.get("precision_score", 0), llm_score)
    out["llm_raw_score"] = llm.get("precision_score")

    # Blockers: união (nunca remover blockers determinísticos)
    base_blockers = list(out.get("blockers") or [])
    llm_blockers = [b for b in (llm.get("blockers") or []) if isinstance(b, str)][:10]
    out["blockers"] = list(dict.fromkeys(base_blockers + llm_blockers))[:15]

    for key in REVIEW_LLM_ALLOWED_KEYS:
        if llm.get(key):
            out[key] = llm[key]

    out["guardrails"] = {
        "llm_merged": True,
        "decision_source": "conservative_merge",
        "score_ceiling": deterministic_ceiling,
        "hallucination_risk": _hallucination_flags(baseline, llm),
    }
    return out


def _conservative_decision(base: str, llm: str) -> str:
    """Ordem de conservadorismo: reject > revise > approve."""
    rank = {"approve": 0, "revise": 1, "reject": 2}
    b = rank.get(base, 2)
    l = rank.get(llm, 2) if llm in ALLOWED_DECISIONS else b
    inv = {0: "approve", 1: "revise", 2: "reject"}
    return inv[max(b, l)]


def _hallucination_flags(baseline: dict, llm: dict) -> list[str]:
    flags: list[str] = []
    if llm.get("decision") == "approve" and baseline.get("decision") != "approve":
        flags.append("llm_optimistic_approve_blocked")
    try:
        if float(llm.get("precision_score", 0)) > float(baseline.get("precision_score", 0)) + 5:
            flags.append("llm_score_inflation_clamped")
    except (TypeError, ValueError):
        flags.append("llm_invalid_score")
    if llm.get("upload_ready") is True and baseline.get("decision") != "approve":
        flags.append("llm_upload_ready_ignored")
    llm_steps = llm.get("steps")
    if isinstance(llm_steps, list):
        for s in llm_steps:
            if (s.get("action") or "") not in ALLOWED_ACTIONS:
                flags.append(f"llm_invented_action:{s.get('action')}")
                break
    return flags


def llm_payload_limits() -> dict:
    """Parâmetros conservadores para reduzir alucinação."""
    return {
        "temperature": 0.05,
        "max_tokens": 4096,
    }
