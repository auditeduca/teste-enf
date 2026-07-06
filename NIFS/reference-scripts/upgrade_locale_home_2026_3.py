#!/usr/bin/env python3
"""Upgrade by-locale home_page.json files to schema 2026.3.0."""
from __future__ import annotations

import json
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from locale_home_2026_3_bundles import get_bundle
from locale_home_full_bodies import get_full_body

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "datasets" / "content" / "site" / "home_page.json"
BY_LOCALE = ROOT / "datasets" / "by-locale"
EXTRACTED = ROOT / "datasets" / "content" / "schemas" / "extracted-locales"

ACTIVE_LOCALES = ["en", "es", "fr", "de", "it", "ja"]
EXTRA_LOCALES = ["ro-RO", "uk-UA", "el-GR"]
MERGE_KEYS = (
    "hero",
    "search",
    "solutions",
    "categories",
    "featured",
    "management_block",
    "global_platform",
    "seo",
    "tool_ecosystem",
)

NEW_SECTION_KEYS = (
    "profile_selector",
    "clinical_feed",
    "nursing_os_map",
    "knowledge_hub",
    "clinical_cases",
    "competency_track",
    "ai_assistant",
    "patient_safety_center",
    "occupational_health",
    "impact_dashboard",
    "sustainability_block",
    "governance_center",
    "cta_final",
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _merge_education_into_knowledge(kh: dict, edu: dict) -> dict:
    out = deepcopy(kh)
    if edu.get("title"):
        out["title"] = edu["title"]
    if edu.get("subtitle"):
        out["subtitle"] = edu["subtitle"]
    if edu.get("image"):
        out["image"] = edu["image"]
    if edu.get("image_alt"):
        out["image_alt"] = edu["image_alt"]
    if edu.get("badge"):
        out["badge"] = deepcopy(edu["badge"])
    cta = edu.get("cta") or {}
    if cta.get("label"):
        out.setdefault("cta", {})["label"] = cta["label"]
    if cta.get("href"):
        out.setdefault("cta", {})["href"] = cta["href"]
    links = edu.get("links") or []
    if links and out.get("items"):
        for i, link in enumerate(links[: len(out["items"])]):
            if link.get("label"):
                out["items"][i]["title"] = link["label"]
            if link.get("href"):
                out["items"][i]["href"] = link["href"]
            if link.get("icon"):
                out["items"][i]["icon"] = link["icon"]
    return out


def _merge_daily_into_feed(cf: dict, daily: dict) -> dict:
    out = deepcopy(cf)
    if daily.get("badge"):
        out["badge"] = daily["badge"]
    if daily.get("more_label"):
        out["more_label"] = daily["more_label"]
    if daily.get("more_href"):
        out["more_href"] = daily["more_href"]
    return out


def upgrade_locale(old: dict, template: dict, locale: str) -> dict:
    bundle = get_bundle(locale)
    out = deepcopy(template)
    out["locale"] = locale
    out["generated_at"] = _now_iso()
    out["i18n_status"] = old.get("i18n_status", "translated")
    out["partition"] = old.get("partition", "locale")

    for key in MERGE_KEYS:
        if key in old:
            out[key] = deepcopy(old[key])

    kh = _merge_education_into_knowledge(
        bundle.get("knowledge_hub", template.get("knowledge_hub", {})),
        old.get("education_block") or {},
    )
    out["knowledge_hub"] = kh

    cf = _merge_daily_into_feed(
        bundle.get("clinical_feed", template.get("clinical_feed", {})),
        old.get("daily_tip") or {},
    )
    out["clinical_feed"] = cf

    for key in NEW_SECTION_KEYS:
        if key in bundle:
            out[key] = deepcopy(bundle[key])

    full = get_full_body(locale)
    for key, val in full.items():
        out[key] = deepcopy(val)

    out.pop("daily_tip", None)
    out.pop("education_block", None)
    return out


def _write_locale(locale: str, doc: dict) -> Path:
    loc_dir = BY_LOCALE / locale
    loc_dir.mkdir(parents=True, exist_ok=True)
    path = loc_dir / "home_page.json"
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _load_extracted(locale: str) -> dict | None:
    for name in (f"home_page.{locale}.json", f"home_page.{locale.replace('-', '_')}.json"):
        path = EXTRACTED / name
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    return None


def main() -> int:
    if not TEMPLATE.is_file():
        print(f"Missing template: {TEMPLATE}", file=sys.stderr)
        return 1
    template = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    if template.get("schema_version") != "2026.3.0":
        print("Template is not 2026.3.0 — run migrate_home_page_2026_3.py --promote first", file=sys.stderr)
        return 1

    written: list[str] = []

    # pt-BR partition mirrors canonical site source
    pt_path = _write_locale("pt-BR", deepcopy(template))
    pt_path.write_text(json.dumps({**template, "partition": "locale", "i18n_status": "translated"}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    written.append(str(pt_path.relative_to(ROOT)))

    for locale in ACTIVE_LOCALES:
        old_path = BY_LOCALE / locale / "home_page.json"
        old = json.loads(old_path.read_text(encoding="utf-8")) if old_path.is_file() else {"locale": locale}
        doc = upgrade_locale(old, template, locale)
        path = _write_locale(locale, doc)
        written.append(str(path.relative_to(ROOT)))

    for locale in EXTRA_LOCALES:
        extracted = _load_extracted(locale)
        if extracted:
            extracted["locale"] = locale
            extracted["i18n_status"] = "translated"
            extracted["partition"] = "locale"
            extracted["generated_at"] = _now_iso()
            extracted.pop("daily_tip", None)
            extracted.pop("education_block", None)
            path = _write_locale(locale, extracted)
        else:
            old_path = BY_LOCALE / locale / "home_page.json"
            old = json.loads(old_path.read_text(encoding="utf-8")) if old_path.is_file() else {"locale": locale}
            doc = upgrade_locale(old, template, locale)
            path = _write_locale(locale, doc)
        written.append(str(path.relative_to(ROOT)))

    for rel in written:
        print(rel)
    print(f"Upgraded {len(written)} locale(s) to 2026.3.0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
