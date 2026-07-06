"""Executa agentes reais (subprocess + runners) — ponte Task Center ↔ finalize."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
if str(SCRIPTS / "task_center") not in sys.path:
    sys.path.insert(0, str(SCRIPTS / "task_center"))


def run_pending_agents(*, use_llm: bool = False, agents: list[str] | None = None) -> dict:
    """Executa todos os agentes com pendências (run_pending_agents.py)."""
    from run_pending_agents import run_pending  # noqa: WPS433

    report = run_pending(use_llm=use_llm)
    steps = report.get("steps", [])
    if agents:
        allowed = set(agents)
        steps = [s for s in steps if s.get("step") in allowed or s.get("agent") in allowed]
    ok = sum(1 for s in steps if s.get("ok"))
    return {
        "ok": ok > 0 or len(steps) == 0,
        "mode": "run_pending_agents",
        "steps_run": len(steps),
        "steps_ok": ok,
        "steps": steps,
        "inventory_after": report.get("inventory_after"),
    }


def run_task_center_batch(
    *,
    task_ids: list[str] | None = None,
    status: str = "pending",
    use_llm: bool = False,
    limit: int = 20,
) -> dict:
    """Executa tarefas do registro Task Center."""
    from registry import list_tasks, sync_registry  # noqa: WPS433
    from runner import run_batch_tasks, run_task  # noqa: WPS433

    sync_registry()
    if task_ids:
        return run_batch_tasks(task_ids[:limit], use_llm=use_llm)

    listed = list_tasks(status=status, limit=limit)
    ids = [t["id"] for t in listed.get("tasks", []) if t.get("status") == "pending"]
    if not ids:
        return {"ok": True, "total": 0, "succeeded": 0, "results": [], "note": "no_pending_tasks"}
    return run_batch_tasks(ids, use_llm=use_llm)


def run_agent_by_name(agent: str, *, use_llm: bool = False, limit: int = 10) -> dict:
    """Executa um agente pelo nome (PROG.{agent})."""
    from runner import run_task  # noqa: WPS433

    task_id = f"PROG.{agent}"
    return run_task(task_id, use_llm=use_llm, limit=limit)
