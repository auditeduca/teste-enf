"""Modular chrome — partials HTML (fonte única) + bundle JS compartilhado (páginas leves)."""

from __future__ import annotations

import json
import re
from pathlib import Path

from chrome_lib import render_accessibility_bar, render_shell_extras
from website_lib import render_footer, render_header

ROOT = Path(__file__).resolve().parents[1]
PARTIALS_DIR = ROOT / "website" / "assets" / "partials"
TEMPLATES_JS = ROOT / "website" / "assets" / "js" / "chrome-templates.js"

# Substituído em runtime por chrome-loader.js conforme data-ce-prefix da página.
PREFIX_TOKEN = "__CE_PREFIX__"

PARTIAL_NAMES = ("header", "accessibility-bar", "footer")


def tokenize_paths(html: str) -> str:
    """Turn depth-0 relative URLs into prefix tokens for any page depth."""

    def href_repl(match: re.Match) -> str:
        url = match.group(1)
        if url.startswith(("http://", "https://", "//", "#", "mailto:", "tel:", "javascript:")):
            return match.group(0)
        return f'href="{PREFIX_TOKEN}{url}"'

    html = re.sub(r'href="([^"]+)"', href_repl, html)
    html = re.sub(r'src="(assets/[^"]+)"', rf'src="{PREFIX_TOKEN}\1"', html)
    html = html.replace(
        '"assets/data/locale-options.json"',
        f'"{PREFIX_TOKEN}assets/data/locale-options.json"',
    )

    def action_repl(match: re.Match) -> str:
        url = match.group(1)
        if url.startswith(("http://", "https://", "#")):
            return match.group(0)
        return f'action="{PREFIX_TOKEN}{url}"'

    html = re.sub(r'action="([^"]+)"', action_repl, html)
    return html


def _build_partial_html() -> dict[str, str]:
    depth = 0
    return {
        "accessibility-bar": f'<div class="site-top-spacer">\n{render_accessibility_bar()}\n</div>',
        "header": render_header(depth),
        "footer": render_footer(depth) + render_shell_extras(depth),
    }


def export_chrome_partials() -> dict[str, Path]:
    """Write HTML partials (editáveis) e o bundle JS compartilhado."""
    partials = _build_partial_html()

    PARTIALS_DIR.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    tokenized: dict[str, str] = {}

    for name, html in partials.items():
        body = tokenize_paths(html.strip())
        tokenized[name] = body
        path = PARTIALS_DIR / f"{name}.html"
        path.write_text(body + "\n", encoding="utf-8", newline="\n")
        written[name] = path

    export_chrome_templates_js(tokenized)
    written["chrome-templates.js"] = TEMPLATES_JS
    return written


def export_chrome_templates_js(tokenized: dict[str, str] | None = None) -> Path:
    """Bundle partials into one cached JS file (loaded once across all pages)."""
    if tokenized is None:
        tokenized = {
            name: (PARTIALS_DIR / f"{name}.html").read_text(encoding="utf-8").strip()
            for name in PARTIAL_NAMES
            if (PARTIALS_DIR / f"{name}.html").is_file()
        }
        if len(tokenized) < len(PARTIAL_NAMES):
            return export_chrome_partials()["chrome-templates.js"]

    TEMPLATES_JS.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(tokenized, ensure_ascii=False)
    TEMPLATES_JS.write_text(
        "/** Auto-generated from assets/partials/ — do not edit by hand. */\n"
        f"window.CE_CHROME_PARTIALS = {payload};\n",
        encoding="utf-8",
        newline="\n",
    )
    return TEMPLATES_JS


def render_chrome_mounts(depth: int = 0) -> str:
    """Leves placeholders — conteúdo injetado por chrome-loader.js."""
    from website_lib import rel_prefix

    prefix = rel_prefix(depth)
    return f"""
<div id="ce-chrome-mount-header" class="ce-chrome-mount" data-ce-partial="header" aria-busy="true"></div>
<div id="ce-chrome-mount-a11y" class="ce-chrome-mount" data-ce-partial="accessibility-bar" aria-busy="true"></div>
<noscript>
  <p class="ce-chrome-noscript"><a href="{prefix}index.html">Calculadoras de Enfermagem</a> — ative JavaScript para navegação completa.</p>
</noscript>"""


def render_chrome_footer_mount(depth: int = 0) -> str:
    return """
<div id="ce-chrome-mount-footer" class="ce-chrome-mount" data-ce-partial="footer" aria-busy="true"></div>"""


if __name__ == "__main__":
    paths = export_chrome_partials()
    for name, path in paths.items():
        print(f"wrote {path.relative_to(ROOT)}")
