"""Paths and loaders for Visual Intelligence agents."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MD = ROOT / "datasets" / "master-data" / "visual-intelligence"
OG_OUT = ROOT / "website" / "assets" / "images" / "og"
OG_RETINA = OG_OUT / "retina"


def load_json(name: str) -> dict:
    path = MD / name
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def canonical() -> dict:
    return load_json("canonical.json")


def brand_identity() -> dict:
    return load_json("brand_identity.json")


def og_templates() -> dict:
    return load_json("og_templates.json")


def cultural_rules() -> dict:
    return load_json("cultural_rules.json")


def visual_personas() -> dict:
    return load_json("visual_personas.json")


def scoring_rubric() -> dict:
    return load_json("scoring_rubric.json")


def og_manifest() -> dict:
    path = MD / "og_manifest.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"schema_version": "2026.3.0", "entries": {}}


def save_og_manifest(data: dict) -> Path:
    path = MD / "og_manifest.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    return path
