"""Pipeline discover → fetch → extract → structure → relate → validate → apply."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "apgar_agents"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_common.sanitize import sanitize_agent_result  # noqa: E402
from apply_entry import apply_records  # noqa: E402
from discover import discover  # noqa: E402
from extract import extract_all  # noqa: E402
from fetch_stage import fetch_all  # noqa: E402
from relate import run_relate  # noqa: E402
from structure import structure_from_extract_report  # noqa: E402
from validate_program import run_validation  # noqa: E402

STAGES = ("discover", "fetch", "extract", "structure", "relate", "validate", "apply")


def run_pipeline(
    *,
    limit: int | None = 10,
    only_stale: bool = True,
    skip_fetch: bool = False,
    apply: bool = True,
) -> dict:
    steps = {}

    steps["discover"] = discover(limit=limit)
    if not skip_fetch:
        steps["fetch"] = fetch_all(limit=limit, only_stale=only_stale)
    steps["extract"] = extract_all(limit=limit)
    structured = structure_from_extract_report(limit=limit)
    steps["structure"] = {
        "corpus_count": len(structured.get("corpus", [])),
        "provisions_count": len(structured.get("provisions", [])),
    }
    steps["relate"] = run_relate()

    validation = run_validation()
    steps["validate"] = {
        "ok": validation.ok,
        "errors": validation.errors[:20],
        "warnings": validation.warnings[:10],
    }

    apply_result = {}
    if apply and validation.ok:
        apply_result = apply_records(
            corpus=structured.get("corpus"),
            provisions=structured.get("provisions"),
            tool_links=steps["relate"].get("new_links"),
        )
    elif apply and structured.get("provisions"):
        apply_result = apply_records(
            corpus=structured.get("corpus"),
            provisions=structured.get("provisions"),
        )
    steps["apply"] = apply_result

    return sanitize_agent_result({
        "ok": validation.ok,
        "stages": steps,
        "pipeline": list(STAGES),
        "provisions_structured": len(structured.get("provisions", [])),
        "corpus_updated": len(structured.get("corpus", [])),
    })
