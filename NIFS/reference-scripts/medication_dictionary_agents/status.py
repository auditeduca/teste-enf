"""Status consolidado — dicionário de medicamentos vinculado a DrugReference."""
from __future__ import annotations

import json
from pathlib import Path

from config import DRUG_REFS, MD_DIR, OUTPUT, QUEUE_PATH

ROOT = Path(__file__).resolve().parent.parent.parent


def _load(path: Path) -> dict:
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        obj, _ = json.JSONDecoder().raw_decode(text.lstrip("\ufeff"))
        return obj if isinstance(obj, dict) else {}


def collect_status() -> dict:
    from catalog import queue_stats  # noqa: WPS433

    stats = queue_stats()
    queue = _load(QUEUE_PATH)
    canonical = _load(MD_DIR / "canonical.json")
    doc = _load(OUTPUT)

    return {
        "program_code": canonical.get("program_code", "MEDICATION_DICTIONARY"),
        "parent_entity_type": "DrugReference",
        "parent_id_field": "drug_ref_code",
        "code_pattern": canonical.get("code_pattern", "{CONCEPT}_DICT_{NNN}"),
        "dataset": str(OUTPUT.relative_to(ROOT)),
        "source_catalog": canonical.get("source_catalog"),
        "total_drug_references": stats["total_drug_references"],
        "linked": stats["linked"],
        "with_definition": stats["with_definition"],
        "pending": stats["pending"],
        "completion_pct": stats["completion_pct"],
        "queue_total": queue.get("total", stats["pending"]),
        "queue_generated_at": queue.get("generated_at"),
        "records": doc.get("count", len(doc.get("records", []))),
        "single_command": "python scripts/medication_dictionary_agents/run_batch.py --limit 10",
    }
