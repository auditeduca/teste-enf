"""Registro Master Data — conteúdos pendentes."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CONTENT_DIR = ROOT / "datasets" / "master-data" / "content-pending"
DATASETS = ROOT / "datasets"


def load_json(name: str) -> dict:
    return json.loads((CONTENT_DIR / name).read_text(encoding="utf-8"))


def canonical() -> dict:
    return load_json("canonical.json")


def content_types() -> dict:
    return load_json("content_types.json")


def field_docs() -> dict:
    return load_json("field_documentation.json")


def modules() -> dict:
    return load_json("modules.json")


def pending_items() -> dict:
    return load_json("pending_items.json")


def fields_by_type(type_code: str) -> list[dict]:
    prefix = f"CONTENT.{type_code}."
    return [f for f in field_docs()["fields"] if f["field_id"].startswith(prefix)]


def fields_by_module(module_key: str) -> list[dict]:
    return [f for f in field_docs()["fields"] if f.get("module") == module_key]


def get_field(field_id: str) -> dict:
    for f in field_docs()["fields"]:
        if f["field_id"] == field_id:
            return f
    raise KeyError(f"Campo desconhecido: {field_id}")
