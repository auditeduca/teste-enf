"""Status — dados abertos ANVISA."""
from __future__ import annotations

import json
from pathlib import Path

from catalog import pipeline_stats  # noqa: E402
from config import ANV_DIR, ROOT


def collect_status() -> dict:
    canonical = json.loads((ANV_DIR / "canonical.json").read_text(encoding="utf-8"))
    stats = pipeline_stats()
    return {
        "program_code": canonical.get("program_code"),
        "organization": canonical.get("organization"),
        "pipeline_stages": canonical.get("pipeline_stages"),
        "refresh_policy": canonical.get("refresh_policy"),
        **stats,
        "single_command": "python scripts/anvisa_open_data_agents/run_batch.py --monthly",
        "portal_url": canonical.get("organization", {}).get("portal_dados_gov"),
    }
