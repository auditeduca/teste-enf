"""Split sharded translations into per-locale files for lazy admin loading.

Reads content/translations.json shard-by-shard (~160k records) and writes
compact envelopes to datasets/by-locale/{locale}/translations.json.

Usage:
  python scripts/bootstrap_translation_locales.py
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from dataset_io import iter_records, read_envelope_meta, write_envelope
from partition_lib import DATASETS, SITE_LOCALES, normalize_locale

from content_paths import content_rel

TRANSLATIONS_GLOBAL = content_rel("translations")
NOW = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

LANG_TO_SITE_LOCALE = {
    "pt": "pt-BR",
    "en": "en",
    "es": "es",
    "fr": "fr",
    "de": "de",
    "it": "it",
    "ja": "ja",
    "zh": "zh-CN",
    "ar": "ar",
    "hi": "hi-IN",
    "ru": "ru-RU",
    "ko": "ko-KR",
    "tr": "tr-TR",
    "pl": "pl-PL",
    "nl": "nl-NL",
    "sv": "sv-SE",
    "no": "no-NO",
    "da": "da-DK",
    "fi": "fi-FI",
    "cs": "cs-CZ",
    "hu": "hu-HU",
    "ro": "ro-RO",
    "bg": "bg-BG",
    "hr": "hr-HR",
    "sr": "sr-RS",
    "sl": "sl-SI",
    "uk": "uk-UA",
    "vi": "vi-VN",
    "th": "th-TH",
    "id": "id-ID",
}


def _bucket_locale(rec: dict) -> str | None:
    lang = (rec.get("language_code") or "").lower()
    if lang in LANG_TO_SITE_LOCALE:
        return LANG_TO_SITE_LOCALE[lang]
    target = rec.get("target_locale") or ""
    return normalize_locale(target) if target else None


def main() -> None:
    meta = read_envelope_meta(TRANSLATIONS_GLOBAL)
    buckets: dict[str, list] = defaultdict(list)
    skipped = 0
    total = 0

    print("Streaming", meta.get("count", "?"), "translations from shards…")
    for rec in iter_records(TRANSLATIONS_GLOBAL):
        total += 1
        loc = _bucket_locale(rec)
        if loc not in SITE_LOCALES:
            skipped += 1
            continue
        buckets[loc].append(rec)
        if total % 25000 == 0:
            print(f"  …{total} scanned")

    manifest = {
        "generated_at": NOW,
        "schema_version": "2026.1.0",
        "strategy": "physical_v4",
        "source": TRANSLATIONS_GLOBAL,
        "total_scanned": total,
        "skipped_non_site_locales": skipped,
        "locales": {},
    }

    base_meta = {k: v for k, v in meta.items() if k not in ("records", "shard_files", "sharded", "shard_count")}

    for locale in SITE_LOCALES:
        records = buckets.get(locale, [])
        env = {
            **base_meta,
            "entity": "Translation",
            "partition": "locale",
            "locale": locale,
            "source_global": TRANSLATIONS_GLOBAL,
            "records": records,
            "count": len(records),
            "generated_at": NOW,
        }
        rel = f"by-locale/{locale}/translations.json"
        write_envelope(rel, env)
        manifest["locales"][locale] = {"path": rel, "count": len(records)}
        print(f"{locale}: {len(records)} translations")

    out = DATASETS / "by-locale" / "translations_manifest.json"
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("Wrote", out)


if __name__ == "__main__":
    main()
