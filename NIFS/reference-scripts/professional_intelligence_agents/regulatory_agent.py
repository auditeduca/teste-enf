"""Regulatory Nursing Agent — stub for professional scope questions."""
from __future__ import annotations

from paths import regulation_categories, tool_professional_context


PROCEDURE_KEYWORDS = {
    "medicação": ["medication_safety", "professional_practice"],
    "medicamento": ["medication_safety", "professional_practice"],
    "procedimento": ["professional_practice", "patient_safety"],
    "notificação": ["patient_safety"],
    "braden": ["patient_safety", "management"],
    "glasgow": ["professional_practice", "patient_safety"],
}


def query_regulatory(
    question: str,
    *,
    country: str = "BR",
    state: str | None = None,
    role: str = "enfermeiro",
    formation: str | None = None,
) -> dict:
    q = question.lower()
    matched_cats = []
    for kw, cats in PROCEDURE_KEYWORDS.items():
        if kw in q:
            matched_cats.extend(cats)
    matched_cats = list(dict.fromkeys(matched_cats)) or ["professional_practice"]

    cats = regulation_categories().get("categories", {})
    refs = []
    for cat_id in matched_cats:
        cat = cats.get(cat_id, {})
        for inst in cat.get("br_instruments", []):
            refs.append({
                "instrument_code": inst,
                "category": cat_id,
                "category_label": cat.get("label"),
            })

    br_instruments = {
        "LEG.BR.LEI.7498.1986": {
            "title": "Lei 7.498/1986 — Exercício profissional da enfermagem",
            "authority": "Presidência da República",
            "summary": "Define atribuições de enfermeiro, técnico e auxiliar.",
        },
        "LEG.BR.COFEN.RES.688.2022": {
            "title": "Resolução COFEN 688/2022 — Código de Ética",
            "authority": "COFEN",
            "summary": "Deveres, direitos e responsabilidades éticas.",
        },
        "LEG.BR.LEI.8080.1990": {
            "title": "Lei 8.080/1990 — Lei Orgânica da Saúde",
            "authority": "Presidência da República",
            "summary": "Direito à saúde e organização do SUS.",
        },
        "LEG.BR.MS.PC4.2017": {
            "title": "Portaria MS — Notificação compulsória",
            "authority": "Ministério da Saúde",
            "summary": "Lista de agravos de notificação compulsória.",
        },
    }

    enriched_refs = []
    for r in refs:
        meta = br_instruments.get(r["instrument_code"], {})
        enriched_refs.append({**r, **meta})

    answer = (
        f"Conforme a legislação aplicável ao exercício da enfermagem no {country}"
        + (f" (estado {state})" if state else "")
        + f", na função de {role}"
        + (f" com formação {formation}" if formation else "")
        + ", a conduta deve respeitar atribuições legais, protocolos institucionais "
        "e registro documental. Esta resposta é orientativa — confirme com COREN local e protocolo da instituição."
    )

    return {
        "ok": True,
        "agent": "Regulatory Nursing Agent",
        "question": question,
        "context": {"country": country, "state": state, "role": role, "formation": formation},
        "answer": answer,
        "references": enriched_refs,
        "categories_analyzed": matched_cats,
        "disclaimer": "Orientação educacional — não substitui parecer jurídico ou decisão clínica.",
        "tools_with_context": list(tool_professional_context().get("tools", {}).keys()),
    }
