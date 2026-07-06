"""Etapa fetch — Planalto, BVS, LexML."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

from agent_common.legislation_fetch import cache_fetch, lexml_search  # noqa: E402
from config import BL_DIR, SCRAPE_CACHE, SCRAPE_SOURCES


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_sources() -> list[dict]:
    return json.loads(SCRAPE_SOURCES.read_text(encoding="utf-8")).get("sources", [])


def fetch_source(source: dict) -> dict:
    sid = source["source_id"]
    mode = source.get("fetch_mode", "scrape")
    if mode == "lexml_api":
        kw = source.get("lexml_keyword") or source.get("title", "")
        result = lexml_search(kw)
        result["source_id"] = sid
        result["fetch_mode"] = "lexml_api"
        path = SCRAPE_CACHE / f"{sid.replace('.', '_')}.json"
        SCRAPE_CACHE.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result["cache_path"] = str(path)
        return result
    fetched = cache_fetch(SCRAPE_CACHE, sid, source["url"])
    fetched["fetched_at"] = _now()
    fetched["parent_entity_code"] = source.get("parent_entity_code")
    fetched["domain_code"] = source.get("domain_code")
    path = SCRAPE_CACHE / f"{sid.replace('.', '_')}.json"
    path.write_text(json.dumps(fetched, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return fetched


def fetch_all(*, limit: int | None = None, only_stale: bool = False) -> dict:
    from discover import discover  # noqa: WPS433

    disc = discover(limit=limit) if only_stale else None
    stale_ids = {s["source_id"] for s in (disc or {}).get("stale_sources", [])}
    sources = _load_sources()
    if limit:
        sources = sources[:limit]
    if only_stale and stale_ids:
        sources = [s for s in sources if s["source_id"] in stale_ids]
    results = [fetch_source(s) for s in sources]
    ok = sum(1 for r in results if r.get("ok"))
    report = {
        "generated_at": _now(),
        "total": len(results),
        "fetched_ok": ok,
        "results": results,
    }
    out = BL_DIR / "fetch_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["report_path"] = str(out)
    return report
