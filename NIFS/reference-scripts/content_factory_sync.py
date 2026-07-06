"""Sync Content Factory (ContentRequest) from content-pending queue.

Populates datasets/by-country/{CC}/content_requests.json from
datasets/master-data/content-pending/pending_items.json so the kanban
pipeline reflects real editorial work.

Usage:
  python scripts/content_factory_sync.py
  python scripts/content_factory_sync.py --country BR
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from dataset_io import read_envelope, write_envelope
from partition_lib import SUPPORTED_COUNTRIES

ROOT = Path(__file__).resolve().parent.parent
DATASETS = ROOT / "datasets"
PENDING_PATH = DATASETS / "master-data" / "content-pending" / "pending_items.json"

NOW = lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

STATUS_MAP = {
    "pending": "DRAFT",
    "queued": "DRAFT",
    "draft": "DRAFT",
    "search": "GENERATING",
    "generating": "GENERATING",
    "in_progress": "GENERATING",
    "in_review": "REVIEW",
    "review": "REVIEW",
    "approved": "APPROVED",
    "applied": "PUBLISHED",
    "published": "PUBLISHED",
    "validated": "PUBLISHED",
    "done": "PUBLISHED",
}


def _map_status(item: dict) -> str:
    for key in ("status", "lifecycle"):
        val = str(item.get(key) or "").lower()
        if val in STATUS_MAP:
            return STATUS_MAP[val]
    pct = int(item.get("completion_pct") or 0)
    if pct >= 100:
        return "PUBLISHED"
    if pct >= 75:
        return "APPROVED"
    if pct >= 50:
        return "REVIEW"
    if pct > 0:
        return "GENERATING"
    return "DRAFT"


def _default_language(country: str) -> str:
    defaults = {
        "BR": "pt-BR",
        "PT": "pt-PT",
        "US": "en-US",
        "ES": "es-ES",
        "FR": "fr-FR",
        "DE": "de-DE",
        "IT": "it-IT",
        "JP": "ja-JP",
    }
    return defaults.get(country.upper(), "pt-BR")


def build_records(pending_items: list[dict], country: str) -> list[dict]:
    language = _default_language(country)
    records: list[dict] = []
    for item in pending_items:
        pending_id = item.get("pending_id") or item.get("entity_code") or ""
        request_code = pending_id.replace("PEND.", "CF.") if pending_id.startswith("PEND.") else f"CF.{pending_id}"
        records.append({
            "request_code": request_code,
            "master_entity": item.get("parent_entity_code") or item.get("entity_code") or "",
            "template": f"TPL.{item.get('artifact_type', 'CONTENT')}",
            "language": language,
            "description": item.get("title_pt") or item.get("title") or "",
            "content_type": item.get("artifact_type"),
            "status": _map_status(item),
            "country_code": country.upper(),
            "source_pending_id": pending_id,
            "completion_pct": item.get("completion_pct"),
            "canonical_url": item.get("canonical_url"),
            "updated_at": NOW(),
        })
    return records


def sync_content_requests(country: str = "BR", *, pending_only: bool = True) -> dict:
    cc = country.strip().upper()
    if cc not in SUPPORTED_COUNTRIES:
        raise ValueError(f"Unsupported country: {cc}")

    rel = f"by-country/{cc}/content_requests.json"
    existing = read_envelope(rel) if (DATASETS / rel).exists() else {}

    pending = {}
    if PENDING_PATH.exists():
        pending = __import__("json").loads(PENDING_PATH.read_text(encoding="utf-8"))
    items = pending.get("items") or []

    if pending_only and cc != "BR":
        # Fila editorial atual é BR — demais países mantêm arquivo vazio até expansão.
        records = []
    else:
        records = build_records(items, cc)

    env = {k: v for k, v in existing.items() if k != "records"}
    env.setdefault("entity", "ContentRequest")
    env.setdefault("schema_version", "2026.1.0")
    env["country_code"] = cc
    env["partition"] = "country"
    env["records"] = records
    env["count"] = len(records)
    env["generated_at"] = NOW()
    env["source"] = "master-data/content-pending/pending_items.json"
    env["note"] = f"Content Factory sync — {len(records)} pedidos a partir da fila editorial"
    write_envelope(rel, env)

    by_status: dict[str, int] = {}
    for rec in records:
        st = rec.get("status", "DRAFT")
        by_status[st] = by_status.get(st, 0) + 1

    return {
        "country": cc,
        "synced": len(records),
        "by_status": by_status,
        "path": rel,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync ContentRequest kanban from content-pending queue")
    parser.add_argument("--country", default="BR", help="Country code (default: BR)")
    parser.add_argument("--all-countries", action="store_true", help="Sync BR from pending; others stay empty")
    args = parser.parse_args()

    if args.all_countries:
        results = [sync_content_requests(cc) for cc in SUPPORTED_COUNTRIES]
        for r in results:
            print(f"{r['country']}: {r['synced']} requests {r.get('by_status', {})}")
        return 0

    result = sync_content_requests(args.country)
    print(f"{result['country']}: synced {result['synced']} -> {result['path']}")
    print("by_status:", result.get("by_status"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
