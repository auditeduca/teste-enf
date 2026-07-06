#!/usr/bin/env python3
"""Generate Portuguese (pt-BR) static HTML website from Calculadoras de Enfermagem datasets — maximum reuse."""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ROOT / "datasets"
OUT = ROOT / "website" / "pt"

sys.path.insert(0, str(ROOT / "scripts"))
from content_paths import content_path  # noqa: E402
from locale_content_lib import (
    resolve_locale_home,
    skip_link_label,
    sync_pt_br_home_partition,
)
from website_lib import render_locale_ctx  # noqa: E402
from chrome_lib import build_locale_options  # noqa: E402
from article_lib import render_article_page, render_simulation_page  # noqa: E402
from hub_config_lib import hydrate_hub_counts, load_hub_template  # noqa: E402
from hub_lib import (
    build_article_items,
    build_competency_items,
    build_education_hub_items,
    build_glossary_items,
    build_library_items,
    build_protocol_items,
    build_quiz_items,
    build_simulado_items,
    build_tool_concepts_orchestrator,
    build_tool_items,
    merge_orchestrator_hub,
    render_hub_page,
    render_institutional_hub,
)
from institutional_lib import (  # noqa: E402
    render_about_page,
    render_accessibility_center,
    render_contact_page,
    render_mission_page,
    render_objective_page,
    render_privacy_center,
    render_search_page,
    render_sitemap_page,
    render_sustainability_center,
)
from protocol_lib import protocol_slug, render_protocol_page  # noqa: E402
from module_landing_lib import render_module_landing  # noqa: E402
from templates_lib import (  # noqa: E402
    build_flashcard_items,
    render_cv_wizard,
    render_flashcard_study,
    render_labor_calculator_page,
    render_labor_calculators_hub,
    render_metrics_dashboard,
    render_forum_hub,
    render_mindmap_page,
    render_nnn_library,
    build_nnn_linkage_index,
    render_sbar_wizard,
    render_scrape_hub,
    render_self_tests,
    render_vaccine_calendar,
)
from tool_lib import render_tool_page  # noqa: E402
from website_lib import (  # noqa: E402
    copy_static_assets,
    load_json,
    render_home_page,
    render_hub_section,
    render_list_section,
    render_page,
    seo_lookup,
    slugify,
    tool_page_href,
    unique_tool_slug,
    write_page,
)

# ── Institutional PT content (single source, reused by render_institutional) ──
INST = {
    "missao": {
        "hero": ("Missão, Visão e Valores", "Compromisso com a excelência na educação e prática da enfermagem."),
        "crumbs": [("Sobre", "sobre/index.html"), ("Missão, Visão e Valores", None)],
        "sections": [],
        "values": [],
    },
    "sobre": {
        "hero": ("Sobre Nós", "Plataforma educacional e clínica para enfermagem — Calculadoras de Enfermagem 2026."),
        "crumbs": [("Sobre Nós", None)],
        "sections": [],
    },
    "acessibilidade": {
        "hero": ("Acessibilidade", "Compromisso com inclusão digital."),
        "crumbs": [("Acessibilidade", None)],
        "sections": [
            ("Recursos", "Skip link, landmarks ARIA, contraste adequado e navegação por teclado são requisitos desta geração HTML."),
            ("Melhorias", "Reporte barreiras de acessibilidade pelo formulário de contato para priorização."),
        ],
    },
}


def render_institutional_body(key: str) -> str:
    data = INST[key]
    parts = []
    for title, text in data.get("sections", []):
        parts.append(f'<section class="section section-container"><div class="card"><h2>{title}</h2><p>{text}</p></div></section>')
    if data.get("values"):
        cards = "".join(
            f'<div class="value-card"><h3>{t}</h3><p>{tx}</p></div>' for t, tx in data["values"]
        )
        parts.append(f'<section class="section section-container"><h2>Valores</h2><div class="values-grid">{cards}</div></section>')
    return "".join(parts)


def render_institutional(key: str, seo_records: list, depth: int = 1) -> str:
    data = INST[key]
    path = f"/{key}"
    title, desc = seo_lookup(seo_records, path, data["hero"][0])
    crumbs = [(label, href) for label, href in data["crumbs"]]
    return render_page(
        depth=depth,
        title=title,
        description=desc,
        canonical_path=path,
        hero_title=data["hero"][0],
        hero_subtitle=data["hero"][1],
        breadcrumbs=crumbs,
        body=render_institutional_body(key),
    )


def tool_cards(tools: list, hub: str, slug_map: dict[str, str], limit: int | None = None) -> list[tuple[str, str, str, str]]:
    rows = tools[:limit] if limit else tools
    out = []
    for t in rows:
        slug = slug_map[t["tool_code"]]
        out.append((
            t["name"],
            f"{t.get('tool_type', 'clinical')} · {t.get('domain', '')}",
            t.get("category", "clinical"),
            tool_page_href(slug, hub),
        ))
    return out


def _localize_page(out: Path, rel: str, prefix: str, lang: str, direction: str) -> None:
    from seo_lib import localize_html
    from website_lib import write_page

    src = (out / rel).read_text(encoding="utf-8")
    write_page(out / prefix, rel, localize_html(src, prefix, lang, direction))


def _localize_batch(out: Path, html_pages: list[str], prefix: str, lang: str, direction: str) -> None:
    for rel in html_pages:
        _localize_page(out, rel, prefix, lang, direction)


def _export_tool_concepts_index(data: dict) -> None:
    """Export tool concept ecosystems for client-side hub customization."""
    dst_dir = ROOT / "website" / "assets" / "data"
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / "tool-concepts-index.json"
    export = {
        "schema_version": "2026.2.0",
        "concepts": data["concepts"],
        "ecosystems": {
            code: {
                "tool_code": eco["tool_code"],
                "slug": eco["slug"],
                "title": eco["title"],
                "full_name": eco["full_name"],
                "kind": eco["kind"],
                "kind_label": eco["kind_label"],
                "hero_title": eco["hero_title"],
                "hero_subtitle": eco["hero_subtitle"],
                "resource_count": eco["resource_count"],
                "items": eco["items"],
            }
            for code, eco in data["ecosystems"].items()
        },
    }
    dst.write_text(json.dumps(export, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _export_hub_orchestrator_config() -> None:
    """Copy hub orchestrator template to shared assets."""
    import shutil

    src = content_path("hub_orchestrator")
    dst_dir = ROOT / "website" / "assets" / "data"
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / "hub-orchestrator.json"
    shutil.copy2(src, dst)


def _export_user_profile_config() -> None:
    """Copy profile experience config to shared assets for client-side personalization."""
    import shutil

    src = content_path("user_profile_experience")
    dst_dir = ROOT / "website" / "assets" / "data"
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / "user-profile-config.json"
    shutil.copy2(src, dst)


def _maybe_generate_og(force: bool = False) -> None:
    """Sync VEIP OG assets when manifest is incomplete or --generate-og."""
    md = ROOT / "datasets" / "master-data" / "visual-intelligence"
    manifest_path = md / "og_manifest.json"
    templates_path = md / "og_templates.json"
    if not templates_path.exists():
        return
    templates = json.loads(templates_path.read_text(encoding="utf-8")).get("templates", {})
    manifest_entries = 0
    if manifest_path.exists():
        manifest_entries = len(json.loads(manifest_path.read_text(encoding="utf-8")).get("entries", {}))
    if not force and manifest_entries >= len(templates):
        return
    veip = ROOT / "scripts" / "visual_intelligence_agents"
    sys.path.insert(0, str(veip))
    from og_generator import generate_all  # noqa: WPS433

    print(f"  VEIP: generating OG images ({manifest_entries}/{len(templates)} in manifest)...")
    generate_all(locale="pt-BR")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Calculadoras de Enfermagem static website (pt-BR + locales)")
    parser.add_argument("--pt-only", action="store_true", help="Skip locale variants (faster dev build)")
    parser.add_argument("--no-zip", action="store_true", help="Skip deploy zip packaging")
    parser.add_argument("--optimize-assets", action="store_true", help="Minify CSS/JS and use minified files in build")
    parser.add_argument("--webp", action="store_true", help="Convert raster images to WebP before build (requires Pillow)")
    parser.add_argument("--generate-og", action="store_true", help="Regenerate VEIP Open Graph images before build")
    args = parser.parse_args()

    t0 = time.monotonic()
    print("Calculadoras de Enfermagem — website generator (pt-BR)")
    _maybe_generate_og(args.generate_og)
    locale_data = build_locale_options()
    print(f"  locale options: {locale_data['count']} countries")
    seo = load_json(DATASETS / "metadata" / "seo_metadata.json")["records"]
    tools = load_json(DATASETS / "clinical" / "clinical_tools_catalog.json")["records"]
    definitions = {
        d["tool_code"]: d
        for d in load_json(DATASETS / "clinical" / "calculator_definitions.json")["records"]
    }
    quizzes = load_json(DATASETS / "education" / "quizzes.json")["records"]
    flashcards = load_json(DATASETS / "education" / "flashcards.json")["records"]
    paths = load_json(DATASETS / "education" / "learning_paths.json")["records"]
    exams = load_json(DATASETS / "education" / "simulated_exams.json")["records"]
    nanda = load_json(DATASETS / "clinical" / "nursing_diagnoses.json")["records"]
    guidelines = load_json(DATASETS / "clinical" / "clinical_guidelines.json")["records"]
    protocols = load_json(DATASETS / "clinical" / "institutional_protocols.json")["records"]
    competencies = load_json(DATASETS / "education" / "competencies.json")["records"]
    glossary = load_json(DATASETS / "master" / "nursing_dictionary.json")["records"]
    articles = load_json(content_path("articles"))["records"]
    assessments = load_json(DATASETS / "education" / "assessments.json")["records"]
    template_pages = load_json(content_path("template_pages"))
    labor_calculators = load_json(content_path("labor_calculators"))
    _hub_listings_fallback: dict = {}
    _hl_path = DATASETS / "content" / "hub_listings.json"
    if not _hl_path.exists():
        _hl_path = DATASETS / "archive" / "content" / "hub_listings.json"
    if _hl_path.exists():
        _hub_listings_fallback = load_json(_hl_path).get("hubs", {})
    institutional_hubs = load_json(content_path("institutional_hubs"))
    job_listings = load_json(DATASETS / "community" / "job_listings.json")["records"]
    course_listings = load_json(DATASETS / "community" / "course_listings.json")["records"]
    forum_topics = load_json(DATASETS / "community" / "forum_topics.json")["records"]
    forum_posts = load_json(DATASETS / "community" / "forum_posts.json")["records"]
    career_paths = load_json(DATASETS / "community" / "career_paths.json")["records"]
    contents = load_json(content_path("contents"))["records"]
    interventions = load_json(DATASETS / "clinical" / "nursing_interventions.json")["records"]
    outcomes = load_json(DATASETS / "clinical" / "nursing_outcomes.json")["records"]
    nnn_linkages = load_json(DATASETS / "clinical" / "nnn_linkages.json")["records"]
    entity_relations = load_json(DATASETS / "master" / "entity_relations.json")["records"]
    reassessment_rules = load_json(DATASETS / "operations" / "reassessment_rules.json")["records"]
    guidelines_by_code = {g.get("guideline_code"): g for g in guidelines}

    slug_map: dict[str, str] = {}
    used_slugs: set[str] = set()
    for tool in tools:
        slug_map[tool["tool_code"]] = unique_tool_slug(tool, used_slugs)

    generated: list[str] = []

    def emit(rel: str, html: str) -> None:
        write_page(OUT, rel, html)
        generated.append(rel)

    # Shared assets (header, footer, a11y bar CSS/JS from React src)
    from chrome_partials import export_chrome_partials
    from marketing_lib import export_marketing_config

    export_chrome_partials()
    export_marketing_config()
    _export_user_profile_config()
    _export_hub_orchestrator_config()

    if args.webp or args.optimize_assets:
        from pathlib import Path as _Path
        assets_root = _Path(__file__).resolve().parents[1] / "website" / "assets"
        if args.webp:
            try:
                from image_webp_lib import convert_tree_to_webp
                img_dir = assets_root / "images"
                if img_dir.exists():
                    n = len(convert_tree_to_webp(img_dir, quality=82, max_width=1920))
                    print(f"  WebP: {n} imagens processadas")
            except SystemExit as exc:
                print(f"  WebP skipped: {exc}")
        if args.optimize_assets:
            from minify_lib import minify_tree
            for sub in ("css", "js"):
                d = assets_root / sub
                if d.exists():
                    minify_tree(d, in_place=True, suffix=".min")
            print("  Assets: CSS/JS minificados (*.min.*)")

    copy_static_assets(OUT, use_minified=args.optimize_assets)

    sync_pt_br_home_partition()

    home_content = load_json(content_path("home_page"))
    daily_tips = load_json(content_path("daily_tips"))
    home_title = home_content["seo"]["title"]
    home_desc = home_content["seo"]["description"]
    emit("index.html", render_home_page(
        home_content, depth=0, title=home_title, description=home_desc, slug_map=slug_map,
        daily_tips=daily_tips,
    ))

    privacy = load_json(content_path("privacy_center"))
    emit("privacidade/index.html", render_privacy_center(
        privacy, depth=1,
        title=privacy["seo"]["title"],
        description=privacy["seo"]["description"],
    ))

    sustain = load_json(content_path("sustainability_center"))
    emit("sustentabilidade/index.html", render_sustainability_center(
        sustain, depth=1,
        title=sustain["seo"]["title"],
        description=sustain["seo"]["description"],
    ))

    inst_content = load_json(content_path("institutional_pages"))

    emit("missao/index.html", render_mission_page(inst_content["missao"], depth=1))
    emit("objetivo/index.html", render_objective_page(inst_content["objetivo"], depth=1))
    emit("sobre/index.html", render_about_page(inst_content["sobre"], depth=1))
    emit("acessibilidade/index.html", render_accessibility_center(inst_content["acessibilidade"], depth=1))
    emit("contato/index.html", render_contact_page(inst_content["contato"], depth=1, canonical_path="/contato"))
    emit("fale-conosco/index.html", render_contact_page(inst_content["contato"], depth=1, canonical_path="/fale-conosco"))
    emit("busca/index.html", render_search_page(inst_content["busca"], depth=1))

    # Institutional simple pages — skip pages handled above
    _inst_skip = {"privacidade", "missao", "objetivo", "sobre", "acessibilidade", "contato", "fale-conosco", "busca", "mapa-site"}
    for key in INST:
        if key in _inst_skip:
            continue
        emit(f"{key}/index.html", render_institutional(key, seo))

    hub_orchestrator_template = load_json(content_path("hub_orchestrator"))
    tool_concepts_data = build_tool_concepts_orchestrator(
        tools,
        quizzes=quizzes,
        flashcards=flashcards,
        paths=paths,
        protocols=protocols,
        competencies=competencies,
        slug_map=slug_map,
        depth=1,
        articles=articles,
        exams=exams,
        guidelines=guidelines,
        diagnoses=nanda,
        definitions=definitions,
        courses=course_listings,
        jobs=job_listings,
        template_pages=template_pages,
        contents=contents,
        interventions=interventions,
        outcomes=outcomes,
        nnn_linkages=nnn_linkages,
        entity_relations=entity_relations,
        reassessment_rules=reassessment_rules,
        glossary=glossary,
        forum_topics=forum_topics,
        career_paths=career_paths,
    )
    _export_tool_concepts_index(tool_concepts_data)
    hub_orchestrator = merge_orchestrator_hub(hub_orchestrator_template, tool_concepts_data)

    def hub_orchestrator_kwargs(concept: str = "") -> dict:
        return {"orchestrator": hub_orchestrator, "active_concept": concept}

    # Full hub pages (protocolos + ferramentas — mockup modular)
    protocol_items = build_protocol_items(protocols, slug_map, depth=1)
    tool_items = build_tool_items(tools, slug_map, hub="ferramentas")
    hub_protocols = hydrate_hub_counts(load_hub_template("protocols"), protocol_items)
    hub_tools = load_hub_template("tools")

    hp_title = hub_protocols.get("seo", {}).get("title") or seo_lookup(seo, "/protocolos", hub_protocols["hero"]["title"])[0]
    hp_desc = hub_protocols.get("seo", {}).get("description") or seo_lookup(seo, "/protocolos", hub_protocols["hero"]["title"])[1]
    emit("protocolos/index.html", render_hub_page(
        hub_protocols, protocol_items, depth=1, title=hp_title, description=hp_desc,
        hero_image="hero-protocols-hub.png", **hub_orchestrator_kwargs(),
    ))

    ft_title = hub_tools.get("seo", {}).get("title") or seo_lookup(seo, "/ferramentas", hub_tools["hero"]["title"])[0]
    ft_desc = hub_tools.get("seo", {}).get("description") or seo_lookup(seo, "/ferramentas", hub_tools["hero"]["title"])[1]
    emit("ferramentas/index.html", render_hub_page(
        hub_tools, tool_items, depth=1, title=ft_title, description=ft_desc,
        hero_image="hero-protocols-hub.png", **hub_orchestrator_kwargs(),
    ))

    calc_tools = [t for t in tools if t.get("tool_type") == "calculator" or "calc" in (t.get("category") or "")]
    scale_tools = [t for t in tools if t.get("tool_type") == "score" or "scale" in (t.get("category") or "")]
    calc_hub = {**hub_tools, "reference_page": "/calculadoras", "breadcrumb": [{"label": "Calculadoras", "href": None}]}
    calc_hub["hero"] = {**hub_tools["hero"], "title": "Calculadoras", "subtitle": "Calculadoras clínicas e de medicação — Calculadoras de Enfermagem 2026."}
    scale_hub = {**hub_tools, "reference_page": "/escalas", "breadcrumb": [{"label": "Escalas de Avaliação", "href": None}]}
    scale_hub["hero"] = {**hub_tools["hero"], "title": "Escalas de Avaliação", "subtitle": "Escalas assistenciais e scores clínicos."}

    calc_title, calc_desc = seo_lookup(seo, "/calculadoras", "Calculadoras")
    emit("calculadoras/index.html", render_hub_page(
        calc_hub, build_tool_items(calc_tools or tools[:40], slug_map, hub="sibling"),
        depth=1, title=calc_title, description=calc_desc, hero_image="hero-protocols-hub.png",
        **hub_orchestrator_kwargs(),
    ))

    scale_title, scale_desc = seo_lookup(seo, "/escalas", "Escalas de Avaliação")
    emit("escalas/index.html", render_hub_page(
        scale_hub, build_tool_items(scale_tools or tools[:40], slug_map, hub="sibling"),
        depth=1, title=scale_title, description=scale_desc, hero_image="hero-protocols-hub.png",
        **hub_orchestrator_kwargs(),
    ))

    library_items = build_library_items(guidelines, depth=1)
    hub_library = hydrate_hub_counts(load_hub_template("library"), library_items)
    lib_title = hub_library.get("seo", {}).get("title") or seo_lookup(seo, "/biblioteca", hub_library["hero"]["title"])[0]
    lib_desc = hub_library.get("seo", {}).get("description") or seo_lookup(seo, "/biblioteca", hub_library["hero"]["title"])[1]
    emit("biblioteca/index.html", render_hub_page(
        hub_library, library_items, depth=1, title=lib_title, description=lib_desc,
        hero_image="hero-protocols-hub.png", **hub_orchestrator_kwargs(),
    ))

    simulado_items = build_simulado_items(exams, depth=1)
    hub_simulados = hydrate_hub_counts(load_hub_template("simulados"), simulado_items)
    sim_title = hub_simulados.get("seo", {}).get("title") or seo_lookup(seo, "/simulados", hub_simulados["hero"]["title"])[0]
    sim_desc = hub_simulados.get("seo", {}).get("description") or seo_lookup(seo, "/simulados", hub_simulados["hero"]["title"])[1]
    emit("simulados/index.html", render_hub_page(
        hub_simulados, simulado_items, depth=1, title=sim_title, description=sim_desc,
        hero_image="hero-protocols-hub.png", **hub_orchestrator_kwargs(),
    ))

    article_items = build_article_items(articles, depth=1)
    hub_artigos = hydrate_hub_counts(load_hub_template("artigos"), article_items)
    art_hub_title = hub_artigos.get("seo", {}).get("title") or seo_lookup(seo, "/artigos", hub_artigos["hero"]["title"])[0]
    art_hub_desc = hub_artigos.get("seo", {}).get("description") or seo_lookup(seo, "/artigos", hub_artigos["hero"]["title"])[1]
    emit("artigos/index.html", render_hub_page(
        hub_artigos, article_items, depth=1, title=art_hub_title, description=art_hub_desc,
        hero_image="hero-protocols-hub.png", **hub_orchestrator_kwargs(),
    ))

    for article in articles:
        slug = article.get("slug") or slugify(article.get("title", "artigo"))
        emit(f"artigos/{slug}/index.html", render_article_page(article, depth=2))

    for exam in exams:
        slug = slugify(exam.get("exam_code", exam.get("title_pt", "exam")))
        emit(f"simulados/{slug}/index.html", render_simulation_page(exam, depth=2, quizzes=quizzes))

    for protocol in protocols:
        pslug = protocol_slug(protocol)
        guideline = guidelines_by_code.get(protocol.get("source_guideline_code"))
        emit(f"protocolos/{pslug}/index.html", render_protocol_page(
            protocol, depth=2, slug_map=slug_map, guideline=guideline,
        ))

    tp = template_pages.get("pages", {})
    samples = template_pages.get("scrape_samples", {})

    fc_items = build_flashcard_items(flashcards, depth=1)
    hub_flash = hydrate_hub_counts(load_hub_template("flashcards"), fc_items)
    fc_title = hub_flash.get("seo", {}).get("title") or seo_lookup(seo, "/flashcards", hub_flash["hero"]["title"])[0]
    fc_desc = hub_flash.get("seo", {}).get("description") or seo_lookup(seo, "/flashcards", hub_flash["hero"]["title"])[1]
    emit("flashcards/index.html", render_hub_page(
        hub_flash, fc_items, depth=1, title=fc_title, description=fc_desc, hero_image="hero-protocols-hub.png",
        **hub_orchestrator_kwargs(),
    ))

    deck_labels = {
        "DECK.NANDA": "NANDA-I", "DECK.NIC": "Intervenções NIC", "DECK.NOC": "Resultados NOC",
        "DECK.DRUG": "Farmacologia", "DECK.TOOLS": "Ferramentas clínicas", "DECK.GLOSSARY": "Glossário",
    }
    decks: dict[str, list] = {}
    for fc in flashcards:
        decks.setdefault(fc.get("deck_code", "GERAL"), []).append(fc)
    for deck_code, deck_cards in decks.items():
        dslug = slugify(deck_code)
        emit(f"flashcards/{dslug}/index.html", render_flashcard_study(
            deck_code, deck_cards, depth=2, deck_label=deck_labels.get(deck_code, deck_code),
        ))

    # Medications — nursing monographs + reference catalog
    from medication_lib import render_medication_hub, render_medication_page
    drug_refs = load_json(DATASETS / "clinical" / "drug_references.json")["records"]
    monographs = load_json(DATASETS / "clinical" / "drug_monographs.json")["records"]
    safety_goals = {g["goal_code"]: g for g in load_json(DATASETS / "clinical" / "patient_safety_goals.json")["records"]}
    med_rights = load_json(DATASETS / "clinical" / "medication_rights.json")["records"]
    emit("medicamentos/index.html", render_medication_hub(monographs, drug_refs, depth=1))
    for m in monographs:
        emit(f"medicamentos/{m['slug']}/index.html", render_medication_page(
            m, safety_goals, med_rights, depth=2,
        ))

    # NANDA / NIC / NOC libraries (client-side detail + NNN linkage cross-refs)
    nic = load_json(DATASETS / "clinical" / "nursing_interventions.json")["records"]
    noc = load_json(DATASETS / "clinical" / "nursing_outcomes.json")["records"]
    nnn_linkages = load_json(DATASETS / "clinical" / "nnn_linkages.json")["records"]
    nnn_idx = build_nnn_linkage_index(nnn_linkages, nanda, nic, noc)
    emit("nanda/index.html", render_nnn_library(nanda, kind="nanda", depth=1, linkage_index=nnn_idx))
    emit("nic/index.html", render_nnn_library(nic, kind="nic", depth=1, linkage_index=nnn_idx))
    emit("noc/index.html", render_nnn_library(noc, kind="noc", depth=1, linkage_index=nnn_idx))
    emit("sae/index.html", render_module_landing(tp["sae"], depth=1))
    emit("sbar/index.html", render_module_landing(tp["sbar"], depth=1))
    emit("sbar/novo/index.html", render_sbar_wizard(depth=2))
    emit("gestao/indicadores/index.html", render_metrics_dashboard(tp["indicadores"], depth=2))
    emit("curriculo/index.html", render_module_landing(tp["curriculo"], depth=1))
    emit("curriculo/criar/index.html", render_cv_wizard(depth=2))
    emit("calendario-vacinal/index.html", render_vaccine_calendar(tp["calendario_vacinal"], depth=1))
    emit("mapas-mentais/index.html", render_mindmap_page(tp["mapas_mentais"], depth=1))
    emit("trilhas/index.html", render_module_landing(tp["trilhas"], depth=1))
    emit("autoconhecimento/index.html", render_self_tests(assessments, tp["autoconhecimento"], depth=1))

    _seniority = {"junior": "Júnior", "pleno": "Pleno", "senior": "Sênior"}
    job_items = [
        {
            "title": j.get("title_pt", ""),
            "org": "Rede Calculadoras de Enfermagem",
            "location": j.get("region_pt") or ("Brasil" if j.get("country_code") == "BR" else j.get("country_code", "")),
            "tags": [t for t in [j.get("employment_type", ""), _seniority.get(j.get("seniority", ""), ""), j.get("macro_region", "")] if t],
            "posted": "2026", "href": "#",
        }
        for j in job_listings
    ] + samples.get("empregos", [])
    course_items = [
        {
            "title": c.get("title_pt", ""),
            "org": c.get("provider", "Calculadoras de Enfermagem Academy"),
            "location": c.get("modality", "online").title(),
            "tags": [t for t in [f"{c.get('ceu_hours', 0)}h", c.get("level", ""), "Gratuito" if c.get("is_free") else "Pago"] if t],
            "posted": "CEU", "href": c.get("provider_url", "#"),
        }
        for c in course_listings
    ] + samples.get("cursos", [])
    emit("empregos/index.html", render_scrape_hub(tp["empregos"], job_items, depth=1))
    emit("concursos/index.html", render_scrape_hub(tp["concursos"], samples.get("concursos", []), depth=1))
    emit("cursos/index.html", render_scrape_hub(tp["cursos_hub"], course_items, depth=1))
    emit("forum/index.html", render_forum_hub(forum_topics, forum_posts, depth=1))
    emit("calculadoras-trabalhistas/index.html", render_labor_calculators_hub(
        labor_calculators.get("hub", {}), labor_calculators.get("calculators", []), depth=1,
    ))
    for calc in labor_calculators.get("calculators", []):
        emit(f'calculadoras-trabalhistas/{calc["slug"]}/index.html', render_labor_calculator_page(calc, depth=2))

    # Listing hubs — unified hub_templates.json
    def _listing_hub(key: str) -> dict:
        try:
            return load_hub_template(key)
        except KeyError:
            return _hub_listings_fallback.get(key, {})

    quiz_items = build_quiz_items(quizzes, depth=1)
    emit("quiz/index.html", render_hub_page(
        hydrate_hub_counts(_listing_hub("quiz"), quiz_items), quiz_items, depth=1,
        hero_image="hero-protocols-hub.png", **hub_orchestrator_kwargs(),
    ))
    gloss_items = build_glossary_items(glossary, depth=1)
    emit("glossario/index.html", render_hub_page(
        hydrate_hub_counts(_listing_hub("glossario"), gloss_items), gloss_items, depth=1,
        hero_image="hero-protocols-hub.png", **hub_orchestrator_kwargs(),
    ))
    comp_items = build_competency_items(competencies, depth=1)
    emit("competencias/index.html", render_hub_page(
        hydrate_hub_counts(_listing_hub("competencias"), comp_items), comp_items, depth=1,
        hero_image="hero-protocols-hub.png", **hub_orchestrator_kwargs(),
    ))
    edu_items = build_education_hub_items(
        quizzes=quizzes, flashcards=flashcards, paths=paths, exams=exams, depth=1,
    )
    emit("educacao/index.html", render_hub_page(
        hydrate_hub_counts(_listing_hub("educacao"), edu_items),
        edu_items,
        depth=1, hero_image="hero-protocols-hub.png", **hub_orchestrator_kwargs(),
    ))
    tabelas_items = [
        {
            "id": "eletrólitos", "title": "Eletrólitos séricos", "description": "Valores de referência Na, K, Ca, Mg.",
            "badge": "Referência", "category": "Laboratorial", "category_id": "lab", "theme": "Laboratório",
            "filter_tags": ["Laboratorial"], "updated": "2026", "updated_sort": "2026",
            "href": "../calculadoras/index.html?q=eletrólito", "views": 420, "featured": True,
        },
        {
            "id": "gotejamento", "title": "Gotejamento IV", "description": "Fatores de conversão gtt/min ↔ ml/h.",
            "badge": "Cálculo", "category": "Medicação", "category_id": "med", "theme": "Medicação",
            "filter_tags": ["Medicação"], "updated": "2026", "updated_sort": "2026",
            "href": "../ferramentas/index.html?q=gotejamento", "views": 380, "featured": True,
        },
        {
            "id": "imc", "title": "IMC e antropometria", "description": "Classificação OMS adulto e pediátrico.",
            "badge": "Referência", "category": "Antropometria", "category_id": "anthro", "theme": "Pediatria",
            "filter_tags": ["Pediatria"], "updated": "2026", "updated_sort": "2026",
            "href": "../ferramentas/bmi/index.html", "views": 350, "featured": True,
        },
    ]
    emit("tabelas/index.html", render_hub_page(
        hydrate_hub_counts(_listing_hub("tabelas"), tabelas_items), tabelas_items, depth=1,
        hero_image="hero-protocols-hub.png", **hub_orchestrator_kwargs(),
    ))

    orchestrator_items = tool_concepts_data["all_items"]
    rec_title = hub_orchestrator.get("seo", {}).get("title") or seo_lookup(seo, "/recursos", hub_orchestrator["hero"]["title"])[0]
    rec_desc = hub_orchestrator.get("seo", {}).get("description") or seo_lookup(seo, "/recursos", hub_orchestrator["hero"]["title"])[1]
    emit("recursos/index.html", render_hub_page(
        hub_orchestrator, orchestrator_items, depth=1, title=rec_title, description=rec_desc,
        hero_image="hero-protocols-hub.png", **hub_orchestrator_kwargs(""),
    ))

    inst_pages = institutional_hubs.get("pages", {})
    inst_defaults = institutional_hubs.get("default_links", [])

    # Secondary institutional / placeholder pages (minimal real PT content, no "Em construção")
    secondary = [
        ("gestao", "Gestão Clínica", "Recursos de gestão e indicadores."),
        ("blog", "Blog", "Artigos e novidades."),
        ("dicas", "Dicas", "Dicas práticas de enfermagem."),
        ("tutoriais", "Tutoriais", "Guias passo a passo."),
        ("ajuda", "Ajuda", "Central de ajuda."),
        ("faq", "FAQ", "Perguntas frequentes."),
        ("equipe", "Equipe", "Conheça a equipe."),
        ("historia", "História", "Trajetória do projeto."),
        ("carreiras", "Carreiras", "Oportunidades."),
        ("imprensa", "Imprensa", "Assessoria de imprensa."),
        ("treinamentos", "Treinamentos", "Capacitações."),
        ("impacto", "Impacto Social", "Indicadores de impacto."),
        ("esg", "ESG", "Governança ambiental, social e corporativa."),
        ("noticias", "Notícias", "Notícias do setor."),
        ("casos", "Casos Clínicos", "Estudos de caso."),
        ("login", "Login", "Acesso à conta."),
        ("perfil", "Perfil", "Área do usuário."),
    ]
    for slug, hero_t, hero_s in secondary:
        if slug in ("sustentabilidade", "privacidade"):
            continue
        page_spec = inst_pages.get(slug, {
            "title": hero_t,
            "subtitle": hero_s,
            "route": f"/{slug}",
            "links": inst_defaults,
        })
        page_spec.setdefault("route", f"/{slug}")
        if slug == "blog" and "links" not in inst_pages.get("blog", {}):
            page_spec["links"] = inst_pages.get("blog", {}).get("links") or [
                {"title": "Artigos e Conteúdos", "description": hero_s, "href": "/artigos", "type": "artigo"},
                {"title": "Notícias", "description": "Novidades do setor.", "href": "/noticias", "type": "artigo"},
            ]
        emit(f"{slug}/index.html", render_institutional_hub(
            page_spec, depth=1, default_links=inst_defaults,
        ))

    # Termos — redireciona para aba na Central de Privacidade
    tt, td = seo_lookup(seo, "/termos", "Termos de Uso")
    emit("termos/index.html", render_page(
        depth=1, title=tt, description=td, canonical_path="/termos",
        hero_title="Termos de Uso", hero_subtitle="Consulte a Central de Privacidade.",
        breadcrumbs=[("Termos de Uso", None)],
        body='<section class="section section-container"><div class="card"><p>Os termos de uso completos estão na <a href="../privacidade/index.html#panel-termos">Central de Privacidade</a>.</p></div></section>',
    ))

    # 404
    t404, d404 = seo_lookup(seo, "/404", "Página não encontrada")
    emit("404/index.html", render_page(
        depth=1, title=t404, description=d404, canonical_path="/404",
        hero_title="Página não encontrada", hero_subtitle="O recurso solicitado não existe.",
        breadcrumbs=[("404", None)],
        body='<section class="section section-container"><div class="card"><p>A página que você procurou não foi encontrada nesta versão estática do site Calculadoras de Enfermagem 2026.</p><p>Use o mapa do site ou retorne à página inicial para continuar a navegação.</p><p><a class="btn" href="../index.html">Voltar ao início</a> · <a href="../mapa-site/index.html">Mapa do site</a></p></div></section>',
    ))

    # 100 tool pages (reuse render_tool_page)
    for tool in tools:
        slug = slug_map[tool["tool_code"]]
        definition = definitions.get(tool["tool_code"])
        emit(f"ferramentas/{slug}/index.html", render_tool_page(
            tool, definition, depth=2, path_slug=slug,
            slug_map=slug_map, tools=tools, protocols=protocols,
        ))

    # Mapa do site (structured + auto-generated links)
    map_links = sorted(set(generated))
    map_rows = [(p.replace("/index.html", "").replace("index.html", "/") or "Início", p) for p in map_links]
    emit("mapa-site/index.html", render_sitemap_page(
        inst_content["mapa_site"], depth=1, extra_links=map_rows[:200],
    ))

    html_pages = [p for p in generated if p.endswith(".html")]

    # ── i18n: locale variants ──
    from seo_lib import LOCALES
    from post_build_seo import finalize_post_build_seo

    translated_home_prefixes: set[str] = set()

    if not args.pt_only:
        for prefix, hreflang, lang, direction in LOCALES:
            if not prefix:
                continue
            home_doc, use_locale_home = resolve_locale_home(hreflang)
            if not use_locale_home:
                continue
            translated_home_prefixes.add(prefix)
            with render_locale_ctx(
                lang=lang,
                locale=hreflang,
                direction=direction,
                url_prefix=prefix,
                skip_label=skip_link_label(hreflang),
            ):
                emit(
                    f"{prefix}/index.html",
                    render_home_page(
                        home_doc,
                        depth=1,
                        title=home_doc["seo"]["title"],
                        description=home_doc["seo"]["description"],
                        slug_map=slug_map,
                        daily_tips=daily_tips,
                        canonical_path="/",
                    ),
                )

        locale_jobs = [(prefix, lang, direction) for prefix, _hl, lang, direction in LOCALES if prefix]
        with ThreadPoolExecutor(max_workers=min(6, len(locale_jobs) or 1)) as pool:
            futures = [
                pool.submit(
                    _localize_batch,
                    OUT,
                    [p for p in html_pages if p not in ({"index.html"} if prefix in translated_home_prefixes else set())],
                    prefix,
                    lang,
                    direction,
                )
                for prefix, lang, direction in locale_jobs
            ]
            for fut in futures:
                fut.result()
        n_translated = len(translated_home_prefixes)
        print(f"  Locales: {len(LOCALES)} ({', '.join(p or 'pt-BR' for p, *_ in LOCALES)}) — {n_translated} home(s) com conteúdo traduzido")
    else:
        print("  Locales: 1 (pt-BR only — --pt-only)")

    seo_stats = finalize_post_build_seo(OUT, html_pages, build_locales=not args.pt_only)

    from build_lib import count_build_files, validate_a11y_sample, validate_jsonld_sample, write_build_report, zip_build

    elapsed = time.monotonic() - t0
    file_counts = count_build_files(OUT)
    jsonld = validate_jsonld_sample(OUT)
    a11y = validate_a11y_sample(OUT)
    phases = [
        {"name": "Generate pages (pt-BR)", "status": "OK", "elapsed_s": round(elapsed * 0.85, 2)},
        {"name": "Locales + post-build SEO", "status": "OK", "elapsed_s": round(elapsed * 0.15, 2)},
    ]
    write_build_report(
        OUT, phase_results=phases, file_counts=file_counts,
        jsonld=jsonld, a11y=a11y, elapsed_s=elapsed,
    )
    if not args.no_zip and not args.pt_only:
        zip_path = zip_build(OUT)
        print(f"  Zip: {zip_path}")

    all_pages = sorted(set(generated))
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "locale": "pt-BR",
        "locales_built": 1 if args.pt_only else len(LOCALES),
        "output_dir": str(OUT.relative_to(ROOT)).replace("\\", "/"),
        "page_count": len(all_pages),
        "tool_pages": len(tools),
        "search_index_entries": seo_stats.get("search_entries", 0),
        "pages": all_pages,
    }
    manifest_path = OUT / "generation_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"  Pages: {len(generated)}")
    print(f"  Search index: {seo_stats.get('search_entries', 0)} entries (from HTML scan)")
    print(f"  Tools: {len(tools)}")
    print(f"  Output: {OUT}")
    print(f"  Manifest: {manifest_path}")
    print(f"  Elapsed: {elapsed:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
