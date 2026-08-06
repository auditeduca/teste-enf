#!/usr/bin/env python3
"""Smoke checks for CKO-CART-001 delivery."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    checks: list[tuple[str, bool]] = []
    html = (ROOT / "biblioteca-carinho-de-emergencia.html").read_text(encoding="utf-8")
    js = (ROOT / "js" / "cart-renderer.js").read_text(encoding="utf-8")
    css = (ROOT / "css" / "pages" / "cart-emergencia.css").read_text(encoding="utf-8")
    man = json.loads((ROOT / "data" / "cko-cart-001.manifest.json").read_text(encoding="utf-8"))

    checks.append(("page has cart root", "cko-cart-root" in html))
    checks.append(("page loads renderer", "/js/cart-renderer.js" in html))
    checks.append(("page loads css", "cart-emergencia.css" in html))
    checks.append(("global shell kept", "global-header-container" in html and "footer-placeholder" in html))
    checks.append(("webp asset exists", (ROOT / "img" / "carrinho-emergencia-interativo.webp").exists()))
    checks.append(("7 zones", len(man["cartZones"]) == 7))
    checks.append(("simulate button", "Simular plantão com vencidos" in js))
    checks.append(("export pdf", "exportPdf" in js))
    checks.append(("export excel", "exportExcel" in js))
    checks.append(("export word", "exportWord" in js))
    checks.append(("deep link zona", 'searchParams.get("zona")' in js))
    checks.append(("navy tokens", "#1A3E74" in css and "#1E4D8C" in css and "#163269" in css))
    checks.append(("fonts product", "Inter" in html and "Nunito Sans" in html))
    checks.append(("tips present", len(man["tipsAndErrors"]) >= 8))
    checks.append(("related content", len(man["relatedContent"]) >= 5))
    checks.append(("homolog seals", len(man["homologInstitutions"]["publicSeals"]) >= 5))
    checks.append(("live region a11y", 'aria-live="polite"' in html))
    checks.append(("skip link", 'href="#main-content"' in html))

    art = man.get("educationalArticle") or {}
    checks.append(("educational article", bool(art.get("sections")) and len(art["sections"]) >= 4))
    checks.append(("article mount", "cko-cart-article" in html))
    checks.append(("article page exists", (ROOT / "biblioteca" / "artigo-carrinho-de-emergencia-enfermagem.html").exists()))
    notice = "Cia de Enfermagem Global Platform"
    checks.append(("copyright in manifest", notice in (man.get("contentCopyright") or {}).get("notice", "")))
    checks.append(("copyright in renderer", "cko-copyright" in js))
    tip_bodies = " ".join(t.get("body", "") for t in man["tipsAndErrors"])
    checks.append(("tips are internal copy", "Conteúdo educativo interno" in tip_bodies or "orientação interna" in tip_bodies.lower() or "Texto próprio" in tip_bodies or "Orientação interna" in tip_bodies))
    checks.append(("docs index", (ROOT / "docs-internos" / "CKO-CART-001-LEIA-ME.md").exists()))
    checks.append(("page shell js", "/js/cko-page-shell.js" in html))
    checks.append(("page shell css", "cko-page-shell.css" in html))
    checks.append(("page shell mount", 'data-cko-page="carinho"' in html))
    shell = json.loads((ROOT / "data" / "cko-shell-pages.json").read_text(encoding="utf-8"))
    checks.append(("shell catalog pages", len(shell.get("pages", {})) >= 5))
    checks.append(("shell nav materiais", len(shell.get("navSets", {}).get("materiais", [])) >= 5))
    if shutil.which("node"):
        r_shell = subprocess.run(
            ["node", "--check", str(ROOT / "js" / "cko-page-shell.js")],
            capture_output=True,
            text=True,
        )
        checks.append(("shell js syntax", r_shell.returncode == 0))

    for z in man["cartZones"]:
        h = z["hotspot"]
        ok = 0 <= h["xPercent"] <= 100 and 0 <= h["yPercent"] <= 100
        checks.append((f"hotspot {z['id']}", ok))

    for asset in man["assets"]["local"]:
        digest = asset.get("sha256", "")
        checks.append((f"hash set {asset['id']}", len(digest) == 64 and "PLACEHOLDER" not in digest))

    if shutil.which("node"):
        r = subprocess.run(
            ["node", "--check", str(ROOT / "js" / "cart-renderer.js")],
            capture_output=True,
            text=True,
        )
        checks.append(("js syntax", r.returncode == 0))
        if r.returncode != 0:
            print(r.stderr)

    # conference rule simulation (pure python)
    alert = man["conferenceRules"]["expiryAlertDays"]
    warn = man["conferenceRules"]["expiryWarningDays"]
    checks.append(("expiry thresholds", alert == 30 and warn == 90))
    checks.append(("seal required", man["conferenceRules"]["sealRequired"] is True))

    fail = [c for c in checks if not c[1]]
    for name, ok in checks:
        print(("OK" if ok else "FAIL"), name)
    print("TOTAL", len(checks), "FAIL", len(fail))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
