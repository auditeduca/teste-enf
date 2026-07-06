"""Catálogo clínico — lista ferramentas para batch na AI Factory."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CATALOG_PATH = ROOT / "datasets" / "clinical" / "clinical_tools_catalog.json"
LOGS_DIR = ROOT / "datasets" / "master-data" / "ai-factory" / "logs"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_catalog_doc() -> dict:
    if not CATALOG_PATH.is_file():
        return {"records": []}
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def load_catalog() -> list[dict]:
    return _load_catalog_doc().get("records", [])


def save_catalog(doc: dict) -> None:
    doc["count"] = len(doc.get("records", []))
    doc["generated_at"] = _now()
    CATALOG_PATH.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _latest_runs_by_tool(limit_files: int = 400) -> dict[str, dict]:
    if not LOGS_DIR.is_dir():
        return {}
    files = sorted(LOGS_DIR.glob("RUN.*.json"), key=lambda f: f.stat().st_mtime, reverse=True)[:limit_files]
    latest: dict[str, dict] = {}
    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        code = data.get("tool_code")
        if not code or code in latest:
            continue
        steps_done = len([s for s in data.get("steps", []) if s.get("status") == "completed"])
        latest[code] = {
            "pipeline_status": "completed" if data.get("ok") else "partial",
            "last_run_id": data.get("run_id"),
            "last_run_at": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "pipeline_steps_completed": steps_done,
        }
    return latest


def mark_pipeline_result(
    tool_code: str,
    *,
    run_id: str,
    ok: bool,
    steps_completed: int,
) -> dict | None:
    """Atualiza catálogo após execução do pipeline."""
    doc = _load_catalog_doc()
    updated = None
    for rec in doc.get("records", []):
        if rec.get("tool_code") != tool_code:
            continue
        pipeline_status = "completed" if ok else "partial"
        rec["pipeline_status"] = pipeline_status
        rec["last_run_id"] = run_id
        rec["last_run_at"] = _now()
        rec["pipeline_steps_completed"] = steps_completed
        if ok and rec.get("status") == "cataloged":
            rec["status"] = "pipeline_completed"
        rec["updated_at"] = _now()
        updated = rec
        break
    if updated:
        save_catalog(doc)
    return updated


def pipeline_stats() -> dict:
    records = load_catalog()
    runs = _latest_runs_by_tool()
    completed = 0
    partial = 0
    pending = 0
    for rec in records:
        code = rec.get("tool_code")
        ps = rec.get("pipeline_status") or runs.get(code, {}).get("pipeline_status") or "pending"
        if ps == "completed":
            completed += 1
        elif ps == "partial":
            partial += 1
        else:
            pending += 1
    return {
        "total": len(records),
        "completed": completed,
        "partial": partial,
        "pending": pending,
    }


def list_tools(
    *,
    search: str = "",
    category: str = "",
    tool_type: str = "",
    status: str = "",
    pipeline_status: str = "",
    limit: int = 500,
    offset: int = 0,
) -> dict:
    records = load_catalog()
    latest_runs = _latest_runs_by_tool()
    q = search.strip().lower()

    def match(rec: dict) -> bool:
        code = rec.get("tool_code")
        run = latest_runs.get(code, {})
        ps = rec.get("pipeline_status") or run.get("pipeline_status") or "pending"
        if category and (rec.get("category") or "") != category:
            return False
        if tool_type and (rec.get("tool_type") or "") != tool_type:
            return False
        if status and (rec.get("status") or "") != status:
            return False
        if pipeline_status and ps != pipeline_status:
            return False
        if not q:
            return True
        blob = " ".join(
            str(rec.get(k, ""))
            for k in ("tool_code", "name", "name_pt", "acronym", "domain", "taxonomy_code")
        ).lower()
        return q in blob

    filtered = [r for r in records if match(r)]
    page = filtered[offset : offset + limit]

    items = []
    for r in page:
        code = r.get("tool_code")
        run = latest_runs.get(code, {})
        ps = r.get("pipeline_status") or run.get("pipeline_status") or "pending"
        items.append({
            "tool_code": code,
            "name": r.get("name") or r.get("name_pt"),
            "acronym": r.get("acronym"),
            "category": r.get("category"),
            "tool_type": r.get("tool_type"),
            "domain": r.get("domain"),
            "taxonomy_code": r.get("taxonomy_code"),
            "status": r.get("status"),
            "pipeline_status": ps,
            "last_run_id": r.get("last_run_id") or run.get("last_run_id"),
            "last_run_at": r.get("last_run_at") or run.get("last_run_at"),
            "pipeline_steps_completed": r.get("pipeline_steps_completed") or run.get("pipeline_steps_completed"),
            "calculator_definition_status": r.get("calculator_definition_status"),
            "brief": f"Enriquecer ferramenta {r.get('name') or code}",
        })

    categories = sorted({r.get("category") for r in records if r.get("category")})
    types = sorted({r.get("tool_type") for r in records if r.get("tool_type")})
    stats = pipeline_stats()

    return {
        "total": len(filtered),
        "count": len(items),
        "offset": offset,
        "limit": limit,
        "catalog_total": len(records),
        "pipeline_stats": stats,
        "categories": categories,
        "tool_types": types,
        "tools": items,
    }


def resolve_tools_by_codes(codes: list[str]) -> list[dict]:
    by_code = {r.get("tool_code"): r for r in load_catalog()}
    out = []
    for code in codes:
        rec = by_code.get(code)
        if rec:
            out.append(rec)
    return out
