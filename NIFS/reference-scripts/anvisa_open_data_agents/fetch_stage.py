"""Etapa fetch — download CSV oficial ANVISA."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from agent_common.anvisa_fetch import cache_csv_fetch  # noqa: E402
from config import ANV_DIR, SCRAPE_CACHE, SCRAPE_SOURCES  # noqa: E402

# Limite por dataset (bytes) — VigiMed ~117MB; amostra inicial 50MB
MAX_BYTES_BY_SOURCE = {
    "ANV.VIGIMED_MEDICAMENTOS": 50_000_000,
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_sources() -> list[dict]:
    return json.loads(SCRAPE_SOURCES.read_text(encoding="utf-8")).get("sources", [])


def fetch_source(source: dict, *, verify_ssl: bool = True) -> dict:
    sid = source["source_id"]
    max_bytes = MAX_BYTES_BY_SOURCE.get(sid)
    return cache_csv_fetch(
        SCRAPE_CACHE,
        sid,
        source["url"],
        max_bytes=max_bytes,
        verify_ssl=verify_ssl,
    )


def fetch_all(
    *,
    limit: int | None = None,
    only_stale: bool = False,
    priority_only: bool = True,
    verify_ssl: bool = True,
) -> dict:
    from discover import discover  # noqa: WPS433

    disc = discover(limit=limit, priority_only=priority_only) if only_stale else None
    stale_ids = {s["source_id"] for s in (disc or {}).get("stale_sources", [])}
    sources = _load_sources()
    if priority_only:
        pri = [s for s in sources if s.get("priority") == 1]
        sources = pri or sources[:5]
    if limit:
        sources = sources[:limit]
    if only_stale and stale_ids:
        sources = [s for s in sources if s["source_id"] in stale_ids]
    results = [fetch_source(s, verify_ssl=verify_ssl) for s in sources]
    ok = sum(1 for r in results if r.get("ok"))
    report = {
        "generated_at": _now(),
        "total": len(results),
        "fetched_ok": ok,
        "results": results,
    }
    out = ANV_DIR / "fetch_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["report_path"] = str(out)
    return report
