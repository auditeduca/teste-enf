"""Agente de validação — calculadoras/escalas em NIFS/DELIVERY/html."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
DELIVERY_HTML = WORKSPACE / "NIFS" / "DELIVERY" / "html"
TOOLS_JSON = WORKSPACE / "reference-website" / "data" / "tools"
SCHEMA_PATH = WORKSPACE / "reference-website" / "data" / "schemas" / "tool.schema.json"

EXCLUDED_SLUGS = frozenset({
    "calculadora-template",
    "calculadora-template-v2",
    "calculadora-preview",
})

REQUIRED_TOP = ["id", "slug", "seo", "overview", "calculator"]
TOOL_CONFIG_RX = re.compile(
    r'<script type="application/json" id="tool-config">(.*?)</script>',
    re.DOTALL,
)
UNWANTED_SECTIONS = [
    "disclaimer-card",
    "cip-section",
    "cog-section-wrapper",
    "cip-kg-links",
]


@dataclass
class PageIssue:
    slug: str
    severity: str  # error | warning | info
    code: str
    message: str


@dataclass
class ValidationReport:
    root: str
    pages_checked: int = 0
    pages_ok: int = 0
    issues: list[PageIssue] = field(default_factory=list)

    def add(self, slug: str, severity: str, code: str, message: str) -> None:
        self.issues.append(PageIssue(slug, severity, code, message))

    def to_dict(self) -> dict:
        errors = [i for i in self.issues if i.severity == "error"]
        warnings = [i for i in self.issues if i.severity == "warning"]
        return {
            "root": self.root,
            "pages_checked": self.pages_checked,
            "pages_ok": self.pages_ok,
            "errors": len(errors),
            "warnings": len(warnings),
            "issues": [
                {"slug": i.slug, "severity": i.severity, "code": i.code, "message": i.message}
                for i in self.issues
            ],
        }


def _load_json_tools() -> dict[str, dict]:
    tools: dict[str, dict] = {}
    if not TOOLS_JSON.is_dir():
        return tools
    for jf in TOOLS_JSON.glob("*.json"):
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
            slug = data.get("slug", jf.stem)
            tools[slug] = data
        except Exception:
            pass
    return tools


def validate_page(html_path: Path, source_tools: dict[str, dict], report: ValidationReport) -> None:
    slug = html_path.stem
    report.pages_checked += 1
    content = html_path.read_text(encoding="utf-8", errors="replace")
    page_ok = True

    if 'id="tool-config"' not in content:
        report.add(slug, "error", "missing_tool_config", "Sem bloco #tool-config")
        page_ok = False
    else:
        m = TOOL_CONFIG_RX.search(content)
        if not m:
            report.add(slug, "error", "malformed_tool_config", "tool-config malformado")
            page_ok = False
        else:
            try:
                cfg = json.loads(m.group(1))
            except json.JSONDecodeError as e:
                report.add(slug, "error", "invalid_tool_config_json", f"JSON inválido: {e}")
                page_ok = False
                cfg = None

            if cfg:
                missing = [k for k in REQUIRED_TOP if k not in cfg]
                if missing:
                    report.add(
                        slug,
                        "error",
                        "incomplete_tool_config",
                        f"Campos obrigatórios ausentes: {', '.join(missing)}",
                    )
                    page_ok = False

                formula = (cfg.get("calculator") or {}).get("formula") or {}
                ftype = formula.get("type")
                if ftype not in ("sum", "expression", "avg", "max", "formula"):
                    report.add(slug, "warning", "unknown_formula_type", f"Tipo de fórmula: {ftype}")

                if slug in source_tools:
                    source = source_tools[slug]
                    if cfg != source:
                        report.add(
                            slug,
                            "warning",
                            "embed_out_of_sync",
                            "tool-config embutido difere do JSON em data/tools/",
                        )

    if "partials-loader.js" not in content:
        report.add(slug, "error", "missing_partials_loader", "Sem js/partials-loader.js")
        page_ok = False

    if "calc-engine-v2.js" in content and 'src="js/calc-engine-v2.js"' in content:
        report.add(
            slug,
            "warning",
            "duplicate_calc_engine",
            "calc-engine-v2.js duplicado no HTML (deve vir via partials-loader)",
        )

    for section in UNWANTED_SECTIONS:
        if f'class="{section}"' in content or f"class='{section}'" in content:
            report.add(slug, "warning", "unwanted_section", f"Seção indesejada presente: {section}")

    required_ids = ["calcResultValue", "calcForm"]
    for el_id in required_ids:
        if f'id="{el_id}"' not in content:
            report.add(slug, "warning", "missing_element", f"Elemento #{el_id} ausente")

    if page_ok:
        report.pages_ok += 1


def run_validation(
    *,
    root: Path | None = None,
    slugs: list[str] | None = None,
) -> ValidationReport:
    root = root or DELIVERY_HTML
    report = ValidationReport(root=str(root))
    source_tools = _load_json_tools()

    if slugs:
        paths = [root / f"{s}.html" for s in slugs if s not in EXCLUDED_SLUGS]
    else:
        paths = sorted(
            p for p in root.glob("*.html")
            if p.stem not in EXCLUDED_SLUGS
            and 'id="tool-config"' in p.read_text(encoding="utf-8", errors="replace")
        )

    for html_path in paths:
        if not html_path.is_file():
            report.add(html_path.stem, "error", "file_not_found", str(html_path))
            continue
        validate_page(html_path, source_tools, report)

    return report
