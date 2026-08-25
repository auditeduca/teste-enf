"""Compare live/source vs vault first-copy and vault vs internal projection."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .paths import FETCH_DIR, ROOT
from .vault import compare_to_first, first_copy, put_bytes

FORBIDDEN_IN_INTERNAL = (
    "adsbygoogle",
    "googleads",
    "doubleclick",
    'type="email"',
    "cdn.jsdelivr",
    "opendyslexic",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _dump(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _load_events() -> dict:
    path = ROOT / "cko_inbox" / "extracted" / "change_events.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"business_key": "IPE-CHANGE-EVENTS-001", "uuid": None, "status": "OBSERVED", "events": []}


def compare_source(*, network: bool, fetch_fn) -> dict:
    """AG-COMPARE-SOURCE — live or inbox bytes vs first WORM copy."""
    targets = [
        ("SRC-ORIGIN-FOOTER", ROOT / "cko_inbox" / "origin" / "footer.html", "https://www.calculadorasdeenfermagem.com.br/footer.html"),
        ("SRC-ORIGIN-MENU", ROOT / "cko_inbox" / "origin" / "menu-global.html", "https://www.calculadorasdeenfermagem.com.br/menu-global.html"),
        ("SRC-ORIGIN-BODY", ROOT / "cko_inbox" / "origin" / "global-body-elements.html", "https://www.calculadorasdeenfermagem.com.br/global-body-elements.html"),
        ("SRC-LEI-9610-1998", ROOT / "cko_inbox" / "official" / "lei-9610.html", "https://www.planalto.gov.br/ccivil_03/leis/l9610.htm"),
        ("SRC-ISO-8000-CATALOG", ROOT / "cko_inbox" / "official" / "iso-8000-catalog.html", "https://www.iso.org/standard/80766.html"),
    ]
    results = []
    for logical_id, path, url in targets:
        observed = None
        http_status = None
        if network:
            rec = fetch_fn(url)
            observed = rec.get("body")
            http_status = rec.get("http_status")
            if observed:
                put_bytes(observed, logical_id=logical_id, source_url=url, media_type="text/html")
        if observed is None and path.exists():
            observed = path.read_bytes()
        if observed is None:
            results.append({
                "logical_id": logical_id,
                "status": "EVIDENCE_PENDING",
                "http_status": http_status,
                "url": url,
            })
            continue
        results.append({**compare_to_first(logical_id, observed), "http_status": http_status, "url": url})
    drifts = [item for item in results if item.get("status") == "SOURCE_DRIFT"]
    payload = {
        "business_key": "IPE-COMPARE-SOURCE-001",
        "uuid": None,
        "status": "SOURCE_DRIFT" if drifts else "OBSERVED",
        "network": network,
        "compared": results,
        "drift_count": len(drifts),
        "compared_at": _now(),
        "llm_used": False,
    }
    _dump(ROOT / "cko_inbox" / "extracted" / "compare_source.json", payload)
    return {
        "agent_id": "AG-COMPARE-SOURCE",
        "class": "MONITORING",
        "role": "CHECKER",
        "status": payload["status"],
        "drift_count": len(drifts),
        "compared": len(results),
        "llm_used": False,
        "promotes_to_md": False,
    }


def compare_internal() -> dict:
    """AG-COMPARE-INTERNAL — vault/origin vs CKO projection. Ads stripped = expected rewrite."""
    pairs = [
        ("SRC-ORIGIN-FOOTER", FETCH_DIR / "index.html", "MASK-ORIGIN-HTML"),
        ("SRC-SITE-SHELL", FETCH_DIR / "index.html", "MASK-ORIGIN-HTML"),
    ]
    results = []
    for logical_id, internal_path, mask_id in pairs:
        copy = first_copy(logical_id)
        internal_text = internal_path.read_text(encoding="utf-8") if internal_path.exists() else ""
        source_text = ""
        if copy and copy.get("bytes_payload"):
            source_text = copy["bytes_payload"].decode("utf-8", errors="replace")
        expected_absent = [token for token in FORBIDDEN_IN_INTERNAL if token.lower() in internal_text.lower()]
        expected_in_source = [token for token in FORBIDDEN_IN_INTERNAL if token.lower() in source_text.lower()]
        hash_equal = False
        if copy and internal_path.exists():
            import hashlib
            hash_equal = hashlib.sha256(internal_path.read_bytes()).hexdigest() == copy.get("first_sha256")
        kind = "MATCH"
        if not copy:
            kind = "HOLD"
        elif hash_equal:
            kind = "MATCH"
        elif expected_in_source and not expected_absent:
            kind = "EXPECTED_REWRITE"
        elif expected_absent:
            kind = "INTERNAL_DRIFT"
        elif not hash_equal:
            kind = "EXPECTED_REWRITE"
        results.append({
            "logical_id": logical_id,
            "mask_id": mask_id,
            "status": kind,
            "internal_path": str(internal_path.relative_to(ROOT)) if internal_path.exists() else None,
            "source_has_forbidden": expected_in_source,
            "internal_has_forbidden": expected_absent,
            "hash_equal": hash_equal,
        })
        if kind == "INTERNAL_DRIFT":
            events = _load_events()
            events["events"].append({
                "event_id": f"EVT-INT-{logical_id[-8:]}",
                "kind": "INTERNAL_DRIFT",
                "logical_id": logical_id,
                "detected_at": _now(),
                "note": "Projeção interna contém tokens proibidos. Ajustar renderer.",
                "tokens": expected_absent,
            })
            events["population"] = len(events["events"])
            events["updated_at"] = _now()
            _dump(ROOT / "cko_inbox" / "extracted" / "change_events.json", events)

    payload = {
        "business_key": "IPE-COMPARE-INTERNAL-001",
        "uuid": None,
        "status": "OBSERVED",
        "compared": results,
        "internal_drift_count": sum(1 for item in results if item["status"] == "INTERNAL_DRIFT"),
        "compared_at": _now(),
        "llm_used": False,
        "rule": "Hash diferente da origem com ads/email removidos = EXPECTED_REWRITE, não falha.",
    }
    _dump(ROOT / "cko_inbox" / "extracted" / "compare_internal.json", payload)
    return {
        "agent_id": "AG-COMPARE-INTERNAL",
        "class": "MONITORING",
        "role": "CHECKER",
        "status": "INTERNAL_DRIFT" if payload["internal_drift_count"] else "OBSERVED",
        "internal_drift_count": payload["internal_drift_count"],
        "llm_used": False,
        "promotes_to_md": False,
    }


def monitor_drift() -> dict:
    """AG-MONITOR-DRIFT — surface change events for admin/frontend."""
    events = _load_events()
    real_events = [item for item in (events.get("events") or []) if not str(item.get("logical_id") or "").startswith("TEST-")]
    events["status"] = "OBSERVED"
    events["monitor_run_at"] = _now()
    events["population"] = len(real_events)
    events["open_source_drift"] = sum(1 for item in real_events if item.get("kind") == "SOURCE_DRIFT")
    events["open_internal_drift"] = sum(1 for item in real_events if item.get("kind") == "INTERNAL_DRIFT")
    events["rule"] = "Qualquer SOURCE_DRIFT ou INTERNAL_DRIFT deve ser informado para ajuste. Sem IPE → sem reliance."
    _dump(ROOT / "cko_inbox" / "extracted" / "change_events.json", events)
    _dump(ROOT / "cko_assurance" / "monitoring_events.json", {
        "business_key": "IPE-MONITOR-001",
        "uuid": None,
        "status": "IMPLEMENTED",
        "implemented": True,
        "publication_implemented": False,
        "source": "cko_inbox/extracted/change_events.json",
        "population": events["population"],
        "open_source_drift": events["open_source_drift"],
        "open_internal_drift": events["open_internal_drift"],
        "wired_to_frontend": True,
        "admin_href": "admin/monitoring.html",
    })
    return {
        "agent_id": "AG-MONITOR-DRIFT",
        "class": "MONITORING",
        "role": "CHECKER",
        "status": "HOLD" if events["open_source_drift"] or events["open_internal_drift"] else "OBSERVED",
        "population": events["population"],
        "open_source_drift": events["open_source_drift"],
        "open_internal_drift": events["open_internal_drift"],
        "wired_to_frontend": True,
        "llm_used": False,
        "promotes_to_md": False,
    }
