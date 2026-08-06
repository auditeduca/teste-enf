# -*- coding: utf-8 -*-
"""Valida data-cko-template + assets do contrato cko-page-templates.json."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "data" / "cko-page-templates.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="HTML relativo à raiz")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    templates = cfg.get("templates", {})
    shared = cfg.get("shared", {})

    if args.file:
        paths = [ROOT / args.file]
    else:
        paths = []
        for p in sorted(ROOT.glob("*.html")):
            t = p.read_text(encoding="utf-8", errors="ignore")
            if "data-cko-template=" in t or "cko-page-templates.js" in t:
                paths.append(p)

    errors = 0
    warns = 0
    print(f"CKO Page Templates Validator — {len(paths)} arquivo(s)")
    for path in paths:
        if not path.is_file():
            print(f"MISSING {path}")
            errors += 1
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = path.relative_to(ROOT).as_posix()
        m = re.search(r'data-cko-template="([^"]+)"', text)
        tpl = m.group(1) if m else None
        if not tpl:
            print(f"{rel}  [error] sem data-cko-template")
            errors += 1
            continue
        if tpl not in templates:
            print(f"{rel}  [error] template desconhecido: {tpl}")
            errors += 1
            continue
        defn = templates[tpl]
        file_errs = []
        file_warns = []
        for css in shared.get("requiredAssets", {}).get("css", []):
            if css.endswith("cko-page-shell.css") and not defn.get("shell"):
                continue
            if css not in text:
                file_warns.append(f"falta {css}")
        for js in shared.get("requiredAssets", {}).get("js", []):
            if js.endswith("cko-page-shell.js") and not defn.get("shell"):
                continue
            if js not in text:
                file_warns.append(f"falta {js}")
        if 'id="main-content"' not in text and "<main" not in text.lower():
            file_errs.append("main ausente")
        if defn.get("shell"):
            for slot in defn.get("slots", ["chrome", "hero", "sidebar"]):
                if f'data-cko-slot="{slot}"' not in text:
                    file_errs.append(f"slot {slot} ausente")
            if "cko-layout" not in text:
                file_errs.append("cko-layout ausente")
        if tpl == "calculator" and "cko-calc" not in text and "data-cko-calc" not in text:
            file_warns.append("sem marcadores cko-calc-* (recomendado)")
        errors += len(file_errs)
        warns += len(file_warns)
        if file_errs or file_warns:
            print(f"{rel}  template={tpl} errors={len(file_errs)} warns={len(file_warns)}")
            for e in file_errs:
                print(f"  [error] {e}")
            for w in file_warns:
                print(f"  [warn] {w}")
        else:
            print(f"{rel}  template={tpl} OK")

    print("---")
    print(f"totals errors={errors} warns={warns}")
    if errors:
        return 1
    if args.strict and warns:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
