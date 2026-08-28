#!/usr/bin/env python3
"""Sincroniza CKO-APGAR-001 (v3) → apgar-cko.json (cko-v1 para a UI)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V3_PATH = ROOT / "NIFS/DELIVERY/js/modules/data/cko/CKO-APGAR-001.json"
V1_PATH = ROOT / "NIFS/DELIVERY/js/modules/data/apgar-cko.json"


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


def sync(v3: dict, v1: dict) -> dict:
    meta = v3.get("metadata", {})
    v1["metadata"]["version"] = meta.get("version", v1["metadata"].get("version"))
    v1["metadata"]["code"] = "CKO-APGAR-001"
    v1["metadata"]["status"] = "published"
    if meta.get("name"):
        v1["metadata"]["seo"]["title"] = f"{meta['name']} - Avaliação do Recém-Nascido"
    if meta.get("domain"):
        v1["metadata"]["breadcrumb"]["category"] = meta["domain"]

    model = v3.get("assessment_model", {})
    v1["knowledge"]["clinical_purpose"] = (
        f"Avaliar {model.get('concept', 'vitalidade neonatal').lower()} no 1º e 5º minuto de vida"
    )
    term = v3.get("terminology", {})
    v1["knowledge"]["terminology"] = {
        "snomed": [
            m.get("code", "") for m in v3.get("interoperability", {}).get("OMOP", {}).get("mappings", [])
            if m.get("vocabulary") == "SNOMED"
        ],
        "loinc": [
            m.get("code", "") for m in v3.get("interoperability", {}).get("OMOP", {}).get("mappings", [])
            if m.get("vocabulary") == "LOINC"
        ],
        "related_diagnosis_codes": [f"NANDA.{n['code']}" for n in term.get("nanda", []) if n.get("code")],
        "nanda": term.get("nanda", []),
        "nic": term.get("nic", []),
        "noc": term.get("noc", []),
    }

    np = v3.get("nursing_process", {})
    v1["reasoning"]["sae"] = {
        "nanda": [
            {"diagnosis": d.split(" (")[0], "definition": d}
            for d in np.get("diagnosis", [])
        ],
        "nic": [
            {"intervention": i.split(" (")[0], "activities": [i]}
            for i in np.get("interventions", [])
        ],
        "noc": [
            {"outcome": o.split(" (")[0], "indicators": [o]}
            for o in np.get("outcomes", [])
        ],
    }

    cr = v3.get("clinical_reasoning", {})
    ai = v3.get("ai", {})
    v1["ai"] = {
        "summary": ai.get("summary", v1["ai"].get("summary")),
        "clinicalPearls": ai.get("clinical_pearls", v1["ai"].get("clinicalPearls", [])),
        "commonErrors": ai.get("common_errors", v1["ai"].get("commonErrors", [])),
        "contraindications": v1["ai"].get("contraindications", []),
        "explainLikeResident": cr.get("hypotheses", [""])[0] if cr.get("hypotheses") else v1["ai"].get("explainLikeResident"),
        "keywords": ai.get("keywords", v1["ai"].get("keywords", [])),
        "reasoning": cr.get("recommendations", v1["ai"].get("reasoning", [])),
        "clinical_reasoning": cr,
        "machine_representation": ai.get("machine_representation"),
    }

    ks = v3.get("knowledge_sources", {})
    refs = ks.get("references", [])
    v1["evidence"]["references"] = [{"text": ref_to_text(r)} for r in refs]
    if refs:
        v1["evidence"]["foundation"] = ref_to_text(refs[0])
    v1["evidence"]["validation"] = (
        "Validado por " + meta.get("validated_by", "evidência clínica") + f" (revisão {meta.get('last_review', '')})."
    )

    v1["interoperability"] = v3.get("interoperability", v1.get("interoperability", {}))
    v1["_source_cko_v3"] = v3.get("cko_id", "CKO-APGAR-001")
    return v1


def main() -> None:
    v3 = json.loads(V3_PATH.read_text(encoding="utf-8"))
    v1 = json.loads(V1_PATH.read_text(encoding="utf-8"))
    updated = sync(v3, v1)
    V1_PATH.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Sincronizado: {V3_PATH.name} → {V1_PATH.name}")


if __name__ == "__main__":
    main()
