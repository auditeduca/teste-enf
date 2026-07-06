"""Paths — Task Center."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MD = ROOT / "datasets" / "master-data" / "task-center"
REGISTRY = MD / "tasks_registry.json"
ACTIVE_JOB = MD / "active_job.json"


def load_registry() -> dict:
    if not REGISTRY.is_file():
        return {"schema_version": "2026.3.6", "entity": "TaskRegistry", "tasks": []}
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def save_registry(data: dict) -> None:
    MD.mkdir(parents=True, exist_ok=True)
    data["count"] = len(data.get("tasks", []))
    REGISTRY.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
