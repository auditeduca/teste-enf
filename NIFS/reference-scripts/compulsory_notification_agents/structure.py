"""Estruturação — texto raspado → registro NC vinculado à legislação pai."""
from __future__ import annotations

import json
import re
from pathlib import Path

from config import BASE_LEGISLATION, CN_DIR, PROMPTS_DIR


def _guess_periodicity(name: str, text: str) -> str:
    blob = f"{name} {text}".lower()
    if any(k in blob for k in ("óbito", "obito", "cólera", "colera", "botulismo", "raiva humana", "meningite")):
        return "immediate_24h"
    if "sentinela" in blob:
        return "sentinel"
    return "weekly"


def _guess_notify_levels(name: str, text: str) -> dict[str, bool]:
    blob = f"{name} {text}".lower()
    if any(k in blob for k in ("cólera", "colera", "botulismo", "covid", "tétano", "tetano")):
        return {"notify_ms": True, "notify_ses": True, "notify_sms": True}
    if "coqueluche" in blob:
        return {"notify_ms": True, "notify_ses": True, "notify_sms": False}
    return {"notify_ms": False, "notify_ses": False, "notify_sms": True}


def deterministic_structure(item: dict, scrape_context: dict | None = None) -> dict:
    name = item.get("condition_name_pt") or item.get("concept_code")
    text = ""
    if scrape_context:
        text = scrape_context.get("text_snippet") or ""
    periodicity = _guess_periodicity(name, text)
    levels = _guess_notify_levels(name, text)
    jur = item.get("jurisdiction_code") or "JUR.BR"
    return {
        "entity_code": item["entity_code"],
        "concept_code": item["concept_code"],
        "parent_entity_code": item.get("parent_entity_code") or BASE_LEGISLATION,
        "parent_entity_type": "LegislationInstrument",
        "jurisdiction_code": jur,
        "jurisdiction_level": item.get("jurisdiction_level") or ("state" if ".BR." in jur and jur != "JUR.BR" else "national"),
        "condition_name_pt": name,
        "cid10": [],
        "notification_periodicity": periodicity,
        **levels,
        "sinan_form": item.get("concept_code", "GERAL")[:32],
        "nursing_guidance_pt": (
            f"Notificação compulsória de {name}. "
            f"Periodicidade: {'imediata (24h)' if periodicity == 'immediate_24h' else 'semanal'}. "
            f"Registrar no SINAN/e-SUS conforme legislação pai {item.get('parent_entity_code')}."
        ),
        "evidence_grade": "B" if item.get("jurisdiction_level") == "state" else "A",
        "evidence_source": {
            "citation": item.get("source_url") or scrape_context.get("url") if scrape_context else "NKOS seed",
            "organization": "MS/SES" if jur == "JUR.BR" else "SES estadual",
            "year": 2026,
        },
        "source_id": item.get("source_id"),
        "mode": "deterministic",
    }


def llm_structure(item: dict, scrape_context: dict, *, api_key: str, model: str) -> dict:
    from apgar_agents.llm import chat_json  # noqa: WPS433

    system = (PROMPTS_DIR / "structure.md").read_text(encoding="utf-8")
    user = json.dumps({"queue_item": item, "scrape": scrape_context}, ensure_ascii=False, indent=2)
    out = chat_json(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        api_key=api_key,
        model=model,
    )
    if isinstance(out, dict):
        out.setdefault("entity_code", item["entity_code"])
        out.setdefault("concept_code", item["concept_code"])
        out.setdefault("parent_entity_code", item.get("parent_entity_code"))
        out.setdefault("parent_entity_type", "LegislationInstrument")
        out.setdefault("jurisdiction_code", item.get("jurisdiction_code", "JUR.BR"))
        out["mode"] = "deepseek"
    return out


def scrape_context_for_item(item: dict) -> dict | None:
    report = CN_DIR / "scrape_report.json"
    if not report.is_file():
        return None
    doc = json.loads(report.read_text(encoding="utf-8"))
    sid = item.get("source_id")
    for r in doc.get("results", []):
        if r.get("source_id") == sid:
            cache = r.get("cache_path")
            text = ""
            if cache and Path(cache).is_file():
                text = json.loads(Path(cache).read_text(encoding="utf-8")).get("text", "")[:4000]
            return {**r, "text_snippet": text}
    return None
