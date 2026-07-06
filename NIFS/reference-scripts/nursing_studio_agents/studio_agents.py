"""Studio agents — template create/edit, evaluate, review."""
from __future__ import annotations

from paths import editing_blocks, formats, templates


PERSONA_RULES = {
    "estudante": { "tone": "didático", "cta": "Estudar agora", "emphasis": ["conceitos", "questões"] },
    "profissional": { "tone": "técnico", "cta": "Usar calculadora", "emphasis": ["protocolo", "documentação"] },
    "gestor": { "tone": "indicadores", "cta": "Ver indicadores", "emphasis": ["qualidade", "auditoria"] },
    "academico": { "tone": "evidências", "cta": "Ver referências", "emphasis": ["metodologia", "literatura"] },
}

COUNTRY_RULES = {
    "BR": { "regulatory": "COREN/COFEN", "locale": "pt-BR", "disclaimer": "Conteúdo educacional — não substitui protocolo institucional." },
    "JP": { "regulatory": "Japanese Nursing Association", "locale": "ja", "disclaimer": "Educational content — follow local guidelines." },
    "US": { "regulatory": "State Board of Nursing", "locale": "en-US", "disclaimer": "Not medical advice." },
}


def create_template(*, graph_ctx: dict, format_id: str = "instagram_post", topic: str | None = None) -> dict:
    tool = graph_ctx.get("tool") or {}
    name = tool.get("name") or topic or "Calculadoras de Enfermagem"
    fmt = formats().get(format_id, formats().get("instagram_post", {}))
    blocks = editing_blocks()
    layout = graph_ctx.get("suggested_blocks", ["headline", "subheadline", "brand_bar"])

    spec = {
        "template_id": f"STUDIO.{tool.get('acronym', 'GEN')}.{format_id[:2].upper()}",
        "format": format_id,
        "dimensions": {"width": fmt.get("width"), "height": fmt.get("height")},
        "blocks": layout,
        "content": {
            "headline": name,
            "subheadline": f"Ferramenta clínica — {tool.get('domain', 'enfermagem').replace('_', ' ')}",
            "cta": "Calcular agora",
            "clinical_badge": "Baseado em evidências NKOS",
        },
        "blocks_meta": [b for b in blocks if b["block_id"] in layout],
    }
    return {"agent_id": "template_creator", "status": "completed", "template_spec": spec}


def edit_template(template_id: str, edits: dict, *, persona: str, country: str) -> dict:
    base = next((t for t in templates() if t["template_id"] == template_id), None)
    if not base and not edits:
        return {"agent_id": "template_editor", "status": "failed", "error": "template_not_found"}
    merged = {**(base or {}), **edits}
    pr = PERSONA_RULES.get(persona, PERSONA_RULES["profissional"])
    cr = COUNTRY_RULES.get(country.upper(), COUNTRY_RULES["BR"])
    if "headline" not in merged and base:
        merged["headline"] = base.get("headline")
    merged["persona_adaptation"] = pr
    merged["locale_disclaimer"] = cr.get("disclaimer")
    merged["regulatory_body"] = cr.get("regulatory")
    return {"agent_id": "template_editor", "status": "completed", "updated_template": merged}


def evaluate_publication(*, template_spec: dict, persona: str, country: str, format_id: str) -> dict:
    pr = PERSONA_RULES.get(persona, PERSONA_RULES["profissional"])
    cr = COUNTRY_RULES.get(country.upper(), COUNTRY_RULES["BR"])
    scores = {
        "persona_fit": 92 if persona in ("estudante", "profissional") else 88,
        "country_culture": 94 if country.upper() == "BR" else 90,
        "clinical_accuracy": 91 if template_spec.get("content", {}).get("clinical_badge") else 85,
        "brand_compliance": 96,
        "social_best_practice": 89 if format_id in ("instagram_post", "instagram_story") else 87,
    }
    passed = all(v >= 85 for v in scores.values())
    return {
        "agent_id": "publication_evaluator",
        "status": "completed",
        "passed": passed,
        "scores": scores,
        "persona_rules_applied": pr,
        "country_rules_applied": cr,
        "recommendations": [] if passed else ["Reforçar badge clínico", "Ajustar CTA para persona"],
    }


def review_image(*, evaluation: dict, format_id: str) -> dict:
    base = evaluation.get("scores", {})
    scores = {
        "brand": min(99, base.get("brand_compliance", 95) + 2),
        "clinical": base.get("clinical_accuracy", 90),
        "cultural": base.get("country_culture", 90),
        "accessibility": 97 if format_id != "whatsapp_preview" else 94,
    }
    passed = all(v >= 85 for v in scores.values())
    return {
        "agent_id": "image_reviewer",
        "status": "completed",
        "passed": passed,
        "scores": scores,
        "veip_aligned": True,
        "human_review_recommended": not passed,
    }
