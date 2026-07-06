"""Micro-fases M1–M9 — conteúdos pendentes."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "content_agents"))
sys.path.insert(0, str(ROOT / "scripts" / "apgar_agents"))

from apgar_agents.phases.base import PhaseAgent  # noqa: E402
from content.field_registry import canonical, modules, pending_items  # noqa: E402
from content.validate_content import run_validation  # noqa: E402


def _search_registry() -> dict:
    p = pending_items()
    return {"total": p.get("total"), "counts": p.get("counts_by_type")}


def _generate_registry(_s: dict) -> dict:
    return {"action": "pending_catalog.py", "note": "Regenerar fila a partir da proposta"}


def _review_approve(_s: dict, _g: dict) -> dict:
    return {"decision": "approve", "notes": "Registry estrutural OK"}


def _validate_registry() -> dict:
    rep = run_validation(write_report=False)
    ok = not any(e["field_id"].startswith("CONTENT.registry") for e in rep.errors)
    return {"ok": ok, "errors": len(rep.errors)}


def _search_type(type_code: str) -> dict:
    items = [i for i in pending_items().get("items", []) if i.get("artifact_type") == type_code]
    return {"type": type_code, "pending_count": len(items), "sample": items[:3]}


def _generate_type(s: dict) -> dict:
    return {"action": "run_field_pipeline", "type": s["type"], "fields": f"CONTENT.{s['type']}.*"}


def _review_type(s: dict, _g: dict) -> dict:
    return {"decision": "revise" if s.get("pending_count", 0) > 0 else "approve", "notes": f"{s.get('pending_count')} pendentes"}


def _validate_type(type_code: str) -> dict:
    rep = run_validation(write_report=False)
    prefix = f"CONTENT.{type_code}"
    related = [e for e in rep.errors if prefix.lower() in e.get("field_id", "").lower() or type_code in e.get("field_id", "")]
    return {"ok": len(related) == 0, "findings": related}


def _search_agents() -> dict:
    return {"pipeline": canonical().get("agent_pipeline"), "prompts": 4}


def _generate_agents(_s: dict) -> dict:
    return {"action": "LangGraph 4 nodes", "roles": ["search", "generate", "review", "validate"]}


def _validate_agents() -> dict:
    prompts = ROOT / "scripts" / "content_agents" / "prompts"
    ok = all((prompts / n).exists() for n in ("search.md", "generate.md", "review.md", "validate.md"))
    return {"ok": ok}


def _validate_ci() -> dict:
    rep = run_validation(write_report=True)
    return {"ok": len(rep.errors) == 0, "checks": rep.checks, "errors": len(rep.errors)}


PHASE_AGENTS = [
    PhaseAgent("M1", "Registro e fila", _search_registry, _generate_registry, _review_approve, _validate_registry),
    PhaseAgent("M2", "Flashcards FLA", lambda: _search_type("FLA"), _generate_type, _review_type, lambda: _validate_type("FLA")),
    PhaseAgent("M3", "Simulados SIM", lambda: _search_type("SIM"), _generate_type, _review_type, lambda: _validate_type("SIM")),
    PhaseAgent("M4", "Mapas mentais MMP", lambda: _search_type("MMP"), _generate_type, _review_type, lambda: _validate_type("MMP")),
    PhaseAgent("M5", "Protocolos PRT", lambda: _search_type("PRT"), _generate_type, _review_type, lambda: _validate_type("PRT")),
    PhaseAgent("M6", "Guias de bolso PKT", lambda: _search_type("PKT"), _generate_type, _review_type, lambda: _validate_type("PKT")),
    PhaseAgent("M7", "FAQ", lambda: _search_type("FAQ"), _generate_type, _review_type, lambda: _validate_type("FAQ")),
    PhaseAgent("M8", "Pipeline agentes", _search_agents, _generate_agents, lambda _s, _g: {"decision": "approve"}, _validate_agents),
    PhaseAgent("M9", "Gate CI", lambda: {"validator": "validate_content.py"}, lambda _s: {"action": "run_validation"}, _review_approve, _validate_ci),
]
