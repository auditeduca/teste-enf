"""Etapa discover — detecta fontes desatualizadas vs cache."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from config import BL_DIR, SCRAPE_CACHE, SCRAPE_SOURCES


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def discover(*, limit: int | None = None) -> dict:
    sources = _load_json(SCRAPE_SOURCES).get("sources", [])
    if limit:
        sources = sources[:limit]
    stale = []
    fresh = []
    for src in sources:
        sid = src["source_id"]
        cache_path = SCRAPE_CACHE / f"{sid.replace('.', '_')}.json"
        entry = {"source_id": sid, "parent_entity_code": src.get("parent_entity_code"), "url": src.get("url")}
        if not cache_path.is_file():
            entry["reason"] = "no_cache"
            stale.append(entry)
            continue
        cached = _load_json(cache_path)
        if not cached.get("ok"):
            entry["reason"] = "last_fetch_failed"
            stale.append(entry)
        else:
            entry["last_modified"] = cached.get("last_modified")
            entry["cached_at"] = cached.get("fetched_at")
            fresh.append(entry)
    report = {
        "generated_at": _now(),
        "total": len(sources),
        "stale": len(stale),
        "fresh": len(fresh),
        "stale_sources": stale,
        "fresh_sources": fresh,
    }
    out = BL_DIR / "discover_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
