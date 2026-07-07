#!/usr/bin/env python3
"""Finaliza páginas de calculadoras: limpa seções extras, remove Gestor mock, CSS crítico."""
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

DISCLAIMER_RE = re.compile(r'\s*<div class="disclaimer-card">.*?</div>\s*', re.DOTALL)
CIP_RE = re.compile(r'\s*<section class="cip-section">.*?</section>\s*', re.DOTALL)
COG_RE = re.compile(r'\s*<section class="cog-section-wrapper">.*?</section>\s*', re.DOTALL)
KG_RE = re.compile(r'\s*<section class="cip-kg-links">.*?</section>\s*', re.DOTALL)

GESTOR_TAB_RE = re.compile(
    r'\s*<button class="tab"[^>]*\bdata-tab="gestor"[^>]*>.*?</button>\s*',
    re.DOTALL | re.IGNORECASE,
)

TOOL_TAGS_RE = re.compile(
    r'\s*<div class="tool-tags">.*?</div>\s*',
    re.DOTALL,
)
RELATED_BLOCK_RE = re.compile(
    r'\s*<div class="related-tools">.*?</div>\s*</div>\s*',
    re.DOTALL,
)

PRINT_REPORT_RE = re.compile(
    r'\s*<div class="print-report[^"]*">.*?</div>\s*</div>\s*',
    re.DOTALL,
)

GESTOR_ORPHAN_RE = re.compile(
    r'\s*(?:<div class="gestor-notice">.*?</div>\s*)?'
    r'<div class="kpi-grid">.*?'
    r'<section class="calc-card">\s*'
    r'<div class="calc-card-header">.*?Trilha de auditoria.*?</section>\s*'
    r'</div>\s*',
    re.DOTALL | re.IGNORECASE,
)


def _remove_balanced_div(content: str, start: int) -> tuple[str, bool]:
    """Remove <div ...>...</div> começando em start (índice do '<')."""
    if start < 0 or not content.startswith("<div", start):
        return content, False
    depth = 0
    i = start
    n = len(content)
    while i < n:
        if content.startswith("<div", i):
            depth += 1
            i += 4
            continue
        if content.startswith("</div>", i):
            depth -= 1
            i += 6
            if depth == 0:
                return content[:start] + content[i:], True
            continue
        i += 1
    return content, False


def _remove_gestor_panel(content: str) -> tuple[str, bool]:
    marker = 'data-tab-panel="gestor"'
    idx = content.find(marker)
    if idx == -1:
        return content, False
    start = content.rfind("<div", 0, idx)
    if start == -1:
        return content, False
    return _remove_balanced_div(content, start)


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

    for pattern, name in [
        (DISCLAIMER_RE, "disclaimer"),
        (CIP_RE, "cip"),
        (COG_RE, "cog"),
        (KG_RE, "kg"),
        (GESTOR_TAB_RE, "gestor_tab"),
        (TOOL_TAGS_RE, "tool_tags"),
        (RELATED_BLOCK_RE, "related_tools"),
        (PRINT_REPORT_RE, "print_report"),
        (GESTOR_ORPHAN_RE, "gestor_orphan"),
    ]:
        if pattern.search(content):
            content = pattern.sub("\n", content)
            if name not in changes:
                changes.append(name)

    cleaned, removed = _remove_gestor_panel(content)
    if removed:
        content = cleaned
        if "gestor_panel" not in changes:
            changes.append("gestor_panel")
    # Segunda passagem para HTML já parcialmente corrompido
    cleaned, removed = _remove_gestor_panel(content)
    if removed:
        content = cleaned
    if GESTOR_ORPHAN_RE.search(content):
        content = GESTOR_ORPHAN_RE.sub("\n", content)
        if "gestor_orphan" not in changes:
            changes.append("gestor_orphan")

    if "disclaimer" in changes and 'about-grid--single' not in content:
        content = content.replace('class="about-grid"', 'class="about-grid about-grid--single"', 1)

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
