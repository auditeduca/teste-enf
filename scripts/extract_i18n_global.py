#!/usr/bin/env python3
"""Extrai dicionários en/es de lang-selector.js → DELIVERY/i18n/global/ (Fase 1.4)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANG_SELECTOR = ROOT / "NIFS" / "DELIVERY" / "js" / "lang-selector.js"
OUT_DIR = ROOT / "NIFS" / "DELIVERY" / "i18n" / "global"

NODE_SCRIPT = ROOT / "scripts" / "extract_i18n_global.mjs"


def main() -> int:
    if not LANG_SELECTOR.is_file():
        print(f"Arquivo não encontrado: {LANG_SELECTOR}", file=sys.stderr)
        return 1
    langs = sys.argv[1:] if len(sys.argv) > 1 else ["en", "es"]
    proc = subprocess.run(
        ["node", str(NODE_SCRIPT), str(LANG_SELECTOR), *langs],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print(proc.stderr or proc.stdout, file=sys.stderr)
        return proc.returncode
    data = json.loads(proc.stdout)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for lang, payload in data.items():
        path = OUT_DIR / f"{lang}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"  {path.relative_to(ROOT)} ({len(payload)} chaves)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
