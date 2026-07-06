"""Bootstrap physical locale partitions for home content and workflows.

Creates datasets/by-locale/{locale}/home_page.json and workflows.json.
Non pt-BR locales receive a localized shell (lang/dir metadata) aligned with site i18n.

Usage:
  python scripts/bootstrap_locale_partitions.py
"""
from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from content_paths import content_rel
from dataset_io import write_envelope
from partition_lib import DATASETS, SITE_LOCALES

NOW = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

LOCALE_META = {
    "pt-BR": {"dir": "ltr", "label": "Português (Brasil)"},
    "en": {"dir": "ltr", "label": "English"},
    "es": {"dir": "ltr", "label": "Español"},
    "fr": {"dir": "ltr", "label": "Français"},
    "de": {"dir": "ltr", "label": "Deutsch"},
    "it": {"dir": "ltr", "label": "Italiano"},
    "ja": {"dir": "ltr", "label": "日本語"},
}


def _load(path: str) -> dict:
    with open(DATASETS / path, encoding="utf-8") as f:
        return json.load(f)


def _localize_home(base: dict, locale: str) -> dict:
    doc = deepcopy(base)
    doc["locale"] = locale
    doc["partition"] = "locale"
    doc["generated_at"] = NOW
    meta = LOCALE_META.get(locale, {"dir": "ltr", "label": locale})
    doc["locale_meta"] = meta
    if locale != "pt-BR":
        doc["i18n_status"] = "shell"
        doc["note"] = f"Locale shell {locale} — body mirrors pt-BR until translated"
    return doc


def main() -> None:
    home_base = _load(content_rel("home_page"))
    workflow_base = _load("ai/workflows.json")

    manifest = {
        "generated_at": NOW,
        "schema_version": "2026.1.0",
        "strategy": "physical_v3",
        "locales": {},
    }

    for locale in SITE_LOCALES:
        loc_dir = DATASETS / "by-locale" / locale
        loc_dir.mkdir(parents=True, exist_ok=True)

        home = _localize_home(home_base, locale)
        home_path = loc_dir / "home_page.json"
        with open(home_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(home, f, indent=2, ensure_ascii=False)
            f.write("\n")

        wf = {k: v for k, v in workflow_base.items() if k != "records"}
        wf["locale"] = locale
        wf["partition"] = "locale"
        wf["records"] = []
        wf["count"] = 0
        wf["generated_at"] = NOW
        write_envelope(f"by-locale/{locale}/workflows.json", wf)

        manifest["locales"][locale] = {
            "home_page": str(home_path.relative_to(DATASETS)).replace("\\", "/"),
            "workflows": f"by-locale/{locale}/workflows.json",
            "direction": LOCALE_META[locale]["dir"],
        }
        print(f"{locale}: home + workflows")

    manifest_path = DATASETS / "by-locale" / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("Wrote", manifest_path)


if __name__ == "__main__":
    main()
