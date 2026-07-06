"""Status for Nursing Professional Intelligence Hub."""
from __future__ import annotations

from paths import (
    MD,
    alert_rules,
    career_maps,
    career_paths,
    certifications,
    legislation_tool_links,
    public_exams,
    regulation_categories,
    tool_professional_context,
)


def collect_status() -> dict:
    tools = tool_professional_context().get("tools", {})
    cats = regulation_categories().get("categories", {})
    exams = public_exams().get("exams", [])
    certs = certifications().get("certifications", [])
    countries = career_maps().get("countries", {})
    alerts = alert_rules().get("rules", [])
    leg_links = legislation_tool_links().get("records", legislation_tool_links().get("links", []))
    paths = career_paths().get("paths", career_paths().get("records", []))

    return {
        "program": "NPIH",
        "name": "Nursing Professional Intelligence Hub",
        "tools_with_professional_context": len(tools),
        "regulation_categories": len(cats),
        "public_exams_seed": len(exams),
        "certifications": len(certs),
        "career_countries": len(countries),
        "alert_rules": len(alerts),
        "legislation_tool_links": len(leg_links),
        "career_paths_community": len(paths) if isinstance(paths, list) else 0,
        "entities": [
            "laws", "regulations", "professional_bodies", "certifications", "careers",
            "jobs", "public_exams", "competencies", "skills", "institutions", "salary_data", "alerts",
        ],
        "master_data_path": str(MD),
        "tool_codes": list(tools.keys()),
    }
