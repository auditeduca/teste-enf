"""Persiste entrada aprovada em medication_dictionary.json."""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from config import OUTPUT, ROOT
from agent_common.json_io import load_json, save_json_atomic

ARCHIVE = ROOT / "datasets" / "_archive_temp"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_output() -> dict:
    default = {
        "schema_version": "2026.2.9",
        "entity": "MedicationDictionaryEntry",
        "parent_entity_type": "DrugReference",
        "code_pattern": "{CONCEPT}_DICT_{NNN}",
        "count": 0,
        "records": [],
    }
    return load_json(OUTPUT, default=default) if OUTPUT.is_file() else default


def apply_entry(entry: dict) -> dict:
    doc = _load_output()
    records = doc.setdefault("records", [])

    if OUTPUT.is_file():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        dest = ARCHIVE / stamp / "datasets" / "clinical" / "medication_dictionary.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(OUTPUT, dest)

    entity_code = entry["entity_code"]
    records = [r for r in records if r.get("entity_code") != entity_code]
    record = {
        **entry,
        "updated_at": _now(),
        "status": entry.get("status") or "published",
        "content_source": entry.get("content_source") or "MEDICATION_DICT_AGENT",
    }
    if "created_at" not in record:
        record["created_at"] = _now()
    records.append(record)
    doc["records"] = records
    doc["count"] = len(records)
    doc["generated_at"] = _now()
    save_json_atomic(OUTPUT, doc)
    return {"entity_code": entity_code, "dataset": str(OUTPUT.relative_to(ROOT))}
