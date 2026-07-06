"""Executa tarefas do Task Center."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = ROOT / "scripts"


def _py(*parts: str) -> list[str]:
    return [sys.executable, str(SCRIPTS / parts[0])] + list(parts[1:])


def run_task(task_id: str, *, use_llm: bool = False, limit: int = 10) -> dict:
    from registry import AGENT_LABELS, complete_task, list_tasks, mark_running, sync_registry

    sync_registry()
    tasks = list_tasks(status="all").get("tasks", [])
    task = next((t for t in tasks if t.get("id") == task_id), None)
    if not task:
        return {"ok": False, "error": "task_not_found", "task_id": task_id}

    agent = task.get("agent", "")
    mark_running(task_id)

    try:
        if task_id.startswith("PROG."):
            return _run_program(agent, task_id, use_llm=use_llm, limit=limit)
        if task.get("type") == "tool_pipeline" and task.get("tool_code"):
            return _run_tool(task["tool_code"], task_id)
        if task.get("agent") == "ai_factory" and task.get("tool_code"):
            return _run_tool(task["tool_code"], task_id)
        if task.get("type") == "graph_phase":
            return _run_graph_phase(task, task_id, use_llm=use_llm, limit=limit)
        return {"ok": False, "error": "unsupported_task_type", "task": task}
    except Exception as exc:
        from registry import update_task
        update_task(task_id, status="failed")
        return {"ok": False, "error": str(exc)[:500], "task_id": task_id}


def _run_program(agent: str, task_id: str, *, use_llm: bool, limit: int) -> dict:
    from registry import complete_task

    cmd_map = {
        "medication_dictionary": _py("medication_dictionary_agents/run_batch.py", "--all-pending", *(["--llm"] if use_llm else [])),
        "compulsory_notifications": _py("compulsory_notification_agents/run_batch.py", "--scrape", "--catalog"),
        "brazilian_legislation": _py("brazilian_legislation_agents/run_batch.py", "--refresh", "--all-sources"),
        "anvisa_open_data": _py("anvisa_open_data_agents/run_batch.py", "--monthly"),
        "global_expansion": _py("global_expansion_agents/run_global.py", "--all", "--rebuild"),
        "library_assets": _py("resource_expansion/sync_library_assets.py", f"--limit={limit}"),
        "content_workflows": _py("content/workflow_runner.py", "--retry-failed"),
        "content_pending": _py("content_agents/run_field_pipeline.py", *(["--llm"] if use_llm else [])),
        "indicators": _py("resource_expansion/build_nursing_indicators.py"),
        "user_profiles": _py("global_expansion/build_user_profiles.py"),
    }
    cmd = cmd_map.get(agent)
    if not cmd:
        if agent == "user_profiles":
            complete_task(task_id, summary="Marcado concluído (sem runner dedicado)")
            return {"ok": True, "task_id": task_id, "note": "marked_complete"}
        return {"ok": False, "error": f"no_runner_for_{agent}"}

    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=7200)
    ok = proc.returncode == 0
    if ok:
        complete_task(task_id, summary=(proc.stdout or "")[-200:])
    else:
        from registry import update_task
        update_task(task_id, status="failed")
    return {
        "ok": ok,
        "task_id": task_id,
        "agent": agent,
        "returncode": proc.returncode,
        "stdout_tail": "\n".join((proc.stdout or "").splitlines()[-8:]),
        "stderr_tail": "\n".join((proc.stderr or "").splitlines()[-8:]),
    }


def _run_tool(tool_code: str, task_id: str) -> dict:
    sys.path.insert(0, str(SCRIPTS / "ai_factory_agents"))
    from workflow_runner import run_workflow  # noqa: WPS433
    from registry import complete_task

    result = run_workflow(tool_code=tool_code, tool_name=tool_code.replace("TOOL.", ""), phase1_only=True)
    if result.get("ok"):
        complete_task(task_id, resolved_codes=[tool_code], summary=result.get("result_summary", "Pipeline OK"))
    else:
        from registry import update_task
        update_task(task_id, status="partial")
    return {"ok": result.get("ok"), "task_id": task_id, "result": result}


def _graph_phase_cmd(task: dict, *, use_llm: bool, limit: int) -> list[str] | None:
    """Mapeia fase GI → CLI (subprocess evita shadow de task_center/paths.py)."""
    api = (task.get("command") or "").lower()
    tid = (task.get("id") or "").upper()
    cmd = _py("graph_intelligence_agents/run_batch.py")
    llm_flag = [] if use_llm else ["--no-llm"]

    if "inventory" in api or tid == "GI.P1_INVENTORY":
        return cmd + ["--inventory"]
    if "fast-screen" in api or tid == "GI.P2_STRUCTURAL":
        return cmd + ["--fast-screen"] + llm_flag
    if "validate" in api or tid == "GI.P3_CLINICAL":
        return cmd + ["--validate"] + llm_flag
    if "generate-content" in api or tid == "GI.P4_CONTENT":
        return cmd + ["--phase-content-batch", f"--limit={limit}"] + llm_flag
    if "cross-tool" in api or tid == "GI.P5_CROSS_TOOL":
        return cmd + ["--phase-cross-batch", f"--limit={limit}"] + llm_flag
    if "structural" in api:
        return cmd + ["--structural"]
    return None


def _run_graph_phase(task: dict, task_id: str, *, use_llm: bool, limit: int = 10) -> dict:
    from registry import complete_task, update_task

    cmd = _graph_phase_cmd(task, use_llm=use_llm, limit=limit)
    if not cmd:
        return {
            "ok": False,
            "error": "unknown_graph_api",
            "task_id": task_id,
            "command": task.get("command"),
        }

    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=7200)
    ok = proc.returncode == 0
    if ok:
        complete_task(task_id, summary=(proc.stdout or "")[-200:])
    else:
        update_task(task_id, status="failed")
    return {
        "ok": ok,
        "task_id": task_id,
        "returncode": proc.returncode,
        "stdout_tail": "\n".join((proc.stdout or "").splitlines()[-8:]),
        "stderr_tail": "\n".join((proc.stderr or "").splitlines()[-8:]),
    }


def run_batch_tasks(task_ids: list[str], *, use_llm: bool = False) -> dict:
    results = []
    for tid in task_ids:
        results.append(run_task(tid, use_llm=use_llm))
    ok = sum(1 for r in results if r.get("ok"))
    return {"ok": ok > 0, "total": len(results), "succeeded": ok, "results": results}
