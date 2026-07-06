"""Persistência do workflow de aprovação — conteúdos pendentes."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
WORKFLOW_DIR = ROOT / "datasets" / "master-data" / "content-pending" / "workflow"
INDEX_PATH = WORKFLOW_DIR / "index.json"

STATUSES = (
    "draft",
    "running",
    "awaiting_approval",
    "approved",
    "rejected",
    "applied",
    "failed",
)

STEP_IDS = ("search", "generate", "review", "validate")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ensure_dir() -> None:
    WORKFLOW_DIR.mkdir(parents=True, exist_ok=True)
    if not INDEX_PATH.exists():
        INDEX_PATH.write_text(
            json.dumps({"schema_version": "2026.2.4", "workflows": []}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def _load_index() -> dict:
    _ensure_dir()
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def _save_index(doc: dict) -> None:
    _ensure_dir()
    INDEX_PATH.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def workflow_path(workflow_id: str) -> Path:
    safe = workflow_id.replace("/", "_")
    return WORKFLOW_DIR / f"{safe}.json"


def create_workflow(*, pending_id: str, entity_code: str, artifact_type: str, field_id: str) -> dict:
    _ensure_dir()
    wf_id = f"WF.{pending_id}.{uuid.uuid4().hex[:8]}"
    doc = {
        "workflow_id": wf_id,
        "pending_id": pending_id,
        "entity_code": entity_code,
        "artifact_type": artifact_type,
        "field_id": field_id,
        "status": "draft",
        "steps": [
            {"id": sid, "label_pt": sid, "status": "pending", "summary_pt": None, "at": None}
            for sid in STEP_IDS
        ],
        "proposal": None,
        "review": None,
        "validation": None,
        "trace": [],
        "error": None,
        "created_at": _now(),
        "updated_at": _now(),
    }
    save_workflow(doc)
    return doc


def save_workflow(doc: dict) -> None:
    doc["updated_at"] = _now()
    workflow_path(doc["workflow_id"]).write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    idx = _load_index()
    workflows = [w for w in idx.get("workflows", []) if w.get("workflow_id") != doc["workflow_id"]]
    workflows.insert(
        0,
        {
            "workflow_id": doc["workflow_id"],
            "pending_id": doc.get("pending_id"),
            "entity_code": doc.get("entity_code"),
            "artifact_type": doc.get("artifact_type"),
            "status": doc.get("status"),
            "updated_at": doc["updated_at"],
        },
    )
    idx["workflows"] = workflows[:500]
    _save_index(idx)


def load_workflow(workflow_id: str) -> dict:
    path = workflow_path(workflow_id)
    if not path.exists():
        raise KeyError(f"Workflow não encontrado: {workflow_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def list_workflows(*, status: str | None = None, limit: int = 100) -> list[dict]:
    idx = _load_index()
    items = idx.get("workflows", [])
    if status:
        items = [w for w in items if w.get("status") == status]
    out = []
    for entry in items[:limit]:
        try:
            out.append(load_workflow(entry["workflow_id"]))
        except (KeyError, json.JSONDecodeError):
            continue
    return out


def update_step(workflow: dict, step_id: str, *, status: str, summary_pt: str | None = None) -> dict:
    for step in workflow.get("steps", []):
        if step["id"] == step_id:
            step["status"] = status
            step["summary_pt"] = summary_pt
            step["at"] = _now()
            break
    workflow["status"] = "running" if status == "running" else workflow.get("status", "running")
    save_workflow(workflow)
    return workflow


def attach_pipeline_result(workflow: dict, pipeline_result: dict) -> dict:
    from agent_common.sanitize import sanitize_agent_result

    clean = sanitize_agent_result(pipeline_result)
    trace = clean.get("trace") or []

    summaries = {
        "search": _step_summary(clean.get("search_result"), "Busca concluída"),
        "generate": _step_summary(clean.get("proposal"), "Proposta gerada"),
        "review": _step_summary(clean.get("review"), clean.get("review", {}).get("decision", "review")),
        "validate": _step_summary(
            clean.get("validation"),
            "PASS" if (clean.get("validation") or {}).get("validation_passed") else "FAIL",
        ),
    }

    for step in workflow.get("steps", []):
        sid = step["id"]
        if sid in summaries:
            step["status"] = "done"
            step["summary_pt"] = summaries[sid]
            step["at"] = _now()

    workflow["proposal"] = clean.get("proposal")
    workflow["review"] = clean.get("review")
    workflow["validation"] = clean.get("validation")
    workflow["trace"] = trace
    workflow["llm_enabled"] = clean.get("llm_enabled", False)

    review_decision = (clean.get("review") or {}).get("decision", "revise")
    validation_ok = bool((clean.get("validation") or {}).get("validation_passed"))

    if review_decision == "reject":
        workflow["status"] = "rejected"
    elif validation_ok and review_decision == "approve":
        workflow["status"] = "awaiting_approval"
    else:
        workflow["status"] = "awaiting_approval"

    save_workflow(workflow)
    return workflow


def set_status(workflow_id: str, status: str, *, note: str | None = None) -> dict:
    wf = load_workflow(workflow_id)
    if status not in STATUSES:
        raise ValueError(f"Status inválido: {status}")
    wf["status"] = status
    if note:
        wf["status_note_pt"] = note
    save_workflow(wf)
    return wf


def _step_summary(data: Any, fallback: str) -> str:
    if not data:
        return fallback
    if isinstance(data, dict):
        for key in ("rationale_pt", "notes_pt", "summary_pt", "decision", "mode"):
            val = data.get(key)
            if val:
                return str(val)[:200]
        return fallback
    return str(data)[:200]
