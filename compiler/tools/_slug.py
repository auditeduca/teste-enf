from __future__ import annotations

"""Mapeamento slug JSON ↔ HTML publicado."""

HTML_SLUG_BY_TOOL: dict[str, str] = {
    "escala-de-glasgow": "glasgow",
    "escala-de-braden": "braden",
    "escala-de-morse": "morse",
}

DEDICATED_BUILDERS = frozenset({"apgar", "glasgow"})


def canonical_slug(tool_slug: str) -> str:
    return HTML_SLUG_BY_TOOL.get(tool_slug, tool_slug)


def page_slug_to_tool_slug(page_slug: str) -> str:
    for tool_slug, html_slug in HTML_SLUG_BY_TOOL.items():
        if html_slug == page_slug:
            return tool_slug
    return page_slug
