"""Paths for Graph Intelligence agents."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MD = ROOT / "datasets" / "master-data" / "graph-intelligence"
LOGS = MD / "logs"


def load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def criteria() -> dict:
    return load_json(MD / "validation_criteria.json")


def prompts_registry() -> dict:
    return load_json(MD / "prompts_registry.json")


def review_plan() -> dict:
    return load_json(MD / "review_plan.json")


def llm_routing() -> dict:
    return load_json(MD / "llm_routing.json")


def agents_registry() -> dict:
    return load_json(MD / "agents_registry.json")


def entity_relations_path() -> Path:
    for candidate in (
        ROOT / "datasets" / "master" / "entity_relations.json",
        ROOT / "datasets" / "master-data" / "entity_relations.json",
        ROOT / "datasets" / "clinical" / "entity_relations.json",
    ):
        if candidate.is_file():
            return candidate
    return ROOT / "datasets" / "master" / "entity_relations.json"


def clinical_tools() -> list[dict]:
    path = ROOT / "datasets" / "clinical" / "clinical_tools_catalog.json"
    return load_json(path).get("records", [])


def knowledge_nodes() -> list[dict]:
    path = ROOT / "datasets" / "ai" / "knowledge_nodes.json"
    return load_json(path).get("records", [])


def decision_trees() -> list[dict]:
    path = ROOT / "datasets" / "clinical" / "clinical_decision_trees.json"
    return load_json(path).get("records", [])


def safety_rules() -> list[dict]:
    path = ROOT / "datasets" / "clinical" / "safety_rules.json"
    return load_json(path).get("records", [])


def nnn_linkages() -> list[dict]:
    path = ROOT / "datasets" / "clinical" / "nnn_linkages.json"
    return load_json(path).get("records", [])


def prompt_template(prompt_id: str) -> str:
    for p in prompts_registry().get("prompts", []):
        if p.get("prompt_id") == prompt_id:
            return p.get("template", "")
    return ""
