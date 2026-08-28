from __future__ import annotations

import json
import re
from pathlib import Path

from compiler.io import mirror_under_delivery, write_generated_json
from compiler.paths import DATA, ROOT
from compiler.tools._slug import DEDICATED_BUILDERS, canonical_slug

TOOLS_DIR = ROOT / "reference-website" / "data" / "tools"
EXCLUDED = frozenset({"calculadora-template", "calculadora-template-v2", "calculadora-preview"})

ICON_BY_CATEGORY: dict[str, str] = {
    "Neonatologia": "i-baby",
    "Emergência": "i-stetho",
    "Emergência e Terapia Intensiva": "i-stetho",
    "Avaliação Neurológica": "i-brain",
    "Nutrição": "i-scale",
    "Dor": "i-pulse",
    "Geriatria": "i-person",
    "Pediatria": "i-baby",
}


def _first_line(text: str) -> str:
    for line in str(text or "").split("\n"):
        cleaned = re.sub(r"^[•\-\s]+", "", line).strip()
        if cleaned:
            return cleaned
    return ""


def _load_all_tools() -> list[dict]:
    tools: list[dict] = []
    for path in sorted(TOOLS_DIR.glob("*.json")):
        if path.stem in EXCLUDED:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        data["_source"] = str(path.relative_to(ROOT))
        tools.append(data)
    return tools


def _related_tools(tool: dict, all_tools: list[dict], limit: int = 6) -> list[dict]:
    category = (tool.get("breadcrumb") or {}).get("category", "")
    name = (tool.get("overview") or {}).get("name", "")
    slug = canonical_slug(tool.get("slug", ""))
    related: list[dict] = []
    for other in all_tools:
        other_slug = canonical_slug(other.get("slug", ""))
        if other_slug == slug or other_slug in DEDICATED_BUILDERS:
            continue
        other_cat = (other.get("breadcrumb") or {}).get("category", "")
        if category and other_cat == category:
            ov = other.get("overview") or {}
            related.append(
                {
                    "href": f"{other_slug}.html",
                    "title": ov.get("name") or other_slug,
                    "desc": (ov.get("objective") or "Ferramenta relacionada")[:120],
                    "icon": ov.get("icon") or "i-clipboard",
                }
            )
    if len(related) < limit:
        for other in all_tools:
            other_slug = canonical_slug(other.get("slug", ""))
            if other_slug == slug or any(r["href"] == f"{other_slug}.html" for r in related):
                continue
            ov = other.get("overview") or {}
            related.append(
                {
                    "href": f"{other_slug}.html",
                    "title": ov.get("name") or other_slug,
                    "desc": (ov.get("objective") or "Ferramenta relacionada")[:120],
                    "icon": ov.get("icon") or "i-clipboard",
                }
            )
            if len(related) >= limit:
                break
    return related[:limit]


def _tags(tool: dict) -> list[dict]:
    overview = tool.get("overview") or {}
    tags: list[dict] = []
    if overview.get("acronym"):
        tags.append({"href": "index.html#calculadoras", "label": "#" + str(overview["acronym"]).replace(" ", "")})
    for label in (overview.get("specialty") or [])[:5]:
        tags.append({"href": "index.html#calculadoras", "label": "#" + str(label).replace(" ", "")})
    for extra in ("NANDA-I", "SAE", "Protocolos", "Medicação"):
        href = {
            "NANDA-I": "diagnosticosnanda.html",
            "SAE": "sae.html",
            "Protocolos": "protocolos.html",
            "Medicação": "medicamentos.html",
        }[extra]
        tags.append({"href": href, "label": "#" + extra.replace(" ", "")})
    return tags


def _learning_trail(tool: dict) -> list[dict]:
    overview = tool.get("overview") or {}
    name = overview.get("name") or overview.get("acronym") or "esta ferramenta"
    category = (tool.get("breadcrumb") or {}).get("category", "Enfermagem")
    icon = overview.get("icon") or ICON_BY_CATEGORY.get(category, "i-book")
    return [
        {
            "href": "biblioteca-provas.html",
            "title": "Quiz",
            "desc": f"Teste seus conhecimentos sobre {name}.",
            "icon": "i-clipboard",
            "cta": "Responder agora",
        },
        {
            "href": "protocolos.html",
            "title": "Protocolos",
            "desc": "Protocolos institucionais e fluxos operacionais de enfermagem.",
            "icon": "i-clipboard",
        },
        {
            "href": "biblioteca.html",
            "title": "Artigos & Evidência",
            "desc": f"Literatura de referência sobre {category.lower()}.",
            "icon": "i-book",
        },
        {
            "href": "medicamentos.html",
            "title": "Medicamentos",
            "desc": "Base NKOS com doses e classes farmacológicas.",
            "icon": "i-pills",
        },
        {
            "href": "sae.html",
            "title": "SAE",
            "desc": "Diagnósticos, resultados e intervenções de enfermagem.",
            "icon": "i-file",
        },
    ]


def _additional_resources() -> list[dict]:
    return [
        {"href": "diagnosticosnanda.html", "title": "NANDA-I", "desc": "Diagnósticos de enfermagem padronizados.", "icon": "i-brain"},
        {"href": "nurse-palm.html", "title": "Nurse-PaLM", "desc": "Dashboard de raciocínio clínico assistido.", "icon": "i-brain"},
        {"href": "biblioteca-provas.html", "title": "Quiz & Provas", "desc": "Questões clínicas para fixação.", "icon": "i-clipboard"},
        {"href": "checklist.html", "title": "Check-lists", "desc": "Listas de verificação para prática segura.", "icon": "i-clipcheck", "ctaIcon": "download"},
    ]


def _profile_content(tool: dict) -> dict:
    overview = tool.get("overview") or {}
    evidence = tool.get("evidence") or {}
    learning = tool.get("learning") or {}
    interpretation = tool.get("interpretation") or {}
    ranges = interpretation.get("ranges") or []
    name = overview.get("name") or overview.get("acronym") or "Ferramenta"

    urgencia_sections = []
    if ranges:
        urgencia_sections.append(
            {
                "heading": "Condutas por faixa",
                "items": [
                    f"{r.get('label', 'Faixa')}: {_first_line(r.get('recommendations') or r.get('clinicalImplications') or '')}"
                    for r in ranges[:4]
                    if _first_line(r.get("recommendations") or r.get("clinicalImplications") or "")
                ],
            }
        )

    estudante_sections = []
    if learning.get("tips"):
        estudante_sections.append({"heading": "Dicas de estudo", "items": learning["tips"][:4]})

    return {
        "urgencia": {
            "title": "Modo Urgência",
            "intro": (overview.get("objective") or "Visão rápida para priorização clínica.")
            + " Use o resultado para estratificação inicial e escalonamento do cuidado.",
            "sections": urgencia_sections,
        },
        "gestor": {
            "title": "Visão Gestor",
            "intro": "Painel orientado a qualidade assistencial, padronização do registro e acompanhamento institucional.",
            "sections": [
                {
                    "heading": "Indicadores de referência",
                    "items": [
                        overview.get("averageTime") and f"Tempo de aplicação estimado: {overview['averageTime']}",
                        "Registro padronizado do resultado no prontuário",
                        "Monitoramento de distribuição por faixa de risco",
                        "Reavaliação conforme protocolo institucional",
                    ],
                }
            ],
        },
        "estudante": {
            "title": "Visão Estudante",
            "intro": f"Resumo de aprendizado sobre {name}, com critérios de pontuação, interpretação e pegadinhas frequentes.",
            "sections": estudante_sections,
        },
        "academico": {
            "title": "Visão Acadêmica",
            "intro": "Síntese acadêmica com fundamento teórico, validade clínica e limitações de uso.",
            "sections": [
                {
                    "heading": "Pérolas de evidência",
                    "items": [
                        _first_line(evidence.get("foundation")),
                        _first_line(evidence.get("history")),
                        _first_line(evidence.get("validation")),
                        _first_line(evidence.get("limitations")),
                    ],
                }
            ],
        },
    }


def _kpis(tool: dict) -> list[str]:
    overview = tool.get("overview") or {}
    interpretation = tool.get("interpretation") or {}
    ranges = interpretation.get("ranges") or []
    items = [
        overview.get("averageTime") and f"Tempo médio de aplicação: {overview['averageTime']}",
        overview.get("complexity") and f"Complexidade: {overview['complexity']}",
        overview.get("evidenceLevel") and f"Nível de evidência: {overview['evidenceLevel']}",
        ranges and "Faixas clínicas: " + " • ".join(r.get("label", "") for r in ranges[:4]),
        "Taxa de registros dentro da faixa esperada (7 dias)",
        "Alarmes clínicos por unidade",
    ]
    return [i for i in items if i]


def tool_to_cko(tool: dict, all_tools: list[dict]) -> dict:
    overview = tool.get("overview") or {}
    sae = tool.get("sae") or {}
    evidence = tool.get("evidence") or {}
    learning = tool.get("learning") or {}
    slug = canonical_slug(tool.get("slug", ""))

    presentation = {
        "profiles": ["padrao", "urgencia", "gestor", "estudante", "academico"],
        "learning_trail": _learning_trail(tool),
        "additional_resources": _additional_resources(),
        "learning": learning.get("examples") and _learning_trail(tool) or _learning_trail(tool),
        "tags": _tags(tool),
        "related_tools": _related_tools(tool, all_tools),
        "kpis": _kpis(tool),
        "profileContent": _profile_content(tool),
        "kg_links": [
            {"href": "biblioteca.html", "icon": "fa-book", "label": "Biblioteca de Recursos"},
            {"href": "nurse-palm.html", "icon": "fa-brain", "label": "Dashboard Nurse-PaLM"},
            {"href": "diagnosticosnanda.html", "icon": "fa-clipboard-list", "label": "NANDA-I"},
            {"href": "sae.html", "icon": "fa-file-medical", "label": "SAE"},
            {"href": "medicamentos.html", "icon": "fa-pills", "label": "Medicamentos"},
            {"href": "protocolos.html", "icon": "fa-shield-halved", "label": "Protocolos"},
        ],
    }

    return {
        "schema_version": "cko-v1",
        "metadata": {
            "id": tool.get("id"),
            "code": tool.get("code"),
            "slug": slug,
            "version": tool.get("version", "1.0.0"),
            "status": tool.get("status", "published"),
            "seo": tool.get("seo") or {},
            "breadcrumb": tool.get("breadcrumb") or {},
        },
        "knowledge": {
            "concept_code": (overview.get("acronym") or slug).upper().replace("-", "_"),
            "tool_code": tool.get("code"),
            "clinical_purpose": overview.get("objective"),
            "domain": overview.get("specialty") or [],
        },
        "reasoning": {
            "sae": {
                "nanda": [{"diagnosis": n.get("diagnosis"), "definition": n.get("definition")} for n in sae.get("nanda", [])],
                "nic": [
                    {"intervention": n.get("intervention"), "activities": n.get("activities", [])}
                    for n in sae.get("nic", [])
                ],
                "noc": [
                    {"outcome": n.get("outcome"), "indicators": n.get("indicators", [])}
                    for n in sae.get("noc", [])
                ],
            }
        },
        "evidence": evidence,
        "ai": {
            "summary": overview.get("objective"),
            "clinicalPearls": learning.get("tips", [])[:6],
            "keywords": [overview.get("acronym"), overview.get("name")] + (overview.get("specialty") or []),
        },
        "presentation": presentation,
    }


def build_tool(tool: dict, all_tools: list[dict]) -> list[dict]:
    slug = canonical_slug(tool.get("slug", ""))
    if slug in DEDICATED_BUILDERS:
        return []

    cko = tool_to_cko(tool, all_tools)
    out = DATA / f"{slug}-cko.json"
    source = tool.get("_source", f"reference-website/data/tools/{tool.get('slug')}.json")
    entry = write_generated_json(
        out,
        cko,
        sources=[source],
        artifact_key=f"js/modules/data/{slug}-cko.json",
    )
    mirror_under_delivery(
        out,
        [f"js/modules/data/{slug}-cko.json", f"html/js/modules/data/{slug}-cko.json"],
    )
    return [entry]


def build_all_generic() -> list[dict]:
    tools = _load_all_tools()
    entries: list[dict] = []
    for tool in tools:
        slug = canonical_slug(tool.get("slug", ""))
        if slug in DEDICATED_BUILDERS:
            continue
        entries.extend(build_tool(tool, tools))
    return entries


def build_cko_index() -> dict:
    """Índice slug → arquivo CKO para runtime."""
    index: dict[str, str] = {
        "apgar": "js/modules/data/apgar-cko.json",
        "glasgow": "js/modules/data/glasgow-cko.json",
        "escala-de-glasgow": "js/modules/data/glasgow-cko.json",
    }
    for path in sorted(DATA.glob("*-cko.json")):
        slug = path.stem.replace("-cko", "")
        rel = f"js/modules/data/{path.name}"
        index[slug] = rel
    for tool_slug, html_slug in {"escala-de-glasgow": "glasgow", "escala-de-braden": "braden", "escala-de-morse": "morse"}.items():
        if html_slug in index:
            index[tool_slug] = index[html_slug]
    return index
