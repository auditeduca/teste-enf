"""Micro-fases M1–M10 + M11 tradução 30 idiomas."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "apgar_agents"))

from apgar.field_registry import canonical, modules  # noqa: E402
from apgar.i18n_catalog import LOCALE_MAP, all_locales  # noqa: E402
from apgar.validate_apgar import run_validation  # noqa: E402
from apgar_agents.phases.base import PhaseAgent  # noqa: E402

APGAR_DIR = ROOT / "datasets" / "master-data" / "apgar"


def _search_identity() -> dict:
    c = canonical()["identity"]
    return {"expected": c, "sources": ["canonical.json", "clinical_tools_catalog.json"]}


def _generate_identity(_search: dict) -> dict:
    return {"action": "sync legacy_uuid + canonical_url", "target": "master-data/apgar/canonical.json"}


def _review_ok(_s: dict, _g: dict) -> dict:
    return {"decision": "approve", "notes": "Identidade estável"}


def _validate_identity() -> dict:
    rep = run_validation()
    ids = [x for x in rep.passed + rep.errors if x["field_id"].startswith("APGAR.identity")]
    ok = not any(x["status"] == "fail" for x in ids)
    return {"ok": ok, "findings": ids}


def _search_clinical() -> dict:
    scl = canonical()["artifacts"]["APGAR_SCL_001"]
    return {"score_max": scl["score_max"], "components": [c["code"] for c in scl["components"]]}


def _generate_clinical(_s: dict) -> dict:
    return {"action": "apply_canonical.py", "fields": ["score_max", "interpretation_bands", "parameters"]}


def _review_clinical(_s: dict, g: dict) -> dict:
    return {"decision": "approve" if _s["score_max"] == 10 else "reject", "notes": "Apgar 1953"}


def _validate_clinical() -> dict:
    rep = run_validation()
    ids = [x for x in rep.passed + rep.errors if "scl." in x["field_id"]]
    ok = not any(x["status"] == "fail" for x in ids)
    return {"ok": ok, "findings": ids}


def _search_i18n() -> dict:
    path = APGAR_DIR / "i18n.json"
    if path.exists():
        doc = json.loads(path.read_text(encoding="utf-8"))
        return {"locale_count": len(doc.get("locales", [])), "expected": len(LOCALE_MAP)}
    return {"locale_count": 0, "expected": len(LOCALE_MAP)}


def _generate_i18n(_s: dict) -> dict:
    return {"action": "apply_canonical.py + i18n_catalog.py", "locales": list(LOCALE_MAP.keys())}


def _review_i18n(s: dict, _g: dict) -> dict:
    tier_ok = s.get("locale_count", 0) >= s.get("expected", 30)
    return {
        "decision": "approve" if tier_ok else "revise",
        "notes": f"{s.get('locale_count')}/{s.get('expected')} locales",
    }


def _validate_i18n() -> dict:
    rep = run_validation()
    ids = [x for x in rep.passed + rep.errors if "i18n" in x["field_id"]]
    ok = not any(x["status"] == "fail" for x in ids)
    return {"ok": ok, "findings": ids, "locale_count": len(all_locales())}


def _validate_full() -> dict:
    rep = run_validation()
    return {"ok": len(rep.errors) == 0, "errors": len(rep.errors), "warnings": len(rep.warnings)}


PHASE_AGENTS: list[PhaseAgent] = [
    PhaseAgent("M1", "Identidade e lineage", _search_identity, _generate_identity, _review_ok, _validate_identity),
    PhaseAgent("M2", "Instrumento clínico SCL", _search_clinical, _generate_clinical, _review_clinical, _validate_clinical),
    PhaseAgent("M3", "UI / field_configurations", _search_clinical, _generate_clinical, _review_clinical, _validate_clinical),
    PhaseAgent("M4", "Catálogo legacy", _search_identity, _generate_identity, _review_ok, _validate_identity),
    PhaseAgent("M5", "Grafo NNN", lambda: {"file": "ontology/apgar_edges.json"}, lambda s: {"sync": True}, _review_ok, _validate_full),
    PhaseAgent("M6", "Motor MCTS", lambda: {"engine": "clinical-engine/apgar"}, lambda s: {"demo": "npm run demo:apgar"}, _review_ok, _validate_full),
    PhaseAgent("M7", "Evidência", lambda: canonical()["official_sources"][0], lambda s: {"grade": "A"}, _review_ok, _validate_full),
    PhaseAgent("M8", "Internacionalização", _search_i18n, _generate_i18n, _review_i18n, _validate_i18n),
    PhaseAgent("M9", "Pipeline agentes", lambda: {"phases": 11}, lambda s: s, _review_ok, _validate_full),
    PhaseAgent("M10", "CI gate", lambda: modules(), lambda s: {"gate": "validate_apgar.py"}, _review_ok, _validate_full),
    PhaseAgent("M11", "Tradução 30 idiomas", _search_i18n, _generate_i18n, _review_i18n, _validate_i18n),
]
