"""Definição canônica dos 30 idiomas do site (build + i18n + SEO)."""
from __future__ import annotations

# language_code → site locale primário
PRIMARY_SITE_LOCALE: dict[str, str] = {
    "pt": "pt-BR",
    "en": "en",
    "es": "es",
    "fr": "fr",
    "de": "de",
    "it": "it",
    "zh": "zh-CN",
    "ja": "ja",
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

SITE_LOCALES: list[str] = list(PRIMARY_SITE_LOCALE.values())

# site_locale → metadados SEO/build
SITE_LOCALE_META: dict[str, dict[str, str]] = {
    "pt-BR": {"url_prefix": "", "hreflang": "pt-BR", "html_lang": "pt-BR", "dir": "ltr", "language_code": "pt"},
    "en": {"url_prefix": "en", "hreflang": "en", "html_lang": "en", "dir": "ltr", "language_code": "en"},
    "es": {"url_prefix": "es", "hreflang": "es", "html_lang": "es", "dir": "ltr", "language_code": "es"},
    "fr": {"url_prefix": "fr", "hreflang": "fr", "html_lang": "fr", "dir": "ltr", "language_code": "fr"},
    "de": {"url_prefix": "de", "hreflang": "de", "html_lang": "de", "dir": "ltr", "language_code": "de"},
    "it": {"url_prefix": "it", "hreflang": "it", "html_lang": "it", "dir": "ltr", "language_code": "it"},
    "ja": {"url_prefix": "ja", "hreflang": "ja", "html_lang": "ja", "dir": "ltr", "language_code": "ja"},
    "zh-CN": {"url_prefix": "zh", "hreflang": "zh-CN", "html_lang": "zh-CN", "dir": "ltr", "language_code": "zh"},
    "ar": {"url_prefix": "ar", "hreflang": "ar", "html_lang": "ar", "dir": "rtl", "language_code": "ar"},
    "hi-IN": {"url_prefix": "hi", "hreflang": "hi-IN", "html_lang": "hi", "dir": "ltr", "language_code": "hi"},
    "ru-RU": {"url_prefix": "ru", "hreflang": "ru-RU", "html_lang": "ru", "dir": "ltr", "language_code": "ru"},
    "ko-KR": {"url_prefix": "ko", "hreflang": "ko-KR", "html_lang": "ko", "dir": "ltr", "language_code": "ko"},
    "tr-TR": {"url_prefix": "tr", "hreflang": "tr-TR", "html_lang": "tr", "dir": "ltr", "language_code": "tr"},
    "pl-PL": {"url_prefix": "pl", "hreflang": "pl-PL", "html_lang": "pl", "dir": "ltr", "language_code": "pl"},
    "nl-NL": {"url_prefix": "nl", "hreflang": "nl-NL", "html_lang": "nl", "dir": "ltr", "language_code": "nl"},
    "sv-SE": {"url_prefix": "sv", "hreflang": "sv-SE", "html_lang": "sv", "dir": "ltr", "language_code": "sv"},
    "no-NO": {"url_prefix": "no", "hreflang": "no-NO", "html_lang": "no", "dir": "ltr", "language_code": "no"},
    "da-DK": {"url_prefix": "da", "hreflang": "da-DK", "html_lang": "da", "dir": "ltr", "language_code": "da"},
    "fi-FI": {"url_prefix": "fi", "hreflang": "fi-FI", "html_lang": "fi", "dir": "ltr", "language_code": "fi"},
    "cs-CZ": {"url_prefix": "cs", "hreflang": "cs-CZ", "html_lang": "cs", "dir": "ltr", "language_code": "cs"},
    "hu-HU": {"url_prefix": "hu", "hreflang": "hu-HU", "html_lang": "hu", "dir": "ltr", "language_code": "hu"},
    "ro-RO": {"url_prefix": "ro", "hreflang": "ro-RO", "html_lang": "ro", "dir": "ltr", "language_code": "ro"},
    "bg-BG": {"url_prefix": "bg", "hreflang": "bg-BG", "html_lang": "bg", "dir": "ltr", "language_code": "bg"},
    "hr-HR": {"url_prefix": "hr", "hreflang": "hr-HR", "html_lang": "hr", "dir": "ltr", "language_code": "hr"},
    "sr-RS": {"url_prefix": "sr", "hreflang": "sr-RS", "html_lang": "sr", "dir": "ltr", "language_code": "sr"},
    "sl-SI": {"url_prefix": "sl", "hreflang": "sl-SI", "html_lang": "sl", "dir": "ltr", "language_code": "sl"},
    "uk-UA": {"url_prefix": "uk", "hreflang": "uk-UA", "html_lang": "uk", "dir": "ltr", "language_code": "uk"},
    "vi-VN": {"url_prefix": "vi", "hreflang": "vi-VN", "html_lang": "vi", "dir": "ltr", "language_code": "vi"},
    "th-TH": {"url_prefix": "th", "hreflang": "th-TH", "html_lang": "th", "dir": "ltr", "language_code": "th"},
    "id-ID": {"url_prefix": "id", "hreflang": "id-ID", "html_lang": "id", "dir": "ltr", "language_code": "id"},
}

I18N_PAGE_TYPES = [
    ("HOME", "/", "HomePageContent"),
    ("TOOLS", "/ferramentas/", "ToolsHub"),
    ("SIM", "/simulados/", "SimuladosHub"),
    ("FLA", "/flashcards/", "FlashcardsHub"),
    ("PRT", "/protocolos/", "ProtocolosHub"),
    ("EMP", "/empregos/", "JobsHub"),
    ("CUR", "/cursos/", "CoursesHub"),
    ("CAR", "/carreiras/", "CareersHub"),
    ("LIB", "/biblioteca/", "LibraryHub"),
    ("FAQ", "/faq/", "FaqPage"),
]


def seo_locales() -> list[tuple[str, str, str, str]]:
    """(url_prefix, hreflang, html_lang, dir) — compatível com seo_lib.LOCALES."""
    out: list[tuple[str, str, str, str]] = []
    for loc in SITE_LOCALES:
        m = SITE_LOCALE_META[loc]
        out.append((m["url_prefix"], m["hreflang"], m["html_lang"], m["dir"]))
    return out
