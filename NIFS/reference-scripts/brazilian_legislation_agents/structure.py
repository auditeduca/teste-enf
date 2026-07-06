"""Etapa structure — normaliza corpus e provisions."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from config import BL_DIR, INSTRUMENTS, PROMPTS_DIR


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def structure_corpus_from_extract(extract_result: dict, *, domain_code: str) -> dict:
    parent = extract_result["parent_entity_code"]
    slug = parent.replace("LEG.BR.", "")
    text_len = extract_result.get("text_length", 0)
    n_arts = len(extract_result.get("articles", []))
    return {
        "entity_code": f"CORP.{slug}.001",
        "concept_code": f"{slug}_CORPUS",
        "parent_entity_code": parent,
        "parent_entity_type": "LegislationInstrument",
        "domain_code": domain_code,
        "summary_pt": (
            f"Corpus condensado de {parent} — {n_arts} dispositivos extraídos "
            f"({text_len} chars fonte). Atualizado por agente."
        ),
        "key_topics": [],
        "content_hash": extract_result.get("content_hash"),
        "last_sync_at": _now(),
        "provision_count": n_arts,
        "status": "published",
        "content_source": "BRAZILIAN_LEGISLATION_AGENT",
    }


def structure_provision(article: dict, *, domain_code: str, jurisdiction_code: str = "JUR.BR") -> dict:
    return {
        **article,
        "domain_code": domain_code,
        "jurisdiction_code": jurisdiction_code,
        "professional_scope": article.get("professional_scope") or ["enfermagem", "multiprofissional"],
        "nursing_relevance_pt": article.get("nursing_relevance_pt")
        or f"Dispositivo {article.get('article_label')} — revisar aplicabilidade à prática de enfermagem e SUS.",
        "evidence_grade": "A",
        "status": "published",
        "content_source": "BRAZILIAN_LEGISLATION_AGENT",
        "updated_at": _now(),
    }


def structure_from_extract_report(*, limit: int | None = None) -> dict:
    report_path = BL_DIR / "extract_report.json"
    if not report_path.is_file():
        from extract import extract_all  # noqa: WPS433

        extract_all(limit=limit)

    extract_doc = json.loads(report_path.read_text(encoding="utf-8"))
    instruments = {
        r["entity_code"]: r
        for r in json.loads(INSTRUMENTS.read_text(encoding="utf-8")).get("records", [])
    }
    corpus_items = []
    provisions = []
    for res in extract_doc.get("results", []):
        parent = res.get("parent_entity_code")
        inst = instruments.get(parent, {})
        domain = inst.get("domain_code") or "LEX_DOM.BR.SUS"
        if res.get("articles"):
            corpus_items.append(structure_corpus_from_extract(res, domain_code=domain))
            for art in res["articles"]:
                provisions.append(structure_provision(art, domain_code=domain))
        if limit and len(provisions) >= limit:
            break

    return {
        "corpus": corpus_items,
        "provisions": provisions[:limit] if limit else provisions,
        "structured_at": _now(),
    }
