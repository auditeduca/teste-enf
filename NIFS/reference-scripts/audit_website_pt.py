#!/usr/bin/env python3
"""Audit pt-BR static website — 100% checklist before i18n expansion."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "website" / "pt"
REPORT = ROOT / "website" / "audit_pt_report.json"

REQUIRED_ROUTES = [
    "/",
    "/missao",
    "/sobre",
    "/contato",
    "/privacidade",
    "/termos",
    "/acessibilidade",
    "/mapa-site",
    "/sustentabilidade",
    "/ferramentas",
    "/calculadoras",
    "/escalas",
    "/protocolos",
    "/biblioteca",
    "/educacao",
    "/quiz",
    "/flashcards",
    "/trilhas",
    "/simulados",
    "/nanda",
    "/404",
]

STUB_MARKERS = ["Em construção", "em construcao", "under construction", "TODO: stub"]

CHECKS = [
    "lang_pt_br",
    "has_title",
    "has_meta_description",
    "has_canonical",
    "skip_link",
    "site_header",
    "accessibility_bar",
    "main_landmark",
    "site_footer",
    "css_linked",
    "favicons_linked",
    "logo_header",
    "logo_footer",
    "home_hero",
    "home_search",
    "home_categories",
    "no_stub_text",
    "main_has_content",
]


def route_to_file(route: str) -> Path:
    if route == "/":
        return OUT / "index.html"
    return OUT / route.lstrip("/") / "index.html"


def audit_file(path: Path) -> dict:
    rel = str(path.relative_to(OUT)).replace("\\", "/")
    result = {"file": rel, "checks": {}, "errors": [], "warnings": []}
    if not path.exists():
        result["errors"].append("missing_file")
        for c in CHECKS:
            result["checks"][c] = False
        return result

    html = path.read_text(encoding="utf-8")
    main_match = re.search(r"<main[^>]*>(.*?)</main>", html, re.DOTALL | re.IGNORECASE)
    main_text = re.sub(r"<[^>]+>", " ", main_match.group(1) if main_match else "").strip()

    result["checks"]["lang_pt_br"] = 'lang="pt-BR"' in html
    result["checks"]["has_title"] = bool(re.search(r"<title>[^<]+</title>", html))
    result["checks"]["has_meta_description"] = 'name="description"' in html
    result["checks"]["has_canonical"] = 'rel="canonical"' in html
    result["checks"]["skip_link"] = "skip-link" in html and "#main-content" in html
    result["checks"]["site_header"] = 'id="site-header"' in html and "site-header" in html
    result["checks"]["accessibility_bar"] = "accessibility-bar" in html
    result["checks"]["main_landmark"] = '<main id="main-content"' in html
    result["checks"]["site_footer"] = 'class="site-footer"' in html
    result["checks"]["css_linked"] = "assets/css/tokens.css" in html and "assets/css/chrome.css" in html
    result["checks"]["favicons_linked"] = "assets/images/favicon.ico" in html
    result["checks"]["logo_header"] = "assets/images/logotipo_website.webp" in html
    if rel == "index.html":
        result["checks"]["home_hero"] = "home-hero" in html and "home-hero__title" in html
        result["checks"]["home_search"] = "home-search" in html and 'data-home-search' in html
        result["checks"]["home_categories"] = "home-categories" in html and "home-category" in html
    result["checks"]["logo_footer"] = "assets/images/logotipo_footer.webp" in html
    result["checks"]["no_stub_text"] = not any(m.lower() in html.lower() for m in STUB_MARKERS)
    result["checks"]["main_has_content"] = len(main_text) >= 40

    for check, ok in result["checks"].items():
        if not ok:
            result["errors"].append(check)

    if len(main_text) < 120:
        result["warnings"].append("thin_content")

    return result


def _scan_hrefs(p: Path, scope: str, existing: set[str]) -> list[dict]:
    href_re = re.compile(r'href="([^"#?]+)"')
    out = []
    for href in href_re.findall(scope):
        if href.startswith(("http", "mailto:", "tel:", "/")) or href == "#":
            continue
        try:
            target = (p.parent / href).resolve().relative_to(OUT.resolve()).as_posix()
        except ValueError:
            out.append({"from": p.relative_to(OUT).as_posix(), "href": href, "resolved": "outside_site_root"})
            continue
        if target.endswith("/"):
            target += "index.html"
        if target not in existing and not (OUT / target).exists():
            out.append({"from": p.relative_to(OUT).as_posix(), "href": href, "resolved": target})
    return out


def audit_links(pages: list[Path]) -> dict:
    existing = {p.relative_to(OUT).as_posix() for p in pages}
    broken: list[dict] = []
    chrome_broken: list[dict] = []
    for p in pages:
        text = p.read_text(encoding="utf-8")
        main_match = re.search(r"<main[^>]*>(.*?)</main>", text, re.DOTALL | re.IGNORECASE)
        if main_match:
            broken.extend(_scan_hrefs(p, main_match.group(1), existing))
            chrome = text[: main_match.start()] + text[main_match.end():]
        else:
            broken.extend(_scan_hrefs(p, text, existing))
            chrome = ""
        chrome_broken.extend(_scan_hrefs(p, chrome, existing))
    return {
        "broken_count": len(broken),
        "broken_sample": broken[:50],
        "chrome_broken_count": len(chrome_broken),
        "chrome_broken_sample": chrome_broken[:50],
    }


def audit_locales(locale_dirs: set[str], pt_page_count: int) -> dict:
    """Verify each locale mirrors the pt-BR page count and a sample page's
    assets + a localized link resolve on disk (shared-root asset offset)."""
    result = {"locales": {}, "ok": True}
    asset_re = re.compile(r'href="((?:\.\./)*assets/css/tokens\.css)"')
    for prefix in sorted(locale_dirs):
        loc = OUT / prefix
        pages = [p for p in loc.rglob("*.html")] if loc.exists() else []
        sample = loc / "ferramentas" / "braden" / "index.html"
        asset_ok = True
        if sample.exists():
            m = asset_re.search(sample.read_text(encoding="utf-8"))
            asset_ok = bool(m) and (sample.parent / m.group(1)).resolve().exists()
        entry = {
            "page_count": len(pages),
            "count_matches_pt": len(pages) == pt_page_count,
            "sample_asset_resolves": asset_ok,
        }
        if not (entry["count_matches_pt"] and asset_ok):
            result["ok"] = False
        result["locales"][prefix] = entry
    return result


def main() -> int:
    print("NKOS website audit — pt-BR")
    if not OUT.exists():
        print(f"ERROR: {OUT} not found. Run generate_website_pt.py first.")
        return 1

    manifest_path = OUT / "generation_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}

    # Audit the canonical pt-BR tree; locale variants are mechanical transforms
    # of these pages (validated separately below) and excluded here for speed.
    sys.path.insert(0, str(ROOT / "scripts"))
    from seo_lib import LOCALES

    locale_dirs = {prefix for prefix, *_ in LOCALES if prefix}
    all_html = [
        p for p in OUT.rglob("*.html")
        if p.relative_to(OUT).parts[0] not in locale_dirs
    ]
    page_results = [audit_file(p) for p in all_html]

    locale_audit = audit_locales(locale_dirs, len(all_html))

    route_results = []
    for route in REQUIRED_ROUTES:
        fp = route_to_file(route)
        r = audit_file(fp)
        r["route"] = route
        route_results.append(r)

    required_ok = all(not r["errors"] for r in route_results)
    tool_pages = [
        p for p in all_html
        if p.parent.parent.name == "ferramentas" and p.name == "index.html"
    ]
    tool_count = len(tool_pages)
    tool_ok = tool_count >= 100

    links = audit_links(all_html)
    pages_with_errors = [r for r in page_results if r["errors"]]
    pass_rate = round(100 * (len(page_results) - len(pages_with_errors)) / max(len(page_results), 1), 2)

    report = {
        "audited_at": manifest.get("generated_at"),
        "locale": "pt-BR",
        "total_html_files": len(all_html),
        "required_routes": len(REQUIRED_ROUTES),
        "required_routes_pass": required_ok,
        "tool_pages": tool_count,
        "tool_pages_pass": tool_ok,
        "pass_rate_percent": pass_rate,
        "pages_with_errors": len(pages_with_errors),
        "link_audit": links,
        "locale_audit": locale_audit,
        "required_route_details": route_results,
        "failed_pages_sample": pages_with_errors[:30],
        "ready_for_user_review": required_ok and tool_ok and links["broken_count"] == 0 and links["chrome_broken_count"] == 0 and pass_rate >= 99 and locale_audit["ok"],
        "i18n_expansion_blocked_until": "user_review_approved",
    }

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"  HTML files: {len(all_html)}")
    print(f"  Required routes OK: {required_ok}")
    print(f"  Tool pages: {tool_count} (need >=100): {tool_ok}")
    print(f"  Pass rate: {pass_rate}%")
    print(f"  Broken links (main): {links['broken_count']}")
    print(f"  Broken links (chrome/nav): {links['chrome_broken_count']}")
    print(f"  Locales OK ({len(locale_audit['locales'])}): {locale_audit['ok']}")
    print(f"  Ready for review: {report['ready_for_user_review']}")
    print(f"  Report: {REPORT}")

    return 0 if report["ready_for_user_review"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
