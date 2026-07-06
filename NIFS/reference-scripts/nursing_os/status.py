"""Nursing OS — status aggregator across domains."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MD = ROOT / "datasets" / "master-data"


def _load(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _file_exists(rel: str) -> bool:
    return (ROOT / rel).exists()


def collect_status() -> dict:
    canon = _load(MD / "nursing-os" / "canonical.json")
    domains = _load(MD / "nursing-os" / "domains.json").get("domains", [])
    phases = _load(MD / "nursing-os" / "phases.json").get("phases", [])

    domain_status = []
    for d in domains:
        path = MD / d.get("path", "")
        if not path.suffix:
            path = path / "canonical.json"
        domain_status.append({
            "domain_id": d["domain_id"],
            "name": d["name"],
            "maturity": d.get("maturity", "unknown"),
            "canonical_exists": path.exists() if path.is_file() else (path.parent / "canonical.json").exists(),
            "api_prefix": d.get("api_prefix"),
            "platform_route": d.get("platform_route"),
        })

    veip_og = _load(MD / "visual-intelligence" / "og_manifest.json")
    articles = _load(ROOT / "datasets/content/editorial/articles.json")
    agents = _load(MD / "nursing-ai-agents" / "agents_registry.json")

    return {
        "program": canon.get("program_code", "NURSING_OS"),
        "name": canon.get("name"),
        "pillars": canon.get("pillars", []),
        "domains": domain_status,
        "phases": phases,
        "metrics": {
            "og_templates": len(_load(MD / "visual-intelligence" / "og_templates.json").get("templates", {})),
            "og_manifest_entries": len(veip_og.get("entries", {})),
            "clinical_articles": articles.get("count", 0),
            "ai_agents_registered": len(agents.get("agents", [])),
            "human_imagery_markets": len(_load(MD / "visual-intelligence" / "human_imagery_system.json").get("markets", {})),
            "npih_tools_context": len(_load(MD / "professional-intelligence" / "tool_professional_context.json").get("tools", {})),
            "npih_career_countries": len(_load(MD / "professional-intelligence" / "career_maps_by_country.json").get("countries", {})),
            "ai_factory_agents": len(_load(MD / "ai-factory" / "agents_registry.json").get("agents", [])),
            "ai_factory_phase1": len(_load(MD / "ai-factory" / "agents_registry.json").get("phase1_priority", [])),
            "nka_services": len(_load(MD / "nursing-knowledge-api" / "services_registry.json").get("services", {})),
            "studio_formats": len(_load(MD / "nursing-studio" / "social_formats.json").get("formats", {})),
        },
        "integrations": {
            "veip": _file_exists("scripts/visual_intelligence_agents/run_batch.py"),
            "clinical_articles": _file_exists("scripts/clinical_article_agents/run_batch.py"),
            "context_engine": _file_exists("datasets/master-data/context-engine/canonical.json"),
            "nakn": _file_exists("datasets/master-data/academic-knowledge/work_schema.json"),
            "npih": _file_exists("scripts/professional_intelligence_agents/run_batch.py"),
            "ai_factory": _file_exists("scripts/ai_factory_agents/run_batch.py"),
            "nka": _file_exists("scripts/nursing_knowledge_api/run_batch.py"),
            "studio": _file_exists("scripts/nursing_studio_agents/run_batch.py"),
        },
        "npih": _load(MD / "professional-intelligence" / "canonical.json"),
        "ai_factory": _load(MD / "ai-factory" / "canonical.json"),
        "nursing_knowledge_api": _load(MD / "nursing-knowledge-api" / "canonical.json"),
        "nursing_studio": _load(MD / "nursing-studio" / "canonical.json"),
    }


def resolve_context(body: dict) -> dict:
    """Resolve adaptive outputs from context DNA."""
    persona = body.get("persona", "profissional")
    locale = body.get("locale", "pt-BR")
    mode = body.get("mode", "professional")
    tool = body.get("tool_code")

    country = body.get("country") or locale.split("-")[-1].upper()
    if len(country) > 2:
        country = {"pt": "BR", "en": "US", "ja": "JP", "zh": "CN", "de": "DE", "fr": "FR", "ar": "SA"}.get(locale.split("-")[0], "BR")

    human = _load(MD / "visual-intelligence" / "human_imagery_system.json")
    market = human.get("markets", {}).get(country, {})

    agents_reg = _load(MD / "nursing-ai-agents" / "agents_registry.json")
    agent = "clinical"
    if mode == "study" or persona == "estudante":
        agent = "education"
    elif persona == "gestor":
        agent = "management"
    elif persona == "academico":
        agent = "academic"
    if body.get("intent") == "visual_request":
        agent = "visual"
    elif body.get("intent") == "regulatory_question":
        agent = "regulatory"
    elif body.get("intent") == "exam_prep":
        agent = "exam_prep"

    npih = {}
    if tool:
        ctx_file = MD / "professional-intelligence" / "tool_professional_context.json"
        ctx_data = _load(ctx_file).get("tools", {}).get(tool, {})
        if ctx_data:
            npih = {
                "has_professional_context": True,
                "persona_adaptation": (ctx_data.get("persona_adaptation") or {}).get(persona, {}),
                "exam_topics": ctx_data.get("exam_topics", []),
            }

    return {
        "context": body,
        "country": country,
        "ux": {
            "layout_density": "minimal" if mode == "emergency" else "balanced",
            "copy_tone": "technical" if persona == "gestor" else "supportive",
        },
        "visual": {
            "human_imagery": market,
            "og_page": tool.lower().replace("tool.", "") if tool else body.get("page_type", "home"),
            "archetype": human.get("archetypes", {}).get("clinical_professional"),
        },
        "ai": {
            "recommended_agent": agent,
            "agents_available": [a["agent_id"] for a in agents_reg.get("agents", [])],
        },
        "professional_intelligence": npih,
    }
