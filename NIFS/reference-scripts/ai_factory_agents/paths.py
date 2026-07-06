"""Paths and loaders — Nursing AI Factory."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parent.parent.parent
MD = ROOT / "datasets" / "master-data" / "ai-factory"
LOGS = MD / "logs"
TASKS_PATH = MD / "ai_tasks.json"


def load_json(name: str) -> dict:
    return json.loads((MD / name).read_text(encoding="utf-8"))


def canonical() -> dict:
    return load_json("canonical.json")


def agents_registry() -> dict:
    return load_json("agents_registry.json")


def workflows() -> dict:
    return load_json("workflows.json")


def prompts_registry() -> dict:
    return load_json("prompts_registry.json")


def rules_engine() -> dict:
    return load_json("rules_engine.json")


def evaluations_schema() -> dict:
    return load_json("evaluations_schema.json")


def knowledge_sources() -> dict:
    return load_json("knowledge_sources.json")


def load_tasks() -> dict:
    if not TASKS_PATH.exists():
        return {"schema_version": "2026.3.4", "entity": "AiTask", "count": 0, "records": []}
    return json.loads(TASKS_PATH.read_text(encoding="utf-8"))


def save_tasks(data: dict) -> None:
    data["count"] = len(data.get("records", []))
    TASKS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_task(record: dict) -> dict:
    data = load_tasks()
    record.setdefault("task_id", f"TASK.{uuid4().hex[:12].upper()}")
    record.setdefault("created_at", datetime.now(timezone.utc).isoformat())
    data.setdefault("records", []).append(record)
    save_tasks(data)
    return record


def append_log(workflow_run_id: str, payload: dict) -> Path:
    LOGS.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    path = LOGS / f"{workflow_run_id}_{ts}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def resolve_knowledge_source(source_id: str) -> dict | None:
    for s in knowledge_sources().get("sources", []):
        if s["source_id"] == source_id:
            p = ROOT / s["path"]
            return {**s, "exists": p.exists()}
    return None
