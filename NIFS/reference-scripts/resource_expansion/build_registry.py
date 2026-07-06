"""Registries: CV, escalas, indicadores, dicionário, slides, biblioteca, games."""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "datasets" / "master-data" / "resource-expansion"
LIB_OUT = ROOT / "datasets" / "content" / "library"
SITEMAP = ROOT / "website" / "pt" / "sitemap.xml"
CATALOG = ROOT / "datasets" / "clinical" / "clinical_tools_catalog.json"
ASSETS = ROOT / "datasets" / "metadata" / "assets.json"
INDICATORS = ROOT / "datasets" / "operations" / "nursing_indicators.json"
DICT = ROOT / "datasets" / "master" / "nursing_dictionary.json"
SITE_URL = "https://calculadorasdeenfermagem.com.br"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _tool_slugs() -> list[tuple[str, str]]:
    """(slug, tool_code) from sitemap ferramentas."""
    if not SITEMAP.is_file():
        cat = json.loads(CATALOG.read_text(encoding="utf-8"))
        return [(t.get("acronym", "tool").lower(), t["tool_code"]) for t in cat.get("records", [])[:100]]
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    root = ET.parse(SITEMAP).getroot()
    out = []
    cat_by_acronym = {
        (r.get("acronym") or "").upper(): r.get("tool_code")
        for r in json.loads(CATALOG.read_text(encoding="utf-8")).get("records", [])
    }
    for loc in root.findall("sm:url", ns):
        path = (loc.find("sm:loc", ns).text or "").split(".com.br")[-1]
        m = re.search(r"/ferramentas/([^/]+)/?", path)
        if not m:
            continue
        slug = m.group(1).lower()
        code = cat_by_acronym.get(slug.upper()) or f"TOOL.{slug.upper().replace('-', '_')}"
        out.append((slug, code))
    return out


def build_modules_registry() -> dict:
    items = [
        {
            "module_id": "M19_cv_generator",
            "entity_code": "CV_GEN_001",
            "artifact": "CVW",
            "routes": ["/curriculo", "/curriculo/criar"],
            "status": "ui_exists",
            "completion_pct": 40,
            "agent_pipeline": ["search", "generate", "review", "validate"],
            "evidence_grade_required": "A",
            "gaps": ["PDF export", "i18n templates", "master-data canonical", "persistência servidor"],
        },
        {
            "module_id": "M20_scales_generator",
            "entity_code": "SCL_GEN_001",
            "artifact": "SCL",
            "routes": ["/escalas"],
            "status": "apgar_pilot_100",
            "completion_pct": 5,
            "target_scales": 40,
            "agent": "apgar_agents",
            "evidence_grade_required": "A",
        },
        {
            "module_id": "M21_indicators_generator",
            "entity_code": "IND_GEN_001",
            "artifact": "IND",
            "routes": ["/gestao/indicadores"],
            "status": "dataset_stub",
            "completion_pct": 15,
            "record_count": len(json.loads(INDICATORS.read_text(encoding="utf-8")).get("records", [])),
            "evidence_grade_required": "A",
        },
        {
            "module_id": "M22_dictionary",
            "entity_code": "DICT_GEN_001",
            "artifact": "DICT",
            "routes": ["/glossario"],
            "status": "terms_only",
            "completion_pct": 25,
            "term_count": len(json.loads(DICT.read_text(encoding="utf-8")).get("records", [])),
            "gaps": ["definition_pt", "detail pages", "trilingual agent"],
            "evidence_grade_required": "A",
        },
        {
            "module_id": "M23_library_assets",
            "entity_code": "LIB_AST_001",
            "artifact": "AST",
            "routes": ["/biblioteca"],
            "status": "pending_sync",
            "completion_pct": 0,
            "evidence_grade_required": "A",
        },
        {
            "module_id": "M24_tool_slides",
            "entity_code": "SLD_GEN_001",
            "artifact": "SLD",
            "routes": ["/ferramentas/{slug}/slides"],
            "status": "registry",
            "completion_pct": 0,
            "evidence_grade_required": "A",
        },
        {
            "module_id": "M25_games",
            "entity_code": "GAM_ROADMAP_001",
            "artifact": "GAM",
            "routes": ["/games"],
            "status": "roadmap",
            "completion_pct": 0,
            "evidence_grade_required": "A",
        },
    ]
    return {
        "schema_version": "2026.2.8",
        "generated_at": _now(),
        "total_modules": len(items),
        "modules": items,
    }


def build_slides_registry() -> dict:
    slides = []
    for slug, tool_code in _tool_slugs():
        concept = tool_code.replace("TOOL.", "").replace(".", "_")
        slides.append({
            "entity_code": f"{concept}_SLD_001",
            "tool_code": tool_code,
            "slug": slug,
            "canonical_url": f"/ferramentas/{slug}/slides/",
            "deck_title_pt": f"Slides técnicos — {tool_code}",
            "slide_count_target": 8,
            "sections": [
                "objetivo_clinico",
                "indicacoes",
                "passo_a_passo",
                "interpretacao",
                "evidencias_grau_a",
                "erros_comuns",
                "integracao_ferramenta",
                "referencias",
            ],
            "template": "TPL.SLIDES_TOOL",
            "status": "pending",
            "evidence_grade_required": "A",
            "agent_pipeline": ["search", "generate", "review", "validate"],
        })
    return {
        "schema_version": "2026.2.8",
        "generated_at": _now(),
        "total_decks": len(slides),
        "site_pattern": "website/assets/data/slides/{slug}.json",
        "decks": slides,
    }


def build_library_visual_manifest() -> dict:
    assets_doc = json.loads(ASSETS.read_text(encoding="utf-8"))
    guidelines = json.loads((ROOT / "datasets/clinical/clinical_guidelines.json").read_text(encoding="utf-8"))
    records = []
    for a in assets_doc.get("records", []):
        path = (a.get("path") or "").lstrip("/")
        if not path.startswith("images/"):
            continue
        records.append({
            "entity_code": f"LIB_AST_{len(records)+1:03d}",
            "asset_code": a.get("asset_code"),
            "asset_type": a.get("asset_type"),
            "remote_url": f"{SITE_URL}/{path}",
            "local_path": f"website/assets/{path}",
            "category": a.get("category"),
            "status": "pending_download",
        })
    # Hero + icons for biblioteca hub
    records.append({
        "entity_code": "LIB_AST_HERO_001",
        "asset_type": "hero",
        "remote_url": f"{SITE_URL}/assets/images/heroes/hero-protocols-hub.png",
        "local_path": "website/assets/images/heroes/hero-protocols-hub.png",
        "hub": "biblioteca",
        "status": "pending_download",
    })
    for i, g in enumerate(guidelines.get("records", [])[:50]):
        code = g.get("guideline_code", f"G{i}")
        records.append({
            "entity_code": f"LIB_GUIDE_AST_{i+1:03d}",
            "guideline_code": code,
            "title": g.get("title"),
            "thumbnail_remote": f"{SITE_URL}/assets/images/library/{code.lower().replace('.', '-')}.webp",
            "local_path": f"website/assets/images/library/{code.lower().replace('.', '-')}.webp",
            "status": "pending_download",
            "fallback": True,
        })
    return {
        "schema_version": "2026.2.8",
        "generated_at": _now(),
        "source_site": SITE_URL,
        "total_assets": len(records),
        "records": records,
    }


def build_games_roadmap() -> dict:
    return {
        "schema_version": "2026.2.8",
        "generated_at": _now(),
        "status": "PLANNED",
        "evidence_grade_required": "A",
        "phases": [
            {
                "phase": 1,
                "label_pt": "Quiz battle & flashcard streak",
                "games": [
                    {"entity_code": "GAM_QUIZ_BATTLE_001", "route": "/games/quiz-battle", "reuse": ["education/quizzes.json", "flashcards.json"]},
                    {"entity_code": "GAM_FLA_STREAK_001", "route": "/games/flash-streak", "reuse": ["education/flashcards.json"]},
                ],
            },
            {
                "phase": 2,
                "label_pt": "Simulador clínico gamificado",
                "games": [
                    {"entity_code": "GAM_SIM_CASE_001", "route": "/games/caso-clinico", "reuse": ["education/simulated_exams.json"]},
                    {"entity_code": "GAM_ESCALA_SPEED_001", "route": "/games/escala-rapida", "reuse": ["clinical/calculator_definitions.json"]},
                ],
            },
            {
                "phase": 3,
                "label_pt": "Trilhas, badges, ranking",
                "games": [
                    {"entity_code": "GAM_TRILHA_XP_001", "route": "/games/trilhas-xp", "features": ["badges", "leaderboard", "weekly_challenge"]},
                    {"entity_code": "GAM_INDICADOR_BOSS_001", "route": "/games/gestor-boss", "reuse": ["operations/nursing_indicators.json"]},
                ],
            },
        ],
        "other_resources_planned": [
            {"code": "CERT", "label_pt": "Certificados digitais pós-simulado", "priority": "P2"},
            {"code": "PRT_PDF", "label_pt": "Protocolos PDF imprimíveis", "priority": "P2"},
            {"code": "VOICE", "label_pt": "Assistente voz SBAR/curriculum", "priority": "P3"},
            {"code": "AR", "label_pt": "AR para procedimentos IPSG", "priority": "P4"},
            {"code": "API", "label_pt": "API FHIR indicadores + escalas", "priority": "P3"},
        ],
    }


def main() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    LIB_OUT.mkdir(parents=True, exist_ok=True)
    mods = build_modules_registry()
    slides = build_slides_registry()
    lib = build_library_visual_manifest()
    games = build_games_roadmap()

    ind_result = {}
    try:
        sys.path.insert(0, str(ROOT / "scripts" / "resource_expansion"))
        from build_nursing_indicators import generate as build_indicators  # noqa: WPS433

        ind_result = build_indicators()
        # Atualiza record_count M21 no registry
        for mod in mods.get("modules", []):
            if mod.get("module_id") == "M21_indicators_generator":
                mod["record_count"] = ind_result.get("total", mod.get("record_count"))
                mod["completion_pct"] = ind_result.get("completion_pct", mod.get("completion_pct"))
                mod["status"] = "complete" if ind_result.get("completion_pct", 0) >= 100 else "dataset_stub"
    except Exception:
        pass

    (OUT / "modules_registry.json").write_text(json.dumps(mods, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "slides_registry.json").write_text(json.dumps(slides, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "games_roadmap.json").write_text(json.dumps(games, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (LIB_OUT / "library_visual_assets.json").write_text(json.dumps(lib, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cov = {
        "generated_at": _now(),
        "modules": mods["total_modules"],
        "slide_decks": slides["total_decks"],
        "library_assets": lib["total_assets"],
        "games_phases": len(games["phases"]),
    }
    (OUT / "coverage_report.json").write_text(json.dumps(cov, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"modules: {mods['total_modules']} | slides: {slides['total_decks']} | library assets: {lib['total_assets']}")
    return cov
