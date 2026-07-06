"""Fila editorial — condições detectadas na raspagem ainda não estruturadas."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from config import BASE_LEGISLATION, CN_DIR, OUTPUT, SCRAPE_SOURCES

QUEUE_PATH = CN_DIR / "pending_queue.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def concept_from_name(name: str) -> str:
    s = (name or "").upper()
    s = re.sub(r"[^A-Z0-9]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_")[:48] or "AGRAVO"


def entity_code_for(concept: str, seq: int = 1) -> str:
    return f"{concept}_NC_{seq:03d}"


def _existing_concepts() -> set[str]:
    doc = _load_json(OUTPUT)
    out = set()
    for rec in doc.get("records", []):
        out.add(rec.get("concept_code") or "")
        out.add((rec.get("condition_name_pt") or "").upper())
    return out - {""}


def build_queue(*, limit: int | None = None) -> dict:
    CN_DIR.mkdir(parents=True, exist_ok=True)
    scrape = _load_json(CN_DIR / "scrape_report.json")
    have = _existing_concepts()
    items = []

    for result in scrape.get("results", []):
        parent = result.get("parent_entity_code") or BASE_LEGISLATION
        jur = result.get("jurisdiction_code") or "JUR.BR"
        level = "state" if ".BR." in jur and jur != "JUR.BR" else "national"
        for cond_name in result.get("conditions_detected", []):
            concept = concept_from_name(cond_name)
            if concept in have or cond_name.upper() in have:
                continue
            items.append({
                "pending_id": f"PEND.{concept}_NC_001",
                "entity_code": entity_code_for(concept),
                "concept_code": concept,
                "parent_entity_code": parent,
                "parent_entity_type": "LegislationInstrument",
                "jurisdiction_code": jur,
                "jurisdiction_level": level,
                "condition_name_pt": cond_name,
                "source_id": result.get("source_id"),
                "source_url": result.get("url"),
                "status": "pending",
                "agent_pipeline": ["search", "scrape", "structure", "validate"],
            })
            if limit and len(items) >= limit:
                break
        if limit and len(items) >= limit:
            break

    doc = {
        "schema_version": "2026.2.9-compulsory-notification-queue",
        "generated_at": _now(),
        "total": len(items),
        "already_structured": len(_load_json(OUTPUT).get("records", [])),
        "items": items,
    }
    QUEUE_PATH.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return doc


def get_pending_item(pending_id: str) -> dict | None:
    if not QUEUE_PATH.is_file():
        build_queue()
    for item in _load_json(QUEUE_PATH).get("items", []):
        if item.get("pending_id") == pending_id:
            return item
    return None


def is_structured(concept_code: str) -> bool:
    doc = _load_json(OUTPUT)
    for rec in doc.get("records", []):
        if rec.get("concept_code") == concept_code:
            return True
    return False


def queue_stats() -> dict:
    out_doc = _load_json(OUTPUT)
    records = out_doc.get("records", [])
    national = sum(1 for r in records if r.get("jurisdiction_level") == "national")
    state = sum(1 for r in records if r.get("jurisdiction_level") == "state")
    sources = len(_load_json(SCRAPE_SOURCES).get("sources", []))
    scrape = _load_json(CN_DIR / "scrape_report.json")
    return {
        "total_conditions": len(records),
        "national": national,
        "state": state,
        "scrape_sources": sources,
        "last_scrape_ok": scrape.get("fetched_ok", 0),
        "last_scrape_total": scrape.get("total", 0),
        "queue_pending": _load_json(QUEUE_PATH).get("total", 0) if QUEUE_PATH.is_file() else 0,
    }
