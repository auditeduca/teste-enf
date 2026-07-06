"""Registro master-data site-full."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SITE_DIR = ROOT / "datasets" / "master-data" / "site-full"


def load_json(name: str) -> dict:
    return json.loads((SITE_DIR / name).read_text(encoding="utf-8"))


def manifest() -> dict:
    return load_json("site_manifest.json")


def field_docs() -> dict:
    return load_json("field_documentation.json")


def modules() -> list[dict]:
    return manifest().get("modules", [])


def module_by_id(module_id: str) -> dict | None:
    for m in modules():
        if m.get("id") == module_id or m.get("code") == module_id:
            return m
    return None


def get_field(field_id: str) -> dict:
    for f in field_docs().get("fields", []):
        if f["field_id"] == field_id:
            return f
    raise KeyError(field_id)
