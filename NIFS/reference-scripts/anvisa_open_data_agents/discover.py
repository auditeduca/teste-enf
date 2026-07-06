"""Etapa discover — fontes desatualizadas (>30 dias ou sem cache)."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from config import ANV_DIR, SCRAPE_CACHE, SCRAPE_SOURCES


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def discover(*, limit: int | None = None, priority_only: bool = True, max_age_days: int = 30) -> dict:
    sources = _load_json(SCRAPE_SOURCES).get("sources", [])
    if priority_only:
        pri = [s for s in sources if s.get("priority") == 1]
        sources = pri or sources[:5]
    if limit:
        sources = sources[:limit]
    stale = []
    fresh = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    for src in sources:
        sid = src["source_id"]
        cache_path = SCRAPE_CACHE / f"{sid.replace('.', '_')}.json"
        entry = {
            "source_id": sid,
            "filename": src.get("filename"),
            "url": src.get("url"),
            "priority": src.get("priority"),
        }
        if not cache_path.is_file():
            entry["reason"] = "no_cache"
            stale.append(entry)
            continue
        cached = _load_json(cache_path)
        if not cached.get("ok"):
            entry["reason"] = "last_fetch_failed"
            stale.append(entry)
            continue
        fetched_at = cached.get("fetched_at")
        try:
            dt = datetime.strptime(fetched_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) if fetched_at else None
        except ValueError:
            dt = None
        if dt and dt < cutoff:
            entry["reason"] = "older_than_30d"
            entry["fetched_at"] = fetched_at
            stale.append(entry)
        else:
            entry["fetched_at"] = fetched_at
            entry["content_hash"] = cached.get("content_hash")
            fresh.append(entry)
    report = {
        "generated_at": _now(),
        "max_age_days": max_age_days,
        "total": len(sources),
        "stale": len(stale),
        "fresh": len(fresh),
        "stale_sources": stale,
        "fresh_sources": fresh,
    }
    out = ANV_DIR / "discover_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
