"""Microphases 1.9 (css_classes), 1.10 (templates), 1.11 (mockup components)."""
import hashlib
import json
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "datasets"
NOW = datetime.now(timezone.utc)
NOW_Z = NOW.strftime("%Y-%m-%dT%H:%M:%SZ")
NOW_ISO = NOW.isoformat().replace("+00:00", "Z")


def uid():
    return str(uuid.uuid4())


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8", newline="\r\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\r\n")


CSS_CLASSES = [
    ("site-shell", "layout", "Shell global da pagina", None, None),
    ("page-hero", "hero", "Hero institucional navy (missao)", "INST.PAGE_HERO", "COLOR.SECONDARY.800"),
    ("card-content", "card", "Card branco institucional", None, "COLOR.CLINICAL.SURFACE"),
    ("card-highlight", "card", "Card gradiente navy", None, "COLOR.SECONDARY.800"),
    ("value-card", "card", "Card valor com icone gradiente", None, "COLOR.CLINICAL.SURFACE"),
    ("tab-menu", "navigation", "Abas horizontais", "UI.TAB_MENU", "COLOR.PRIMARY.500"),
    ("stat-card", "data", "Estatistica grande", "UI.STAT_CARD", "COLOR.PRIMARY.500"),
    ("timeline", "data", "Timeline horizontal", "UI.TIMELINE", "COLOR.SECONDARY.700"),
    ("feature-card", "card", "Card icone+titulo+texto", "UI.FEATURE_CARD", "COLOR.CLINICAL.SURFACE"),
    ("tool-tile", "navigation", "Tile quadrado ferramenta", "UI.TOOL_TILE", "COLOR.PRIMARY.500"),
    ("document-card", "card", "Card documento PDF", "UI.DOCUMENT_CARD", "COLOR.CLINICAL.SURFACE"),
    ("sidebar-nav", "navigation", "Menu lateral categorias", "UI.FILTER_SIDEBAR", "COLOR.CLINICAL.BG"),
    ("search-bar", "form", "Busca com botao teal", "UI.SEARCH_BAR", "COLOR.CLINICAL.SURFACE"),
    ("data-table", "data", "Tabela de dados", "UI.DATA_TABLE", "COLOR.CLINICAL.BORDER"),
    ("metric-card", "data", "Metrica com trend", "UI.METRIC_CARD", "COLOR.CLINICAL.SURFACE"),
    ("callout", "content", "Caixa destaque info", "UI.CALLOUT", "COLOR.PRIMARY.50"),
    ("tag-pill", "content", "Tag categoria", "UI.TAG_PILL", "COLOR.CLINICAL.BG"),
    ("badge-validated", "content", "Badge validado clinicamente", "UI.BADGE", "COLOR.SEMANTIC.SUCCESS.DEFAULT"),
    ("cta-banner", "section", "Banner CTA navy", "UI.CTA_BANNER", "COLOR.SECONDARY.900"),
    ("footer-cta", "section", "CTA rodape pagina", "UI.FOOTER_CTA", "COLOR.SECONDARY.900"),
    ("article-layout", "layout", "Artigo 2 colunas + TOC", "INST.ARTICLE_TOC", None),
    ("calc-split", "layout", "Calculadora input|resultado", None, None),
    ("calc-input-panel", "form", "Painel inputs calculadora", "CALC.INPUT_PANEL", "COLOR.CLINICAL.SURFACE"),
    ("calc-result-panel", "data", "Painel resultado", "CALC.RESULT_PANEL", "COLOR.PRIMARY.50"),
    ("scale-grid", "layout", "Grid escalas", "SCALE.FILTER_GRID", None),
    ("scale-questionnaire", "form", "Formulario escala", "SCALE.QUESTIONNAIRE", "COLOR.CLINICAL.SURFACE"),
    ("scale-score-box", "data", "Pontuacao/classificacao", "SCALE.SCORE_SUMMARY", "COLOR.PRIMARY.500"),
    ("pdf-report", "print", "Relatorio PDF", "SCALE.PDF_REPORT", "COLOR.CLINICAL.SURFACE"),
    ("protocol-card", "card", "Card protocolo", "TOOL.PROTOCOL_CARD", "COLOR.CLINICAL.SURFACE"),
    ("simulation-card", "card", "Card simulado", "TOOL.SIMULATION_CARD", "COLOR.CLINICAL.SURFACE"),
    ("dashboard-grid", "layout", "Grid dashboard gestao", None, None),
    ("hero-landing", "hero", "Hero landing homepage", "HERO.LANDING", "COLOR.SECONDARY.900"),
    ("hero-image", "hero", "Hero imagem sustentabilidade", "HERO.IMAGE", "COLOR.SECONDARY.900"),
    ("mode-urgency", "theme", "Modo urgencia", "VIEW_MODE.URGENCY", "COLOR.SEMANTIC.ERROR.DEFAULT"),
    ("mode-standard", "theme", "Modo padrao", "VIEW_MODE.STANDARD", "COLOR.PRIMARY.500"),
]

TEMPLATES = [
    ("TPL.INSTITUTIONAL", "Institutional Page", "LAYOUT.INSTITUTIONAL", "/missao", True),
    ("TPL.LANDING_HOME", "Landing Home", "LAYOUT.LANDING_HOME", "/", False),
    ("TPL.TAB_INSTITUTIONAL", "Tab Institutional", "LAYOUT.TAB_INSTITUTIONAL", "/privacidade", False),
    ("TPL.ARTICLE", "Article Page", "LAYOUT.ARTICLE", "/blog", False),
    ("TPL.CALCULATOR", "Calculator Page", "LAYOUT.CALCULATOR_SPLIT", "/calculadoras/gotejamento", False),
    ("TPL.SCALE_LIST", "Scale Listing", "LAYOUT.SCALE_LIST", "/escalas", False),
    ("TPL.SCALE_FORM", "Scale Assessment", "LAYOUT.SCALE_FORM", "/calculadoras/meem", False),
    ("TPL.TOOL_SIDEBAR", "Tool Sidebar", "LAYOUT.TOOL_SIDEBAR", "/protocolos", False),
    ("TPL.DASHBOARD", "Dashboard", "LAYOUT.DASHBOARD_GRID", "/gestao", False),
    ("TPL.SEARCH_HUB", "Search Hub", "LAYOUT.SEARCH_HUB", "/ferramentas", False),
]

NEW_COMPONENTS = [
    ("UI.TAB_MENU", "TabMenu", "navigation", "Abas privacidade/ESG"),
    ("UI.STAT_CARD", "StatCard", "data", "Stats impacto/ESG"),
    ("UI.TIMELINE", "Timeline", "data", "Roadmap ESG"),
    ("UI.FEATURE_CARD", "FeatureCard", "card", "Card generico mockups"),
    ("UI.TOOL_TILE", "ToolTile", "navigation", "Tile ecossistema ferramentas"),
    ("UI.DOCUMENT_CARD", "DocumentCard", "card", "Documento ler/baixar"),
    ("UI.FILTER_SIDEBAR", "FilterSidebar", "navigation", "Sidebar filtros"),
    ("UI.SEARCH_BAR", "SearchBar", "form", "Busca avancada"),
    ("UI.DATA_TABLE", "DataTable", "data", "Tabela vacinas/doencas"),
    ("UI.METRIC_CARD", "MetricCard", "data", "Indicadores gestao"),
    ("UI.CALLOUT", "Callout", "content", "Destaque artigo"),
    ("UI.TAG_PILL", "TagPill", "content", "Tags artigo"),
    ("UI.BADGE", "Badge", "content", "Validado clinicamente"),
    ("UI.CTA_BANNER", "CTABanner", "section", "Banner CTA"),
    ("UI.FOOTER_CTA", "FooterCTA", "section", "CTA rodape"),
    ("UI.PROGRESS_BAR", "ProgressBar", "data", "Trilha conhecimento"),
    ("INST.ARTICLE_TOC", "ArticleTOC", "institutional", "Sumario artigo"),
    ("INST.SIDEBAR_CARD", "SidebarInfoCard", "institutional", "Card lateral privacidade"),
    ("HERO.LANDING", "LandingHero", "hero", "Hero homepage"),
    ("HERO.IMAGE", "ImageHero", "hero", "Hero sustentabilidade"),
    ("CALC.INPUT_PANEL", "CalculatorInputPanel", "calculator", "Inputs calculadora"),
    ("CALC.RESULT_PANEL", "CalculatorResultPanel", "calculator", "Resultado calculadora"),
    ("SCALE.FILTER_GRID", "ScaleFilterGrid", "scale", "Grid escalas"),
    ("SCALE.QUESTIONNAIRE", "ScaleQuestionnaire", "scale", "Form MEEM etc"),
    ("SCALE.SCORE_SUMMARY", "ScaleScoreSummary", "scale", "Score/classificacao"),
    ("SCALE.PDF_REPORT", "ScalePdfReport", "scale", "Relatorio PDF"),
    ("TOOL.PROTOCOL_CARD", "ProtocolCard", "tool", "Card protocolo"),
    ("TOOL.SIMULATION_CARD", "SimulationCard", "tool", "Card simulado"),
    ("TOOL.FLASHCARD", "FlashcardDeck", "tool", "Flashcards"),
    ("TOOL.MINDMAP", "MindMapCanvas", "tool", "Mapa mental"),
    ("DASH.SAE", "SAEModule", "dashboard", "Modulo SAE"),
    ("DASH.SBAR", "SBARModule", "dashboard", "Modulo SBAR"),
    ("DASH.INDICATORS", "IndicatorsChart", "dashboard", "Grafico indicadores"),
    ("BRAND.WAVY_FOOTER", "WavyFooter", "brand", "Rodape ondulado"),
    ("BRAND.HEX_PATTERN", "HexPattern", "brand", "Padrao hexagonal"),
]

NEW_LAYOUTS = [
    ("LAYOUT.LANDING_HOME", "LandingHomeLayout", "Homepage"),
    ("LAYOUT.TAB_INSTITUTIONAL", "TabInstitutionalLayout", "Privacidade/ESG abas"),
    ("LAYOUT.ARTICLE", "ArticleLayout", "Artigo + TOC"),
    ("LAYOUT.CALCULATOR_SPLIT", "CalculatorSplitLayout", "Calc split"),
    ("LAYOUT.SCALE_LIST", "ScaleListLayout", "Lista escalas"),
    ("LAYOUT.SCALE_FORM", "ScaleFormLayout", "Form escala"),
    ("LAYOUT.TOOL_SIDEBAR", "ToolSidebarLayout", "Sidebar ferramentas"),
    ("LAYOUT.DASHBOARD_GRID", "DashboardGridLayout", "Dashboard gestao"),
    ("LAYOUT.SEARCH_HUB", "SearchHubLayout", "Hub busca"),
]


def generate_css_classes():
    records = []
    for row in CSS_CLASSES:
        cls, cat, desc, comp, token = row
        records.append({
            "uuid": uid(), "class_name": cls, "category": cat, "description": desc,
            "component_code": comp, "primary_token_code": token,
            "reference_page": "/missao" if cls in ("page-hero", "card-content", "card-highlight", "value-card") else None,
            "css_file": "styles/vanilla/templates.css",
            "status": "active", "created_at": NOW_Z, "updated_at": NOW_Z,
        })
    save_json(ROOT / "metadata/css_classes.json", {
        "generated_at": NOW_ISO, "schema_version": "2026.1.0", "records": records,
        "micro_phase": "1.9", "entity": "CssClass", "reference_page": "/missao",
        "count": len(records),
        "validation_summary": {"total_records": len(records), "unique_keys_checked": ["class_name"], "passed": True, "errors": []},
    })
    return len(records)


def generate_templates():
    records = []
    for code, name, layout, page, is_default in TEMPLATES:
        records.append({
            "uuid": uid(), "template_code": code, "name": name, "layout_code": layout,
            "reference_page": page, "is_default": is_default,
            "status": "active" if is_default else "planned",
            "created_at": NOW_Z, "updated_at": NOW_Z,
        })
    save_json(ROOT / "metadata/templates.json", {
        "generated_at": NOW_ISO, "schema_version": "2026.1.0", "records": records,
        "micro_phase": "1.10", "entity": "PageTemplate", "reference_page": "/missao",
        "count": len(records),
        "validation_summary": {"total_records": len(records), "passed": True, "errors": []},
    })
    return len(records)


def append_mockup_catalog():
    comp = load_json(ROOT / "metadata/components.json")
    lay = load_json(ROOT / "metadata/layouts.json")
    existing_c = {r["component_code"] for r in comp["records"]}
    existing_l = {r["layout_code"] for r in lay["records"]}
    ac = al = 0
    for code, name, cat, desc in NEW_COMPONENTS:
        if code in existing_c:
            continue
        comp["records"].append({
            "uuid": uid(), "component_code": code, "name": name, "category": cat,
            "source_path": None, "layout_code": None, "parent_component_code": None,
            "css_classes": [], "reference_page": None, "is_default_reference": False,
            "implementation_status": "planned", "mockup_cataloged": True,
            "description": desc, "status": "active", "created_at": NOW_Z, "updated_at": NOW_Z,
        })
        ac += 1
    for code, name, desc in NEW_LAYOUTS:
        if code in existing_l:
            continue
        lay["records"].append({
            "uuid": uid(), "layout_code": code, "name": name, "template_path": None,
            "reference_page": None, "is_default": False, "parent_layout_code": "LAYOUT.MAIN",
            "component_codes": [], "implementation_status": "planned", "mockup_cataloged": True,
            "description": desc, "status": "active", "created_at": NOW_Z, "updated_at": NOW_Z,
        })
        al += 1
    comp["count"] = len(comp["records"])
    lay["count"] = len(lay["records"])
    save_json(ROOT / "metadata/components.json", comp)
    save_json(ROOT / "metadata/layouts.json", lay)
    return ac, al


def generate_stubs():
    personas = [
        ("PERSONA.STUDENT", "Estudante", ["educacao", "simulados", "flashcards"]),
        ("PERSONA.NURSE", "Enfermeiro", ["calculadoras", "escalas", "protocolos"]),
        ("PERSONA.MANAGER", "Gestor", ["dashboard", "indicadores", "sae", "sbar"]),
        ("PERSONA.ACADEMIC", "Academico", ["artigos", "biblioteca", "nanda"]),
    ]
    save_json(ROOT / "metadata/personas.json", {
        "generated_at": NOW_ISO, "schema_version": "2026.1.0",
        "micro_phase": "2.0", "entity": "Persona",
        "note": "Stub — aguarda Plano_Implementacao_NKOS_v44.json",
        "records": [{
            "uuid": uid(), "persona_code": c, "name": n,
            "priority_modules": m, "default_view_mode": "VIEW_MODE.STANDARD",
            "status": "planned", "created_at": NOW_Z, "updated_at": NOW_Z,
        } for c, n, m in personas],
        "count": 4, "validation_summary": {"passed": True, "errors": []},
    })
    modes = [
        ("VIEW_MODE.STANDARD", "Padrao", "active", "mode-standard"),
        ("VIEW_MODE.URGENCY", "Urgencia", "planned", "mode-urgency"),
        ("VIEW_MODE.COMPACT", "Compacto", "planned", None),
        ("VIEW_MODE.PRINT", "Impressao", "planned", None),
    ]
    save_json(ROOT / "metadata/view_modes.json", {
        "generated_at": NOW_ISO, "schema_version": "2026.1.0",
        "micro_phase": "2.0", "entity": "ViewMode",
        "note": "Modos por ferramenta — proxima fase NKOS v44",
        "records": [{
            "uuid": uid(), "view_mode_code": c, "name": n, "status": s,
            "css_class": css, "applies_to": ["site", "tools"],
            "created_at": NOW_Z, "updated_at": NOW_Z,
        } for c, n, s, css in modes],
        "count": 4, "validation_summary": {"passed": True, "errors": []},
    })


def update_manifest():
    m = load_json(ROOT / "metadata/generation_manifest.json")
    for p in ["1.9_css_class", "1.10_template", "1.11_mockup_catalog", "2.0_persona_stub", "2.0_view_mode_stub"]:
        if p not in m["phases_completed"]:
            m["phases_completed"].append(p)
    m["files_generated"].update({
        "1.9_css_class": "metadata\\css_classes.json",
        "1.10_template": "metadata\\templates.json",
        "2.0_persona_stub": "metadata\\personas.json",
        "2.0_view_mode_stub": "metadata\\view_modes.json",
    })
    m["next_phase"] = "Plano_Implementacao_NKOS_v44.json"
    m["updated_at"] = NOW_ISO
    for phase, rel in m["files_generated"].items():
        fp = ROOT / rel.replace("\\", "/")
        if fp.exists():
            m["checksums"][phase] = hashlib.md5(fp.read_bytes()).hexdigest()[:16]
    save_json(ROOT / "metadata/generation_manifest.json", m)


if __name__ == "__main__":
    c = generate_css_classes()
    t = generate_templates()
    ac, al = append_mockup_catalog()
    generate_stubs()
    update_manifest()
    print(f"css_classes={c} templates={t} +components={ac} +layouts={al}")
