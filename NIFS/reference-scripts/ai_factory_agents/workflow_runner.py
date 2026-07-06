"""Workflow orchestrator — Nursing AI Factory."""
from __future__ import annotations

from uuid import uuid4

from paths import append_log, append_task, workflows
from phase1_agents import AGENT_RUNNERS

try:
    from catalog import list_tools, resolve_tools_by_codes
except ImportError:
    from ai_factory_agents.catalog import list_tools, resolve_tools_by_codes  # noqa: WPS433


def _parse_tool_from_brief(brief: str) -> tuple[str, str | None]:
    brief = brief.strip()
    tool_name = brief
    tool_code = None
    for prefix in ("Nova calculadora de ", "Nova calculadora ", "Calculadora de ", "Calculadora "):
        if brief.lower().startswith(prefix.lower()):
            tool_name = brief[len(prefix):].strip().rstrip(".")
            break
    if "MEWS" in brief.upper():
        tool_name = "MEWS"
        tool_code = "TOOL.MEWS"
    elif "APGAR" in brief.upper():
        tool_name = "Apgar"
        tool_code = "TOOL.APGAR"
    return tool_name, tool_code


def _tool_page_slug(tool: dict, tool_name: str) -> str:
    acronym = (tool.get("acronym") or "").lower()
    if acronym:
        return acronym
    return tool_name.lower().replace(" ", "-")


def run_workflow(
    brief: str = "",
    *,
    tool_code: str | None = None,
    tool_name: str | None = None,
    tool_record: dict | None = None,
    workflow_id: str = "new_clinical_tool",
    phase1_only: bool = True,
    country: str = "BR",
    persona: str = "profissional",
    persist: bool = True,
) -> dict:
    wf_defs = workflows().get("workflows", {})
    wf = wf_defs.get(workflow_id)
    if not wf:
        return {"ok": False, "error": "workflow_not_found", "available": list(wf_defs.keys())}

    if tool_record:
        tool_code = tool_record.get("tool_code") or tool_code
        tool_name = tool_record.get("name") or tool_record.get("name_pt") or tool_name
    elif tool_code and not tool_name:
        found = resolve_tools_by_codes([tool_code])
        if found:
            tool_record = found[0]
            tool_name = tool_record.get("name") or tool_record.get("name_pt") or tool_code
    elif tool_name and not tool_code:
        tool_code = f"TOOL.{_slug(tool_name)}"
    elif brief.strip():
        tool_name, tool_code = _parse_tool_from_brief(brief)
    else:
        return {"ok": False, "error": "brief_or_tool_code_required"}

    slug = _tool_page_slug(tool_record or {}, tool_name or "")
    if not brief.strip() and tool_name:
        brief = f"Enriquecer ferramenta {tool_name}"
    run_id = f"RUN.{uuid4().hex[:10].upper()}"
    ctx = {
        "brief": brief,
        "tool_name": tool_name,
        "tool_code": tool_code,
        "country": country,
        "persona": persona,
        "page": f"/ferramentas/{slug}",
        "catalog": bool(tool_record),
    }

    steps_out = []
    evaluations = {}
    errors = []

    for step in wf.get("steps", []):
        agent_id = step["agent_id"]
        if phase1_only and not step.get("phase1", False):
            steps_out.append({
                "step": step["step"],
                "agent_id": agent_id,
                "action": step.get("action"),
                "status": "skipped",
                "reason": "phase1_only",
            })
            continue

        runner = AGENT_RUNNERS.get(agent_id)
        if not runner:
            steps_out.append({
                "step": step["step"],
                "agent_id": agent_id,
                "action": step.get("action"),
                "status": "planned",
                "reason": "agent_not_in_phase1",
            })
            continue

        try:
            result = runner(ctx)
            steps_out.append({
                "step": step["step"],
                "agent_id": agent_id,
                "action": step.get("action"),
                "status": result.get("status", "completed"),
                "result": result,
            })
            if result.get("scores"):
                evaluations[agent_id] = result["scores"]
        except Exception as exc:
            errors.append({"agent_id": agent_id, "error": str(exc)})
            steps_out.append({
                "step": step["step"],
                "agent_id": agent_id,
                "status": "failed",
                "error": str(exc),
            })

    all_passed = not errors and len([s for s in steps_out if s.get("status") == "completed"]) >= 1
    payload = {
        "ok": all_passed,
        "run_id": run_id,
        "workflow_id": workflow_id,
        "workflow_name": wf.get("name"),
        "brief": brief,
        "tool_name": tool_name,
        "tool_code": tool_code,
        "phase1_only": phase1_only,
        "steps": steps_out,
        "evaluations": evaluations,
        "errors": errors,
        "estimate": {
            "manual_days": wf.get("estimated_manual_days"),
            "factory_days": wf.get("estimated_factory_days"),
        },
        "human_review_required": True,
    }

    if persist:
        append_task({
            "task_id": run_id,
            "workflow_id": workflow_id,
            "type": "workflow_run",
            "input": {"brief": brief, "country": country},
            "output": payload,
            "status": "completed" if all_passed else "partial",
            "evaluations": evaluations,
        })
        log_path = append_log(run_id, payload)
        payload["log_path"] = str(log_path)
        if tool_code:
            try:
                from catalog import mark_pipeline_result  # noqa: WPS433
            except ImportError:
                from ai_factory_agents.catalog import mark_pipeline_result  # noqa: WPS433
            steps_done = len([s for s in steps_out if s.get("status") == "completed"])
            mark_pipeline_result(
                tool_code,
                run_id=run_id,
                ok=all_passed,
                steps_completed=steps_done,
            )

    return payload


def run_batch(
    tool_codes: list[str] | None = None,
    *,
    all_tools: bool = False,
    limit: int = 10,
    search: str = "",
    category: str = "",
    tool_type: str = "",
    workflow_id: str = "new_clinical_tool",
    phase1_only: bool = True,
    country: str = "BR",
    persona: str = "profissional",
    persist: bool = True,
) -> dict:
    """Executa workflow para várias ferramentas do catálogo — sem digitar brief."""
    if all_tools or not tool_codes:
        listed = list_tools(
            search=search,
            category=category,
            tool_type=tool_type,
            limit=min(limit, 100),
        )
        codes = [t["tool_code"] for t in listed.get("tools", []) if t.get("tool_code")]
    else:
        codes = tool_codes[:limit]

    records = resolve_tools_by_codes(codes)
    if not records:
        return {"ok": False, "error": "no_tools_matched", "requested": len(codes)}

    runs = []
    ok_count = 0
    for rec in records:
        result = run_workflow(
            tool_record=rec,
            workflow_id=workflow_id,
            phase1_only=phase1_only,
            country=country,
            persona=persona,
            persist=persist,
        )
        runs.append({
            "tool_code": rec.get("tool_code"),
            "tool_name": rec.get("name"),
            "ok": result.get("ok"),
            "run_id": result.get("run_id"),
            "steps_completed": len([s for s in result.get("steps", []) if s.get("status") == "completed"]),
        })
        if result.get("ok"):
            ok_count += 1

    return {
        "ok": ok_count > 0,
        "batch": True,
        "total": len(runs),
        "succeeded": ok_count,
        "failed": len(runs) - ok_count,
        "runs": runs,
    }
