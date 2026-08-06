#!/usr/bin/env python3
"""Integrity validator for CKO-CART-001: schema lint, local SHA-256, homolog sources."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "cko-cart-001.manifest.json"
SCHEMA = ROOT / "schemas" / "cko-cart.schema.json"
HOMOLOG = ROOT / "data" / "institutions.homolog.internal.json"

PLACEHOLDER_RE = re.compile(r"PLACEHOLDER", re.I)
SRI_RE = re.compile(r"^sha(256|384|512)-[A-Za-z0-9+/=]+$")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def validate_schema_basic(manifest: dict, schema: dict) -> list[str]:
    errors: list[str] = []
    required = schema.get("required", [])
    for key in required:
        if key not in manifest:
            errors.append(f"missing required key: {key}")
    zones = manifest.get("cartZones") or []
    if len(zones) != 7:
        errors.append(f"cartZones must have 7 items, got {len(zones)}")
    for z in zones:
        for fld in ("id", "title", "hotspot", "items", "deepLink"):
            if fld not in z:
                errors.append(f"zone missing {fld}: {z.get('id')}")
        hs = z.get("hotspot") or {}
        for fld in ("xPercent", "yPercent", "widthPercent", "heightPercent"):
            if fld not in hs:
                errors.append(f"hotspot missing {fld} in {z.get('id')}")
    rules = manifest.get("conferenceRules") or {}
    for fld in ("expiryAlertDays", "expiryWarningDays", "sealRequired", "rules"):
        if fld not in rules:
            errors.append(f"conferenceRules missing {fld}")
    tips = manifest.get("tipsAndErrors") or []
    if len(tips) < 4:
        errors.append("tipsAndErrors needs at least 4 items")
    identity = manifest.get("identity") or {}
    if identity.get("ckoId") != "CKO-CART-001":
        errors.append("identity.ckoId must be CKO-CART-001")
    return errors


def validate_hashes(manifest: dict, update: bool) -> list[str]:
    errors: list[str] = []
    locals_ = (manifest.get("assets") or {}).get("local") or []
    changed = False
    for asset in locals_:
        rel = asset.get("path", "").lstrip("/")
        path = ROOT / rel
        if not path.exists():
            errors.append(f"missing local asset: {asset.get('path')}")
            continue
        digest = sha256_file(path)
        current = (asset.get("sha256") or "").upper()
        if PLACEHOLDER_RE.search(current) or current != digest:
            if update:
                asset["sha256"] = digest
                changed = True
                print(f"[update] {asset.get('path')} -> {digest}")
            else:
                errors.append(
                    f"hash mismatch for {asset.get('path')}: expected {current}, got {digest}"
                )
    if update and changed:
        MANIFEST.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"[wrote] {MANIFEST}")
    return errors


def validate_sri(manifest: dict) -> list[str]:
    errors: list[str] = []
    libs = (manifest.get("assets") or {}).get("externalLibraries") or []
    for lib in libs:
        integrity = lib.get("integrity") or ""
        if PLACEHOLDER_RE.search(integrity) or not SRI_RE.match(integrity):
            errors.append(f"invalid SRI for {lib.get('id')}: {integrity}")
    return errors


def validate_sources(manifest: dict, homolog: dict) -> list[str]:
    errors: list[str] = []
    warnings: list[str] = []
    by_id = {i["id"]: i for i in homolog.get("institutions", [])}
    seals = (manifest.get("homologInstitutions") or {}).get("publicSeals") or []
    for seal in seals:
        iid = seal.get("institutionId")
        if iid not in by_id:
            errors.append(f"public seal unknown institutionId: {iid}")
        else:
            inst = by_id[iid]
            if inst.get("status") == "rejeitada":
                errors.append(f"rejected institution used publicly: {iid}")
            if float(inst.get("relatedness", 0)) < 0.5:
                warnings.append(f"relatedness_low on public seal: {iid}")
    for ref in manifest.get("references") or []:
        iid = ref.get("institutionId")
        if iid and iid not in by_id:
            errors.append(f"reference unknown institutionId: {iid}")
        elif iid and float(by_id[iid].get("relatedness", 0)) < 0.5:
            warnings.append(f"relatedness_low on reference {ref.get('id')}: {iid}")
        url = ref.get("url") or ""
        # URL must appear in homolog base (exact or host family)
        if iid and iid in by_id:
            base = by_id[iid].get("url") or ""
            if url and base and not (
                url.startswith(base.rstrip("/"))
                or base.startswith(url.rstrip("/"))
                or _same_host(url, base)
            ):
                warnings.append(
                    f"reference URL host differs from homolog entry {iid}: {url}"
                )
    for w in warnings:
        print(f"[warn] {w}")
    return errors


def _same_host(a: str, b: str) -> bool:
    try:
        from urllib.parse import urlparse

        return urlparse(a).netloc == urlparse(b).netloc
    except Exception:
        return False


def try_jsonschema(manifest: dict, schema: dict) -> list[str]:
    try:
        import jsonschema  # type: ignore
    except Exception:
        print("[info] jsonschema not installed — using built-in lint only")
        return []
    validator = jsonschema.Draft202012Validator(schema)
    return [f"schema: {e.message}" for e in sorted(validator.iter_errors(manifest), key=lambda e: list(e.path))]


def main(argv: list[str]) -> int:
    update = "--update-hashes" in argv
    if not MANIFEST.exists() or not SCHEMA.exists() or not HOMOLOG.exists():
        print("ERROR: required files missing", file=sys.stderr)
        return 2
    manifest = load_json(MANIFEST)
    schema = load_json(SCHEMA)
    homolog = load_json(HOMOLOG)

    errors: list[str] = []
    # Update hashes first so schema lint sees final digests when --update-hashes is set.
    errors.extend(validate_hashes(manifest, update=update))
    if update:
        manifest = load_json(MANIFEST)
        errors = [e for e in errors if "hash mismatch" not in e]
    errors.extend(validate_schema_basic(manifest, schema))
    errors.extend(try_jsonschema(manifest, schema))
    errors.extend(validate_sri(manifest))
    errors.extend(validate_sources(manifest, homolog))

    if errors:
        print("FAIL — integrity validation")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("OK — CKO-CART-001 manifest integrity")
    print(f"  zones: {len(manifest['cartZones'])}")
    print(f"  tips/errors: {len(manifest['tipsAndErrors'])}")
    print(f"  references: {len(manifest['references'])}")
    print(f"  homolog institutions: {len(homolog['institutions'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
