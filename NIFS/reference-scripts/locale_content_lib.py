"""Per-locale content partitions for static site i18n.

Canonical pt-BR lives under ``datasets/content/``. Translations live under
``datasets/by-locale/{locale}/`` and are used by the build when
``i18n_status`` is ``translated`` or body copy differs from pt-BR.
"""
from __future__ import annotations

import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path

from content_paths import DATASETS, content_path
from partition_lib import SITE_LOCALES, normalize_locale

try:
    from global_expansion.site_locales import SITE_LOCALE_META
except ImportError:
    SITE_LOCALE_META = {}

LOCALE_CONTENT_FILES: dict[str, str] = {
    "home_page": "home_page.json",
    "institutional_pages": "institutional_pages.json",
    "chrome_navigation": "chrome_navigation.json",
    "chrome_shell": "chrome_shell.json",
}

CANONICAL_KEYS: dict[str, str] = {
    "home_page": "home_page",
    "institutional_pages": "institutional_pages",
    "chrome_navigation": "chrome_navigation",
    "chrome_shell": "chrome_shell",
}

SKIP_LINK_LABELS: dict[str, str] = {
    "pt-BR": "Pular para o conteúdo principal",
    "en": "Skip to main content",
    "es": "Saltar al contenido principal",
    "fr": "Aller au contenu principal",
    "de": "Zum Hauptinhalt springen",
    "it": "Vai al contenuto principale",
    "ja": "メインコンテンツへスキップ",
    "ar": "انتقل إلى المحتوى الرئيسي",
    "zh-CN": "跳至主要内容",
    "hi-IN": "मुख्य सामग्री पर जाएं",
    "ru-RU": "Перейти к основному содержанию",
    "ko-KR": "본문으로 건너뛰기",
    "tr-TR": "Ana içeriğe geç",
    "pl-PL": "Przejdź do treści głównej",
    "nl-NL": "Ga naar hoofdinhoud",
    "sv-SE": "Hoppa till huvudinnehåll",
    "no-NO": "Hopp til hovedinnhold",
    "da-DK": "Spring til hovedindhold",
    "fi-FI": "Siirry pääsisältöön",
    "cs-CZ": "Přejít na hlavní obsah",
    "hu-HU": "Ugrás a fő tartalomhoz",
    "ro-RO": "Salt la conținutul principal",
    "bg-BG": "Към основното съдържание",
    "hr-HR": "Preskoči na glavni sadržaj",
    "sr-RS": "Preskoči na glavni sadržaj",
    "sl-SI": "Preskoči na glavno vsebino",
    "uk-UA": "Перейти до основного вмісту",
    "vi-VN": "Chuyển đến nội dung chính",
    "th-TH": "ข้ามไปเนื้อหาหลัก",
    "id-ID": "Lewati ke konten utama",
}

# Short site locale code -> URL prefix (matches seo_lib.LOCALES)
LOCALE_URL_PREFIX: dict[str, str] = {
    loc: (SITE_LOCALE_META.get(loc) or {}).get("url_prefix", loc.split("-")[0].lower())
    for loc in SITE_LOCALES
}
LOCALE_URL_PREFIX["pt-BR"] = ""


def _read_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_canonical_home() -> dict:
    return _read_json(content_path("home_page")) or {}


def load_locale_file(key: str, locale: str) -> dict | None:
    loc = normalize_locale(locale)
    fname = LOCALE_CONTENT_FILES.get(key)
    if not fname:
        raise KeyError(key)
    return _read_json(DATASETS / "by-locale" / loc / fname)


def locale_url_prefix(locale: str) -> str:
    loc = normalize_locale(locale)
    return LOCALE_URL_PREFIX.get(loc, loc.split("-")[0].lower())


def skip_link_label(locale: str) -> str:
    loc = normalize_locale(locale)
    return SKIP_LINK_LABELS.get(loc, SKIP_LINK_LABELS.get(loc.split("-")[0], SKIP_LINK_LABELS["en"]))


def home_is_translated(doc: dict | None, locale: str) -> bool:
    """True when locale home JSON should drive rendered HTML (not shell copy)."""
    loc = normalize_locale(locale)
    if loc == "pt-BR":
        return True
    if not doc:
        return False
    status = (doc.get("i18n_status") or "").lower()
    if status == "translated":
        return True
    if status == "shell":
        return False
    base = load_canonical_home()
    return doc.get("hero", {}).get("title") != base.get("hero", {}).get("title")


def resolve_locale_home(locale: str) -> tuple[dict, bool]:
    """Return ``(home_document, use_for_render)``."""
    loc = normalize_locale(locale)
    if loc == "pt-BR":
        return deepcopy(load_canonical_home()), True
    doc = load_locale_file("home_page", loc)
    if doc is None:
        fallback = deepcopy(load_canonical_home())
        fallback["locale"] = loc
        fallback["i18n_status"] = "missing"
        return fallback, False
    return doc, home_is_translated(doc, loc)


def sync_pt_br_home_partition() -> Path:
    """Keep by-locale/pt-BR/home_page.json aligned with canonical site source."""
    src = load_canonical_home()
    dst = DATASETS / "by-locale" / "pt-BR" / "home_page.json"
    doc = deepcopy(src)
    doc["locale"] = "pt-BR"
    doc["partition"] = "locale"
    doc["i18n_status"] = "source"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return dst


def list_site_locales() -> list[str]:
    return list(SITE_LOCALES)
