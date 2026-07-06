#!/usr/bin/env python3
"""SEO audit for static pt-BR website — meta, JSON-LD, headings, canonical."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "website" / "pt"
REPORT = ROOT / "website" / "audit_seo_pt_report.json"

TITLE_RE = re.compile(r"<title[^>]*>([^<]+)</title>", re.I)
META_DESC = re.compile(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)', re.I)
CANONICAL = re.compile(r'<link[^>]+rel=["\']canonical["\']', re.I)
OG_TITLE = re.compile(r'<meta[^>]+property=["\']og:title["\']', re.I)
JSONLD = re.compile(r'<script[^>]+type=["\']application/ld\+json["\']', re.I)
H1_RE = re.compile(r"<h1[^>]*>", re.I)
LANG_RE = re.compile(r'<html[^>]+lang=["\']([^"\']+)', re.I)


def audit_html(rel: str, html: str) -> dict:
    issues: list[dict] = []
    score = 100

    title_m = TITLE_RE.search(html)
    title = title_m.group(1).strip() if title_m else ""
    if not title:
        issues.append({"code": "MISSING_TITLE", "severity": "error", "message": "Sem <title>"})
        score -= 25
    elif len(title) < 10 or len(title) > 70:
        issues.append({"code": "TITLE_LENGTH", "severity": "warning", "message": f"Title fora do ideal (10–70): {len(title)} chars"})
        score -= 5

    if not META_DESC.search(html):
        issues.append({"code": "MISSING_META_DESC", "severity": "error", "message": "meta description ausente"})
        score -= 20

    if not CANONICAL.search(html):
        issues.append({"code": "MISSING_CANONICAL", "severity": "warning", "message": "link canonical ausente"})
        score -= 8

    if not OG_TITLE.search(html):
        issues.append({"code": "MISSING_OG", "severity": "warning", "message": "og:title ausente"})
        score -= 5

    if not JSONLD.search(html):
        issues.append({"code": "MISSING_JSONLD", "severity": "warning", "message": "JSON-LD ausente"})
        score -= 10

    h1_count = len(H1_RE.findall(html))
    if h1_count == 0:
        issues.append({"code": "NO_H1", "severity": "error", "message": "Nenhum H1"})
        score -= 15
    elif h1_count > 1:
        issues.append({"code": "MULTI_H1", "severity": "warning", "message": f"{h1_count} elementos H1"})
        score -= 5

    if not LANG_RE.search(html):
        issues.append({"code": "MISSING_LANG", "severity": "error", "message": "html lang ausente"})
        score -= 10

    return {"file": rel, "score": max(0, score), "issues": issues}


def main() -> int:
    print("NKOS SEO audit — pt-BR")
    if not OUT.exists():
        print(f"ERROR: {OUT} not found.")
        return 1

    pages = sorted(OUT.rglob("*.html"))[:500]
    results = []
    for p in pages:
        rel = p.relative_to(OUT).as_posix()
        try:
            results.append(audit_html(rel, p.read_text(encoding="utf-8", errors="replace")))
        except OSError as exc:
            results.append({"file": rel, "score": 0, "issues": [{"code": "READ_ERROR", "severity": "error", "message": str(exc)}]})

    total_issues = sum(len(r["issues"]) for r in results)
    avg_score = round(sum(r["score"] for r in results) / len(results), 1) if results else 0
    compliance = avg_score

    report = {
        "audited_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat().replace("+00:00", "Z"),
        "locale": "pt-BR",
        "pages_audited": len(results),
        "total_issues": total_issues,
        "avg_page_score": avg_score,
        "compliance_pct": compliance,
        "passed": compliance >= 85 and total_issues == 0,
        "worst_pages": sorted(results, key=lambda r: r["score"])[:15],
        "methodology": "Static HTML — title, meta, canonical, OG, JSON-LD, H1, lang",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  Pages: {len(results)} | Compliance: {compliance}% | Issues: {total_issues}")
    return 0 if report["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
