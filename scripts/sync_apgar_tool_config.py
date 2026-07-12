#!/usr/bin/env python3
"""Injeta tool-config em apgar.html a partir do JSON canônico."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APGAR_JSON = ROOT / "reference-website" / "data" / "tools" / "apgar.json"
TARGETS = [
    ROOT / "NIFS" / "DELIVERY" / "html" / "apgar.html",
    ROOT / "NIFS" / "DELIVERY" / "apgar.html",
]

TOOL_CONFIG_TAG = '<script type="application/json" id="tool-config">'
RX = re.compile(r'<script type="application/json" id="tool-config">.*?</script>\s*', re.DOTALL)


def main() -> int:
    data = json.loads(APGAR_JSON.read_text(encoding="utf-8"))
    block = TOOL_CONFIG_TAG + json.dumps(data, ensure_ascii=False, separators=(",", ": ")) + "</script>\n\n"
    for path in TARGETS:
        if not path.is_file():
            continue
        html = path.read_text(encoding="utf-8")
        if RX.search(html):
            html = RX.sub(block, html, count=1)
        elif "</main>" in html:
            html = html.replace("</main>", block + "</main>", 1)
        else:
            html += "\n" + block
        path.write_text(html, encoding="utf-8")
        print("tool-config →", path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
