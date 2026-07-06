"""Estatísticas consolidadas."""
from __future__ import annotations

import json
from pathlib import Path

from config import BL_DIR, CORPUS, DOMAINS, INSTRUMENTS, PROVISIONS, TOOL_LINKS


def _load(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def pipeline_stats() -> dict:
    disc = _load(BL_DIR / "discover_report.json")
    fetch = _load(BL_DIR / "fetch_report.json")
    extract = _load(BL_DIR / "extract_report.json")
    return {
        "domains": len(_load(DOMAINS).get("records", [])),
        "instruments": len(_load(INSTRUMENTS).get("records", [])),
        "corpus_entries": len(_load(CORPUS).get("records", [])),
        "provisions": len(_load(PROVISIONS).get("records", [])),
        "tool_links": len(_load(TOOL_LINKS).get("records", [])),
        "discover_stale": disc.get("stale"),
        "last_fetch_ok": fetch.get("fetched_ok"),
        "last_extract_articles": extract.get("articles_extracted"),
    }
