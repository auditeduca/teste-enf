#!/usr/bin/env python3
"""Alinha ícones do perfil Estudante ao padrão SVG do site."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "preview_apgar.html",
    ROOT / "NIFS" / "DELIVERY" / "preview_apgar.html",
    ROOT / "NIFS" / "DELIVERY" / "apgar.html",
    ROOT / "NIFS" / "DELIVERY" / "html" / "apgar.html",
]
CKO = ROOT / "NIFS" / "DELIVERY" / "js" / "modules" / "data" / "apgar-cko.json"

EXAMPLES = [
    (
        """<div class="ex-emoji">✅</div>""",
        """<div class="icon-wrap"><svg class="icon"><use href="#i-check"/></svg></div>""",
    ),
    (
        """<div class="ex-emoji">⚠️</div>""",
        """<div class="icon-wrap icon-wrap--warn"><svg class="icon"><use href="#i-warning"/></svg></div>""",
    ),
    (
        """<div class="ex-emoji">🚨</div>""",
        """<div class="icon-wrap icon-wrap--alarm"><svg class="icon"><use href="#i-warning"/></svg></div>""",
    ),
]

QUIZ_BAR_OLD = '<span class="bar" style="background:#7c3aed" aria-hidden="true"></span>'
QUIZ_BAR_NEW = '<span class="bar" aria-hidden="true"></span>'

ICON_MAP = {
    "ballard.html": "i-baby",
    "capurro.html": "i-users",
    "bps.html": "i-pulse",
    "silverman-andersen.html": "i-pulse",
    "downes.html": "i-pulse",
    "bishop.html": "i-gauge",
    "medicamentos.html": "i-pills",
    "biblioteca-provas.html": "i-clipboard",
    "protocolos.html": "i-clipboard",
    "biblioteca.html": "i-book",
}


def patch_cko() -> None:
    data = json.loads(CKO.read_text(encoding="utf-8"))
    pres = data.setdefault("presentation", {})
    for item in pres.get("related_tools", []):
        href = item.get("href", "")
        for key, icon in ICON_MAP.items():
            if key in href:
                item["icon"] = icon
                break
    for item in pres.get("learning", []):
        href = item.get("href", "")
        for key, icon in ICON_MAP.items():
            if key in href:
                item["icon"] = icon
                break
    CKO.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Atualizado:", CKO)


def patch_html(content: str) -> str:
    for old, new in EXAMPLES:
        content = content.replace(old, new)
    content = content.replace(QUIZ_BAR_OLD, QUIZ_BAR_NEW)
    return content


def main() -> None:
    patch_cko()
    for path in TARGETS:
        if not path.is_file():
            continue
        path.write_text(patch_html(path.read_text(encoding="utf-8")), encoding="utf-8")
        print("Corrigido:", path)


if __name__ == "__main__":
    main()
