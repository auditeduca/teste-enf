#!/usr/bin/env python3
"""Sync institutional center pages into NKOS datasets."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def patch_seo(canonical: str, title: str, description: str) -> None:
    seo = load(ROOT / "datasets" / "metadata" / "seo_metadata.json")
    for rec in seo["records"]:
        if rec.get("canonical_path") == canonical:
            rec["title"] = title
            rec["description"] = description
            rec["updated_at"] = NOW
    save(ROOT / "datasets" / "metadata" / "seo_metadata.json", seo)


def main() -> int:
    privacy = load(ROOT / "datasets" / "content" / "privacy_center.json")
    sustain = load(ROOT / "datasets" / "content" / "sustainability_center.json")
    home = load(ROOT / "datasets" / "content" / "home_page.json")

    patch_seo("/privacidade", privacy["seo"]["title"], privacy["seo"]["description"])
    patch_seo("/sustentabilidade", sustain["seo"]["title"], sustain["seo"]["description"])
    patch_seo("/", home["seo"]["title"], home["seo"]["description"])

    tpl = load(ROOT / "datasets" / "metadata" / "templates.json")
    for rec in tpl["records"]:
        if rec.get("template_code") == "TPL.PRIVACY_CENTER":
            rec["status"] = "active"
            rec["updated_at"] = NOW
        if rec.get("template_code") == "TPL.SUSTAINABILITY_CENTER":
            rec["status"] = "active"
            rec["updated_at"] = NOW
    # Add templates if missing
    codes = {r["template_code"] for r in tpl["records"]}
    if "TPL.PRIVACY_CENTER" not in codes:
        tpl["records"].append({
            "uuid": "a1000001-0000-4000-8000-000000000001",
            "template_code": "TPL.PRIVACY_CENTER",
            "name": "Central de Privacidade",
            "layout_code": "LAYOUT.PRIVACY_CENTER",
            "reference_page": "/privacidade",
            "status": "active",
            "edition": "2026",
            "updated_at": NOW,
        })
    if "TPL.SUSTAINABILITY_CENTER" not in codes:
        tpl["records"].append({
            "uuid": "a1000002-0000-4000-8000-000000000002",
            "template_code": "TPL.SUSTAINABILITY_CENTER",
            "name": "Central de Sustentabilidade Digital",
            "layout_code": "LAYOUT.SUSTAINABILITY_CENTER",
            "reference_page": "/sustentabilidade",
            "status": "active",
            "edition": "2026",
            "updated_at": NOW,
        })
    tpl["count"] = len(tpl["records"])
    save(ROOT / "datasets" / "metadata" / "templates.json", tpl)

    status_path = ROOT / "datasets" / "metadata" / "nkos_implementation_status.json"
    if status_path.exists():
        st = load(status_path)
        st.setdefault("website_pt", {})
        st["website_pt"]["institutional_centers"] = {
            "privacy": "datasets/content/privacy_center.json",
            "sustainability": "datasets/content/sustainability_center.json",
            "updated_at": NOW,
        }
        save(status_path, st)

    print("Institutional pages database updated")
    print(f"  /privacidade — {privacy['seo']['title'][:50]}…")
    print(f"  /sustentabilidade — {sustain['seo']['title'][:50]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
