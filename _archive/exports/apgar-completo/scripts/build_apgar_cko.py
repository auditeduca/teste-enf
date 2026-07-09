#!/usr/bin/env python3
"""Sincroniza apgar-cko.json e apgar-edges.json a partir dos reference-datasets."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "NIFS" / "reference-datasets"
DELIVERY = ROOT / "NIFS" / "DELIVERY" / "js" / "modules" / "data"
CKO_PATH = DELIVERY / "apgar-cko.json"
EDGES_SRC = REF / "ontology" / "apgar_edges.json"
EDGES_DST = DELIVERY / "apgar-edges.json"
CALC_DEF = REF / "clinical" / "calculator_definitions.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def find_apgar_definition(data: dict):
    items = data.get("records", [])
    for item in items:
        if item.get("definition_code") == "CALC.TOOL.APGAR":
            return item
    return None


def sync_edges() -> None:
    if EDGES_SRC.is_file():
        shutil.copy2(EDGES_SRC, EDGES_DST)
        print("Copiado:", EDGES_DST)


def sync_metadata(cko: dict, definition: dict) -> dict:
    meta = cko.setdefault("metadata", {})
    knowledge = cko.setdefault("knowledge", {})
    knowledge["definition_code"] = definition.get("definition_code", knowledge.get("definition_code"))
    knowledge["tool_code"] = definition.get("tool_code", knowledge.get("tool_code"))
    knowledge["clinical_purpose"] = definition.get("description_pt") or knowledge.get("clinical_purpose")
    if definition.get("score_min") is not None:
        knowledge["score_min"] = definition["score_min"]
    if definition.get("score_max") is not None:
        knowledge["score_max"] = definition["score_max"]
    meta["code"] = definition.get("acronym", meta.get("code", "SCALE-APGAR-001"))
    return cko


def sync_bands(cko: dict, definition: dict) -> dict:
    bands = definition.get("interpretation_bands") or []
    if not bands:
        return cko
    ai = cko.setdefault("ai", {})
    reasoning = []
    for band in bands:
        label = band.get("label_pt") or band.get("label_en") or ""
        action = band.get("action_pt") or band.get("action_en") or ""
        lo, hi = band.get("min"), band.get("max")
        if lo is not None and hi is not None:
            reasoning.append(f"{lo}–{hi}: {label}. {action}".strip())
    if reasoning:
        ai["reasoning"] = reasoning
    return cko


def main() -> None:
    if not CKO_PATH.is_file():
        raise SystemExit(f"CKO base não encontrado: {CKO_PATH}")

    cko = load_json(CKO_PATH)
    sync_edges()

    if CALC_DEF.is_file():
        calc_data = load_json(CALC_DEF)
        definition = find_apgar_definition(calc_data)
        if definition:
            cko = sync_metadata(cko, definition)
            cko = sync_bands(cko, definition)
            print("Metadados sincronizados de CALC.TOOL.APGAR")
        else:
            print("Aviso: CALC.TOOL.APGAR não encontrado em calculator_definitions.json")

    CKO_PATH.write_text(json.dumps(cko, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Atualizado:", CKO_PATH)

    html_data = ROOT / "NIFS" / "DELIVERY" / "html" / "js" / "modules" / "data"
    if html_data.is_dir():
        for name in ("apgar-cko.json", "apgar-edges.json"):
            src = DELIVERY / name
            dst = html_data / name
            if not src.is_file():
                continue
            try:
                shutil.copy2(src, dst)
                print("Copiado para html:", dst)
            except shutil.SameFileError:
                pass


if __name__ == "__main__":
    main()
