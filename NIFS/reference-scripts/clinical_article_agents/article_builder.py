"""Build editorial articles (problem + solution) from tool pain registry."""
from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timezone
from typing import Any

from paths import (
    article_template,
    category_pain_defaults,
    load_tools_catalog,
    soft_skills_registry,
    tool_pain_registry,
)

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
AUTHOR = {"name": "Equipe Científica Calculadoras de Enfermagem", "role": "Enfermagem baseada em evidências"}


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", text).strip("-")


def _resolve_tool_pain(tool_code: str) -> dict[str, Any]:
    registry = tool_pain_registry().get("tools", {})
    if tool_code in registry:
        return registry[tool_code]
    catalog = {t["tool_code"]: t for t in load_tools_catalog()}
    tool = catalog.get(tool_code)
    if not tool:
        raise KeyError(f"Unknown tool: {tool_code}")
    cat = tool.get("category", "assessment_scales")
    defaults = category_pain_defaults().get("categories", {}).get(cat, {})
    return {
        "tool_code": tool_code,
        "display_name": tool.get("name", tool_code),
        "slug_hint": tool.get("acronym", tool_code).lower().replace("_", "-"),
        "category": cat,
        "specialty": defaults.get("label", "Enfermagem clínica"),
        "story_clinical": f"A enfermagem precisa aplicar {tool.get('name', tool_code)} com precisão, sob pressão de tempo e com impacto direto na segurança do paciente.",
        "core_pain": defaults.get("core_pain", "Variabilidade e pressão assistencial"),
        "search_queries": defaults.get("search_topics", []),
        "common_errors": defaults.get("common_errors", []),
        "clinical_impact": ["Comprometimento da segurança do paciente", "Variabilidade na assistência", "Eventos adversos evitáveis"],
        "soft_skills": defaults.get("soft_skills", ["raciocinio_clinico", "dupla_checagem"]),
        "mitigation": ["Padronizar protocolo institucional", "Usar calculadora validada", "Dupla checagem", "Registrar e auditar"],
        "digital_support": ["Calculadora digital com memória de cálculo", "Alertas de segurança", "Modo emergência"],
        "regional": defaults.get("regional", {}),
        "problem_titles": [f"{tool.get('name')}: onde enfermeiros mais sentem insegurança na prática"],
        "solution_titles": [f"Como reduzir erros e aumentar segurança ao usar {tool.get('name')}"],
    }


def _soft_skill_blocks(skill_ids: list[str], *, mode: str) -> list[dict]:
    skills = soft_skills_registry().get("skills", {})
    items = []
    for sid in skill_ids:
        sk = skills.get(sid, {})
        if not sk:
            continue
        if mode == "problem":
            items.append({"title": sk["label"], "text": sk.get("problem_context", "")})
        else:
            items.append({"title": sk["label"], "text": sk.get("solution_practice", "")})
    return items


def _tool_href(pain: dict) -> str:
    slug = pain.get("slug_hint")
    if slug:
        return f"/ferramentas/{slug}"
    related = pain.get("related_tool_code")
    if related:
        try:
            rel = _resolve_tool_pain(related)
            if rel.get("slug_hint"):
                return f"/ferramentas/{rel['slug_hint']}"
        except KeyError:
            pass
    return "/ferramentas"


def _regional_cards(regional: dict) -> list[dict]:
    labels = {"BR": "Brasil", "LATAM": "América Latina", "US": "Estados Unidos", "UK": "Reino Unido", "IN": "Índia"}
    cards = []
    for code, label in labels.items():
        r = regional.get(code, {})
        if not r:
            continue
        text = r.get("pain", "")
        if r.get("quote"):
            text += f' — "{r["quote"]}"'
        cards.append({"title": label, "text": text})
    return cards


def build_problem_article(tool_code: str) -> dict[str, Any]:
    pain = _resolve_tool_pain(tool_code)
    code_suffix = tool_code.replace("TOOL.", "").replace(".", "_")
    title = pain.get("problem_titles", [f"Dores na prática: {pain['display_name']}"])[0]
    slug = slugify(title)[:80]

    sections: list[dict] = [
        {"type": "heading", "level": 2, "id": "introducao", "text": "Introdução"},
        {"type": "paragraph", "text": pain.get("story_clinical", "")},
        {
            "type": "callout",
            "variant": "warning",
            "title": "Atenção",
            "text": article_template().get("problem_article", {}).get(
                "callout_warning",
                "Conteúdo educativo — não substitui protocolo institucional.",
            ),
        },
        {"type": "heading", "level": 2, "id": "dor-central", "text": "A dor central na prática"},
        {"type": "paragraph", "text": pain.get("core_pain", "")},
        {"type": "heading", "level": 2, "id": "dores-regionais", "text": "Dores por região"},
    ]
    regional = _regional_cards(pain.get("regional", {}))
    if regional:
        sections.append({"type": "cards", "items": regional})
    else:
        sections.append({"type": "paragraph", "text": "Profissionais em diferentes contextos reportam pressão de tempo, variabilidade de protocolos e medo de erro."})

    sections.extend([
        {"type": "heading", "level": 2, "id": "erros-comuns", "text": "Erros mais frequentes"},
        {"type": "checklist", "items": pain.get("common_errors", [])},
        {"type": "heading", "level": 2, "id": "consequencias", "text": "Impacto clínico"},
        {"type": "checklist", "items": pain.get("clinical_impact", [])},
        {"type": "heading", "level": 2, "id": "soft-skills", "text": "Fatores humanos e soft skills"},
        {"type": "cards", "items": _soft_skill_blocks(pain.get("soft_skills", []), mode="problem")},
        {"type": "heading", "level": 2, "id": "conclusao", "text": "Conclusão"},
        {
            "type": "paragraph",
            "text": f"Compreender as dores reais em {pain['display_name']} é o primeiro passo para construir práticas mais seguras. O próximo passo é combinar padronização, apoio tecnológico e desenvolvimento comportamental — temas abordados no guia de soluções correspondente.",
        },
    ])

    toc = [
        {"id": "introducao", "label": "Introdução"},
        {"id": "dor-central", "label": "A dor central na prática"},
        {"id": "dores-regionais", "label": "Dores por região"},
        {"id": "erros-comuns", "label": "Erros mais frequentes"},
        {"id": "consequencias", "label": "Impacto clínico"},
        {"id": "soft-skills", "label": "Fatores humanos"},
        {"id": "conclusao", "label": "Conclusão"},
    ]

    tags = [pain["display_name"].lower(), "segurança do paciente", "enfermagem", "soft skills"]
    tags.extend(pain.get("search_queries", [])[:3])

    return {
        "article_code": f"ART.{code_suffix}.PROBLEM",
        "slug": slug,
        "title": title,
        "subtitle": f"Dores reais de enfermeiros ao usar {pain['display_name']} — Brasil, América Latina, EUA, UK e Índia.",
        "content_type": "Artigo clínico",
        "category_id": pain.get("category", "clinical"),
        "category": pain.get("specialty", "Clínica"),
        "theme": pain["display_name"],
        "read_minutes": 8,
        "author": AUTHOR,
        "published_at": NOW,
        "updated_at": NOW,
        "tags": list(dict.fromkeys(tags))[:10],
        "featured": tool_code in ("TOOL.INFUSION", "TOOL.CAPURRO"),
        "tool_code": tool_code,
        "article_angle": "problem",
        "toc": toc,
        "related_tools": [
            {
                "title": pain["display_name"],
                "description": "Calculadora clínica validada",
                "href": _tool_href(pain),
                "icon": "calculator",
            },
            {"title": "Segurança do paciente", "description": "Artigos relacionados", "href": "/artigos/seguranca-paciente-pratica-enfermagem", "icon": "shield"},
        ],
        "sections": sections,
        "seo": {
            "title": f"{title} | Calculadoras de Enfermagem",
            "description": f"Dores de enfermeiros sobre {pain['display_name']}: erros comuns, impacto clínico e fatores humanos.",
        },
    }


def build_solution_article(tool_code: str) -> dict[str, Any]:
    pain = _resolve_tool_pain(tool_code)
    code_suffix = tool_code.replace("TOOL.", "").replace(".", "_")
    title = pain.get("solution_titles", [f"Como mitigar riscos em {pain['display_name']}"])[0]
    slug = slugify(title)[:80]

    sections: list[dict] = [
        {"type": "heading", "level": 2, "id": "introducao", "text": "Introdução"},
        {
            "type": "paragraph",
            "text": f"Reduzir erro em {pain['display_name']} exige mais que memorizar fórmulas: combina padronização técnica, ferramentas de apoio, dupla checagem e desenvolvimento de soft skills. Este guia traduz as dores da prática em estratégias aplicáveis no plantão.",
        },
        {
            "type": "callout",
            "variant": "tip",
            "title": "Boa prática",
            "text": article_template().get("solution_article", {}).get(
                "callout_tip",
                "Combine padronização, dupla checagem e calculadora validada.",
            ),
        },
        {"type": "heading", "level": 2, "id": "mitigacao-risco", "text": "Mitigação de risco"},
        {"type": "checklist", "items": pain.get("mitigation", [])},
        {"type": "heading", "level": 2, "id": "tecnicas", "text": "Técnicas e ferramentas de apoio"},
        {"type": "cards", "items": [{"title": "Padronização", "text": "Protocolo único por setor reduz variabilidade entre profissionais e turnos."}, {"title": "Validação cruzada", "text": "Segundo profissional confirma antes de administrar ou classificar."}, {"title": "Memória de cálculo", "text": "Registrar passo a passo facilita auditoria e aprendizado."}]},
        {"type": "heading", "level": 2, "id": "comportamental", "text": "Desenvolvimento comportamental"},
        {"type": "paragraph", "text": "Sob pressão assistencial, a capacidade cognitiva diminui. Micro-pausas antes de confirmar dose ou pontuação, escalação quando a carga excede capacidade e cultura de segurança não punitiva favorecem reporte de near-misses."},
        {"type": "heading", "level": 2, "id": "soft-skills", "text": "Soft skills na prática"},
        {"type": "cards", "items": _soft_skill_blocks(pain.get("soft_skills", []), mode="solution")},
        {"type": "heading", "level": 2, "id": "checklist", "text": "Checklist de segurança"},
        {"type": "checklist", "items": [
            "Confirmar dados do paciente (identificação, peso, alergias)",
            "Aplicar protocolo/calculadora institucional validada",
            "Validar resultado com colega em doses ou classificações críticas",
            "Registrar valor, horário, método e profissional responsável",
            "Reavaliar no intervalo clínico adequado",
        ]},
        {"type": "heading", "level": 2, "id": "tecnologia", "text": "Apoio digital e calculadoras"},
        {"type": "checklist", "items": pain.get("digital_support", [])},
        {"type": "heading", "level": 2, "id": "conclusao", "text": "Conclusão"},
        {
            "type": "paragraph",
            "text": f"Segurança em {pain['display_name']} é resultado de sistema: pessoas preparadas, processos padronizados e tecnologia que reduz carga cognitiva. Calculadoras com memória matemática, alertas e modo emergência amplificam a competência clínica sem substituir julgamento profissional.",
        },
    ]

    toc = [
        {"id": "introducao", "label": "Introdução"},
        {"id": "mitigacao-risco", "label": "Mitigação de risco"},
        {"id": "tecnicas", "label": "Técnicas de apoio"},
        {"id": "comportamental", "label": "Desenvolvimento comportamental"},
        {"id": "soft-skills", "label": "Soft skills"},
        {"id": "checklist", "label": "Checklist de segurança"},
        {"id": "tecnologia", "label": "Apoio digital"},
        {"id": "conclusao", "label": "Conclusão"},
    ]

    return {
        "article_code": f"ART.{code_suffix}.SOLUTION",
        "slug": slug,
        "title": title,
        "subtitle": f"Estratégias de mitigação de risco, ferramentas de apoio e soft skills para {pain['display_name']}.",
        "content_type": "Guia prático",
        "category_id": pain.get("category", "clinical"),
        "category": pain.get("specialty", "Clínica"),
        "theme": pain["display_name"],
        "read_minutes": 7,
        "author": {**AUTHOR, "role": "Segurança do paciente e educação clínica"},
        "published_at": NOW,
        "updated_at": NOW,
        "tags": [pain["display_name"].lower(), "segurança", "soft skills", "mitigação de risco", "guia prático"],
        "featured": tool_code in ("TOOL.INFUSION", "TOOL.CAPURRO"),
        "tool_code": tool_code,
        "article_angle": "solution",
        "toc": toc,
        "related_tools": [
            {"title": pain["display_name"], "description": "Abrir calculadora", "href": _tool_href(pain), "icon": "calculator"},
        ],
        "sections": sections,
        "seo": {
            "title": f"{title} | Calculadoras de Enfermagem",
            "description": f"Guia prático: como reduzir erros em {pain['display_name']} com técnicas, soft skills e apoio digital.",
        },
    }


def build_pair(tool_code: str) -> list[dict]:
    return [build_problem_article(tool_code), build_solution_article(tool_code)]
