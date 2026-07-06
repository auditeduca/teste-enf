"""Resolve clinical result + professional context for a tool."""
from __future__ import annotations

from paths import (
    career_maps,
    legislation_tool_links,
    regulation_categories,
    tool_professional_context,
)


def resolve_tool_context(
    tool_code: str,
    *,
    persona: str = "profissional",
    country: str = "BR",
    clinical_result: str | None = None,
) -> dict:
    ctx_data = tool_professional_context().get("tools", {})
    entry = ctx_data.get(tool_code)
    if not entry:
        return {
            "ok": False,
            "tool_code": tool_code,
            "error": "tool_not_in_professional_context",
            "available_tools": list(ctx_data.keys()),
        }

    adaptation = (entry.get("persona_adaptation") or {}).get(persona, {})
    links = legislation_tool_links().get("records", legislation_tool_links().get("links", []))
    extra_links = [l for l in links if l.get("tool_code") == tool_code]

    return {
        "ok": True,
        "tool_code": tool_code,
        "display_name": entry.get("display_name"),
        "country": country,
        "persona": persona,
        "clinical_result": clinical_result or entry.get("clinical_result_example"),
        "technical_basis": entry.get("technical_basis", {}),
        "legislation": entry.get("legislation", []),
        "legislation_graph_links": extra_links,
        "professional_duties": entry.get("professional_duties", []),
        "documentation_required": entry.get("documentation_required", []),
        "best_practices": entry.get("best_practices", []),
        "exam_topics": entry.get("exam_topics", []),
        "persona_adaptation": adaptation,
        "regulation_categories": list(regulation_categories().get("categories", {}).keys()),
    }
