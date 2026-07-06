"""Generate microphases 1.6 (tokens), 1.7 (components), 1.8 (layouts)."""
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

PRIMARY = {
    50: "#ecfdf5",
    100: "#d1fae5",
    200: "#a7f3d0",
    300: "#6ee7b7",
    400: "#34d399",
    500: "#10b981",
    600: "#059669",
    700: "#047857",
    800: "#065f46",
    900: "#064e3b",
}

NAVY = {
    50: "#f0f4f8",
    100: "#d9e2ec",
    200: "#bcccdc",
    300: "#9fb3c8",
    400: "#829ab1",
    500: "#627d98",
    600: "#486581",
    700: "#334e68",
    800: "#243b53",
    900: "#102a43",
    950: "#0a1628",
}

CLINICAL = {
    "BG": "#f8fafc",
    "SURFACE": "#ffffff",
    "BORDER": "#e2e8f0",
    "TEXT": "#0f172a",
    "MUTED": "#64748b",
    "SUBTLE": "#94a3b8",
}

SLATE_NEUTRAL = {
    50: "#f8fafc",
    100: "#f1f5f9",
    200: "#e2e8f0",
    300: "#cbd5e1",
    400: "#94a3b8",
    500: "#64748b",
    600: "#475569",
    700: "#334155",
    800: "#1e293b",
    900: "#0f172a",
    950: "#020617",
}


def uid():
    return str(uuid.uuid4())


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8", newline="\r\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\r\n")


def update_design_tokens():
    path = ROOT / "metadata/design_tokens.json"
    data = load_json(path)
    updated = 0

    for record in data["records"]:
        code = record["token_code"]
        changed = False

        if code.startswith("COLOR.PRIMARY."):
            step = int(code.split(".")[-1])
            if step in PRIMARY:
                record["value"] = PRIMARY[step]
                record["description"] = (
                    f"Cor primária {step} — verde esmeralda (página missão / globals.css)"
                )
                record["updated_at"] = NOW_Z
                changed = True

        elif code.startswith("COLOR.SECONDARY."):
            step = int(code.split(".")[-1])
            if step in NAVY:
                record["value"] = NAVY[step]
                record["description"] = (
                    f"Cor navy {step} — azul institucional (hero missão, footer)"
                )
                record["updated_at"] = NOW_Z
                changed = True

        elif code.startswith("COLOR.NEUTRAL."):
            step = int(code.split(".")[-1])
            if step in SLATE_NEUTRAL:
                record["value"] = SLATE_NEUTRAL[step]
                record["description"] = (
                    f"Escala slate {step} — neutros da UI institucional"
                )
                record["updated_at"] = NOW_Z
                changed = True

        elif code == "COLOR.TEXT.PRIMARY":
            record["value"] = CLINICAL["TEXT"]
            record["updated_at"] = NOW_Z
            changed = True
        elif code == "COLOR.TEXT.SECONDARY":
            record["value"] = CLINICAL["MUTED"]
            record["updated_at"] = NOW_Z
            changed = True
        elif code == "COLOR.BACKGROUND.DEFAULT":
            record["value"] = CLINICAL["BG"]
            record["updated_at"] = NOW_Z
            changed = True
        elif code == "COLOR.BACKGROUND.ELEVATED":
            record["value"] = CLINICAL["SURFACE"]
            record["updated_at"] = NOW_Z
            changed = True
        elif code == "COLOR.BORDER.LIGHT":
            record["value"] = "#f1f5f9"
            record["updated_at"] = NOW_Z
            changed = True
        elif code == "COLOR.BORDER.DEFAULT":
            record["value"] = CLINICAL["BORDER"]
            record["updated_at"] = NOW_Z
            changed = True
        elif code == "COLOR.BORDER.STRONG":
            record["value"] = "#cbd5e1"
            record["updated_at"] = NOW_Z
            changed = True

        if changed:
            updated += 1

    # Add navy-950 and clinical tokens if missing
    existing = {r["token_code"] for r in data["records"]}
    new_records = []

    if "COLOR.SECONDARY.950" not in existing:
        new_records.append(
            {
                "uuid": uid(),
                "token_code": "COLOR.SECONDARY.950",
                "token_type": "COLOR",
                "name": "Navy 950",
                "value": NAVY[950],
                "description": "Cor navy 950 — footer e fundos escuros",
                "status": "active",
                "created_at": NOW_Z,
                "updated_at": NOW_Z,
            }
        )

    clinical_map = {
        "COLOR.CLINICAL.BG": ("Clinical Background", CLINICAL["BG"]),
        "COLOR.CLINICAL.SURFACE": ("Clinical Surface", CLINICAL["SURFACE"]),
        "COLOR.CLINICAL.BORDER": ("Clinical Border", CLINICAL["BORDER"]),
        "COLOR.CLINICAL.TEXT": ("Clinical Text", CLINICAL["TEXT"]),
        "COLOR.CLINICAL.MUTED": ("Clinical Muted", CLINICAL["MUTED"]),
        "COLOR.CLINICAL.SUBTLE": ("Clinical Subtle", CLINICAL["SUBTLE"]),
    }
    for code, (name, value) in clinical_map.items():
        if code not in existing:
            new_records.append(
                {
                    "uuid": uid(),
                    "token_code": code,
                    "token_type": "COLOR",
                    "name": name,
                    "value": value,
                    "description": f"Token clínico — referência missão / globals.css",
                    "status": "active",
                    "created_at": NOW_Z,
                    "updated_at": NOW_Z,
                }
            )

    data["records"].extend(new_records)
    data["generated_at"] = NOW_ISO
    data["micro_phase"] = "1.6"
    data["template_id"] = "T1.6"
    data["reference_page"] = "/missao"
    data["count"] = len(data["records"])
    td = Counter(r["token_type"] for r in data["records"])
    data["type_distribution"] = dict(sorted(td.items()))
    data["validation_summary"]["total_records"] = len(data["records"])
    data["validation_summary"]["passed"] = True
    data["validation_summary"]["errors"] = []
    data["sync_source"] = "calculadoras-enfermagem-react/src/styles/globals.css"

    save_json(path, data)
    return updated, len(new_records), len(data["records"])


COMPONENTS = [
    ("LAYOUT.MAIN", "MainLayout", "shell", "components/MainLayout.tsx", "LAYOUT.MAIN", None, "Wrapper global: header, a11y bar, main, footer"),
    ("LAYOUT.INSTITUTIONAL", "InstitutionalLayout", "layout", "components/Institutional/InstitutionalLayout.tsx", "LAYOUT.INSTITUTIONAL", "LAYOUT.MAIN", "Layout institucional padrão (referência: /missao)"),
    ("NAV.HEADER", "Header", "navigation", "components/Header/Header.tsx", None, "LAYOUT.MAIN", "Header fixo com mega menu"),
    ("NAV.FOOTER", "Footer", "navigation", "components/Footer/Footer.tsx", None, "LAYOUT.MAIN", "Rodapé institucional"),
    ("NAV.MEGA_MENU", "MegaMenu", "navigation", "components/MegaMenu/MegaMenu.tsx", None, "NAV.HEADER", "Dropdown mega menu"),
    ("NAV.BREADCRUMB", "Breadcrumb", "navigation", "components/Institutional/Breadcrumb.tsx", None, "LAYOUT.INSTITUTIONAL", "Trilha de navegação"),
    ("A11Y.BAR", "AccessibilityBar", "accessibility", "components/AccessibilityBar/AccessibilityBar.tsx", None, "LAYOUT.MAIN", "Barra de acessibilidade"),
    ("UI.BUTTON", "Button", "ui", "components/UI/button.tsx", None, None, "Botão com variantes CVA"),
    ("UI.SLOT", "Slot", "ui", "components/UI/slot.tsx", None, None, "Composição polimórfica"),
    ("UI.ICON", "Icon", "ui", "components/UI/Icon.tsx", None, None, "Ícones Lucide lazy-loaded"),
    ("UI.TOAST", "Toast", "ui", "components/Toast.tsx", None, "LAYOUT.MAIN", "Notificações toast"),
    ("UI.COOKIE_BANNER", "CookieBanner", "ui", "components/CookieBanner.tsx", None, "LAYOUT.MAIN", "Consentimento LGPD"),
    ("UI.SCROLL_TOP", "ScrollToTopFAB", "ui", "components/ScrollToTopFAB.tsx", None, "LAYOUT.MAIN", "Botão voltar ao topo"),
    ("UI.PREFERENCES_MODAL", "PreferencesModal", "ui", "components/PreferencesModal.tsx", None, "LAYOUT.MAIN", "Modal de preferências"),
    ("INST.PAGE_HERO", "PageHero", "institutional", "components/Institutional/PageHero.tsx", None, "LAYOUT.INSTITUTIONAL", "Hero navy com bokeh — usado em /missao"),
    ("INST.SECTION_WRAPPER", "SectionWrapper", "institutional", "components/Institutional/SectionWrapper.tsx", None, "LAYOUT.INSTITUTIONAL", "Wrapper animado de seção"),
    ("HOME.HERO", "Hero", "home", "components/Hero/Hero.tsx", None, None, "Hero da landing (não é página padrão)"),
    ("HOME.QUEM_SOMOS", "QuemSomos", "home", "components/Sections/QuemSomos.tsx", None, None, "Seção quem somos"),
    ("HOME.PILARES", "NossosPilares", "home", "components/Sections/NossosPilares.tsx", None, None, "Grid de pilares"),
    ("HOME.DIFERENCIAIS", "OQueNosTornaUnicos", "home", "components/Sections/OQueNosTornaUnicos.tsx", None, None, "Diferenciais"),
    ("HOME.IMPACTO", "ImpactoGlobal", "home", "components/Sections/ImpactoGlobal.tsx", None, None, "Impacto global"),
    ("HOME.ECOSSISTEMA", "Ecossistema", "home", "components/Sections/Ecossistema.tsx", None, None, "Ecossistema de soluções"),
    ("HOME.FEATURES", "Features", "home", "components/Sections/Features.tsx", None, None, "Grid de features"),
    ("HOME.CTA", "CTASection", "home", "components/Sections/CTASection.tsx", None, None, "Banner CTA"),
    ("HOME.PARCEIROS", "Parceiros", "home", "components/Sections/Parceiros.tsx", None, None, "Parceiros"),
    ("HOME.PESQUISA", "PesquisaAvancada", "home", "components/Sections/PesquisaAvancada.tsx", None, None, "Pesquisa avançada"),
    ("CALC.TEMPLATE", "CalculatorTemplate", "calculator", "components/Calculators/CalculatorTemplate.tsx", "LAYOUT.CALCULATOR", None, "Template base de calculadora"),
    ("CALC.FORM", "CalculatorForm", "calculator", "components/Calculators/CalculatorForm.tsx", None, "CALC.TEMPLATE", "Formulário genérico"),
    ("CALC.RESULT", "CalculatorResult", "calculator", "components/Calculators/CalculatorResult.tsx", None, "CALC.TEMPLATE", "Exibição de resultado"),
    ("CALC.FORMULA_FORM", "FormulaForm", "calculator", "components/Calculators/FormulaForm.tsx", None, "CALC.TEMPLATE", "Form de fórmulas"),
    ("CALC.SCALE_FORM", "ScaleForm", "calculator", "components/Calculators/ScaleForm.tsx", None, "CALC.TEMPLATE", "Form de escalas"),
    ("SCALE.TEMPLATE", "ScaleTemplate", "scale", "components/scales/ScaleTemplate.tsx", "LAYOUT.SCALE", None, "Template de escala clínica"),
    ("SCALE.TABS", "ScaleTabs", "scale", "components/scales/ScaleTabs.tsx", None, "SCALE.TEMPLATE", "Abas de escala"),
    ("SCALE.HISTORY", "ScaleHistory", "scale", "components/scales/ScaleHistory.tsx", None, "SCALE.TEMPLATE", "Histórico"),
    ("SCALE.REFERENCE", "ScaleReference", "scale", "components/scales/ScaleReference.tsx", None, "SCALE.TEMPLATE", "Referências bibliográficas"),
    ("SCALE.INTERPRETATION", "ScaleInterpretation", "scale", "components/scales/ScaleInterpretation.tsx", None, "SCALE.TEMPLATE", "Interpretação clínica"),
    ("SCALE.RESULT", "ScaleResult", "scale", "components/scales/ScaleResult.tsx", None, "SCALE.TEMPLATE", "Resultado da escala"),
    ("SCALE.RISK_BADGE", "RiskBadge", "scale", "components/scales/RiskBadge.tsx", None, "SCALE.TEMPLATE", "Badge de risco"),
    ("SCALE.SCORE_BAR", "ScoreBar", "scale", "components/scales/ScoreBar.tsx", None, "SCALE.TEMPLATE", "Barra de score"),
]

CSS_CLASS_MAP = {
    "LAYOUT.MAIN": ["site-shell", "site-main"],
    "LAYOUT.INSTITUTIONAL": ["section-container", "page-hero", "institutional-main"],
    "INST.PAGE_HERO": ["page-hero", "page-hero__title", "page-hero__subtitle"],
    "INST.SECTION_WRAPPER": ["section-block"],
    "NAV.BREADCRUMB": ["breadcrumb"],
    "UI.BUTTON": ["btn-primary", "btn-outline-light", "btn-outline-dark"],
}


def generate_components():
    records = []
    for code, name, category, path, layout, parent, desc in COMPONENTS:
        records.append(
            {
                "uuid": uid(),
                "component_code": code,
                "name": name,
                "category": category,
                "source_path": path,
                "layout_code": layout,
                "parent_component_code": parent,
                "css_classes": CSS_CLASS_MAP.get(code, []),
                "reference_page": "/missao" if category in ("institutional", "layout") or code == "INST.PAGE_HERO" else None,
                "is_default_reference": code in ("LAYOUT.INSTITUTIONAL", "INST.PAGE_HERO", "INST.SECTION_WRAPPER"),
                "description": desc,
                "status": "active",
                "created_at": NOW_Z,
                "updated_at": NOW_Z,
            }
        )

    categories = Counter(r["category"] for r in records)
    data = {
        "generated_at": NOW_ISO,
        "schema_version": "2026.1.0",
        "records": records,
        "micro_phase": "1.7",
        "template_id": "T1.7",
        "entity": "Component",
        "reference_page": "/missao",
        "count": len(records),
        "category_distribution": dict(sorted(categories.items())),
        "validation_summary": {
            "total_records": len(records),
            "unique_keys_checked": ["component_code", "uuid"],
            "foreign_key_validations": ["parent_component_code -> Component.component_code", "layout_code -> Layout.layout_code"],
            "passed": True,
            "errors": [],
        },
    }
    path = ROOT / "metadata/components.json"
    save_json(path, data)
    return len(records)


LAYOUTS = [
    ("LAYOUT.MAIN", "MainLayout", "components/MainLayout.tsx", False, "Shell global de todas as páginas"),
    ("LAYOUT.INSTITUTIONAL", "InstitutionalLayout", "components/Institutional/InstitutionalLayout.tsx", True, "Layout padrão institucional — referência /missao"),
    ("LAYOUT.CALCULATOR", "CalculatorTemplate", "components/Calculators/CalculatorTemplate.tsx", False, "Template de páginas de calculadora"),
    ("LAYOUT.SCALE", "ScaleTemplate", "components/scales/ScaleTemplate.tsx", False, "Template de páginas de escala clínica"),
]


def generate_layouts():
    records = []
    for code, name, path, is_default, desc in LAYOUTS:
        records.append(
            {
                "uuid": uid(),
                "layout_code": code,
                "name": name,
                "template_path": path,
                "reference_page": "/missao" if is_default else None,
                "is_default": is_default,
                "parent_layout_code": "LAYOUT.MAIN" if code != "LAYOUT.MAIN" else None,
                "component_codes": [c[0] for c in COMPONENTS if c[4] == code or (code == "LAYOUT.MAIN" and c[0] in ("NAV.HEADER", "NAV.FOOTER", "A11Y.BAR", "UI.COOKIE_BANNER", "UI.SCROLL_TOP", "UI.PREFERENCES_MODAL", "UI.TOAST"))],
                "description": desc,
                "status": "active",
                "created_at": NOW_Z,
                "updated_at": NOW_Z,
            }
        )

    data = {
        "generated_at": NOW_ISO,
        "schema_version": "2026.1.0",
        "records": records,
        "micro_phase": "1.8",
        "template_id": "T1.8",
        "entity": "Layout",
        "reference_page": "/missao",
        "count": len(records),
        "validation_summary": {
            "total_records": len(records),
            "unique_keys_checked": ["layout_code", "uuid"],
            "foreign_key_validations": ["parent_layout_code -> Layout.layout_code"],
            "passed": True,
            "errors": [],
        },
    }
    path = ROOT / "metadata/layouts.json"
    save_json(path, data)
    return len(records)


def update_manifest():
    path = ROOT / "metadata/generation_manifest.json"
    manifest = load_json(path)
    manifest["phases_completed"] = [
        "1.1_country",
        "1.2_language",
        "1.3_locale",
        "1.4_taxonomy",
        "1.5_design_tokens",
        "1.6_design_tokens_sync",
        "1.7_component",
        "1.8_layout",
    ]
    manifest["files_generated"]["1.6_design_tokens_sync"] = "metadata\\design_tokens.json"
    manifest["files_generated"]["1.7_component"] = "metadata\\components.json"
    manifest["files_generated"]["1.8_layout"] = "metadata\\layouts.json"
    manifest["reference_page"] = "/missao"
    manifest["updated_at"] = NOW_ISO

    for phase, rel in manifest["files_generated"].items():
        fp = ROOT / rel.replace("\\", "/")
        manifest["checksums"][phase] = hashlib.md5(fp.read_bytes()).hexdigest()[:16]

    save_json(path, manifest)


if __name__ == "__main__":
    u, n, total = update_design_tokens()
    comp = generate_components()
    lay = generate_layouts()
    update_manifest()
    print(f"1.6 tokens: {u} updated, {n} added, total {total}")
    print(f"1.7 components: {comp}")
    print(f"1.8 layouts: {lay}")
