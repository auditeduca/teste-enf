"""Registro unificado de tarefas — inventário + AI Factory + fases do grafo."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from paths import REGISTRY, load_registry, save_registry

ROOT = Path(__file__).resolve().parent.parent.parent

AGENT_LABELS: dict[str, str] = {
    "medication_dictionary": "Dicionário de medicamentos",
    "content_workflows": "Workflows de conteúdo",
    "content_pending": "Conteúdos pendentes",
    "library_assets": "Assets da biblioteca",
    "indicators": "Indicadores de enfermagem",
    "compulsory_notifications": "Notificações compulsórias",
    "brazilian_legislation": "Legislação brasileira",
    "anvisa_open_data": "ANVISA dados abertos",
    "user_profiles": "Perfis de usuário",
    "global_expansion": "Expansão global",
    "graph_screen_groq": "Grafo — screening",
    "graph_validator_claude": "Grafo — validação Claude",
    "graph_content_claude": "Grafo — conteúdo clínico",
    "ai_factory_batch": "AI Factory — lote ferramentas",
}

AGENT_LINKS: dict[str, str] = {
    "medication_dictionary": "/anvisa-open-data",
    "content_workflows": "/content-pending",
    "content_pending": "/content-pending",
    "library_assets": "/resource-expansion",
    "compulsory_notifications": "/compulsory-notifications",
    "brazilian_legislation": "/brazilian-legislation",
    "anvisa_open_data": "/anvisa-open-data",
    "global_expansion": "/global-expansion",
    "graph_validator_claude": "/graph-ai",
    "ai_factory_batch": "/ai-factory",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_ai_tasks() -> list[dict]:
    p = ROOT / "datasets/master-data/ai-factory/ai_tasks.json"
    if not p.is_file():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8")).get("records", [])
    except json.JSONDecodeError:
        return []


def _load_factory_logs(limit: int = 150) -> list[dict]:
    logs_dir = ROOT / "datasets/master-data/ai-factory/logs"
    if not logs_dir.is_dir():
        return []
    files = sorted(logs_dir.glob("RUN.*.json"), key=lambda f: f.stat().st_mtime, reverse=True)[:limit]
    out = []
    for f in files:
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    return out


def sync_registry() -> dict:
    """Reconstrói fila a partir do inventário + logs recentes + fases GI."""
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from agent_common.pending_inventory import collect  # noqa: WPS433

    inv = collect()
    existing = {t["id"]: t for t in load_registry().get("tasks", [])}
    tasks: list[dict] = []
    seen_ids: set[str] = set()

    for action in inv.get("actions", []):
        agent = action["agent"]
        tid = f"PROG.{agent}"
        pending = action.get("pending")
        if pending is None:
            pending = action.get("pending_pct", 0)
        total = int(pending) if isinstance(pending, (int, float)) and pending > 1 else 100
        prev = existing.get(tid, {})
        done = prev.get("done", 0)
        if isinstance(pending, float) and pending < 100:
            progress = max(0, min(100, 100 - pending))
            status = "completed" if progress >= 100 else "pending"
        elif isinstance(pending, int) and pending == 0:
            progress = 100
            status = "completed"
        else:
            progress = prev.get("progress_pct", 0)
            status = prev.get("status", "pending")
            if prev.get("status") == "completed":
                progress = 100

        tasks.append({
            "id": tid,
            "title": AGENT_LABELS.get(agent, agent.replace("_", " ").title()),
            "agent": agent,
            "type": "program",
            "status": status,
            "priority": action.get("priority", 99),
            "total": total,
            "done": done if status != "completed" else total,
            "progress_pct": round(progress if status == "completed" else (done / total * 100 if total else 0), 1),
            "command": action.get("command"),
            "link": AGENT_LINKS.get(agent, "/tasks"),
            "source": "inventory",
            "updated_at": _now(),
            "resolved_codes": prev.get("resolved_codes", []),
        })
        seen_ids.add(tid)

    for rec in _load_ai_tasks():
        tid = rec.get("task_id", "")
        if not tid or tid in seen_ids:
            continue
        if rec.get("type") == "workflow_run" and rec.get("output", {}).get("tool_code"):
            continue  # covered by logs
        status = rec.get("status", "pending")
        tasks.append({
            "id": tid,
            "title": rec.get("phase_id") or rec.get("workflow_id") or tid,
            "agent": rec.get("agent_id", "graph"),
            "type": "graph_phase",
            "status": "completed" if status == "completed" else status,
            "priority": 5,
            "total": 1,
            "done": 1 if status == "completed" else 0,
            "progress_pct": 100 if status == "completed" else 0,
            "command": rec.get("api"),
            "link": "/graph-ai",
            "source": "ai_tasks",
            "updated_at": rec.get("created_at") or _now(),
            "resolved_codes": [],
        })
        seen_ids.add(tid)

    for log in _load_factory_logs():
        run_id = log.get("run_id")
        tool_code = log.get("tool_code")
        if not run_id or run_id in seen_ids:
            continue
        ok = log.get("ok")
        steps_done = len([s for s in log.get("steps", []) if s.get("status") == "completed"])
        steps_total = len([s for s in log.get("steps", []) if s.get("status") != "skipped"]) or 6
        progress = round(steps_done / steps_total * 100, 1) if steps_total else 0
        status = "completed" if ok else ("failed" if log.get("errors") else "partial")

        tasks.append({
            "id": run_id,
            "title": f"{log.get('tool_name') or tool_code}",
            "agent": "ai_factory",
            "type": "tool_pipeline",
            "status": status,
            "priority": 10,
            "total": steps_total,
            "done": steps_done,
            "progress_pct": progress if status != "completed" else 100,
            "tool_code": tool_code,
            "command": "POST /api/ai-factory/run",
            "link": "/ai-factory",
            "source": "ai_factory_log",
            "updated_at": _now(),
            "resolved_codes": [tool_code] if tool_code and ok else [],
            "result_summary": f"{steps_done}/{steps_total} agentes",
        })
        seen_ids.add(run_id)

    tasks.sort(key=lambda t: (t.get("status") != "pending", t.get("priority", 99), t.get("title", "")))

    data = {
        "schema_version": "2026.3.6",
        "entity": "TaskRegistry",
        "synced_at": _now(),
        "inventory_summary": inv.get("summary"),
        "tasks": tasks,
    }
    save_registry(data)
    return data


def list_tasks(*, status: str | None = None, limit: int = 500) -> dict:
    reg = load_registry()
    if not reg.get("tasks"):
        reg = sync_registry()
    tasks = reg.get("tasks", [])
    if status and status != "all":
        if status == "completed":
            tasks = [t for t in tasks if t.get("status") in ("completed", "partial")]
        elif status == "active":
            tasks = [t for t in tasks if t.get("status") in ("pending", "running")]
        else:
            tasks = [t for t in tasks if t.get("status") == status]
    summary = {
        "pending": sum(1 for t in reg.get("tasks", []) if t.get("status") == "pending"),
        "running": sum(1 for t in reg.get("tasks", []) if t.get("status") == "running"),
        "completed": sum(1 for t in reg.get("tasks", []) if t.get("status") in ("completed", "partial")),
        "failed": sum(1 for t in reg.get("tasks", []) if t.get("status") == "failed"),
        "total": len(reg.get("tasks", [])),
    }
    if summary["total"]:
        summary["overall_progress_pct"] = round(
            sum(t.get("progress_pct", 0) for t in reg.get("tasks", [])) / summary["total"],
            1,
        )
    else:
        summary["overall_progress_pct"] = 0

    return {
        "synced_at": reg.get("synced_at"),
        "summary": summary,
        "tasks": tasks[:limit],
    }


def update_task(task_id: str, *, status: str | None = None, progress_pct: float | None = None,
                resolved_codes: list[str] | None = None, done: int | None = None) -> dict:
    reg = load_registry()
    for t in reg.get("tasks", []):
        if t.get("id") == task_id:
            if status:
                t["status"] = status
                if status == "completed":
                    t["progress_pct"] = 100
                    t["completed_at"] = _now()
            if progress_pct is not None:
                t["progress_pct"] = progress_pct
            if done is not None:
                t["done"] = done
            if resolved_codes is not None:
                t["resolved_codes"] = list(set(t.get("resolved_codes", []) + resolved_codes))
            t["updated_at"] = _now()
            save_registry(reg)
            return {"ok": True, "task": t}
    return {"ok": False, "error": "task_not_found"}


def mark_running(task_id: str) -> None:
    update_task(task_id, status="running", progress_pct=5)


def complete_task(task_id: str, *, resolved_codes: list[str] | None = None, summary: str = "") -> dict:
    reg = load_registry()
    for t in reg.get("tasks", []):
        if t.get("id") == task_id:
            t["status"] = "completed"
            t["progress_pct"] = 100
            t["done"] = t.get("total", 1)
            t["completed_at"] = _now()
            if resolved_codes:
                t["resolved_codes"] = list(set(t.get("resolved_codes", []) + resolved_codes))
            if summary:
                t["result_summary"] = summary
            t["updated_at"] = _now()
            save_registry(reg)
            return {"ok": True, "task": t}
    return {"ok": False, "error": "task_not_found"}
