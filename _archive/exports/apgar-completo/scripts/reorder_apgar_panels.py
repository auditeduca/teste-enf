#!/usr/bin/env python3
"""Reordena painéis de perfil: Padrão → Urgência → Gestor → Estudante → Acadêmico."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "preview_apgar.html",
    ROOT / "NIFS" / "DELIVERY" / "preview_apgar.html",
    ROOT / "NIFS" / "DELIVERY" / "apgar.html",
    ROOT / "NIFS" / "DELIVERY" / "html" / "apgar.html",
]

ORDER = ["padrao", "urgencia", "gestor", "estudante", "academico"]
PANEL_OPEN = re.compile(
    r'<div class="tab-panel(?:\s+active)?"\s+data-tab-panel="(\w+)"[^>]*>',
    re.DOTALL,
)


def reorder(content: str) -> str:
    marker = '<div data-tab-panels="perfil">'
    end_marker = "\n    </div>\n\n    <section class=\"about-section\">"
    start = content.find(marker)
    if start == -1:
        return content
    inner_start = start + len(marker)
    end = content.find(end_marker, inner_start)
    if end == -1:
        return content

    inner = content[inner_start:end]
    matches = list(PANEL_OPEN.finditer(inner))
    if len(matches) < 2:
        return content

    panels: dict[str, str] = {}
    for i, m in enumerate(matches):
        pid = m.group(1)
        pstart = m.start()
        pend = matches[i + 1].start() if i + 1 < len(matches) else len(inner)
        panels[pid] = inner[pstart:pend].strip()

    chunks: list[str] = []
    for idx, pid in enumerate(ORDER):
        block = panels.get(pid, "")
        if not block:
            continue
        if idx == 0:
            block = re.sub(
                r'class="tab-panel(?:\s+active)?"',
                'class="tab-panel active"',
                block,
                count=1,
            )
        else:
            block = re.sub(
                r'class="tab-panel(?:\s+active)?"',
                'class="tab-panel"',
                block,
                count=1,
            )
        chunks.append(block)

    new_inner = "\n\n" + "\n\n".join(chunks) + "\n"
    return content[:inner_start] + new_inner + content[end:]


def main() -> None:
    for path in TARGETS:
        if not path.is_file():
            continue
        updated = reorder(path.read_text(encoding="utf-8"))
        path.write_text(updated, encoding="utf-8")
        print("Reordenado:", path)


if __name__ == "__main__":
    main()
