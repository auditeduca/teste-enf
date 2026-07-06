"""Status for Clinical Article Factory."""
from __future__ import annotations

from paths import MD, load_articles, load_tools_catalog, tool_pain_registry


def collect_status() -> dict:
    articles = load_articles()
    registry = tool_pain_registry().get("tools", {})
    records = articles.get("records", [])
    problem = sum(1 for r in records if r.get("article_angle") == "problem")
    solution = sum(1 for r in records if r.get("article_angle") == "solution")
    tool_codes = {r.get("tool_code") for r in records if r.get("tool_code")}
    return {
        "program": "CLINICAL_ARTICLE_FACTORY",
        "articles_total": len(records),
        "problem_articles": problem,
        "solution_articles": solution,
        "tools_with_articles": len(tool_codes),
        "registry_tools_detailed": len(registry),
        "catalog_tools": len(load_tools_catalog()),
        "master_data_path": str(MD),
    }
