#!/usr/bin/env python3
"""Substitui #printTemplate inline por #printTemplateMount + partial relatorio-fiel."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "NIFS" / "DELIVERY" / "preview_apgar.html",
    ROOT / "NIFS" / "DELIVERY" / "apgar.html",
    ROOT / "NIFS" / "DELIVERY" / "html" / "apgar.html",
    ROOT / "preview_apgar.html",
]

MOUNT = '<div id="printTemplateMount"></div>'
MARKER = 'id="printTemplate"'


def replace_print_block(text: str) -> str | None:
    start = text.find(f'<div class="print-area')
    if start == -1:
        start = text.find(f'<div class="print"')
    if start == -1 or MARKER not in text[start : start + 200]:
        idx = text.find(MARKER)
        if idx == -1:
            return None
        start = text.rfind("<div", 0, idx)
    depth = 0
    i = start
    while i < len(text):
        if text.startswith("<div", i):
            depth += 1
            i += 4
            continue
        if text.startswith("</div>", i):
            depth -= 1
            i += 6
            if depth == 0:
                end = i
                return text[:start] + MOUNT + "\n\n" + text[end:].lstrip()
            continue
        i += 1
    return None


def patch(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "printTemplateMount" in text and MARKER not in text:
        return False
    if MARKER not in text:
        return False
    new_text = replace_print_block(text)
    if not new_text:
        raise SystemExit(f"Não foi possível substituir printTemplate em {path}")
    path.write_text(new_text, encoding="utf-8")
    print("Atualizado:", path)
    return True


def main() -> None:
    count = sum(1 for p in FILES if p.is_file() and patch(p))
    print(f"{count} arquivo(s) atualizado(s)")


if __name__ == "__main__":
    main()
