"""Relaciona registros ANVISA com DrugReference e medication_dictionary."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from config import DRUG_REFS, ROOT


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def run_relate(*, medications: list[dict] | None = None) -> dict:
    if medications is None:
        from structure import structure_from_extract_report  # noqa: WPS433

        medications = structure_from_extract_report().get("medications", [])
    drug_doc = json.loads(DRUG_REFS.read_text(encoding="utf-8")) if DRUG_REFS.is_file() else {"records": []}
    by_name: dict[str, str] = {}
    by_reg: dict[str, str] = {}
    for dr in drug_doc.get("records", []):
        code = dr.get("entity_code") or dr.get("drug_ref_code")
        if dr.get("registration_number"):
            by_reg[_norm(dr["registration_number"])] = code
        for field in ("generic_name_pt", "brand_name_pt", "name_pt", "term_pt"):
            if dr.get(field):
                by_name[_norm(dr[field])] = code

    links = []
    matched = 0
    for med in medications:
        reg = _norm(med.get("registration_number", ""))
        name = _norm(med.get("product_name", ""))
        ingredient = _norm(med.get("active_ingredient", ""))
        drug_code = by_reg.get(reg) or by_name.get(name) or by_name.get(ingredient)
        if drug_code:
            matched += 1
            links.append({
                "entity_code": f"TLK.{med['entity_code']}.{drug_code.split('.')[-1]}",
                "anvisa_entity_code": med["entity_code"],
                "drug_reference_code": drug_code,
                "link_type": "anvisa_registration",
                "match_by": "registration" if by_reg.get(reg) else "name",
                "updated_at": _now(),
            })
    report = {
        "generated_at": _now(),
        "medications_total": len(medications),
        "drug_references_total": len(drug_doc.get("records", [])),
        "links_matched": matched,
        "new_links": links,
    }
    out = ROOT / "datasets" / "master-data" / "anvisa-open-data" / "relate_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
