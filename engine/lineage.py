"""Bind vault first-copy → MD work → REG rights → frontend projection."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .paths import FETCH_DIR, INLINE_DIR, ROOT, TOOLS_DIR
from .vault import first_copy

PILOTS = ("gotejamento", "meows", "cinco-ts-pcr", "simulado-tecnico", "dimensionamento")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _dump(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _sha_of(path: Path) -> str | None:
    if not path.exists():
        return None
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bind_lineage() -> dict:
    links = []
    for slug in PILOTS:
        tool_path = TOOLS_DIR / f"{slug}.json"
        md_vault = first_copy(f"MD-TOOL-{slug}")
        origin_vault = first_copy(f"SRC-ORIGIN-TOOL-{slug}")
        fetch = FETCH_DIR / "tools" / f"{slug}.html"
        inline = INLINE_DIR / "tools" / f"{slug}.html"
        fetch_exists = fetch.exists()
        complete = bool(tool_path.exists() and md_vault and fetch_exists)
        links.append({
            "business_key": f"LIN-{slug.upper()}",
            "slug": slug,
            "md_path": str(tool_path.relative_to(ROOT)) if tool_path.exists() else None,
            "md_vault_sha256": (md_vault or {}).get("first_sha256"),
            "origin_url": f"https://www.calculadorasdeenfermagem.com.br/{slug}.html",
            "origin_vault_sha256": (origin_vault or {}).get("first_sha256"),
            "projection_fetch": str(fetch.relative_to(ROOT)) if fetch_exists else None,
            "projection_inline": str(inline.relative_to(ROOT)) if inline.exists() else None,
            "projection_fetch_sha256": _sha_of(fetch),
            "frontend_href": f"tools/{slug}.html",
            "inspector_href": "inspector.html",
            "admin_monitoring_href": "admin/monitoring.html",
            "rights_ref": "REG-RIGHTS-001",
            "instrument_ref": "INS-LEI-9610-1998",
            "mask_id": "MASK-HOLD-WORK" if slug == "dimensionamento" else "MASK-TOOL-WORK",
            "complete": complete,
            "status": "LINKED" if complete else "HOLD",
            "uuid": None,
        })

    chrome = []
    for logical_id, href in (
        ("SRC-ORIGIN-FOOTER", "cko_inbox/origin/footer.html"),
        ("SRC-ORIGIN-MENU", "cko_inbox/origin/menu-global.html"),
        ("SRC-ORIGIN-BODY", "cko_inbox/origin/global-body-elements.html"),
        ("SRC-SITE-SHELL", "cko_inbox/drive/site_shell/INVENTORY.json"),
        ("SRC-LEI-9610-1998", "https://www.planalto.gov.br/ccivil_03/leis/l9610.htm"),
        ("SRC-ISO-8000-CATALOG", "https://www.iso.org/standard/80766.html"),
    ):
        copy = first_copy(logical_id)
        chrome.append({
            "logical_id": logical_id,
            "source": href,
            "vault_sha256": (copy or {}).get("first_sha256"),
            "complete": bool(copy),
            "status": "LINKED" if copy else "HOLD",
        })

    complete_count = sum(1 for item in links if item["complete"])
    payload = {
        "business_key": "MD-LINEAGE-REG-001",
        "uuid": None,
        "status": "IMPLEMENTED" if complete_count else "HOLD",
        "chain": "vault first-copy → CKO-MD → CKO-REG → renderer → frontend",
        "population": len(links),
        "complete_count": complete_count,
        "links": links,
        "sources": chrome,
        "bound_at": _now(),
        "rule": "Frontend só exibe lineage de identidade já existente. Alteração da fonte gera evento de monitoramento.",
    }
    _dump(ROOT / "cko_md" / "lineage_registry.json", payload)
    return {
        "agent_id": "AG-LINEAGE-BIND",
        "class": "ENTITY_RESOLUTION",
        "role": "CHECKER",
        "status": payload["status"],
        "population": len(links),
        "complete_count": complete_count,
        "llm_used": False,
        "promotes_to_md": False,
        "wired_to_frontend": True,
    }
