"""Upload para Firebase Firestore — REST + bundle local + Cloud Function."""
from __future__ import annotations

import json
import os
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from config import (
    DATABASE_SYNC_BATCH_SIZE,
    DATABASE_SYNC_DRY_RUN,
    FIREBASE_CREDENTIALS_JSON,
    FIREBASE_DATABASE_URL,
    FIREBASE_FUNCTIONS_URL,
    FIREBASE_PROJECT_ID,
    FIREBASE_SYNC_SECRET,
    ROOT,
)
from normalizers import build_entity_bundle
from paths import BUNDLES


def _load_service_account() -> dict | None:
    path_str = FIREBASE_CREDENTIALS_JSON()
    if not path_str:
        return None
    path = Path(path_str)
    if not path.is_absolute():
        path = ROOT / path_str
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _get_access_token() -> str | None:
    """OAuth2 JWT para Firestore REST (service account)."""
    sa = _load_service_account()
    if not sa:
        return None

    try:
        import jwt  # type: ignore
    except ImportError:
        return None

    now = int(time.time())
    claim = {
        "iss": sa["client_email"],
        "sub": sa["client_email"],
        "aud": "https://oauth2.googleapis.com/token",
        "iat": now,
        "exp": now + 3600,
        "scope": "https://www.googleapis.com/auth/datastore",
    }
    assertion = jwt.encode(claim, sa["private_key"], algorithm="RS256")
    body = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": assertion,
    }).encode()
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
        return json.loads(resp.read().decode())["access_token"]


def configured() -> bool:
    return bool(
        FIREBASE_PROJECT_ID()
        and (_load_service_account() or FIREBASE_FUNCTIONS_URL())
    )


def save_bundle(meta: dict) -> Path:
    """Salva bundle JSON para upload manual ou Cloud Function."""
    BUNDLES.mkdir(parents=True, exist_ok=True)
    bundle = build_entity_bundle(meta, target="firebase")
    path = BUNDLES / f"{meta['entity_key']}.firebase.json"
    path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _firestore_batch_write(project_id: str, token: str, collection: str, docs: list[dict]) -> dict:
    """Firestore commit via REST (writes limit ~500)."""
    base = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents:commit"
    writes = []
    for doc in docs:
        doc_id = doc["id"]
        fields = _to_firestore_fields(doc)
        writes.append({
            "update": {
                "name": f"projects/{project_id}/databases/(default)/documents/{collection}/{doc_id}",
                "fields": fields,
            },
            "updateMask": {"fieldPaths": []},
        })

    body = json.dumps({"writes": writes}).encode()
    req = urllib.request.Request(
        base,
        data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
        return {"ok": True, "status": resp.status, "count": len(docs)}


def _to_firestore_fields(obj: dict) -> dict:
    """Converte dict Python → Firestore Value map (simplificado)."""
    out: dict = {}
    for k, v in obj.items():
        out[k] = _firestore_value(v)
    return out


def _firestore_value(v: Any) -> dict:
    if v is None:
        return {"nullValue": None}
    if isinstance(v, bool):
        return {"booleanValue": v}
    if isinstance(v, int):
        return {"integerValue": str(v)}
    if isinstance(v, float):
        return {"doubleValue": v}
    if isinstance(v, str):
        return {"stringValue": v}
    if isinstance(v, dict):
        return {"mapValue": {"fields": _to_firestore_fields(v)}}
    if isinstance(v, list):
        return {"arrayValue": {"values": [_firestore_value(i) for i in v]}}
    return {"stringValue": json.dumps(v, ensure_ascii=False)}


def upload_via_cloud_function(bundle_path: Path) -> dict:
    """Delega upload ao Firebase Cloud Function syncNkosBundle."""
    fn_url = FIREBASE_FUNCTIONS_URL()
    if not fn_url:
        return {"ok": False, "error": "FIREBASE_FUNCTIONS_URL not set"}

    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    body = json.dumps({
        "secret": FIREBASE_SYNC_SECRET(),
        "bundle": bundle,
    }).encode()
    req = urllib.request.Request(
        f"{fn_url}/syncNkosBundle",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=300, context=ctx) as resp:
            return {"ok": True, "response": json.loads(resp.read().decode())}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "error": exc.read().decode()[:400], "status": exc.code}


def upload_entity(meta: dict, *, dry_run: bool | None = None, use_function: bool = True) -> dict:
    dry = DATABASE_SYNC_DRY_RUN() if dry_run is None else dry_run
    bundle_path = save_bundle(meta)
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))

    if dry:
        return {
            "ok": True,
            "dry_run": True,
            "entity_key": meta["entity_key"],
            "collection": meta["collection"],
            "bundle_path": str(bundle_path),
            "record_count": bundle["record_count"],
        }

    if use_function and FIREBASE_FUNCTIONS_URL():
        res = upload_via_cloud_function(bundle_path)
        res["entity_key"] = meta["entity_key"]
        res["bundle_path"] = str(bundle_path)
        return res

    project = FIREBASE_PROJECT_ID()
    token = _get_access_token()
    if not project or not token:
        return {
            "ok": False,
            "error": "firebase_credentials_missing",
            "hint": "Defina FIREBASE_PROJECT_ID + FIREBASE_CREDENTIALS_JSON ou FIREBASE_FUNCTIONS_URL",
            "bundle_path": str(bundle_path),
        }

    collection = meta["collection"]
    docs = bundle["rows"]
    batch_size = min(DATABASE_SYNC_BATCH_SIZE(), 400)
    results = []
    ok = True
    for i in range(0, len(docs), batch_size):
        chunk = docs[i : i + batch_size]
        try:
            results.append(_firestore_batch_write(project, token, collection, chunk))
        except Exception as exc:
            ok = False
            results.append({"ok": False, "error": str(exc)[:300]})
            break

    return {
        "ok": ok,
        "entity_key": meta["entity_key"],
        "collection": collection,
        "record_count": len(docs),
        "bundle_path": str(bundle_path),
        "results": results,
    }


def upload_entities(entities: list[dict], *, dry_run: bool | None = None, use_function: bool = True) -> dict:
    if not configured() and not (dry_run if dry_run is not None else DATABASE_SYNC_DRY_RUN()):
        return {"ok": False, "error": "firebase_not_configured"}

    uploads = []
    ok_count = 0
    for meta in entities:
        res = upload_entity(meta, dry_run=dry_run, use_function=use_function)
        uploads.append(res)
        if res.get("ok"):
            ok_count += 1

    return {
        "ok": ok_count == len(entities),
        "target": "firebase",
        "total": len(uploads),
        "succeeded": ok_count,
        "uploads": uploads,
    }
