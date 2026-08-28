#!/usr/bin/env python3
"""Simplifica preview_v2.html: CSS externo + header/footer/a11y via partials-loader.js."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "preview_v2.html"
DELIVERY = ROOT / "NIFS" / "DELIVERY"
OUT_DELIVERY = DELIVERY / "preview_v2.html"
OUT_ROOT = ROOT / "preview_v2.html"

HEAD_ASSETS = """<style id="calc-critical-css">[data-tab-panels]>[data-tab-panel]:not(.active){display:none!important}</style>
<link rel="stylesheet" href="css/site-styles.css">
"""

COMMENT_FIX_OLD = (
    "     6. As classes .calc-*/.est-*/.urg-*/.aca-*/.kpi-*/.audit-* deste arquivo\n"
    "        são específicas de páginas de calculadora/escala e ficam no <style>\n"
    "        local (não em css/main.css nem css/site-styles.css), para não afetar\n"
    "        o resto do site."
)
COMMENT_FIX_NEW = (
    "     6. Estilos de calculadora/escala (.calc-*, .est-*, .urg-*, etc.) estão em\n"
    "        css/site-styles.css — não duplique CSS inline neste arquivo."
)

TAIL_SCRIPTS_RE = re.compile(
    r"\s*<script src=\"js/i18n-loader\.js\"></script>\s*"
    r"<script src=\"js/nurse-palm\.js\"></script>\s*"
    r"<script src=\"js/cognitive-ui\.js\"></script>\s*",
    re.MULTILINE,
)

FONT_AWESOME_MARKER = (
    'referrerpolicy="no-referrer" />\n'
)


def remove_head_style_blocks(content: str) -> str:
    """Remove apenas <style> reais do head (após font-awesome), não menções em comentários."""
    start = content.find(FONT_AWESOME_MARKER)
    if start == -1:
        raise ValueError("Marcador font-awesome não encontrado")
    start += len(FONT_AWESOME_MARKER)
    head_end = content.find("</head>", start)
    if head_end == -1:
        raise ValueError("</head> não encontrado")
    head_tail = content[start:head_end]
    head_tail = re.sub(r"<style[^>]*>.*?</style>\s*", "", head_tail, flags=re.DOTALL)
    return content[:start] + HEAD_ASSETS + "\n" + head_tail + content[head_end:]


def slim(content: str) -> str:
    content = content.replace(COMMENT_FIX_OLD, COMMENT_FIX_NEW)

    if 'href="css/site-styles.css"' not in content:
        content = remove_head_style_blocks(content)

    if TAIL_SCRIPTS_RE.search(content):
        content = TAIL_SCRIPTS_RE.sub(
            '\n<script src="js/partials-loader.js"></script>\n',
            content,
        )
    elif "partials-loader.js" not in content:
        content = content.replace(
            "</body>",
            '\n<script src="js/partials-loader.js"></script>\n</body>',
        )

    return content


def main() -> None:
    if not SRC.is_file():
        raise SystemExit(f"Arquivo não encontrado: {SRC}")

    original = SRC.read_text(encoding="utf-8")
    slimmed = slim(original)

    OUT_DELIVERY.parent.mkdir(parents=True, exist_ok=True)
    OUT_DELIVERY.write_text(slimmed, encoding="utf-8")
    OUT_ROOT.write_text(slimmed, encoding="utf-8")

    orig_lines = original.count("\n") + 1
    new_lines = slimmed.count("\n") + 1
    print(f"preview_v2 simplificado: {orig_lines} → {new_lines} linhas")
    print(f"  → {OUT_DELIVERY}")
    print(f"  → {OUT_ROOT}")
    print("Preview: cd NIFS/DELIVERY && python3 -m http.server 8765")
    print("  http://localhost:8765/preview_v2.html")


if __name__ == "__main__":
    main()
