"""Upload para Supabase via REST API (PostgREST)."""
from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request
from typing import Any

from config import (
    DATABASE_SYNC_BATCH_SIZE,
    DATABASE_SYNC_DRY_RUN,
    SUPABASE_ANON_KEY,
    SUPABASE_SERVICE_ROLE_KEY,
    SUPABASE_URL,
)
from normalizers import build_entity_bundle


def _headers() -> dict[str, str]:
    key = SUPABASE_SERVICE_ROLE_KEY() or SUPABASE_ANON_KEY()
    if not key:
        raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY ou SUPABASE_ANON_KEY não configurada")
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=minimal",
    }


def configured() -> bool:
    return bool(SUPABASE_URL() and (SUPABASE_SERVICE_ROLE_KEY() or SUPABASE_ANON_KEY()))


def upsert_batch(table: str, rows: list[dict], *, dry_run: bool | None = None) -> dict:
    dry = DATABASE_SYNC_DRY_RUN() if dry_run is None else dry_run
    if dry:
        return {"ok": True, "dry_run": True, "table": table, "would_upsert": len(rows)}

    url = f"{SUPABASE_URL()}/rest/v1/{table}"
    body = json.dumps(rows, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=_headers(), method="POST")
    ctx = ssl.create_default_context()

    try:
        with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
            return {"ok": True, "table": table, "upserted": len(rows), "status": resp.status}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        return {"ok": False, "table": table, "error": detail, "status": exc.code}


def upload_entity(meta: dict, *, dry_run: bool | None = None) -> dict:
    bundle = build_entity_bundle(meta, target="supabase")
    table = meta["table"]
    batch_size = DATABASE_SYNC_BATCH_SIZE()
    rows = bundle["rows"]
    results = []
    ok = True

    for i in range(0, len(rows), batch_size):
        chunk = rows[i : i + batch_size]
        res = upsert_batch(table, chunk, dry_run=dry_run)
        results.append(res)
        if not res.get("ok"):
            ok = False
            break

    return {
        "ok": ok,
        "entity_key": meta["entity_key"],
        "table": table,
        "record_count": len(rows),
        "batches": len(results),
        "results": results,
    }


def upload_entities(entities: list[dict], *, dry_run: bool | None = None) -> dict:
    if not configured():
        return {"ok": False, "error": "supabase_not_configured", "hint": "Defina SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY no .env"}

    uploads = []
    ok_count = 0
    for meta in entities:
        res = upload_entity(meta, dry_run=dry_run)
        uploads.append(res)
        if res.get("ok"):
            ok_count += 1

    return {
        "ok": ok_count > 0 and ok_count == len(entities),
        "target": "supabase",
        "total": len(uploads),
        "succeeded": ok_count,
        "uploads": uploads,
    }
