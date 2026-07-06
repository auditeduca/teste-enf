"""Resolve graph context for Studio agents."""
from __future__ import annotations

from paths import graph_relations_for, load_dataset, templates


def resolve_graph_context(
    *,
    entity_code: str | None = None,
    tool_code: str | None = None,
    topic: str | None = None,
    country: str = "BR",
    persona: str = "profissional",
) -> dict:
    code = tool_code or entity_code or ""
    if topic and not code:
        code = f"TOOL.{topic.upper().replace(' ', '_')}"

    tools = load_dataset("datasets/clinical/clinical_tools_catalog.json").get("records", [])
    tool = next((t for t in tools if t.get("tool_code") == code), None)

    npih = load_dataset("datasets/master-data/professional-intelligence/tool_professional_context.json")
    npih_ctx = npih.get("tools", {}).get(code, {}) if code else {}

    articles = load_dataset("datasets/content/editorial/articles.json").get("records", [])
    linked_articles = [a for a in articles if a.get("tool_code") == code][:5]

    relations = graph_relations_for(code) if code else []
    studio_templates = [t for t in templates() if t.get("tool_code") == code or not t.get("tool_code")]

    og = load_dataset("datasets/master-data/visual-intelligence/og_templates.json").get("templates", {})
    og_key = (tool or {}).get("acronym", topic or "ferramentas")
    if og_key:
        og_key = str(og_key).lower()

    return {
        "ok": True,
        "entity_code": code,
        "tool": tool,
        "persona": persona,
        "country": country,
        "graph": {
            "relations_count": len(relations),
            "relations": relations[:15],
            "linked_articles": linked_articles,
            "studio_templates_available": len(studio_templates),
        },
        "professional_context": npih_ctx,
        "visual": {
            "og_template_key": og_key if og_key in og else "ferramentas",
            "human_imagery_market": country,
        },
        "suggested_blocks": ["headline", "subheadline", "clinical_badge", "hero_visual", "brand_bar"],
    }
