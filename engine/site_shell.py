"""Inventory Drive site-shell zip. Quarantine only — do not copy ads/email/CDN into the renderer."""

from __future__ import annotations

import hashlib
import json
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from .paths import ROOT

DRIVE_SITE_SHELL_ID = "1HEOd0k5i_iBtereT_ob_T1q8qI9MzKKU"
SITE_SHELL_SHA256 = "40795badc53e113a1f93f411a4a3a8299067352e7ed62fdc041b36fac1ae3d44"
SITE_SHELL_BYTES = 82453

CHROME_IDS = (
    "global-header-container",
    "language-selector-placeholder",
    "footer-placeholder",
    "barraAcessibilidade",
)

FORBIDDEN_TOKENS = (
    "adsbygoogle",
    "googleads",
    "doubleclick",
    "cdn.jsdelivr",
    "opendyslexic",
    "cookie-modal",
    'type="email"',
    "ca-pub-6472730056006847",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _dump(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def parse_site_shell() -> dict:
    zip_path = ROOT / "cko_inbox" / "drive" / "site-shell-calculadoras-enfermagem.zip"
    dest = ROOT / "cko_inbox" / "drive" / "site_shell" / "INVENTORY.json"
    extract_root = ROOT / "cko_inbox" / "drive" / "site_shell"
    if not zip_path.exists():
        if dest.exists():
            payload = json.loads(dest.read_text(encoding="utf-8"))
            return {
                "agent_id": "AG-PARSE-SITE-SHELL",
                "class": "EXTRACTION",
                "role": "MAKER",
                "status": "SOURCE_DERIVED",
                "replay": True,
                "file_count": payload.get("file_count"),
                "path": str(dest.relative_to(ROOT)),
                "promotes_to_md": False,
            }
        return {
            "agent_id": "AG-PARSE-SITE-SHELL",
            "class": "EXTRACTION",
            "role": "MAKER",
            "status": "EVIDENCE_PENDING",
            "reason": "site-shell zip ausente.",
            "promotes_to_md": False,
        }

    blob = zip_path.read_bytes()
    digest = _sha256_bytes(blob)
    files = []
    token_hits: Counter[str] = Counter()
    chrome_hits: Counter[str] = Counter()
    with zipfile.ZipFile(zip_path) as zf:
        names = [n for n in zf.namelist() if not n.endswith("/")]
        extract_root.mkdir(parents=True, exist_ok=True)
        zf.extractall(extract_root)
        for name in names:
            info = zf.getinfo(name)
            raw = zf.read(name)
            text = raw.decode("utf-8", errors="replace")
            hits = [token for token in FORBIDDEN_TOKENS if token.lower() in text.lower()]
            chrome = [cid for cid in CHROME_IDS if f'id="{cid}"' in text or f"id='{cid}'" in text or cid in text]
            for token in hits:
                token_hits[token] += 1
            for cid in chrome:
                chrome_hits[cid] += 1
            files.append({
                "path": name,
                "bytes": info.file_size,
                "sha256": _sha256_bytes(raw),
                "forbidden_tokens": hits,
                "chrome_ids": chrome,
            })

    payload = {
        "business_key": "SRC-SITE-SHELL-001",
        "uuid": None,
        "status": "SOURCE_DERIVED",
        "quarantine": True,
        "drive_file_id": DRIVE_SITE_SHELL_ID,
        "title": "site-shell-calculadoras-enfermagem.zip",
        "zip_bytes": len(blob),
        "zip_sha256": digest,
        "expected_sha256": SITE_SHELL_SHA256,
        "expected_bytes": SITE_SHELL_BYTES,
        "hash_match": digest == SITE_SHELL_SHA256,
        "file_count": len(files),
        "files": files,
        "forbidden_token_hits": dict(token_hits),
        "chrome_ids_present": dict(chrome_hits),
        "do_not_copy": list(FORBIDDEN_TOKENS),
        "rule": "Cópia inalterada para vault/comparação. Ads, email, cookie modal e CDN OpenDyslexic NÃO entram no renderer CKO.",
        "promoted_to_frontend": False,
        "chrome_projection": "A11Y_PWA_KEYBOARD_BACKTOTOP_NO_ADS",
        "extracted_at": _now(),
    }
    _dump(dest, payload)
    return {
        "agent_id": "AG-PARSE-SITE-SHELL",
        "class": "EXTRACTION",
        "role": "MAKER",
        "status": "SOURCE_DERIVED",
        "file_count": len(files),
        "hash_match": digest == SITE_SHELL_SHA256,
        "forbidden_token_hits": dict(token_hits),
        "chrome_ids_present": dict(chrome_hits),
        "promotes_to_md": False,
        "promoted_to_frontend": False,
        "chrome_projection": "A11Y_PWA_KEYBOARD_BACKTOTOP_NO_ADS",
        "path": str(dest.relative_to(ROOT)),
    }
