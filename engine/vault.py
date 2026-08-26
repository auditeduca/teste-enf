"""Content-addressed WORM vault for unaltered source copies.

Same SHA-256 never overwrites. A new hash for the same logical_id creates a
new object and a CHANGE event. The first copy remains the traceability baseline.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .paths import ROOT

VAULT_DIR = ROOT / "cko_inbox" / "vault"
OBJECTS_DIR = VAULT_DIR / "objects"
MANIFEST_PATH = VAULT_DIR / "MANIFEST.json"
POINTERS_PATH = VAULT_DIR / "pointers.json"
EVENTS_PATH = ROOT / "cko_inbox" / "extracted" / "change_events.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _dump(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _load(path: Path, default: dict) -> dict:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def object_path(sha256: str) -> Path:
    return OBJECTS_DIR / sha256[:2] / sha256


def read_bytes(sha256: str) -> bytes | None:
    path = object_path(sha256)
    if not path.exists():
        return None
    return path.read_bytes()


def _append_event(event: dict) -> None:
    payload = _load(EVENTS_PATH, {
        "business_key": "IPE-CHANGE-EVENTS-001",
        "uuid": None,
        "status": "OBSERVED",
        "events": [],
    })
    payload["events"].append(event)
    payload["population"] = len(payload["events"])
    payload["updated_at"] = _now()
    _dump(EVENTS_PATH, payload)


def put_bytes(
    data: bytes,
    *,
    logical_id: str,
    source_url: str | None = None,
    source_path: str | None = None,
    media_type: str = "application/octet-stream",
    mask_id: str | None = None,
    note: str | None = None,
) -> dict:
    """Store unaltered bytes. Existing object at this hash is never rewritten."""
    digest = _sha256_bytes(data)
    dest = object_path(digest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    existed = dest.exists()
    if existed:
        stored = dest.read_bytes()
        if stored != data:
            raise RuntimeError(f"VAULT_COLLISION: path exists for {digest} with different bytes")
    else:
        dest.write_bytes(data)

    pointers = _load(POINTERS_PATH, {
        "business_key": "MD-VAULT-POINTERS-001",
        "uuid": None,
        "status": "OBSERVED",
        "pointers": {},
    })
    pointer = pointers["pointers"].get(logical_id) or {}
    first = pointer.get("first_sha256")
    previous = pointer.get("latest_sha256")
    changed = bool(first) and first != digest
    if not first:
        pointer = {
            "logical_id": logical_id,
            "first_sha256": digest,
            "first_captured_at": _now(),
            "latest_sha256": digest,
            "latest_captured_at": _now(),
            "source_url": source_url,
            "source_path": source_path,
            "media_type": media_type,
            "mask_id": mask_id,
            "immutable": True,
            "bytes": len(data),
        }
    else:
        pointer["latest_sha256"] = digest
        pointer["latest_captured_at"] = _now()
        pointer["source_url"] = source_url or pointer.get("source_url")
        pointer["source_path"] = source_path or pointer.get("source_path")
        pointer["mask_id"] = mask_id or pointer.get("mask_id")
        pointer["bytes"] = len(data)
    pointers["pointers"][logical_id] = pointer
    pointers["population"] = len(pointers["pointers"])
    pointers["updated_at"] = _now()
    _dump(POINTERS_PATH, pointers)

    manifest = _load(MANIFEST_PATH, {
        "business_key": "IPE-VAULT-MANIFEST-001",
        "uuid": None,
        "status": "OBSERVED",
        "rule": "Cópia original inalterada. Mesmo hash não sobrescreve. Hash novo = objeto novo + evento.",
        "objects": {},
    })
    if digest not in manifest["objects"]:
        manifest["objects"][digest] = {
            "sha256": digest,
            "bytes": len(data),
            "logical_ids": [logical_id],
            "source_url": source_url,
            "source_path": source_path,
            "media_type": media_type,
            "mask_id": mask_id,
            "immutable": True,
            "worm": True,
            "first_put_at": _now(),
            "note": note,
        }
    else:
        ids = manifest["objects"][digest].setdefault("logical_ids", [])
        if logical_id not in ids:
            ids.append(logical_id)
    manifest["population"] = len(manifest["objects"])
    manifest["updated_at"] = _now()
    _dump(MANIFEST_PATH, manifest)

    record = {
        "logical_id": logical_id,
        "sha256": digest,
        "first_sha256": pointer["first_sha256"],
        "bytes": len(data),
        "existed": existed,
        "changed_from_first": changed,
        "path": str(dest.relative_to(ROOT)),
        "immutable": True,
    }
    if changed:
        _append_event({
            "event_id": f"EVT-VAULT-{digest[:12]}",
            "kind": "SOURCE_DRIFT",
            "logical_id": logical_id,
            "first_sha256": first,
            "observed_sha256": digest,
            "previous_sha256": previous,
            "detected_at": _now(),
            "note": "Hash observado diferente da primeira cópia WORM. Ajustar conteúdo interno.",
        })
        record["event"] = "SOURCE_DRIFT"
    return record


def put_path(path: Path, *, logical_id: str, **kwargs) -> dict:
    return put_bytes(path.read_bytes(), logical_id=logical_id, source_path=str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path), **kwargs)


def first_copy(logical_id: str) -> dict | None:
    pointers = _load(POINTERS_PATH, {"pointers": {}})
    pointer = (pointers.get("pointers") or {}).get(logical_id)
    if not pointer:
        return None
    data = read_bytes(pointer["first_sha256"])
    if data is None:
        return None
    return {**pointer, "bytes_payload": data}


def compare_to_first(logical_id: str, observed: bytes) -> dict:
    pointer = first_copy(logical_id)
    observed_hash = _sha256_bytes(observed)
    if pointer is None:
        return {
            "logical_id": logical_id,
            "status": "EVIDENCE_PENDING",
            "reason": "Primeira cópia WORM ausente.",
            "observed_sha256": observed_hash,
        }
    first_hash = pointer["first_sha256"]
    match = first_hash == observed_hash
    result = {
        "logical_id": logical_id,
        "status": "MATCH" if match else "SOURCE_DRIFT",
        "first_sha256": first_hash,
        "observed_sha256": observed_hash,
        "first_captured_at": pointer.get("first_captured_at"),
        "bytes_first": pointer.get("bytes"),
        "bytes_observed": len(observed),
    }
    if not match:
        _append_event({
            "event_id": f"EVT-CMP-{observed_hash[:12]}",
            "kind": "SOURCE_DRIFT",
            "logical_id": logical_id,
            "first_sha256": first_hash,
            "observed_sha256": observed_hash,
            "detected_at": _now(),
            "note": "Conteúdo vivo ou reobservado difere da cópia original inalterada.",
        })
    return result


def put_known_sources(*, network: bool = False, fetch_fn=None) -> dict:
    """Put inbox originals into the WORM vault. Live fetch only adds a new object on hash change."""
    from .paths import TOOLS_DIR

    stored = []

    def _put_if_exists(path: Path, logical_id: str, **kwargs) -> None:
        if path.exists() and path.is_file():
            stored.append(put_path(path, logical_id=logical_id, **kwargs))

    _put_if_exists(ROOT / "cko_inbox" / "origin" / "footer.html", "SRC-ORIGIN-FOOTER", media_type="text/html", mask_id="MASK-ORIGIN-HTML")
    _put_if_exists(ROOT / "cko_inbox" / "origin" / "menu-global.html", "SRC-ORIGIN-MENU", media_type="text/html", mask_id="MASK-ORIGIN-HTML")
    _put_if_exists(ROOT / "cko_inbox" / "origin" / "global-body-elements.html", "SRC-ORIGIN-BODY", media_type="text/html", mask_id="MASK-ORIGIN-HTML")
    _put_if_exists(
        ROOT / "cko_inbox" / "drive" / "site-shell-calculadoras-enfermagem.zip",
        "SRC-SITE-SHELL",
        media_type="application/zip",
        mask_id="MASK-ORIGIN-HTML",
        note="Drive site-shell zip unaltered",
    )
    shell_dir = ROOT / "cko_inbox" / "drive" / "site_shell" / "site-shell"
    for name, logical_id in (
        ("footer.html", "SRC-SHELL-FOOTER"),
        ("menu-global.html", "SRC-SHELL-MENU"),
        ("global-body-elements.html", "SRC-SHELL-BODY"),
        ("homepage.html", "SRC-SHELL-HOME"),
        ("global-scripts.js", "SRC-SHELL-JS"),
        ("global-styles.css", "SRC-SHELL-CSS"),
    ):
        media = "text/css" if name.endswith(".css") else ("text/javascript" if name.endswith(".js") else "text/html")
        _put_if_exists(shell_dir / name, logical_id, media_type=media, mask_id="MASK-ORIGIN-HTML")

    _put_if_exists(
        ROOT / "cko_inbox" / "official" / "lei-9610.html",
        "SRC-LEI-9610-1998",
        media_type="text/html",
        mask_id="MASK-LAW-BR",
        note="Lei 9.610/98 HTML público Planalto, cópia inalterada",
    )
    _put_if_exists(
        ROOT / "cko_inbox" / "official" / "iso-8000-catalog.html",
        "SRC-ISO-8000-CATALOG",
        media_type="text/html",
        mask_id="MASK-TECH-STD",
    )

    for slug in ("gotejamento", "meows", "cinco-ts-pcr", "simulado-tecnico", "dimensionamento"):
        _put_if_exists(TOOLS_DIR / f"{slug}.json", f"MD-TOOL-{slug}", media_type="application/json", mask_id="MASK-TOOL-WORK")
        tool_html = ROOT / "cko_inbox" / "origin" / "tools" / f"{slug}.html"
        _put_if_exists(tool_html, f"SRC-ORIGIN-TOOL-{slug}", media_type="text/html", mask_id="MASK-ORIGIN-HTML")
    _put_if_exists(
        ROOT / "cko_inbox" / "origin" / "tools" / "braden.html",
        "SRC-ORIGIN-TOOL-braden",
        media_type="text/html",
        mask_id="MASK-SCALE-THIRD-PARTY",
        note="Terceiros. Não promover a data/tools.",
    )

    live = []
    if network and fetch_fn:
        official = [
            ("SRC-LEI-9610-1998", "https://www.planalto.gov.br/ccivil_03/leis/l9610.htm", "MASK-LAW-BR"),
            ("SRC-ISO-8000-CATALOG", "https://www.iso.org/standard/80766.html", "MASK-TECH-STD"),
        ]
        for logical_id, url, mask_id in official:
            rec = fetch_fn(url)
            body = rec.get("body")
            live.append({
                "logical_id": logical_id,
                "url": url,
                "http_status": rec.get("http_status"),
                "epistemic_status": rec.get("epistemic_status"),
            })
            if body:
                dest = ROOT / "cko_inbox" / "official" / ("lei-9610.html" if "9610" in logical_id else "iso-8000-catalog.html")
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(body)
                stored.append(put_bytes(body, logical_id=logical_id, source_url=url, media_type="text/html", mask_id=mask_id))

    return {
        "agent_id": "AG-VAULT-PUT",
        "class": "EVIDENCE",
        "role": "MAKER",
        "status": "OBSERVED" if stored else "EVIDENCE_PENDING",
        "stored": len(stored),
        "changed_from_first": sum(1 for item in stored if item.get("changed_from_first")),
        "objects": [{"logical_id": item["logical_id"], "sha256": item["sha256"], "bytes": item["bytes"]} for item in stored],
        "live_fetches": live,
        "worm": True,
        "llm_used": False,
        "promotes_to_md": False,
    }
