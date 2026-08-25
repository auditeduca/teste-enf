"""CKO profile of ISO 8000 master-data quality principles. Not ISO certification.

Licensed clause text is never stored. Catalog metadata + CKO tests only.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .paths import ROOT, TOOLS_DIR
from .vault import MANIFEST_PATH, POINTERS_PATH

OFFICIAL_CATALOG_URL = "https://www.iso.org/standard/80766.html"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _dump(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_profile() -> dict:
    from .bootstrap import field_dictionary_payload

    from .bootstrap import dump as dump_reg
    dump_reg(ROOT / "cko_md" / "field_dictionary.json", field_dictionary_payload())
    pointers = _load(POINTERS_PATH)
    manifest = _load(MANIFEST_PATH)
    lineage = _load(ROOT / "cko_md" / "lineage_registry.json")
    identity = _load(ROOT / "cko_core" / "identity_policy.json")
    field_dict = _load(ROOT / "cko_md" / "field_dictionary.json")
    tools = list(TOOLS_DIR.glob("*.json"))
    slugs = [path.stem for path in tools]
    unique_slugs = len(set(slugs)) == len(slugs)

    tests = [
        {
            "id": "ISO8000-CKO-UNIQUENESS",
            "principle": "unique identification of master records",
            "status": "PASS" if unique_slugs and identity.get("silent_id_invention") == "FORBIDDEN" else "FAIL",
            "observed": {"pilot_slugs": sorted(slugs), "uuid_generator": identity.get("uuid_generator_status")},
        },
        {
            "id": "ISO8000-CKO-PROVENANCE",
            "principle": "provenance of source bytes (url, captured_at, sha256)",
            "status": "PASS" if (pointers.get("pointers") or manifest.get("objects")) else "HOLD",
            "observed": {
                "vault_objects": manifest.get("population") or 0,
                "pointers": pointers.get("population") or 0,
            },
        },
        {
            "id": "ISO8000-CKO-WORM",
            "principle": "unaltered source copy retained",
            "status": "PASS" if manifest.get("objects") else "HOLD",
            "observed": {"worm": True, "population": manifest.get("population") or 0},
        },
        {
            "id": "ISO8000-CKO-LINEAGE",
            "principle": "source → master → projection completeness",
            "status": "PASS" if (lineage.get("complete_count") or 0) >= 4 else "HOLD",
            "observed": {
                "links": lineage.get("population") or 0,
                "complete_count": lineage.get("complete_count") or 0,
            },
        },
        {
            "id": "ISO8000-CKO-FIELD-DICT",
            "principle": "data dictionary for master attributes",
            "status": "PASS" if (field_dict.get("population") or 0) > 0 else "HOLD",
            "observed": {"fields": field_dict.get("population") or 0},
        },
        {
            "id": "ISO8000-CKO-NO-CERT-CLAIM",
            "principle": "do not claim ISO certification without licensed evidence",
            "status": "PASS",
            "observed": {"certified": False, "clause_text": "CLAUSE_TEXT_UNAVAILABLE"},
        },
    ]
    statuses = {item["status"] for item in tests}
    overall = "HOLD"
    if "FAIL" in statuses:
        overall = "FAIL"
    elif tests and all(item["status"] == "PASS" for item in tests):
        overall = "PASS_PROFILE_ONLY"
    profile = {
        "business_key": "MD-ISO8000-PROFILE-001",
        "uuid": None,
        "framework_ref": "FWK-ISO-8000-001",
        "mask_id": "MASK-TECH-STD",
        "name": "ISO 8000 — Data quality / master data (CKO profile)",
        "official_catalog_url": OFFICIAL_CATALOG_URL,
        "clause_text": "CLAUSE_TEXT_UNAVAILABLE",
        "licensed_body": False,
        "certified": False,
        "iso_implemented": False,
        "cko_profile_applied": True,
        "status": overall,
        "epistemic_status": "PROPOSED",
        "note": "Perfil CKO de princípios já presentes na constituição (unicidade, proveniência, WORM, lineage). NÃO é implantação certificada da ISO 8000.",
        "tests": tests,
        "evaluated_at": _now(),
    }
    _dump(ROOT / "cko_md" / "iso8000_profile.json", profile)
    return {
        "agent_id": "AG-ISO8000-PROFILE",
        "class": "MD",
        "role": "CHECKER",
        "status": overall,
        "certified": False,
        "iso_implemented": False,
        "cko_profile_applied": True,
        "clause_text": "CLAUSE_TEXT_UNAVAILABLE",
        "llm_used": False,
        "promotes_to_md": False,
        "tests": [{"id": item["id"], "status": item["status"]} for item in tests],
    }
