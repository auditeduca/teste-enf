"""Pipeline sync_catalog → discover → fetch → extract → structure → relate → validate → apply."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent_common.sanitize import sanitize_agent_result  # noqa: E402
from apply_entry import apply_records  # noqa: E402
from catalog import sync_catalog  # noqa: E402
from discover import discover  # noqa: E402
from extract import extract_all  # noqa: E402
from fetch_stage import fetch_all  # noqa: E402
from relate import run_relate  # noqa: E402
from structure import structure_from_extract_report  # noqa: E402
from validate_program import run_validation  # noqa: E402

STAGES = (
    "sync_catalog", "discover", "fetch", "extract",
    "structure", "relate", "validate", "apply",
)


def run_pipeline(
    *,
    limit: int | None = 5,
    only_stale: bool = True,
    skip_fetch: bool = False,
    sync_catalog_first: bool = True,
    apply: bool = True,
    verify_ssl: bool = True,
) -> dict:
    steps: dict = {}

    if sync_catalog_first:
        steps["sync_catalog"] = sync_catalog(verify_ssl=verify_ssl)

    steps["discover"] = discover(limit=limit, priority_only=True)
    if not skip_fetch:
        steps["fetch"] = fetch_all(
            limit=limit,
            only_stale=only_stale,
            priority_only=True,
            verify_ssl=verify_ssl,
        )
    steps["extract"] = extract_all(limit=limit, priority_only=True)
    structured = structure_from_extract_report(limit=limit)
    steps["structure"] = {
        "medications": len(structured.get("medications", [])),
        "prices": len(structured.get("prices", [])),
        "restrictions": len(structured.get("restrictions", [])),
        "catalog": len(structured.get("catalog", [])),
    }
    steps["relate"] = run_relate(medications=structured.get("medications"))

    validation = run_validation()
    steps["validate"] = {
        "ok": validation.ok,
        "errors": validation.errors[:20],
        "warnings": validation.warnings[:10],
    }

    apply_result = {}
    if apply:
        apply_result = apply_records(
            catalog=structured.get("catalog"),
            medications=structured.get("medications"),
            prices=structured.get("prices"),
            restrictions=structured.get("restrictions"),
            tool_links=steps["relate"].get("new_links"),
        )
    steps["apply"] = apply_result

    return sanitize_agent_result({
        "ok": validation.ok or bool(structured.get("medications")),
        "stages": steps,
        "pipeline": list(STAGES),
        "medications_structured": len(structured.get("medications", [])),
        "links_matched": steps["relate"].get("links_matched", 0),
    })
