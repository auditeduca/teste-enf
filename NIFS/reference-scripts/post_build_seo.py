"""Post-build SEO: scan generated HTML for search index, sitemaps with hreflang, RSS.

Runs after all pages are written so metadata always matches rendered output
(phase-6 pattern from the reference SSG).
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

from seo_lib import (
    DEFAULT_LANG,
    LOCALES,
    SITE_NAME,
    SITE_URL,
    absolute_url,
    generate_feed,
    generate_robots,
    generate_sitemap_index,
    write_search_index,
)

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.I | re.S)
DESC_RE = re.compile(r'<meta name="description" content="([^"]*)"', re.I)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.I | re.S)
CANON_RE = re.compile(r'<link rel="canonical" href="([^"]+)"', re.I)
HASHTAGS_RE = re.compile(r'<meta name="ce-hashtags" content="([^"]*)"', re.I)
TAG_RE = re.compile(r"<[^>]+>")

SECTION_TAGS: dict[str, list[str]] = {
    "ferramentas": ["#ferramentas", "#clinico", "#enfermagem"],
    "calculadoras": ["#calculadoras", "#ferramentas", "#enfermagem"],
    "escalas": ["#escalas", "#ferramentas", "#enfermagem"],
    "protocolos": ["#protocolos", "#clinico", "#enfermagem"],
    "medicamentos": ["#medicamentos", "#farmacia", "#enfermagem"],
    "artigos": ["#artigos", "#educacao", "#enfermagem"],
    "simulados": ["#simulados", "#educacao", "#enfermagem"],
    "flashcards": ["#flashcards", "#educacao", "#enfermagem"],
    "privacidade": ["#privacidade", "#lgpd", "#institucional"],
    "sustentabilidade": ["#sustentabilidade", "#esg", "#institucional"],
    "acessibilidade": ["#acessibilidade", "#wcag", "#institucional"],
    "missao": ["#missao", "#institucional", "#enfermagem"],
    "objetivo": ["#objetivo", "#institucional", "#plataforma"],
    "busca": ["#busca", "#pesquisa"],
    "mapa-site": ["#mapa", "#navegacao", "#institucional"],
    "contato": ["#contato", "#suporte", "#institucional"],
    "fale-conosco": ["#contato", "#suporte", "#institucional"],
}

SECTION_PRIORITY = {
    "": 1.0,
    "ferramentas": 0.9,
    "calculadoras": 0.9,
    "escalas": 0.9,
    "medicamentos": 0.85,
    "protocolos": 0.85,
    "artigos": 0.7,
    "nanda": 0.8,
    "nic": 0.8,
    "noc": 0.8,
}
SECTION_CHANGEFREQ = {
    "": "weekly",
    "ferramentas": "monthly",
    "calculadoras": "monthly",
    "escalas": "monthly",
    "medicamentos": "monthly",
    "protocolos": "monthly",
    "nanda": "yearly",
    "nic": "yearly",
    "noc": "yearly",
}


def _clean(text: str) -> str:
    return TAG_RE.sub("", text).strip()


def _locale_dirs() -> set[str]:
    return {prefix for prefix, *_ in LOCALES if prefix}


def _canonical_path_from_rel(rel: str) -> str:
    p = rel.replace("\\", "/").replace("/index.html", "")
    if not p or p == "index.html":
        return "/"
    return "/" + p.strip("/") + "/"


def scan_search_index(out_dir: Path) -> list[dict]:
    """Build search index from pt-BR pages only (canonical paths)."""
    skip = _locale_dirs()
    entries: list[dict] = []
    for html_file in sorted(out_dir.rglob("index.html")):
        rel = html_file.relative_to(out_dir).as_posix()
        parts = Path(rel).parts
        if parts and parts[0] in skip:
            continue
        try:
            content = html_file.read_text(encoding="utf-8")
        except OSError:
            continue
        canon_m = CANON_RE.search(content)
        url = _canonical_path_from_rel(rel)
        if canon_m:
            raw = canon_m.group(1)
            if raw.startswith(SITE_URL):
                url = raw[len(SITE_URL) :].rstrip("/") + "/"
                if url == "//":
                    url = "/"
        section = parts[0] if len(parts) > 1 else ""
        title_m = TITLE_RE.search(content)
        desc_m = DESC_RE.search(content)
        h1_m = H1_RE.search(content)
        title = _clean(title_m.group(1)) if title_m else url
        tags: list[str] = []
        ht_m = HASHTAGS_RE.search(content)
        if ht_m:
            tags.extend(t.strip() for t in ht_m.group(1).split(",") if t.strip())
        for t in SECTION_TAGS.get(section, []):
            if t not in tags:
                tags.append(t)
        type_tag = f"#{section.replace('-', '')}" if section else "#home"
        if type_tag not in tags and section:
            tags.append(type_tag)
        entries.append({
            "title": title.split("|")[0].strip(),
            "description": (_clean(desc_m.group(1)) if desc_m else "")[:200],
            "h1": (_clean(h1_m.group(1)) if h1_m else title)[:120],
            "url": url,
            "section": section,
            "type": section.replace("-", " ").title() or "Página",
            "hashtags": tags,
        })
    return entries


def _section_of_rel(rel: str) -> str:
    parts = Path(rel.replace("\\", "/")).parts
    return parts[0] if len(parts) > 1 else ""


def generate_sitemap_locale(out_dir: Path, html_pages: list[str], *, prefix: str = "",
                            lastmod: str | None = None) -> Path:
    """Write sitemap.xml with xhtml:hreflang alternates per URL."""
    lastmod = lastmod or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rows: list[str] = []
    seen: set[str] = set()

    for rel in sorted(set(html_pages)):
        canon_path = _canonical_path_from_rel(rel)
        loc = absolute_url(canon_path, prefix)
        if loc in seen:
            continue
        seen.add(loc)
        section = _section_of_rel(rel)
        priority = SECTION_PRIORITY.get(section, 0.6)
        changefreq = SECTION_CHANGEFREQ.get(section, "monthly")
        alts = [
            f'    <xhtml:link rel="alternate" hreflang="{hl}" href="{xml_escape(absolute_url(canon_path, lp))}"/>'
            for lp, hl, *_ in LOCALES
        ]
        alts.append(
            f'    <xhtml:link rel="alternate" hreflang="x-default" href="{xml_escape(absolute_url(canon_path))}"/>'
        )
        rows.append(
            "  <url>\n"
            f"    <loc>{xml_escape(loc)}</loc>\n"
            f"    <lastmod>{lastmod}</lastmod>\n"
            f"    <changefreq>{changefreq}</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            + "\n".join(alts) + "\n"
            "  </url>"
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(rows)
        + "\n</urlset>\n"
    )
    target = out_dir if not prefix else out_dir / prefix
    target.mkdir(parents=True, exist_ok=True)
    path = target / "sitemap.xml"
    path.write_text(xml, encoding="utf-8", newline="\n")
    return path


def finalize_post_build_seo(
    out_dir: Path,
    html_pages: list[str],
    *,
    build_locales: bool = True,
) -> dict:
    """Generate search index, sitemaps (with hreflang), robots, RSS from built HTML."""
    entries = scan_search_index(out_dir)
    write_search_index(out_dir, entries)

    generate_sitemap_locale(out_dir, html_pages, prefix="")
    prefixes = [""]
    if build_locales:
        for prefix, *_ in LOCALES:
            if prefix:
                generate_sitemap_locale(out_dir, html_pages, prefix=prefix)
                prefixes.append(prefix)

    generate_sitemap_index(out_dir, prefixes)
    generate_robots(out_dir)

    feed_items = [
        {"title": e["title"], "path": e["url"], "description": e.get("description", "")}
        for e in entries
        if e.get("section") in ("ferramentas", "calculadoras", "escalas", "medicamentos", "protocolos", "artigos")
    ][:30]
    if not feed_items:
        feed_items = [{"title": e["title"], "path": e["url"], "description": e.get("description", "")} for e in entries[:15]]
    generate_feed(out_dir, feed_items)

    return {"search_entries": len(entries), "feed_items": len(feed_items), "locales": len(prefixes)}
