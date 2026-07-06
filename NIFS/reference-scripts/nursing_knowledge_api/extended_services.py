"""Content, identity, education, regulation, career, jobs, research, visual, agent services."""
from __future__ import annotations

from paths import (
    articles,
    career_paths,
    learning_paths,
    load_dataset,
    user_profiles,
)


def list_articles(*, tool_code: str | None = None, limit: int = 20) -> dict:
    recs = articles()
    if tool_code:
        recs = [a for a in recs if a.get("tool_code") == tool_code]
    return {"ok": True, "count": len(recs), "articles": recs[:limit]}


def get_article(article_id: str) -> dict:
    for a in articles():
        if str(a.get("id")) == article_id or a.get("slug") == article_id:
            return {"ok": True, "article": a}
    return {"ok": False, "error": "article_not_found"}


def list_profile_templates() -> dict:
    return {"ok": True, "profiles": [
        {"profile_key": p.get("profile_key"), "label": p.get("label_pt"), "entity_code": p.get("entity_code")}
        for p in user_profiles()
    ]}


def resolve_profile(identity: dict) -> dict:
    key = identity.get("role", "student")
    profile_map = {
        "student": "estudante", "estudante": "estudante",
        "professional": "profissional", "profissional": "profissional",
        "manager": "gestor", "gestor": "gestor",
    }
    pk = profile_map.get(key, key)
    template = next((p for p in user_profiles() if p.get("profile_key") == pk), None)
    return {
        "ok": True,
        "identity": identity,
        "profile_template": template,
        "personalization": {
            "country": identity.get("country", "BR"),
            "level": identity.get("level", "beginner"),
            "interest": identity.get("interest"),
            "modules_priority": (template or {}).get("priority_modules", []),
        },
    }


def get_education_path(slug: str) -> dict:
    slug_norm = slug.upper().replace("-", "_")
    for lp in learning_paths():
        if slug_norm in (lp.get("path_code") or "").upper() or slug.lower() in (lp.get("title") or "").lower():
            return {"ok": True, "path": lp, "type": "learning_path"}
    for cp in career_paths():
        if ("ICU" in slug_norm or "INTENSIVE" in slug_norm) and cp.get("career_path_code") == "CAREER.ICU":
            return {"ok": True, "path": cp, "type": "career_path", "linked_learning": cp.get("linked_learning_path_codes", [])}
    return {"ok": False, "error": "path_not_found", "slug": slug}


def list_education_paths() -> dict:
    return {"ok": True, "count": len(learning_paths()), "paths": [
        {"slug": p.get("path_code", "").replace(".", "-").lower(), "title": p.get("title_pt"), "steps": p.get("step_count")}
        for p in learning_paths()[:30]
    ]}


def regulation_by_topic(country: str, topic: str) -> dict:
    cats = load_dataset("datasets/master-data/professional-intelligence/regulation_categories.json").get("categories", {})
    matched = {k: v for k, v in cats.items() if topic.lower() in k.lower() or topic.lower() in v.get("label", "").lower()}
    if not matched and topic.lower() in ("medication", "medicacao", "medicação"):
        matched = {"medication_safety": cats.get("medication_safety", {})}
    return {
        "ok": True,
        "country": country.upper(),
        "topic": topic,
        "categories": matched,
        "instruments": [inst for c in matched.values() for inst in c.get("br_instruments", [])] if country.upper() == "BR" else [],
    }


def get_career_path(slug: str) -> dict:
    slug_norm = slug.upper().replace("-", "_")
    for cp in career_paths():
        code = cp.get("career_path_code", "")
        if slug_norm in code or slug.lower() in (cp.get("title_pt") or "").lower():
            certs = load_dataset("datasets/master-data/professional-intelligence/certifications_registry.json").get("certifications", [])
            return {
                "ok": True,
                "path": cp,
                "competencies": cp.get("linked_tool_codes", []),
                "certifications_suggested": [c for c in certs if c.get("specialty") in ("critical_care", "emergency")][:3],
            }
    return {"ok": False, "error": "career_path_not_found"}


def list_career_paths() -> dict:
    return {"ok": True, "paths": [{"slug": c.get("career_path_code", "").replace("CAREER.", "").lower(), "title": c.get("title_pt")} for c in career_paths()]}


def job_match(profile: str, country: str, identity: dict | None = None) -> dict:
    exams = load_dataset("datasets/master-data/professional-intelligence/public_exams_seed.json").get("exams", [])
    missing = []
    compatibility = 85
    if "icu" in profile.lower() or "uti" in profile.lower():
        missing = ["ventilation", "hemodynamic_monitoring"] if country.lower() in ("brazil", "br") else ["ventilation"]
        compatibility = 92 if len(missing) <= 1 else 78
    return {
        "ok": True,
        "profile": profile,
        "country": country,
        "compatibility": compatibility,
        "missing_skills": missing,
        "matched_exams": exams[:2],
        "identity_context": identity,
    }


def research_trends() -> dict:
    arts = articles()
    topics: dict[str, int] = {}
    for a in arts:
        tc = a.get("tool_code") or "general"
        topics[tc] = topics.get(tc, 0) + 1
    top = sorted(topics.items(), key=lambda x: -x[1])[:10]
    return {
        "ok": True,
        "summary_pt": "Principais temas de pesquisa e conteúdo clínico em enfermagem nos datasets NKOS.",
        "trends": [{"topic": k, "count": v} for k, v in top],
        "integration": "NAKN — acervo TCC em expansão",
    }


def visual_generate_brief(*, country: str, persona: str, topic: str, style: str) -> dict:
    return {
        "ok": True,
        "brief": {"country": country, "persona": persona, "topic": topic, "style": style},
        "integration": "POST /api/visual-intelligence/generate",
        "suggested_template": topic.lower().replace(" ", "_") if topic else "ferramentas",
        "veip": True,
    }


def agent_run(agent_id: str, body: dict) -> dict:
    if agent_id in ("career-coach", "career_coach"):
        goal = body.get("user_goal") or body.get("goal", "")
        return {
            "ok": True,
            "agent": "career-coach",
            "status": "planned",
            "message": "Requer Nursing AI Agent API — Fase 3",
            "preview_plan": {
                "goal": goal,
                "steps": ["Avaliar competências", "Mapear certificações", "Trilha UTI", "Simulados"],
            },
        }
    return {"ok": False, "error": "agent_not_available", "agent_id": agent_id, "phase": 3}
