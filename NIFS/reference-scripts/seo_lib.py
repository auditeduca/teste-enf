"""SEO + i18n platform helpers for the Calculadoras de Enfermagem static site.

Centralizes everything search engines and crawlers need that is *not* page
body content: absolute/canonical URLs, hreflang alternates, schema.org JSON-LD,
XML sitemaps (+ sitemap index), robots.txt, an RSS feed and a client-side
search index.

The single integration point for per-page markup is ``head_seo()``, consumed by
``website_lib.render_document``. Site-wide artifact generation
(``generate_sitemaps``/``generate_robots``/``generate_feed``/``write_search_index``)
is called once at the end of the build.
"""
from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SITE_URL = "https://calculadorasdeenfermagem.com.br"
SITE_NAME = "Calculadoras de Enfermagem"
DEFAULT_LANG = "pt-BR"
LOGO_PATH = "/assets/images/logotipo_website.webp"

# Build locales for hreflang/multi-locale routing.
# (url_prefix, hreflang, html_lang, dir). pt-BR is the canonical root (no prefix).
try:
    from global_expansion.site_locales import seo_locales

    LOCALES: list[tuple[str, str, str, str]] = seo_locales()
except ImportError:
    LOCALES = [
        ("", "pt-BR", "pt-BR", "ltr"),
        ("en", "en", "en", "ltr"),
        ("es", "es", "es", "ltr"),
        ("fr", "fr", "fr", "ltr"),
        ("de", "de", "de", "ltr"),
        ("it", "it", "it", "ltr"),
        ("ja", "ja", "ja", "ltr"),
    ]


def _esc(text: object) -> str:
    return html.escape(str(text) if text is not None else "", quote=True)


def _norm_path(canonical_path: str) -> str:
    """Normalize a canonical path to a leading-slash, trailing-slash directory URL."""
    p = (canonical_path or "/").strip()
    if not p.startswith("/"):
        p = "/" + p
    if p == "/":
        return "/"
    return p if p.endswith("/") else p + "/"


def absolute_url(canonical_path: str, prefix: str = "") -> str:
    """Absolute URL for a canonical path under an optional locale ``prefix``."""
    p = _norm_path(canonical_path)
    base = SITE_URL + (f"/{prefix}" if prefix else "")
    if p == "/":
        return base + "/"
    return base + p


def render_alternates(canonical_path: str) -> str:
    """hreflang alternate links for every build locale, plus x-default (pt-BR)."""
    links = [
        f'<link rel="alternate" hreflang="{hl}" href="{_esc(absolute_url(canonical_path, prefix))}">'
        for prefix, hl, _lang, _dir in LOCALES
    ]
    links.append(
        f'<link rel="alternate" hreflang="x-default" href="{_esc(absolute_url(canonical_path))}">'
    )
    return "\n  ".join(links)


# ─────────────────────────── JSON-LD ───────────────────────────

def _org_node() -> dict:
    return {
        "@type": "Organization",
        "@id": f"{SITE_URL}/#organization",
        "name": SITE_NAME,
        "url": f"{SITE_URL}/",
        "logo": SITE_URL + LOGO_PATH,
    }


def _website_node() -> dict:
    return {
        "@type": "WebSite",
        "@id": f"{SITE_URL}/#website",
        "url": f"{SITE_URL}/",
        "name": SITE_NAME,
        "inLanguage": DEFAULT_LANG,
        "publisher": {"@id": f"{SITE_URL}/#organization"},
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": f"{SITE_URL}/ferramentas/?q={{search_term_string}}",
            },
            "query-input": "required name=search_term_string",
        },
    }


def _breadcrumb_node(canonical_path: str, page_title: str) -> dict | None:
    p = _norm_path(canonical_path)
    if p == "/":
        return None
    segments = [s for s in p.strip("/").split("/") if s]
    items = [{
        "@type": "ListItem", "position": 1, "name": "Início", "item": f"{SITE_URL}/",
    }]
    acc = ""
    for i, seg in enumerate(segments, start=2):
        acc += "/" + seg
        is_last = i == len(segments) + 1
        name = page_title if is_last else seg.replace("-", " ").capitalize()
        items.append({
            "@type": "ListItem",
            "position": i,
            "name": name,
            "item": absolute_url(acc),
        })
    return {"@type": "BreadcrumbList", "itemListElement": items}


def default_jsonld(title: str, description: str, canonical_path: str,
                   extra: list[dict] | dict | None = None) -> dict:
    """schema.org @graph: Organization + WebSite + WebPage (+ Breadcrumb + extras)."""
    url = absolute_url(canonical_path)
    graph: list[dict] = [
        _org_node(),
        _website_node(),
        {
            "@type": "WebPage",
            "@id": f"{url}#webpage",
            "url": url,
            "name": title,
            "description": description,
            "inLanguage": DEFAULT_LANG,
            "isPartOf": {"@id": f"{SITE_URL}/#website"},
        },
    ]
    bc = _breadcrumb_node(canonical_path, title)
    if bc:
        graph.append(bc)
    if extra:
        graph.extend(extra if isinstance(extra, list) else [extra])
    return {"@context": "https://schema.org", "@graph": graph}


def render_jsonld(obj: dict) -> str:
    return (
        '<script type="application/ld+json">'
        + json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
        + "</script>"
    )


def head_seo(title: str, description: str, canonical_path: str,
             *, locale_prefix: str = "", og_type: str = "website",
             json_ld: dict | list[dict] | None = None) -> str:
    """Full per-page SEO head block: canonical, og:url/site_name, hreflang, JSON-LD."""
    canon = absolute_url(canonical_path, locale_prefix)
    if json_ld is None:
        ld = default_jsonld(title, description, canonical_path)
    elif isinstance(json_ld, list):
        ld = default_jsonld(title, description, canonical_path, extra=json_ld)
    else:
        ld = json_ld
    return (
        f'<link rel="canonical" href="{_esc(canon)}">\n  '
        f'<meta property="og:url" content="{_esc(canon)}">\n  '
        f'<meta property="og:site_name" content="{_esc(SITE_NAME)}">\n  '
        f'<meta name="robots" content="index,follow">\n  '
        + render_alternates(canonical_path)
        + "\n  "
        + render_jsonld(ld)
    )


# ─────────────────────────── Sitemaps ───────────────────────────

def _page_url(rel: str, prefix: str = "") -> str:
    path = "/" + rel.replace("\\", "/")
    path = path.replace("/index.html", "/")
    if path.endswith("index.html"):
        path = path[: -len("index.html")]
    if not path.endswith("/"):
        path += "/"
    base = SITE_URL + (f"/{prefix}" if prefix else "")
    return base + (path if path != "/" else "/")


def generate_sitemaps(out_dir: Path, pages: list[str], *, prefix: str = "",
                      lastmod: str | None = None) -> Path:
    """Write a sitemap.xml under ``out_dir`` for the given relative page paths."""
    lastmod = lastmod or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    seen: set[str] = set()
    rows = []
    for rel in sorted(set(pages)):
        url = _page_url(rel, prefix)
        if url in seen:
            continue
        seen.add(url)
        priority = "1.0" if url.rstrip("/") == (SITE_URL + (f"/{prefix}" if prefix else "")).rstrip("/") else "0.7"
        rows.append(
            f"  <url>\n    <loc>{_esc(url)}</loc>\n"
            f"    <lastmod>{lastmod}</lastmod>\n"
            f"    <changefreq>weekly</changefreq>\n"
            f"    <priority>{priority}</priority>\n  </url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(rows)
        + "\n</urlset>\n"
    )
    path = out_dir / "sitemap.xml"
    path.write_text(xml, encoding="utf-8", newline="\n")
    return path


def generate_sitemap_index(out_dir: Path, locale_prefixes: list[str],
                           *, lastmod: str | None = None) -> Path:
    """Write sitemap-index.xml referencing each locale sitemap."""
    lastmod = lastmod or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rows = []
    for prefix in locale_prefixes:
        loc = SITE_URL + (f"/{prefix}" if prefix else "") + "/sitemap.xml"
        rows.append(f"  <sitemap>\n    <loc>{_esc(loc)}</loc>\n    <lastmod>{lastmod}</lastmod>\n  </sitemap>")
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(rows)
        + "\n</sitemapindex>\n"
    )
    path = out_dir / "sitemap-index.xml"
    path.write_text(xml, encoding="utf-8", newline="\n")
    return path


def generate_robots(out_dir: Path) -> Path:
    txt = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /assets/data/\n\n"
        f"Sitemap: {SITE_URL}/sitemap-index.xml\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n"
    )
    path = out_dir / "robots.txt"
    path.write_text(txt, encoding="utf-8", newline="\n")
    return path


# ─────────────────────────── RSS feed ───────────────────────────

def generate_feed(out_dir: Path, items: list[dict]) -> Path:
    """Write an RSS 2.0 feed. ``items``: {title, path, description}."""
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    entries = []
    for it in items:
        link = absolute_url(it["path"])
        entries.append(
            "  <item>\n"
            f"    <title>{_esc(it['title'])}</title>\n"
            f"    <link>{_esc(link)}</link>\n"
            f"    <guid isPermaLink=\"true\">{_esc(link)}</guid>\n"
            f"    <description>{_esc(it.get('description', ''))}</description>\n"
            f"    <pubDate>{now}</pubDate>\n"
            "  </item>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0"><channel>\n'
        f"  <title>{_esc(SITE_NAME)}</title>\n"
        f"  <link>{SITE_URL}/</link>\n"
        "  <description>Calculadoras, escalas, protocolos e conteúdo clínico de enfermagem — Calculadoras de Enfermagem 2026.</description>\n"
        f"  <language>{DEFAULT_LANG}</language>\n"
        f"  <lastBuildDate>{now}</lastBuildDate>\n"
        + "\n".join(entries)
        + "\n</channel></rss>\n"
    )
    path = out_dir / "feed.xml"
    path.write_text(xml, encoding="utf-8", newline="\n")
    return path


# ─────────────────────────── Search index ───────────────────────────

# ─────────────────────────── Locale (i18n) build ───────────────────────────

# Add one extra "../" hop to every *relative* asset path so locale pages
# (one directory deeper) resolve to the single shared /assets tree at the root.
# Lookbehind on a delimiter avoids touching absolute URLs (…domain/assets/…).
_ASSET_OFFSET_RE = re.compile(r'(?<=["\'(])((?:\.\./)*)assets/')


def _bump_ce_prefix(html: str) -> str:
    """Shift chrome path prefix up one directory for locale subfolders."""

    def bump_html_attr(match: re.Match) -> str:
        return f'data-ce-prefix="../{match.group(1)}"'

    html = re.sub(r'data-ce-prefix="([^"]*)"', bump_html_attr, html, count=1)
    html = re.sub(
        r'(<meta name="ce-asset-prefix" content=")([^"]*)(")',
        r'\1../\2\3',
        html,
        count=1,
    )
    return html


def localize_html(page_html: str, prefix: str, lang: str, direction: str = "ltr") -> str:
    """Derive a locale variant from an already-rendered pt-BR page.

    Adjusts ``<html lang/dir>``, the canonical + og:url (locale-prefixed) and
    shifts relative asset paths up one level to the shared root assets. hreflang
    alternates already enumerate every locale, so they are left untouched.
    """
    out = re.sub(
        r'<html lang="pt-BR"([^>]*)>',
        lambda m: f'<html lang="{lang}" dir="{direction}"{m.group(1)}>',
        page_html,
        count=1,
    )
    out = _bump_ce_prefix(out)
    out = out.replace(
        f'rel="canonical" href="{SITE_URL}/',
        f'rel="canonical" href="{SITE_URL}/{prefix}/',
    )
    out = out.replace(
        f'property="og:url" content="{SITE_URL}/',
        f'property="og:url" content="{SITE_URL}/{prefix}/',
    )
    out = _ASSET_OFFSET_RE.sub(r'../\1assets/', out)
    og_locale = lang if lang != "pt-BR" else "pt_BR"
    if lang == "en":
        og_locale = "en"
    out = re.sub(
        r'<meta property="og:locale" content="[^"]*">',
        f'<meta property="og:locale" content="{og_locale}">',
        out,
        count=1,
    )
    return out


def write_search_index(out_dir: Path, entries: list[dict]) -> Path:
    """Write assets/data/search-index.json. ``entries``: {title, description, url, type}."""
    path = out_dir / "assets" / "data" / "search-index.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8", newline="\n")
    return path
