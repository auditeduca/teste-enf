#!/usr/bin/env python3
"""Digital sustainability audit — page weight, WebP ratio, estimated carbon."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "website" / "pt"
REPORT = ROOT / "website" / "audit_sustainability_pt_report.json"

# Heuristic: ~0.81 kWh/GB transfer × 442 g CO2/kWh → ~0.35 g CO2 per MB (simplified)
CO2_G_PER_KB = 0.00035
GREEN_PAGE_KB = 500
WARN_PAGE_KB = 1200

IMG_RE = re.compile(r'<img[^>]+src=["\']([^"\']+)', re.I)
CSS_RE = re.compile(r'<link[^>]+rel=["\']stylesheet["\']', re.I)
SCRIPT_RE = re.compile(r'<script[^>]+src=["\']([^"\']+)', re.I)


def page_weight_kb(html: str, page_path: Path) -> dict:
    html_kb = len(html.encode("utf-8")) / 1024
    imgs = IMG_RE.findall(html)
    webp = sum(1 for s in imgs if ".webp" in s.lower())
    css_n = len(CSS_RE.findall(html))
    js_n = len(SCRIPT_RE.findall(html))
    asset_kb = 0.0
    for src in imgs[:20]:
        if src.startswith(("http", "data:", "//")):
            continue
        try:
            ap = (page_path.parent / src).resolve()
            if ap.is_file():
                asset_kb += ap.stat().st_size / 1024
        except (OSError, ValueError):
            pass
    total_kb = round(html_kb + asset_kb, 1)
    return {
        "html_kb": round(html_kb, 1),
        "asset_kb": round(asset_kb, 1),
        "total_kb": total_kb,
        "image_count": len(imgs),
        "webp_count": webp,
        "css_links": css_n,
        "js_links": js_n,
        "est_co2_g": round(total_kb * CO2_G_PER_KB, 4),
        "green": total_kb <= GREEN_PAGE_KB,
    }


def main() -> int:
    print("NKOS digital sustainability audit — pt-BR")
    if not OUT.exists():
        print(f"ERROR: {OUT} not found.")
        return 1

    pages = sorted(OUT.rglob("*.html"))[:400]
    rows = []
    for p in pages:
        rel = p.relative_to(OUT).as_posix()
        html = p.read_text(encoding="utf-8", errors="replace")
        w = page_weight_kb(html, p)
        score = 100
        if w["total_kb"] > WARN_PAGE_KB:
            score -= 40
        elif w["total_kb"] > GREEN_PAGE_KB:
            score -= 15
        if w["image_count"] and w["webp_count"] / w["image_count"] < 0.5:
            score -= 10
        if w["js_links"] > 8:
            score -= 10
        rows.append({"file": rel, "score": max(0, score), **w})

    avg_kb = round(sum(r["total_kb"] for r in rows) / len(rows), 1) if rows else 0
    total_imgs = sum(r["image_count"] for r in rows)
    total_webp = sum(r["webp_count"] for r in rows)
    webp_ratio = round(total_webp / total_imgs * 100, 1) if total_imgs else 100.0
    green_pct = round(sum(1 for r in rows if r["green"]) / len(rows) * 100, 1) if rows else 0
    avg_co2 = round(sum(r["est_co2_g"] for r in rows) / len(rows), 4) if rows else 0
    compliance = round(sum(r["score"] for r in rows) / len(rows), 1) if rows else 0

    report = {
        "audited_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat().replace("+00:00", "Z"),
        "locale": "pt-BR",
        "pages_audited": len(rows),
        "avg_page_weight_kb": avg_kb,
        "webp_ratio_pct": webp_ratio,
        "green_pages_pct": green_pct,
        "est_co2_g_per_page_view": avg_co2,
        "compliance_pct": compliance,
        "passed": compliance >= 75 and green_pct >= 50,
        "thresholds_kb": {"green": GREEN_PAGE_KB, "warn": WARN_PAGE_KB},
        "heaviest_pages": sorted(rows, key=lambda r: -r["total_kb"])[:15],
        "methodology": "Static weight + WebP ratio + simplified CO2 heuristic (SWDM-inspired)",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  Avg {avg_kb} KB | WebP {webp_ratio}% | Compliance {compliance}% | CO2~{avg_co2}g/view")
    return 0 if report["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
