#!/usr/bin/env python3
"""Adiciona favicon e sincroniza assets de marca (logos) no DELIVERY."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "reference-website"
DELIVERY = ROOT / "NIFS" / "DELIVERY"
HTML = DELIVERY / "html"

FAVICON_SNIPPET = """<link rel="icon" type="image/png" sizes="32x32" href="{prefix}favicon-32x32.png" />
<link rel="icon" type="image/png" sizes="16x16" href="{prefix}favicon-16x16.png" />
<link rel="shortcut icon" href="{prefix}favicon.ico" />
"""

APGAR_FILES = [
    DELIVERY / "preview_apgar.html",
    DELIVERY / "apgar.html",
    HTML / "apgar.html",
    DELIVERY / "relatorio_fiel.html",
]


def sync_assets() -> None:
    img_dst = DELIVERY / "images"
    img_dst.mkdir(parents=True, exist_ok=True)
    for name in ("logotipo_footer.webp", "logotipo_website.webp"):
        shutil.copy2(REF / "images" / name, img_dst / name)
    for name in ("favicon-16x16.png", "favicon-32x32.png", "favicon.ico"):
        shutil.copy2(REF / name, DELIVERY / name)
        shutil.copy2(REF / name, HTML / name)


def inject_favicon(path: Path, prefix: str = "") -> bool:
    text = path.read_text(encoding="utf-8")
    if "favicon-16x16.png" in text:
        return False
    marker = '<meta name="viewport"'
    idx = text.find(marker)
    if idx == -1:
        return False
    end = text.find(">", idx) + 1
    snippet = "\n" + FAVICON_SNIPPET.format(prefix=prefix)
    path.write_text(text[:end] + snippet + text[end:], encoding="utf-8")
    return True


def main() -> None:
    sync_assets()
    updates = 0
    for p in APGAR_FILES:
        if not p.is_file():
            continue
        prefix = "../" if p.parent.name == "html" else ""
        if inject_favicon(p, prefix):
            print("Favicon:", p)
            updates += 1
    print(f"Assets sincronizados; {updates} HTML(s) atualizado(s)")


if __name__ == "__main__":
    main()
