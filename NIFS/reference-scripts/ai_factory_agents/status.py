"""Status — Nursing AI Factory."""
from __future__ import annotations

from paths import (
    MD,
    agents_registry,
    canonical,
    evaluations_schema,
    knowledge_sources,
    load_tasks,
    prompts_registry,
    rules_engine,
    workflows,
)


def collect_status() -> dict:
    reg = agents_registry()
    agents = reg.get("agents", [])
    phase1 = reg.get("phase1_priority", [])
    wf = workflows().get("workflows", {})
    tasks = load_tasks()
    kb = knowledge_sources().get("sources", [])

    kb_resolved = []
    for s in kb:
        from paths import ROOT
        kb_resolved.append({**s, "exists": (ROOT / s["path"]).exists()})

    return {
        "program": canonical().get("program_code", "NAIF"),
        "name": canonical().get("name"),
        "mode": canonical().get("mode", "internal"),
        "pipeline": canonical().get("pipeline", []),
        "agents_total": len(agents),
        "agents_phase1": len(phase1),
        "agents_mvp": sum(1 for a in agents if a.get("status") == "mvp"),
        "workflows": list(wf.keys()),
        "prompts": len(prompts_registry().get("prompts", [])),
        "rules": len(rules_engine().get("rules", [])),
        "knowledge_sources": len(kb),
        "knowledge_sources_ready": sum(1 for s in kb_resolved if s.get("exists")),
        "tasks_completed": tasks.get("count", 0),
        "phase1_agents": phase1,
        "evaluation_types": list(evaluations_schema().get("evaluation_types", {}).keys()),
        "master_data_path": str(MD),
        "platform_route": canonical().get("platform_route"),
    }
