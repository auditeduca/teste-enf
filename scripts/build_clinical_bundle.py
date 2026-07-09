#!/usr/bin/env python3
"""Gera bundles de terminologia clínica para o runtime (Fase 1.2 / 2)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "NIFS" / "reference-datasets"
OUT = ROOT / "NIFS" / "DELIVERY" / "js" / "bundles"

SOURCES = {
    "nanda": (REF / "clinical" / "nursing_diagnoses.json", "nanda_code", "NursingDiagnosis"),
    "nic": (REF / "clinical" / "nursing_interventions.json", "nic_code", "NursingIntervention"),
    "noc": (REF / "clinical" / "nursing_outcomes.json", "noc_code", "NursingOutcome"),
}


def localized_labels(rec: dict) -> dict[str, str]:
    if rec.get("localized_labels"):
        return dict(rec["localized_labels"])
    pt = rec.get("name_pt") or rec.get("name") or ""
    en = rec.get("name") or pt
    return {"pt-BR": pt, "en": en}


def compact_record(rec: dict, code_key: str) -> dict:
    code = rec.get(code_key, "")
    return {
        "code": code,
        "label": localized_labels(rec).get("pt-BR", ""),
        "localized_labels": localized_labels(rec),
        "definition": rec.get("definition", ""),
    }


def build_index(kind: str, path: Path, code_key: str) -> dict[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    index: dict[str, dict] = {}
    for rec in data.get("records", []):
        code = rec.get(code_key)
        if not code:
            continue
        index[str(code).zfill(5) if kind == "nanda" or kind == "noc" else str(code)] = compact_record(
            rec, code_key
        )
    # Apgar usa códigos sem zero à esquerda em alguns lugares — manter ambas chaves
    extra: dict[str, dict] = {}
    for code, item in index.items():
        stripped = code.lstrip("0") or "0"
        if stripped != code:
            extra[stripped] = item
    index.update(extra)
    return index


def write_bundle(lang: str, indexes: dict[str, dict]) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "2026.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "default_locale": "pt-BR",
        "locale": lang,
        "nanda": indexes["nanda"],
        "nic": indexes["nic"],
        "noc": indexes["noc"],
    }
    out_path = OUT / f"clinical-terminology.{lang}.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out_path


def main() -> None:
    indexes = {}
    for kind, (path, code_key, _) in SOURCES.items():
        if not path.is_file():
            raise SystemExit(f"Dataset ausente: {path}")
        indexes[kind] = build_index(kind, path, code_key)
        print(f"  {kind}: {len(indexes[kind])} entradas indexadas de {path.name}")

    out = write_bundle("pt-BR", indexes)
    print(f"Bundle escrito: {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
