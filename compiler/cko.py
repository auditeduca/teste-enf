from __future__ import annotations

from pathlib import Path
from typing import Any

from compiler.io import load_json, write_generated_json


def ref_to_text(ref: dict) -> str:
    if ref.get("text"):
        return ref["text"]
    authors = ", ".join(ref.get("authors", []))
    year = ref.get("year", "")
    title = ref.get("title", "")
    journal = ref.get("journal") or ref.get("publisher") or ""
    vol = ref.get("volume", "")
    pages = ref.get("pages", "")
    doi = ref.get("doi", "")
    parts = [p for p in [f"{authors} ({year}). {title}.", journal, vol, pages] if p]
    line = " ".join(parts).strip()
    if doi:
        line += f" doi:{doi}"
    return line


def find_calc_definition(data: dict, definition_code: str) -> dict | None:
    for item in data.get("records", []):
        if item.get("definition_code") == definition_code:
            return item
    return None


def apply_calc_definition(cko: dict, definition: dict) -> dict:
    meta = cko.setdefault("metadata", {})
    knowledge = cko.setdefault("knowledge", {})
    knowledge["definition_code"] = definition.get("definition_code", knowledge.get("definition_code"))
    knowledge["tool_code"] = definition.get("tool_code", knowledge.get("tool_code"))
    knowledge["clinical_purpose"] = definition.get("description_pt") or knowledge.get("clinical_purpose")
    if definition.get("score_min") is not None:
        knowledge["score_min"] = definition["score_min"]
    if definition.get("score_max") is not None:
        knowledge["score_max"] = definition["score_max"]
    if not meta.get("code"):
        meta["code"] = definition.get("acronym", meta.get("code"))
    bands = definition.get("interpretation_bands") or []
    if bands:
        ai = cko.setdefault("ai", {})
        reasoning = []
        for band in bands:
            label = band.get("label_pt") or band.get("label_en") or ""
            action = band.get("action_pt") or band.get("action_en") or ""
            lo, hi = band.get("min"), band.get("max")
            if lo is not None and hi is not None:
                reasoning.append(f"{lo}–{hi}: {label}. {action}".strip())
        if reasoning:
            ai["reasoning"] = reasoning
    return cko


def sync_v3_to_v1(v3: dict, overlay: dict) -> dict:
    """Compila CKO v3 + overlay UI → formato cko-v1 para runtime."""
    meta_v3 = v3.get("metadata", {})
    term = v3.get("terminology", {})
    np = v3.get("nursing_process", {})
    cr = v3.get("clinical_reasoning", {})
    ai_v3 = v3.get("ai", {})

    meta_overlay = overlay.get("metadata", {})
    runtime = overlay.get("runtime") or {}
    concept = v3.get("assessment_model", {}).get("concept", "avaliação clínica")
    concept_code = runtime.get("concept_code") or "APGAR"
    tool_code = runtime.get("tool_code") or "TOOL.APGAR"
    domains = runtime.get("domain") or ["neonatology", "obstetrics", "nursing"]
    edges_file = runtime.get("edges_file") or "js/modules/data/apgar-edges.json"
    clinical_purpose = runtime.get("clinical_purpose") or (
        f"Avaliar {concept.lower()} no 1º e 5º minuto de vida"
    )
    seo_title = meta_overlay.get("seo", {}).get("title") or meta_v3.get("name", "Ferramenta")
    default_limitations = (
        "Não diagnosticar asfixia perinatal isoladamente; interpretar com gasometria de cordão."
        if concept_code == "APGAR"
        else "O GCS isolado não substitui exame neurológico completo nem neuroimagem."
    )
    v1: dict[str, Any] = {
        "schema_version": "cko-v1",
        "metadata": {
            "id": meta_overlay.get("id"),
            "code": v3.get("cko_id", "CKO-UNKNOWN"),
            "slug": meta_overlay.get("slug", "apgar"),
            "version": meta_v3.get("version", "1.0.0"),
            "status": "published",
            "seo": {
                "title": seo_title,
                "description": meta_overlay.get("seo", {}).get("description", ""),
                "canonical": meta_overlay.get("seo", {}).get("canonical", ""),
            },
            "breadcrumb": {
                "category": meta_v3.get("domain", ""),
                "categoryHref": meta_overlay.get("breadcrumb", {}).get("categoryHref", "index.html#calculadoras"),
            },
        },
        "knowledge": {
            "concept_code": concept_code,
            "tool_code": tool_code,
            "domain": domains,
            "clinical_purpose": clinical_purpose,
            "terminology": {
                "snomed": [
                    m.get("code", "")
                    for m in v3.get("interoperability", {}).get("OMOP", {}).get("mappings", [])
                    if m.get("vocabulary") == "SNOMED"
                ],
                "loinc": [
                    m.get("code", "")
                    for m in v3.get("interoperability", {}).get("OMOP", {}).get("mappings", [])
                    if m.get("vocabulary") == "LOINC"
                ],
                "related_diagnosis_codes": [
                    f"NANDA.{n['code']}" for n in term.get("nanda", []) if n.get("code")
                ],
                "nanda": [{"code": n["code"]} for n in term.get("nanda", []) if n.get("code")],
                "nic": [{"code": n["code"]} for n in term.get("nic", []) if n.get("code")],
                "noc": [{"code": n["code"]} for n in term.get("noc", []) if n.get("code")],
            },
        },
        "reasoning": {
            "edges_file": edges_file,
            "sae": {
                "nanda": [{"code": c} for c in (np.get("diagnosis_codes") or [])],
                "nic": [{"code": c} for c in (np.get("intervention_codes") or [])],
                "noc": [{"code": c} for c in (np.get("outcome_codes") or [])],
            },
        },
        "evidence": {
            "limitations": runtime.get("evidence_limitations") or default_limitations,
            "evidence_level": "I",
        },
        "ai": {
            "summary": ai_v3.get("summary", ""),
            "clinicalPearls": ai_v3.get("clinical_pearls", []),
            "commonErrors": ai_v3.get("common_errors", []),
            "contraindications": [],
            "explainLikeResident": (cr.get("hypotheses") or [""])[0],
            "keywords": ai_v3.get("keywords", []),
            "reasoning": cr.get("recommendations", []),
            "clinical_reasoning": cr,
            "machine_representation": ai_v3.get("machine_representation"),
        },
        "interoperability": v3.get("interoperability", {}),
        "presentation": overlay.get("presentation", {}),
        "_source_cko_v3": v3.get("cko_id"),
    }

    if concept_code == "APGAR":
        v1["knowledge"]["timing_minutes"] = [1, 5]

    if not v1["reasoning"]["sae"]["nanda"]:
        v1["reasoning"]["sae"]["nanda"] = [{"code": n["code"]} for n in term.get("nanda", []) if n.get("code")]
    if not v1["reasoning"]["sae"]["nic"]:
        v1["reasoning"]["sae"]["nic"] = [{"code": n["code"]} for n in term.get("nic", []) if n.get("code")]
    if not v1["reasoning"]["sae"]["noc"]:
        v1["reasoning"]["sae"]["noc"] = [{"code": n["code"]} for n in term.get("noc", []) if n.get("code")]

    refs = v3.get("knowledge_sources", {}).get("references", [])
    v1["evidence"]["references"] = [{"text": ref_to_text(r)} for r in refs]
    if refs:
        v1["evidence"]["foundation"] = ref_to_text(refs[0])
    v1["evidence"]["validation"] = (
        "Validado por " + meta_v3.get("validated_by", "evidência clínica")
        + f" (revisão {meta_v3.get('last_review', '')})."
    )
    return v1
