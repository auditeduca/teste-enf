#!/usr/bin/env python3
"""Valida que todas as calculadoras têm CKO gerado."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_DIR = ROOT / "NIFS" / "DELIVERY" / "html"
DATA_DIR = ROOT / "NIFS" / "DELIVERY" / "js" / "modules" / "data"
INDEX_PATH = ROOT / "NIFS" / "DELIVERY" / "js" / "bundles" / "cko-index.json"
ALIASES = {
    "escala-de-glasgow": "glasgow",
    "escala-de-braden": "braden",
    "escala-de-morse": "morse",
}

EXCLUDED = {"calculadora-template", "calculadora-template-v2", "calculadora-preview"}


def page_slug(html_path: Path) -> str | None:
    text = html_path.read_text(encoding="utf-8")
    m = re.search(r'<body[^>]*data-page="([^"]+)"', text)
    if m:
        return m.group(1)
    if "tool-config" in text:
        return html_path.stem
    return None


def main() -> int:
    missing: list[str] = []
    checked = 0
    for html in sorted(HTML_DIR.glob("*.html")):
        if html.stem in EXCLUDED:
            continue
        if 'id="tool-config"' not in html.read_text(encoding="utf-8"):
            if html.stem != "apgar":
                continue
        slug = page_slug(html) or html.stem
        canonical = ALIASES.get(slug, slug)
        cko = DATA_DIR / f"{canonical}-cko.json"
        checked += 1
        if not cko.is_file():
            missing.append(f"{html.name} → {cko.name}")

    index_count = 0
    if INDEX_PATH.is_file():
        index_count = json.loads(INDEX_PATH.read_text(encoding="utf-8")).get("count", 0)

    print(json.dumps({"checked": checked, "cko_files": len(list(DATA_DIR.glob("*-cko.json"))), "index_count": index_count, "missing": missing}, indent=2, ensure_ascii=False))
    if missing:
        print(f"ERRO: {len(missing)} CKO ausente(s)", file=sys.stderr)
        return 1
    print(f"OK: {checked} calculadoras com CKO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
