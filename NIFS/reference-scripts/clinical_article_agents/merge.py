"""Merge generated articles into editorial/articles.json."""
from __future__ import annotations

from datetime import datetime, timezone

from paths import ARTICLES_PATH, load_articles, save_articles

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def merge_articles(new_records: list[dict], *, replace: bool = True) -> dict:
    data = load_articles()
    existing = {r["article_code"]: i for i, r in enumerate(data.get("records", []))}
    added = 0
    updated = 0
    for rec in new_records:
        code = rec["article_code"]
        if code in existing and replace:
            data["records"][existing[code]] = rec
            updated += 1
        elif code not in existing:
            data["records"].append(rec)
            existing[code] = len(data["records"]) - 1
            added += 1
    data["generated_at"] = NOW
    data["count"] = len(data["records"])
    save_articles(data)
    return {"ok": True, "added": added, "updated": updated, "total": data["count"], "path": str(ARTICLES_PATH)}
