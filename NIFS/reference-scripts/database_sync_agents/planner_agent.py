"""Agente DeepSeek — ler, interpretar e planejar finalização da base."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from paths import load_json  # noqa: E402
from reader import build_context_snapshot  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _default_plan(context: dict, *, target: str = "supabase") -> dict:
    """Plano determinístico quando DeepSeek indisponível."""
    tiers = context.get("tiers", ["tier1_core", "tier2_clinical", "tier3_content"])
    steps = [
        {"step": 1, "action": "security_backup", "params": {"tiers": tiers}, "reason": "Backup obrigatório antes de alterações"},
        {
            "step": 2,
            "action": "run_agents",
            "params": {"mode": "task_center", "status": "pending", "limit": 15},
            "reason": "Executar agentes reais (medicamentos, conteúdo, ANVISA, etc.)",
        },
        {"step": 3, "action": "validate", "params": {"tiers": tiers}, "reason": "Validar integridade local após agentes"},
        {"step": 4, "action": "generate_schema", "params": {}, "reason": "DDL Supabase"},
    ]
    n = 5
    for tier in tiers:
        steps.append({
            "step": n,
            "action": "sync_upload",
            "params": {"tier": tier, "target": target, "dry_run": True},
            "reason": f"Upload {tier} (dry-run primeiro)",
        })
        n += 1
    steps.append({
        "step": n,
        "action": "write_report",
        "params": {},
        "reason": "Relatório final",
    })
    return {
        "mode": "deterministic",
        "goal": "finalize_nkos_database",
        "interpretation": "Base local validada; executar backup, schema e upload por tiers.",
        "risk_level": "medium",
        "upload_ready": context.get("validation_ok", False),
        "steps": steps,
        "blockers_before_execute": context.get("validation_errors", [])[:5],
        "created_at": _now(),
    }


def _planner_prompt() -> str:
    from paths import resolve_prompt  # noqa: WPS433
    return resolve_prompt("FINALIZE_PLANNER_SYSTEM") or (
        "Plano NKOS JSON. Step 1: security_backup. Ações whitelist only."
    )


def _ensure_backup_first(steps: list[dict], tiers: list) -> list[dict]:
    from guardrails import sanitize_plan_steps  # noqa: WPS433
    steps = sanitize_plan_steps(steps)
    if not steps or steps[0].get("action") != "security_backup":
        steps.insert(0, {
            "step": 1,
            "action": "security_backup",
            "params": {"tiers": tiers},
            "reason": "Injetado — backup obrigatório",
        })
    return sanitize_plan_steps(steps)


def plan_finalize(
    *,
    tiers: list[str] | None = None,
    target: str = "supabase",
    use_llm: bool = True,
    payload: dict | None = None,
) -> dict:
    """DeepSeek: READ → INTERPRET → PLAN (com guardrails)."""
    payload = payload or {}
    context = build_context_snapshot(tiers=tiers)
    baseline = _default_plan(context, target=target)

    if not use_llm:
        baseline["context"] = context
        return baseline

    from llm_router import llm_enabled, route_chat_json  # noqa: WPS433
    from guardrails import llm_payload_limits, merge_plan_safe  # noqa: WPS433

    if not llm_enabled(payload):
        baseline["llm_skipped"] = True
        baseline["context"] = context
        return baseline

    system = _planner_prompt()
    user_content = (
        "Contexto NKOS (leia e interprete — NÃO invente dados):\n"
        f"```json\n{json.dumps(context, ensure_ascii=False, indent=2)[:14000]}\n```\n\n"
        f"Destino: {target}\n"
        "Retorne JSON: goal, interpretation, risk_level, steps[]"
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_content},
    ]

    try:
        llm = route_chat_json(
            messages,
            task="database_validation",
            payload={**payload, **llm_payload_limits()},
        )
        parsed = llm.get("parsed") or {}
        if isinstance(parsed, str):
            parsed = json.loads(parsed)
        if not parsed.get("steps"):
            parsed = {}
        content = merge_plan_safe(baseline, parsed)
        content["steps"] = _ensure_backup_first(content.get("steps") or [], context.get("tiers", []))
        content["mode"] = "deepseek"
        content["llm_model"] = llm.get("model")
        content["created_at"] = _now()
        content.pop("context", None)
        return content
    except Exception as exc:
        baseline["llm_error"] = str(exc)[:300]
        return baseline

