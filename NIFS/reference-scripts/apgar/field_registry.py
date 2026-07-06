"""Registro de campos APGAR — carrega canonical + field_documentation."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
APGAR_DIR = ROOT / "datasets" / "master-data" / "apgar"
DATASETS = ROOT / "datasets"


def load_json(name: str) -> dict:
    return json.loads((APGAR_DIR / name).read_text(encoding="utf-8"))


def canonical() -> dict:
    return load_json("canonical.json")


def field_docs() -> dict:
    return load_json("field_documentation.json")


def modules() -> dict:
    return load_json("modules.json")


def fields_by_module(module_id: str) -> list[dict]:
    prefix = module_id.replace("M1_", "").replace("M2_", "").split("_")[0]
    mod_map = {
        "M1_identity": "identity",
        "M2_clinical_instrument": "clinical_instrument",
        "M3_ui_fields": "clinical_instrument",
        "M4_catalog": "catalog",
        "M5_graph": "graph",
        "M6_engine": "engine",
        "M7_evidence": "evidence",
        "M8_i18n": "i18n",
        "M9_agents": "graph",
        "M10_ci_gate": "identity",
    }
    key = mod_map.get(module_id, prefix)
    return [f for f in field_docs()["fields"] if f.get("module") == key or f.get("module", "").startswith(key)]
