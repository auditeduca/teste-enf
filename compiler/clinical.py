from __future__ import annotations

from pathlib import Path

from compiler.io import write_generated_json
from compiler.paths import BUNDLES, REF

SOURCES = {
    "nanda": (REF / "clinical" / "nursing_diagnoses.json", "nanda_code"),
    "nic": (REF / "clinical" / "nursing_interventions.json", "nic_code"),
    "noc": (REF / "clinical" / "nursing_outcomes.json", "noc_code"),
}


def localized_labels(rec: dict) -> dict[str, str]:
    if rec.get("localized_labels"):
        return dict(rec["localized_labels"])
    pt = rec.get("name_pt") or rec.get("name") or ""
    en = rec.get("name") or pt
    return {"pt-BR": pt, "en": en}


def compact_record(rec: dict, code_key: str) -> dict:
    return {
        "code": rec.get(code_key, ""),
        "label": localized_labels(rec).get("pt-BR", ""),
        "localized_labels": localized_labels(rec),
        "definition": rec.get("definition", ""),
    }


def build_index(kind: str, path: Path, code_key: str) -> dict[str, dict]:
    from compiler.io import load_json

    data = load_json(path)
    index: dict[str, dict] = {}
    for rec in data.get("records", []):
        code = rec.get(code_key)
        if not code:
            continue
        key = str(code).zfill(5) if kind in ("nanda", "noc") else str(code)
        index[key] = compact_record(rec, code_key)
    extra: dict[str, dict] = {}
    for code, item in index.items():
        stripped = code.lstrip("0") or "0"
        if stripped != code:
            extra[stripped] = item
    index.update(extra)
    return index


def build_terminology_bundle(locale: str = "pt-BR") -> dict:
    from datetime import datetime, timezone

    indexes: dict[str, dict] = {}
    source_paths: list[str] = []
    for kind, (path, code_key) in SOURCES.items():
        if not path.is_file():
            raise FileNotFoundError(path)
        indexes[kind] = build_index(kind, path, code_key)
        source_paths.append(str(path.relative_to(path.parents[2])))
    payload = {
        "schema_version": "2026.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "default_locale": "pt-BR",
        "locale": locale,
        "nanda": indexes["nanda"],
        "nic": indexes["nic"],
        "noc": indexes["noc"],
    }
    out = BUNDLES / f"clinical-terminology.{locale}.json"
    entry = write_generated_json(
        out,
        payload,
        sources=source_paths,
        artifact_key=f"bundles/clinical-terminology.{locale}.json",
    )
    return entry


def build_tools_catalog() -> dict:
    from datetime import datetime, timezone
    from compiler.io import load_json

    src = REF / "clinical" / "clinical_tools_catalog.json"
    data = load_json(src)
    tools = []
    for rec in data.get("records", []):
        acronym = (rec.get("acronym") or "").lower()
        tools.append(
            {
                "tool_code": rec.get("tool_code"),
                "slug": rec.get("slug") or acronym,
                "name": rec.get("name"),
                "acronym": rec.get("acronym"),
                "category": rec.get("category"),
                "definition_code": rec.get("definition_code"),
            }
        )
    payload = {
        "schema_version": "2026.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "count": len(tools),
        "tools": tools,
    }
    out = BUNDLES / "tools-catalog.json"
    rel_src = str(src.relative_to(REF.parent))
    return write_generated_json(out, payload, sources=[rel_src], artifact_key="bundles/tools-catalog.json")
