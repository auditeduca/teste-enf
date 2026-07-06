"""Fila editorial — DrugReference sem entrada DICT vinculada."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from config import DRUG_MONO, DRUG_REFS, MD_DIR, OUTPUT, QUEUE_PATH


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def concept_from_drug_code(drug_code: str) -> str:
    code = (drug_code or "").strip().upper()
    if code.startswith("DRUG."):
        code = code[5:]
    return re.sub(r"[^A-Z0-9_]", "_", code)


def entity_code_for_drug(drug_code: str, seq: int = 1) -> str:
    return f"{concept_from_drug_code(drug_code)}_DICT_{seq:03d}"


def _load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        obj, _ = json.JSONDecoder().raw_decode(text.lstrip("\ufeff"))
        return obj if isinstance(obj, dict) else {}


def _monograph_by_ref() -> dict[str, dict]:
    doc = _load_json(DRUG_MONO)
    out = {}
    for rec in doc.get("records", []):
        ref = rec.get("drug_ref_code")
        if ref:
            out[ref] = rec
    return out


def _existing_refs() -> set[str]:
    doc = _load_json(OUTPUT)
    refs = set()
    for rec in doc.get("records", []):
        refs.add(rec.get("drug_ref_code") or rec.get("parent_entity_code") or "")
    return refs - {""}


def build_queue(*, limit: int | None = None) -> dict:
    MD_DIR.mkdir(parents=True, exist_ok=True)
    drugs = _load_json(DRUG_REFS).get("records", [])
    mono_map = _monograph_by_ref()
    have = _existing_refs()

    items = []
    for drug in drugs:
        drug_code = drug.get("drug_code") or ""
        if not drug_code or drug_code in have:
            continue
        concept = concept_from_drug_code(drug_code)
        mono = mono_map.get(drug_code, {})
        items.append({
            "pending_id": f"PEND.{concept}_DICT_001",
            "entity_code": entity_code_for_drug(drug_code),
            "concept_code": concept,
            "parent_entity_code": drug_code,
            "parent_entity_type": "DrugReference",
            "drug_ref_code": drug_code,
            "linked_monograph_code": mono.get("monograph_code"),
            "term_pt": drug.get("generic_name_pt") or drug.get("generic_name") or concept,
            "term_en": drug.get("generic_name"),
            "atc_code": drug.get("atc_code"),
            "pharmacological_class": drug.get("pharmacological_class"),
            "high_alert_medication": bool(drug.get("high_alert")),
            "routes": drug.get("routes") or [],
            "status": "pending",
            "agent_pipeline": ["search", "generate", "review", "validate"],
        })
        if limit and len(items) >= limit:
            break

    doc = {
        "schema_version": "2026.2.9-medication-dictionary-queue",
        "generated_at": _now(),
        "total": len(items),
        "source_count": len(drugs),
        "already_linked": len(have),
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


def queue_stats() -> dict:
    """Estatísticas da fila vs DrugReference pai."""
    drugs = _load_json(DRUG_REFS).get("records", [])
    have = _existing_refs()
    with_def = sum(
        1
        for rec in _load_json(OUTPUT).get("records", [])
        if rec.get("definition_pt") or rec.get("definition")
    )
    total_drugs = len(drugs)
    linked = len(have)
    pending = max(total_drugs - linked, 0)
    return {
        "total_drug_references": total_drugs,
        "linked": linked,
        "with_definition": with_def,
        "pending": pending,
        "completion_pct": round(linked / total_drugs * 100, 1) if total_drugs else 0,
    }


def is_linked(drug_ref_code: str) -> bool:
    return drug_ref_code in _existing_refs()
