"""Executor — aplica o plano DeepSeek passo a passo."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

from backup import create_security_backup, list_backups
from orchestrator import run_pipeline
from paths import MD, append_log
from schema_builder import write_schema_file
from validate_program import run_validation


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def execute_step(step: dict, *, run_id: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    action = step.get("action", "")
    params = step.get("params") or {}
    out = {"step": step.get("step"), "action": action, "ok": False}

    if action == "security_backup":
        result = create_security_backup(
            full=params.get("full", False),
            tiers=params.get("tiers"),
            label=params.get("label", f"pre_finalize_{run_id}"),
        )
        out.update(result)
        out["ok"] = result.get("ok", False)
        return out

    if action == "run_agents":
        from agent_executor import run_pending_agents, run_task_center_batch  # noqa: WPS433

        use_llm = params.get("use_llm", payload.get("use_llm", False))
        mode = params.get("mode", "task_center")
        if mode == "pending":
            result = run_pending_agents(use_llm=use_llm, agents=params.get("agents"))
        else:
            result = run_task_center_batch(
                task_ids=params.get("task_ids"),
                status=params.get("status", "pending"),
                use_llm=use_llm,
                limit=int(params.get("limit", 15)),
            )
        out.update(result)
        out["ok"] = result.get("ok", False)
        return out

    if action == "run_agent":
        from agent_executor import run_agent_by_name  # noqa: WPS433

        agent = params.get("agent", "")
        if not agent:
            out["error"] = "missing_agent_param"
            return out
        result = run_agent_by_name(
            agent,
            use_llm=params.get("use_llm", payload.get("use_llm", False)),
            limit=int(params.get("limit", 10)),
        )
        out.update(result)
        out["ok"] = result.get("ok", False)
        return out

    if action == "validate":
        tier = params.get("tier")
        tiers = params.get("tiers") or ([tier] if tier else None)
        keys = None
        if tiers:
            from config import ENTITY_TIERS
            keys = [e["entity_key"] for t in tiers for e in ENTITY_TIERS.get(t, [])]
        rep = run_validation(keys)
        out["ok"] = rep.ok
        out["errors"] = rep.errors[:10]
        out["warnings"] = rep.warnings[:10]
        out["entities"] = {k: v.get("record_count") for k, v in rep.entities.items()}
        return out

    if action == "generate_schema":
        path = write_schema_file()
        out["ok"] = True
        out["schema_path"] = path
        return out

    if action == "sync_upload":
        dry_run = params.get("dry_run")
        if payload.get("live"):
            dry_run = False
        elif dry_run is None:
            dry_run = not payload.get("live", False)

        result = run_pipeline(
            tier=params.get("tier"),
            entity_keys=params.get("entities"),
            target=params.get("target", "supabase"),
            use_llm=params.get("use_llm", False),
            dry_run=dry_run,
            validate_only=False,
            payload={**payload, "force": params.get("force", False)},
        )
        out.update(result)
        out["ok"] = result.get("ok", False)
        return out

    if action == "write_report":
        out["ok"] = True
        out["backups_available"] = len(list_backups(5))
        return out

    out["error"] = f"unknown_action:{action}"
    return out


def execute_plan(
    plan: dict,
    *,
    payload: dict | None = None,
    stop_on_error: bool = True,
) -> dict:
    """Executa todos os steps do plano."""
    payload = payload or {}
    run_id = f"FIN.{uuid4().hex[:10].upper()}"
    steps_out = []
    backup_id = None

    for step in plan.get("steps", []):
        if step.get("action") == "security_backup" and backup_id:
            steps_out.append({"step": step.get("step"), "action": "security_backup", "ok": True, "skipped": "already_backed_up"})
            continue

        result = execute_step(step, run_id=run_id, payload=payload)
        steps_out.append(result)

        if result.get("action") == "security_backup" and result.get("ok"):
            backup_id = result.get("backup_id")

        if stop_on_error and not result.get("ok") and not result.get("skipped"):
            break

    report = {
        "ok": all(s.get("ok") for s in steps_out),
        "run_id": run_id,
        "backup_id": backup_id,
        "plan_mode": plan.get("mode"),
        "interpretation": plan.get("interpretation"),
        "risk_level": plan.get("risk_level"),
        "steps_executed": len(steps_out),
        "steps": steps_out,
        "finished_at": _now(),
    }

    append_log(run_id, report)
    report_path = MD / "last_finalize_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
