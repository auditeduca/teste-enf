"""Paths and loaders — Nursing Professional Intelligence Hub."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MD = ROOT / "datasets" / "master-data" / "professional-intelligence"
REG_BR = ROOT / "datasets" / "regulatory" / "br"
CAREER_PATHS = ROOT / "datasets" / "community" / "career_paths.json"


def load_json(name: str) -> dict:
    return json.loads((MD / name).read_text(encoding="utf-8"))


def canonical() -> dict:
    return load_json("canonical.json")


def tool_professional_context() -> dict:
    return load_json("tool_professional_context.json")


def regulation_categories() -> dict:
    return load_json("regulation_categories.json")


def public_exams() -> dict:
    return load_json("public_exams_seed.json")


def career_maps() -> dict:
    return load_json("career_maps_by_country.json")


def certifications() -> dict:
    return load_json("certifications_registry.json")


def exam_prep_templates() -> dict:
    return load_json("exam_prep_templates.json")


def alert_rules() -> dict:
    return load_json("alert_rules.json")


def legislation_tool_links() -> dict:
    if not (REG_BR / "legislation_tool_links.json").exists():
        return {"links": []}
    return json.loads((REG_BR / "legislation_tool_links.json").read_text(encoding="utf-8"))


def career_paths() -> dict:
    if not CAREER_PATHS.exists():
        return {"paths": []}
    return json.loads(CAREER_PATHS.read_text(encoding="utf-8"))
