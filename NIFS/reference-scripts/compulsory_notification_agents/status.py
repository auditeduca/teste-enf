"""Status — notificações compulsórias BR."""
from __future__ import annotations

import json
from pathlib import Path

from config import CN_DIR, JURISDICTIONS, LEGISLATION, OUTPUT, ROOT, SCRAPE_SOURCES
from catalog import queue_stats  # noqa: E402


def _load(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def collect_status() -> dict:
    stats = queue_stats()
    canonical = _load(CN_DIR / "canonical.json")
    conditions = _load(OUTPUT)
    return {
        "program_code": canonical.get("program_code", "COMPULSORY_NOTIFICATIONS"),
        "parent_hierarchy": canonical.get("parent_hierarchy"),
        "code_patterns": canonical.get("code_patterns"),
        "jurisdictions": len(_load(JURISDICTIONS).get("records", [])),
        "legislation_instruments": len(_load(LEGISLATION).get("records", [])),
        "conditions_total": stats["total_conditions"],
        "conditions_national": stats["national"],
        "conditions_state": stats["state"],
        "scrape_sources": stats["scrape_sources"],
        "last_scrape_ok": stats["last_scrape_ok"],
        "last_scrape_total": stats["last_scrape_total"],
        "queue_pending": stats["queue_pending"],
        "dataset": str(OUTPUT.relative_to(ROOT)),
        "single_command": "python scripts/compulsory_notification_agents/run_batch.py --scrape --limit 10",
    }
