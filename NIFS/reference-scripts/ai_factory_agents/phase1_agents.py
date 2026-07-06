"""Phase 1 agent runners — stubs with structured outputs."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def _slug(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return s.upper()[:32]


def run_clinical_content(*, tool_name: str, tool_code: str | None = None, country: str = "BR", persona: str = "profissional") -> dict:
    articles_path = ROOT / "datasets/content/editorial/articles.json"
    article_count = 0
    if articles_path.exists():
        article_count = json.loads(articles_path.read_text(encoding="utf-8")).get("count", 0)

    return {
        "agent_id": "clinical_content",
        "status": "completed",
        "output": {
            "tool_name": tool_name,
            "tool_code": tool_code or f"TOOL.{_slug(tool_name)}",
            "sections": ["overview", "when_to_use", "interpretation", "documentation", "references"],
            "validation": {
                "sources_required": True,
                "legislation_checked": country == "BR",
                "protocols_linked": True,
            },
            "integration_hint": "POST /api/clinical-articles/generate",
            "articles_in_catalog": article_count,
        },
        "scores": {"accuracy": 90, "references": 85, "legislation": 88, "readability": 92},
    }


def run_developer(*, tool_name: str, tool_code: str | None = None) -> dict:
    code = tool_code or f"TOOL.{_slug(tool_name)}"
    return {
        "agent_id": "developer",
        "status": "completed",
        "output": {
            "tool_code": code,
            "artifacts": [
                {"type": "react_page", "path": f"platform/src/pages/tools/{code.replace('TOOL.', '')}Page.jsx", "status": "scaffold_suggested"},
                {"type": "api_route", "path": "scripts/nkp_api.py", "status": "extend_existing_patterns"},
                {"type": "master_data", "path": "datasets/clinical/clinical_tools_catalog.json", "status": "add_record"},
            ],
            "patterns": ["design_tokens", "clinical_tools_catalog", "nkp_api entity registry"],
        },
    }


def run_code_reviewer(*, paths: list[str] | None = None) -> dict:
    report_path = ROOT / "datasets/metadata/code_review_report.json"
    base = {"security": 93, "performance": 90, "accessibility": 96, "quality": 94}
    if report_path.exists():
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
            if isinstance(report.get("scores"), dict):
                base.update({k: v for k, v in report["scores"].items() if k in base})
        except json.JSONDecodeError:
            pass

    passed = all(base[k] >= 90 for k in ("security", "accessibility"))
    return {
        "agent_id": "code_reviewer",
        "status": "completed",
        "output": {
            "paths_reviewed": paths or ["scaffold"],
            "findings": [] if passed else [{"severity": "warning", "message": "Review humano recomendado antes do merge"}],
            "passed": passed,
        },
        "scores": base,
    }


def run_seo(*, tool_name: str, canonical_path: str | None = None) -> dict:
    slug = canonical_path or f"/ferramentas/{_slug(tool_name).lower().replace('_', '-')}"
    title = f"{tool_name} — Calculadora de Enfermagem | NKOS"
    return {
        "agent_id": "seo",
        "status": "completed",
        "output": {
            "title": title[:60],
            "meta_description": f"Calcule {tool_name} com referências clínicas, protocolos e contexto profissional. Gratuito para enfermeiros.",
            "canonical_path": slug,
            "schema": {"@type": "MedicalWebPage", "name": tool_name},
            "internal_links": ["/ferramentas", "/educacao", slug],
        },
        "scores": {"keywords": 88, "structure": 90, "schema": 85, "internal_links": 82},
    }


def run_visual_governance(*, page: str, tool_name: str) -> dict:
    og_key = _slug(tool_name).lower().replace("_", "")
    return {
        "agent_id": "visual_governance",
        "status": "completed",
        "output": {
            "og_template_suggested": og_key if og_key in ("braden", "glasgow", "apgar") else "ferramentas",
            "integration": "POST /api/visual-intelligence/generate",
            "audit_path": page,
        },
        "scores": {"brand": 97, "clinical": 95, "cultural": 94, "accessibility": 99},
    }


def run_regulatory(*, tool_name: str, tool_code: str | None = None, country: str = "BR") -> dict:
    code = tool_code or f"TOOL.{_slug(tool_name)}"
    npih_path = ROOT / "datasets/master-data/professional-intelligence/tool_professional_context.json"
    has_context = False
    if npih_path.exists():
        has_context = code in json.loads(npih_path.read_text(encoding="utf-8")).get("tools", {})

    return {
        "agent_id": "regulatory",
        "status": "completed",
        "output": {
            "country": country,
            "tool_code": code,
            "legislation_links_required": country == "BR",
            "npih_context_exists": has_context,
            "integration": "POST /api/professional-intelligence/regulatory/query",
            "impact_pages": [] if has_context else [f"/ferramentas/{_slug(tool_name).lower()}"],
        },
        "alerts": [] if has_context else [{"type": "missing_npih_context", "action": "add to tool_professional_context.json"}],
    }


AGENT_RUNNERS = {
    "clinical_content": lambda ctx: run_clinical_content(
        tool_name=ctx["tool_name"], tool_code=ctx.get("tool_code"), country=ctx.get("country", "BR"), persona=ctx.get("persona", "profissional"),
    ),
    "developer": lambda ctx: run_developer(tool_name=ctx["tool_name"], tool_code=ctx.get("tool_code")),
    "code_reviewer": lambda ctx: run_code_reviewer(paths=ctx.get("paths")),
    "seo": lambda ctx: run_seo(tool_name=ctx["tool_name"], canonical_path=ctx.get("canonical_path")),
    "visual_governance": lambda ctx: run_visual_governance(page=ctx.get("page", "/ferramentas"), tool_name=ctx["tool_name"]),
    "regulatory": lambda ctx: run_regulatory(tool_name=ctx["tool_name"], tool_code=ctx.get("tool_code"), country=ctx.get("country", "BR")),
}
