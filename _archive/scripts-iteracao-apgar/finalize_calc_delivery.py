#!/usr/bin/env python3
"""Finaliza páginas de calculadoras: CSS crítico apenas (preserva gestor, print, relacionadas)."""
from __future__ import annotations

import argparse
import glob
import os
import re

HTML_DIR = os.path.join(os.path.dirname(__file__), "..", "NIFS", "DELIVERY", "html")

CRITICAL_CSS = (
    '<style id="calc-critical-css">'
    "[data-tab-panels]>[data-tab-panel]:not(.active){display:none!important}"
    "</style>\n"
)


def _ensure_critical_css(content: str) -> tuple[str, bool]:
    if 'id="calc-critical-css"' in content:
        return content, False
    marker = '<link rel="stylesheet" href="css/site-styles.css">'
    if marker in content:
        return content.replace(marker, CRITICAL_CSS + marker, 1), True
    head_end = content.find("</head>")
    if head_end > 0:
        return content[:head_end] + CRITICAL_CSS + content[head_end:], True
    return content, False


def finalize_file(path: str) -> list[str]:
    with open(path, encoding="utf-8") as f:
        content = f.read()

    if 'id="tool-config"' not in content:
        return []

    original = content
    changes: list[str] = []

    content, css_added = _ensure_critical_css(content)
    if css_added:
        changes.append("critical_css")

    if content != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    return changes


def main() -> None:
    parser = argparse.ArgumentParser(description="Finalizar HTML das calculadoras")
    parser.add_argument("--dir", default=HTML_DIR)
    args = parser.parse_args()
    files = sorted(glob.glob(os.path.join(args.dir, "*.html")))
    total = 0
    for path in files:
        changes = finalize_file(path)
        if changes:
            total += 1
            print(f"{os.path.basename(path)}: {', '.join(changes)}")
    print(f"\nFinalizados {total} arquivos em {args.dir}")


if __name__ == "__main__":
    main()
