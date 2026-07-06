"""Normaliza registros NKOS → linhas Supabase / documentos Firebase."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from dataset_io import read_envelope


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stable_uuid(seed: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"nkos:{seed}"))


def load_entity_records(meta: dict) -> tuple[dict, list[dict]]:
    env = read_envelope(meta["path"])
    return env, env.get("records", [])


def to_supabase_row(meta: dict, record: dict, envelope: dict) -> dict[str, Any]:
    pk = meta["pk"]
    business_key = str(record.get(pk) or "")
    row_id = record.get("uuid") or _stable_uuid(f"{meta['entity_key']}:{business_key}")

    return {
        "id": row_id,
        "entity_key": meta["entity_key"],
        "business_key": business_key,
        "country_code": record.get("country_code") or record.get("country"),
        "locale_code": record.get("locale_code") or record.get("locale"),
        "schema_version": envelope.get("schema_version"),
        "payload": record,
        "synced_at": _now(),
    }


def to_firebase_doc(meta: dict, record: dict, envelope: dict) -> dict[str, Any]:
    pk = meta["pk"]
    business_key = str(record.get(pk) or "")
    doc_id = record.get("uuid") or _stable_uuid(f"{meta['entity_key']}:{business_key}")

    return {
        "id": doc_id,
        "entityKey": meta["entity_key"],
        "businessKey": business_key,
        "countryCode": record.get("country_code") or record.get("country"),
        "localeCode": record.get("locale_code") or record.get("locale"),
        "schemaVersion": envelope.get("schema_version"),
        "payload": record,
        "syncedAt": _now(),
    }


def build_entity_bundle(meta: dict, *, target: str = "supabase") -> dict:
    envelope, records = load_entity_records(meta)
    rows = []
    for rec in records:
        if target == "firebase":
            rows.append(to_firebase_doc(meta, rec, envelope))
        else:
            rows.append(to_supabase_row(meta, rec, envelope))

    return {
        "entity_key": meta["entity_key"],
        "target": target,
        "table": meta.get("table"),
        "collection": meta.get("collection"),
        "schema_version": envelope.get("schema_version"),
        "record_count": len(rows),
        "rows": rows,
    }
