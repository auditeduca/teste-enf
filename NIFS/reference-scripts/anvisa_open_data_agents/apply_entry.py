"""Persiste datasets ANVISA normalizados."""
from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from agent_common.json_io import load_json, save_json_atomic  # noqa: E402
from config import BR_OUT, CATALOG_OUT, MEDICATIONS_OUT, PRICES_OUT, RESTRICTIONS_OUT, ROOT as CFG_ROOT  # noqa: E402

ARCHIVE = CFG_ROOT / "datasets" / "_archive_temp"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _archive(path: Path) -> None:
    if path.is_file():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        rel = path.relative_to(CFG_ROOT / "datasets")
        dest = ARCHIVE / stamp / "datasets" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)


def _save_entity(path: Path, *, entity: str, records: list, schema: str) -> int:
    if not records:
        return 0
    _archive(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = load_json(path) if path.is_file() else {}
    merged = {r["entity_code"]: r for r in doc.get("records", [])}
    for item in records:
        merged[item["entity_code"]] = {**item, "updated_at": _now()}
    out = {
        "schema_version": schema,
        "generated_at": _now(),
        "entity": entity,
        "content_source": "ANVISA_OPEN_DATA",
        "organization": "ORG.ANVISA",
        "count": len(merged),
        "records": list(merged.values()),
    }
    save_json_atomic(path, out)
    return len(records)


def apply_records(
    *,
    catalog: list | None = None,
    medications: list | None = None,
    prices: list | None = None,
    restrictions: list | None = None,
    tool_links: list | None = None,
) -> dict:
    applied = {
        "catalog": _save_entity(CATALOG_OUT, entity="AnvisaDataset", records=catalog or [], schema="2026.2.12-anvisa-catalog"),
        "medications": _save_entity(MEDICATIONS_OUT, entity="AnvisaMedicationRecord", records=medications or [], schema="2026.2.12-anvisa-medications"),
        "prices": _save_entity(PRICES_OUT, entity="AnvisaMedicationPrice", records=prices or [], schema="2026.2.12-anvisa-prices"),
        "restrictions": _save_entity(RESTRICTIONS_OUT, entity="AnvisaMedicationRestriction", records=restrictions or [], schema="2026.2.12-anvisa-restrictions"),
    }
    if tool_links:
        links_path = BR_OUT / "drug_reference_links.json"
        applied["drug_links"] = _save_entity(links_path, entity="AnvisaDrugReferenceLink", records=tool_links, schema="2026.2.12-anvisa-links")
    return applied
