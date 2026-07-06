"""Paths — Database Sync Agent."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from config import MD, ROOT

LOGS = MD / "logs"
BUNDLES = MD / "bundles"
SCHEMA_OUT = MD / "supabase_schema.sql"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(name: str) -> dict:
    p = MD / name
    if not p.is_file():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def resolve_prompt(prompt_id: str) -> str:
    """Carrega prompt e injeta ANTI_HALLUCINATION_RULES."""
    reg = load_json("prompts_registry.json")
    anti = ""
    for p in reg.get("prompts", []):
        if p.get("prompt_id") == "ANTI_HALLUCINATION_RULES":
            anti = p.get("template", "")
            break
    for p in reg.get("prompts", []):
        if p.get("prompt_id") == prompt_id:
            tpl = p.get("template", "")
            return tpl.replace("{{ANTI_HALLUCINATION_RULES}}", anti)
    return ""


def save_json(name: str, data: dict) -> Path:
    MD.mkdir(parents=True, exist_ok=True)
    p = MD / name
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return p


def append_log(run_id: str, payload: dict) -> Path:
    LOGS.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    path = LOGS / f"{run_id}_{ts}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def last_log() -> dict | None:
    if not LOGS.is_dir():
        return None
    files = sorted(LOGS.glob("SYNC.*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not files:
        return None
    return json.loads(files[0].read_text(encoding="utf-8"))
