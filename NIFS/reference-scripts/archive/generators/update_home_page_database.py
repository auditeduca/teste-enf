#!/usr/bin/env python3
"""Sync home page content into NKOS datasets (SEO, template, sections)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "datasets" / "content" / "home_page.json"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main() -> int:
    home = load(HOME)
    seo_title = home["seo"]["title"]
    seo_desc = home["seo"]["description"]

    # SEO metadata for /
    seo_path = ROOT / "datasets" / "metadata" / "seo_metadata.json"
    seo_data = load(seo_path)
    for rec in seo_data["records"]:
        if rec.get("canonical_path") == "/":
            rec["title"] = seo_title
            rec["description"] = seo_desc
            rec["updated_at"] = NOW
    save(seo_path, seo_data)

    # Template status
    tpl_path = ROOT / "datasets" / "metadata" / "templates.json"
    tpl_data = load(tpl_path)
    for rec in tpl_data["records"]:
        if rec.get("template_code") == "TPL.LANDING_HOME":
            rec["status"] = "active"
            rec["name"] = "Landing Home — Inteligência Clínica"
            rec["updated_at"] = NOW
    save(tpl_path, tpl_data)

    # Sections — align with mockup blocks
    sec_path = ROOT / "datasets" / "metadata" / "sections.json"
    sec_data = load(sec_path)
    mapping = {
        "SEC.TPL_LANDING_HOME.HERO": {
            "section_type": "HERO",
            "component_codes": ["UI.HOME_HERO", "UI.HOME_SEARCH"],
            "content_ref": "home_page.json#hero",
        },
        "SEC.TPL_LANDING_HOME.CNT": {
            "section_type": "CATEGORIES",
            "component_codes": ["UI.HOME_CATEGORY_GRID"],
            "content_ref": "home_page.json#categories",
        },
        "SEC.TPL_LANDING_HOME.FAQ": {
            "section_type": "FEATURED",
            "component_codes": ["UI.HOME_FEATURED_TOOLS"],
            "content_ref": "home_page.json#featured",
        },
        "SEC.TPL_LANDING_HOME.CTA": {
            "section_type": "CTA",
            "component_codes": ["UI.CTA_BANNER"],
            "content_ref": "home_page.json#search",
        },
    }
    for rec in sec_data["records"]:
        code = rec.get("section_code")
        if code in mapping:
            rec.update(mapping[code])
            rec["updated_at"] = NOW
    save(sec_path, sec_data)

    # Implementation status note
    status_path = ROOT / "datasets" / "metadata" / "nkos_implementation_status.json"
    if status_path.exists():
        status = load(status_path)
        status.setdefault("website_pt", {})
        status["website_pt"]["home_page"] = {
            "content_file": "datasets/content/home_page.json",
            "template": "TPL.LANDING_HOME",
            "updated_at": NOW,
            "sections": list(mapping.keys()),
        }
        save(status_path, status)

    print(f"Home page database updated from {HOME.name}")
    print(f"  SEO: {seo_title[:60]}…")
    print(f"  Template TPL.LANDING_HOME -> active")
    print(f"  Sections: {len(mapping)} aligned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
