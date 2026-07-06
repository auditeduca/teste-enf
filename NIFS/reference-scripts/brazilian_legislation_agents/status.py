"""Status — legislação brasileira consolidada."""
from __future__ import annotations

import json
from pathlib import Path

from catalog import pipeline_stats  # noqa: E402
from config import BL_DIR, ROOT


def collect_status() -> dict:
    canonical = json.loads((BL_DIR / "canonical.json").read_text(encoding="utf-8"))
    stats = pipeline_stats()
    return {
        "program_code": canonical.get("program_code"),
        "pipeline_stages": canonical.get("pipeline_stages"),
        "parent_hierarchy": canonical.get("parent_hierarchy"),
        **stats,
        "single_command": "python scripts/brazilian_legislation_agents/run_batch.py --refresh",
    }
