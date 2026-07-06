"""Persiste entrada NC aprovada."""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from config import OUTPUT, ROOT

ARCHIVE = ROOT / "datasets" / "_archive_temp"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_output() -> dict:
    if OUTPUT.is_file():
        return json.loads(OUTPUT.read_text(encoding="utf-8"))
    return {
        "schema_version": "2026.2.9",
        "entity": "CompulsoryNotificationEntry",
        "parent_entity_type": "LegislationInstrument",
        "code_pattern": "{CONCEPT}_NC_{NNN}",
        "count": 0,
        "records": [],
    }


def apply_entry(entry: dict) -> dict:
    doc = _load_output()
    records = doc.setdefault("records", [])

    if OUTPUT.is_file():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        dest = ARCHIVE / stamp / "datasets" / "regulatory" / "br" / "compulsory_notifications.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(OUTPUT, dest)

    entity_code = entry["entity_code"]
    records = [r for r in records if r.get("entity_code") != entity_code]
    record = {
        **entry,
        "updated_at": _now(),
        "status": entry.get("status") or "published",
        "content_source": entry.get("content_source") or "COMPULSORY_NOTIFICATION_AGENT",
    }
    if "created_at" not in record:
        record["created_at"] = _now()
    records.append(record)
    doc["records"] = records
    doc["count"] = len(records)
    doc["generated_at"] = _now()
    OUTPUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"entity_code": entity_code, "dataset": str(OUTPUT.relative_to(ROOT))}
