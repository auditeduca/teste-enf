"""Paths — Nursing Studio."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MD = ROOT / "datasets" / "master-data" / "nursing-studio"
OUT = ROOT / "website" / "assets" / "images" / "studio"
RELATIONS = ROOT / "datasets" / "master" / "entity_relations.json"


def load_json(name: str) -> dict:
    return json.loads((MD / name).read_text(encoding="utf-8"))


def load_dataset(rel: str) -> dict:
    p = ROOT / rel
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def templates() -> list[dict]:
    return load_json("templates_seed.json").get("templates", [])


def formats() -> dict:
    return load_json("social_formats.json").get("formats", {})


def editing_blocks() -> list[dict]:
    return load_json("editing_blocks.json").get("blocks", [])


def graph_relations_for(entity_code: str, limit: int = 30) -> list[dict]:
    rel_path = ROOT / "datasets" / "master" / "entity_relations.json"
    if not rel_path.exists():
        rel_path = ROOT / "datasets" / "master-data" / "entity_relations.json"
    if not rel_path.exists():
        rel_path = ROOT / "datasets" / "clinical" / "entity_relations.json"
    if not rel_path.exists():
        return []
    data = json.loads(rel_path.read_text(encoding="utf-8"))
    records = data.get("records", [])
    code = entity_code.upper()
    out = []
    for r in records:
        src = (r.get("source_code") or r.get("source_entity") or "").upper()
        tgt = (r.get("target_code") or r.get("target_entity") or "").upper()
        if code in src or code in tgt:
            out.append(r)
        if len(out) >= limit:
            break
    return out
