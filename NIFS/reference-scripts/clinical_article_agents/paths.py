"""Paths and loaders — Clinical Article Factory."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MD = ROOT / "datasets" / "master-data" / "clinical-articles"
ARTICLES_PATH = ROOT / "datasets" / "content" / "editorial" / "articles.json"
TOOLS_PATH = ROOT / "datasets" / "clinical" / "clinical_tools_catalog.json"


def load_json(name: str) -> dict:
    return json.loads((MD / name).read_text(encoding="utf-8"))


def tool_pain_registry() -> dict:
    return load_json("tool_pain_registry.json")


def category_pain_defaults() -> dict:
    return load_json("category_pain_defaults.json")


def soft_skills_registry() -> dict:
    return load_json("soft_skills_registry.json")


def article_template() -> dict:
    return load_json("article_template.json")


def load_tools_catalog() -> list[dict]:
    data = json.loads(TOOLS_PATH.read_text(encoding="utf-8"))
    return data.get("records", [])


def load_articles() -> dict:
    if not ARTICLES_PATH.exists():
        return {"schema_version": "2026.1.0", "entity": "Article", "count": 0, "records": []}
    return json.loads(ARTICLES_PATH.read_text(encoding="utf-8"))


def save_articles(data: dict) -> None:
    data["count"] = len(data.get("records", []))
    ARTICLES_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
