"""Raspagem — fontes nacionais e estaduais."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from config import CN_DIR, SCRAPE_SOURCES
from fetch import cache_fetch


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_sources() -> list[dict]:
    if not SCRAPE_SOURCES.is_file():
        return []
    return json.loads(SCRAPE_SOURCES.read_text(encoding="utf-8")).get("sources", [])


def _extract_conditions(text: str) -> list[str]:
    """Heurística: linhas com nomes de agravos em listas oficiais."""
    patterns = [
        r"(?i)(?:^|\n)\s*\d+\s*[|.)\-]?\s*([A-Za-zÀ-ú0-9][^\n|]{4,80})",
        r"(?i)(?:doença|agravo|evento|infecção|acidente|febre|tétano|dengue|hiv|tuberculose)[^\n]{3,60}",
    ]
    found: set[str] = set()
    for pat in patterns:
        for m in re.finditer(pat, text):
            chunk = m.group(1) if m.lastindex else m.group(0)
            chunk = re.sub(r"\s+", " ", chunk).strip(" .|-")
            if 5 <= len(chunk) <= 90 and not chunk.lower().startswith("portaria"):
                found.add(chunk)
    return sorted(found)[:80]


def _extract_portaria_refs(text: str) -> list[str]:
    refs = set()
    for m in re.finditer(
        r"(?i)portaria\s+(?:gm/?ms|ms|gm)\s*n[º°]?\s*([\d.]+)\s*,?\s*de\s*(\d{1,2})[^\d]*(\d{4})",
        text,
    ):
        num, _day, year = m.groups()
        refs.add(f"Portaria GM/MS nº {num}/{year}")
    return sorted(refs)


def scrape_source(source: dict) -> dict:
    sid = source["source_id"]
    url = source["url"]
    fetched = cache_fetch(sid, url)
    text = fetched.get("text") or ""
    return {
        "source_id": sid,
        "parent_entity_code": source.get("parent_entity_code"),
        "jurisdiction_code": source.get("jurisdiction_code"),
        "url": url,
        "fetched_ok": fetched.get("ok", False),
        "error": fetched.get("error"),
        "text_length": len(text),
        "conditions_detected": _extract_conditions(text),
        "portaria_refs": _extract_portaria_refs(text),
        "scraped_at": _now(),
        "cache_path": fetched.get("cache_path"),
    }


def scrape_all(*, limit: int | None = None) -> dict:
    sources = _load_sources()
    if limit:
        sources = sources[:limit]
    results = [scrape_source(s) for s in sources]
    ok = sum(1 for r in results if r.get("fetched_ok"))
    report = {
        "generated_at": _now(),
        "total": len(results),
        "fetched_ok": ok,
        "results": results,
    }
    out = CN_DIR / "scrape_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["report_path"] = str(out)
    return report
