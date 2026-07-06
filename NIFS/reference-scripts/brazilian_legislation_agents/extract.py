"""Etapa extract — artigos e trechos de texto raspado."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from config import BL_DIR, SCRAPE_CACHE


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def extract_articles(text: str, *, parent_entity_code: str) -> list[dict]:
    """Extrai Art. Nº do texto Planalto."""
    if not text:
        return []
    found = []
    pattern = re.compile(
        r"(?i)(Art\.?\s*(?:\d+[\ºo°]?|\d+)[^\n]{0,20})\s*[-–]?\s*([^\n]{20,800})",
    )
    for i, m in enumerate(pattern.finditer(text)):
        label = re.sub(r"\s+", " ", m.group(1)).strip()
        body = re.sub(r"\s+", " ", m.group(2)).strip()
        concept = re.sub(r"[^A-Z0-9]", "_", label.upper())[:40]
        parent_slug = parent_entity_code.replace("LEG.BR.", "").replace(".", "_")
        found.append({
            "entity_code": f"{parent_slug}_{concept}_PROV_{i+1:03d}",
            "concept_code": f"{parent_slug}_{concept}",
            "parent_entity_code": parent_entity_code,
            "parent_entity_type": "LegislationInstrument",
            "article_label": label,
            "title_pt": label,
            "text_pt": body[:1200],
            "extract_mode": "regex_planalto",
        })
        if len(found) >= 40:
            break
    return found


def extract_from_cache(source_id: str, parent_entity_code: str) -> dict:
    path = SCRAPE_CACHE / f"{source_id.replace('.', '_')}.json"
    if not path.is_file():
        return {"source_id": source_id, "ok": False, "error": "cache_miss", "articles": []}
    doc = json.loads(path.read_text(encoding="utf-8"))
    text = doc.get("text") or ""
    articles = extract_articles(text, parent_entity_code=parent_entity_code)
    return {
        "source_id": source_id,
        "parent_entity_code": parent_entity_code,
        "ok": bool(articles),
        "content_hash": _content_hash(text),
        "text_length": len(text),
        "articles": articles,
        "extracted_at": _now(),
    }


def extract_all(*, limit: int | None = None) -> dict:
    from config import SCRAPE_SOURCES  # noqa: WPS433

    sources = json.loads(SCRAPE_SOURCES.read_text(encoding="utf-8")).get("sources", [])
    if limit:
        sources = [s for s in sources if s.get("fetch_mode") != "lexml_api"][:limit]
    results = [
        extract_from_cache(s["source_id"], s["parent_entity_code"])
        for s in sources
        if s.get("fetch_mode") != "lexml_api"
    ]
    total_arts = sum(len(r.get("articles", [])) for r in results)
    report = {
        "generated_at": _now(),
        "sources": len(results),
        "articles_extracted": total_arts,
        "results": results,
    }
    out = BL_DIR / "extract_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
