"""Paths — Nursing Knowledge API."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MD = ROOT / "datasets" / "master-data" / "nursing-knowledge-api"
LOGS = MD / "logs"


def load_json(name: str) -> dict:
    return json.loads((MD / name).read_text(encoding="utf-8"))


def load_dataset(rel: str) -> dict:
    p = ROOT / rel
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def tools_catalog() -> list[dict]:
    return load_dataset("datasets/clinical/clinical_tools_catalog.json").get("records", [])


def calculator_definitions() -> list[dict]:
    return load_dataset("datasets/clinical/calculator_definitions.json").get("records", [])


def articles() -> list[dict]:
    return load_dataset("datasets/content/editorial/articles.json").get("records", [])


def learning_paths() -> list[dict]:
    return load_dataset("datasets/education/learning_paths.json").get("records", [])


def career_paths() -> list[dict]:
    return load_dataset("datasets/community/career_paths.json").get("records", [])


def user_profiles() -> list[dict]:
    return load_dataset("datasets/master-data/global-expansion/user_profiles_registry.json").get("profiles", [])


def resolve_tool_id(tool_id: str) -> dict | None:
    tid = tool_id.strip().upper().replace("-", "_").replace(" ", "_")
    if not tid.startswith("TOOL."):
        slug_map = {
            "BRADEN": "TOOL.BRADEN", "BRADEN_SCALE": "TOOL.BRADEN",
            "GCS": "TOOL.GCS", "GLASgow": "TOOL.GCS", "GLASGOW": "TOOL.GCS",
            "APGAR": "TOOL.APGAR", "INFUSION": "TOOL.INFUSION", "BMI": "TOOL.BMI",
            "MEWS": "TOOL.MEWS", "MORSE": "TOOL.MORSE",
        }
        tid = slug_map.get(tid, f"TOOL.{tid}")
    for t in tools_catalog():
        if t.get("tool_code") == tid or t.get("acronym", "").upper() == tid.replace("TOOL.", ""):
            return t
        if tool_id.lower() in (t.get("name") or "").lower():
            return t
    return None
