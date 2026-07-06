"""Shared HTML website builder — maximum reuse for Calculadoras de Enfermagem static site generation."""
from __future__ import annotations

import html
import json
import re
import shutil
from contextvars import ContextVar
from pathlib import Path
from typing import Any

from menu_data import FOOTER_LINKS, MAIN_NAV_ITEMS, MEGA_MENU_ASIDE, MEGA_POPULAR_LOCALES, ROUTE_ALIASES
from chrome_content_lib import get_shell

_chrome = get_shell()
_brand = _chrome["brand"]

SITE_NAME = _brand["site_name"]
LOCALE = "pt-BR"
LANG = "pt-BR"

_DEFAULT_RENDER_LOCALE = {
    "lang": "pt-BR",
    "locale": "pt-BR",
    "direction": "ltr",
    "url_prefix": "",
    "skip_label": "Pular para o conteúdo principal",
}
_render_locale: ContextVar[dict[str, str]] = ContextVar("render_locale", default=_DEFAULT_RENDER_LOCALE.copy())


class render_locale_ctx:
    """Thread-safe locale context for parallel locale builds."""

    def __init__(
        self,
        *,
        lang: str,
        locale: str,
        direction: str = "ltr",
        url_prefix: str = "",
        skip_label: str | None = None,
    ) -> None:
        self._state = {
            "lang": lang,
            "locale": locale,
            "direction": direction,
            "url_prefix": url_prefix,
            "skip_label": skip_label or _DEFAULT_RENDER_LOCALE["skip_label"],
        }
        self._token = None

    def __enter__(self) -> "render_locale_ctx":
        self._token = _render_locale.set(self._state)
        return self

    def __exit__(self, *exc: object) -> None:
        if self._token is not None:
            _render_locale.reset(self._token)


def get_render_locale() -> dict[str, str]:
    return _render_locale.get()

ASSETS_SRC = Path(__file__).resolve().parents[1] / "website" / "assets"

BRAND = _brand["assets"]
THEME_COLOR = _brand["theme_color"]
BRAND_FRAMEWORK = _brand["framework"]


def brand_text(text: Any) -> str:
    """Normalize legacy NKOS branding in user-facing copy."""
    if text is None:
        return ""
    s = str(text)
    s = s.replace("NKOS 2026", BRAND_FRAMEWORK)
    s = s.replace("NKOS2026", "CalculadorasEnfermagem")
    s = re.sub(r"\bNKOS\b", SITE_NAME, s)
    return s


def esc(text: Any) -> str:
    return html.escape(str(text) if text is not None else "", quote=True)


def slugify(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", (text or "").lower()).strip("-")
    return s or "item"


def unique_tool_slug(tool: dict, used: set[str]) -> str:
    """Stable URL slug; disambiguates acronym collisions via tool_id."""
    base = slugify(tool.get("acronym") or tool["tool_code"].replace("TOOL.", ""))
    if base not in used:
        used.add(base)
        return base
    disambig = f"{base}-{tool.get('tool_id', tool.get('tool_code', 'x'))}"
    used.add(disambig)
    return disambig


def tool_page_href(slug: str, hub: str = "sibling") -> str:
    """hub: root | ferramentas | sibling (other section at depth 1)."""
    if hub == "root":
        return f"ferramentas/{slug}/index.html"
    if hub == "ferramentas":
        return f"{slug}/index.html"
    return f"../ferramentas/{slug}/index.html"


def rel_prefix(depth: int) -> str:
    return "../" * depth if depth else ""


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def route_href(route: str, depth: int) -> str:
    """Convert React route (/missao) to relative static HTML path."""
    route = (route or "/").strip()
    if route in ROUTE_ALIASES:
        route = "/" + ROUTE_ALIASES[route]
    slug = route.strip("/")
    if not slug:
        return rel_prefix(depth) + "index.html"
    return rel_prefix(depth) + f"{slug}/index.html"


def asset_href(depth: int, *parts: str) -> str:
    return rel_prefix(depth) + "assets/" + "/".join(parts)


def image_href(depth: int, filename: str) -> str:
    """Path under ``assets/images/``. Accepts a bare filename or a nested path."""
    name = (filename or "").lstrip("/")
    if name.startswith("images/"):
        return rel_prefix(depth) + "assets/" + name
    return asset_href(depth, "images", name)


def og_image_href(depth: int, canonical_path: str | None = None) -> str:
    """Resolve OG asset from VEIP manifest, else brand logo fallback."""
    try:
        from pathlib import Path
        import json

        manifest_path = Path(__file__).resolve().parent.parent / "datasets/master-data/visual-intelligence/og_manifest.json"
        if manifest_path.exists() and canonical_path:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            entry = manifest.get("entries", {}).get(canonical_path.rstrip("/") or "/")
            if entry:
                asset = entry.get("jpg") or entry.get("asset") or entry.get("svg")
                if asset:
                    return image_href(depth, asset)
    except (OSError, json.JSONDecodeError, KeyError):
        pass
    return image_href(depth, BRAND["logo_header"])


def render_head_assets(
    depth: int,
    title: str,
    description: str,
    *,
    canonical_path: str | None = None,
    og_image: str | None = None,
    og_width: int = 1200,
    og_height: int = 630,
) -> str:
    """Favicon + social preview — VEIP OG or assets/images/logotipo_website.webp."""
    favicon = image_href(depth, BRAND["favicon"])
    if og_image:
        og = og_image if og_image.startswith("http") else image_href(depth, og_image)
    else:
        og = og_image_href(depth, canonical_path)
    return f"""
  <meta name="theme-color" content="{esc(THEME_COLOR)}">
  <link rel="icon" type="image/x-icon" href="{esc(favicon)}">
  <meta property="og:image" content="{esc(og)}">
  <meta property="og:image:width" content="{og_width}">
  <meta property="og:image:height" content="{og_height}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{esc(og)}">"""


def copy_static_assets(out_dir: Path, *, use_minified: bool = False) -> None:
    """Copy website/assets → output. Optionally prefer *.min.css / *.min.js."""
    dst = out_dir / "assets"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(ASSETS_SRC, dst)

    if not use_minified:
        return

    for ext in (".css", ".js"):
        for mini in list(dst.rglob(f"*.min{ext}")):
            base = mini.parent / mini.name.replace(f".min{ext}", ext)
            if base.exists():
                base.write_bytes(mini.read_bytes())
            mini.unlink()


def _svg_icon(name: str) -> str:
    from icons_lib import lucide_icon

    extra = "site-nav__chevron" if name == "chevron" else ""
    return lucide_icon(name, css_class=extra)


def render_breadcrumbs(items: list[tuple[str, str | None]], depth: int) -> str:
    parts = [f'<a href="{esc(rel_prefix(depth))}index.html">Início</a>']
    for label, href in items:
        if href:
            if not href.startswith(("../", "http", "/")):
                href = rel_prefix(depth) + href
            parts.append(f'<a href="{esc(href)}">{esc(label)}</a>')
        else:
            parts.append(f'<span aria-current="page">{esc(label)}</span>')
    sep = '<span class="breadcrumb__sep" aria-hidden="true"> &gt; </span>'
    return f'<nav class="breadcrumb" aria-label="Breadcrumb">{sep.join(parts)}</nav>'


def _render_mega_category(cat: dict, depth: int) -> str:
    links = "".join(
        f'<a class="mega-menu__link" href="{esc(route_href(item["href"], depth))}">{esc(item["label"])}</a>'
        for item in cat.get("items", [])
    )
    count = f'<span class="mega-menu__count">{esc(cat["count"])}</span>' if cat.get("count") else ""
    return f"""
<div class="mega-menu__col-block">
  <h3 class="mega-menu__category-title">{esc(cat["title"])}{count}</h3>
  {links}
</div>"""


def _render_mega_aside(nav_label: str, depth: int) -> str:
    from flags_lib import flag_asset_path
    from icons_lib import lucide_icon

    meta = MEGA_MENU_ASIDE.get(nav_label, {})
    img_src = image_href(depth, meta.get("image", "homepage-hero.webp"))
    featured_title = esc(meta.get("featured_title", "Destaques"))
    featured = "".join(
        f'<a class="mega-menu__featured-link" href="{esc(route_href(item["href"], depth))}">{esc(item["label"])}</a>'
        for item in meta.get("featured", [])
    )
    locale_buttons = []
    for code in MEGA_POPULAR_LOCALES:
        cc = code.split("-", 1)[-1]
        flag_src = image_href(depth, flag_asset_path(cc))
        locale_buttons.append(
            f'<button type="button" class="locale-option locale-option--compact" role="option" '
            f'data-locale-code="{esc(code)}" data-country-code="{esc(cc)}" aria-label="{esc(code)}">'
            f'<span class="locale-option__flag" aria-hidden="true">'
            f'<img class="locale-flag-img locale-option__flag-img" src="{esc(flag_src)}" alt="" width="20" height="15" loading="lazy" decoding="async">'
            f"</span>"
            f'<span class="locale-option__text">{esc(code.replace("-", " · "))}</span>'
            f"</button>"
        )
    locale_codes = "".join(locale_buttons)
    locales_title = get_shell()["header"]["locale_panels"]["mega_aside_locales_title"]
    return f"""
<aside class="mega-menu__aside" aria-label="Destaques e idiomas">
  <img class="mega-menu__aside-img" src="{esc(img_src)}" alt="{esc(meta.get("image_alt", ""))}" width="280" height="160" loading="lazy">
  <div class="mega-menu__featured">
    <h4 class="mega-menu__featured-title">{featured_title}</h4>
    {featured}
  </div>
  <div class="mega-menu__locale">
    <h4 class="mega-menu__featured-title">{lucide_icon("globe", size="16")}<span>{esc(locales_title)}</span></h4>
    <div class="mega-menu__locale-list">{locale_codes}</div>
  </div>
</aside>"""


def render_mega_menu(categories: list[dict], depth: int, *, nav_label: str = "") -> str:
    if not categories:
        return ""
    split = max(1, (len(categories) + 1) // 2)
    col1 = "".join(_render_mega_category(cat, depth) for cat in categories[:split])
    col2 = "".join(_render_mega_category(cat, depth) for cat in categories[split:])
    aside = _render_mega_aside(nav_label, depth) if nav_label else ""
    return f"""<div class="mega-menu"><div class="mega-menu__inner section-container"><div class="mega-menu__layout"><div class="mega-menu__col">{col1}</div><div class="mega-menu__col">{col2}</div>{aside}</div></div></div>"""


def render_header(depth: int) -> str:
    home = route_href("/", depth)
    logo_src = image_href(depth, BRAND["logo_header"])

    nav_items = []
    for item in MAIN_NAV_ITEMS:
        chevron = _svg_icon("chevron") if item.get("children") else ""
        menu_attr = ' data-menu="true"' if item.get("children") else ""
        mega = render_mega_menu(item["children"], depth, nav_label=item["label"]) if item.get("children") else ""
        nav_items.append(f"""
<div class="site-nav__item"{menu_attr}>
  <a class="site-nav__link" href="{esc(route_href(item["href"], depth))}">{esc(item["label"])}{chevron}</a>
  {mega}
</div>""")

    mobile_nav = []
    for item in MAIN_NAV_ITEMS:
        if not item.get("children"):
            mobile_nav.append(
                f'<a class="mobile-nav__link" href="{esc(route_href(item["href"], depth))}">{esc(item["label"])}</a>'
            )
            continue
        sub = []
        for cat in item["children"]:
            sub.append(f'<div class="mobile-nav__cat">{esc(cat["title"])}</div>')
            for link in cat.get("items", []):
                sub.append(f'<a class="mobile-nav__link" href="{esc(route_href(link["href"], depth))}">{esc(link["label"])}</a>')
        mobile_nav.append(f"""
<button type="button" class="mobile-nav__toggle" data-mobile-submenu-toggle aria-expanded="false">{esc(item["label"])}{_svg_icon("chevron")}</button>
<div class="mobile-nav__sub">{"".join(sub)}</div>""")

    from chrome_lib import LOCALE_COUNT, render_header_actions, render_header_mega_panels

    return f"""
<header class="site-header" id="site-header" role="banner">
  <div class="section-container site-header__inner">
    <a class="site-logo" href="{esc(home)}">
      <img src="{esc(logo_src)}" alt="{esc(SITE_NAME)} — Logotipo" width="160" height="56" loading="eager" fetchpriority="high" onerror="this.hidden=true">
      <span class="site-logo__text">{esc(SITE_NAME)}</span>
    </a>
    <nav class="site-nav" aria-label="Principal">{"".join(nav_items)}</nav>
    {render_header_actions(depth, country_count=LOCALE_COUNT)}
  </div>
</header>
{render_header_mega_panels(depth, country_count=LOCALE_COUNT)}
<div class="mobile-menu-overlay" aria-hidden="true">
  <div class="mobile-menu-overlay__backdrop"></div>
  <div class="mobile-menu-panel">
    <div class="mobile-auth">
      <a class="btn-outline" href="{esc(route_href("/entrar", depth))}">Entrar</a>
      <a class="btn-primary-sm" href="{esc(route_href("/criar-conta", depth))}">Criar conta</a>
    </div>
    <nav aria-label="Menu mobile">{"".join(mobile_nav)}</nav>
  </div>
</div>"""


def render_footer(depth: int) -> str:
    home = route_href("/", depth)
    logo_src = image_href(depth, BRAND["logo_footer"])
    footer_cfg = get_shell()["footer"]

    def link_list(section: str) -> str:
        return "".join(
            f'<li><a href="{esc(route_href(link["href"], depth))}">{esc(link["label"])}</a></li>'
            for link in FOOTER_LINKS[section]
        )

    from icons_lib import lucide_icon

    social_html = "".join(
        f'<a href="{esc(item["url"])}" target="_blank" rel="noopener noreferrer" aria-label="{esc(item["label"])}">'
        f'{lucide_icon(item["icon"], size="18")}</a>'
        for item in footer_cfg["social"]
    )

    nl = footer_cfg["newsletter"]
    sections = footer_cfg["sections"]

    return f"""
<footer class="site-footer" role="contentinfo">
  <div class="site-footer__main section-container">
    <div class="footer-grid">
      <div class="footer-grid__brand">
        <a class="footer-logo" href="{esc(home)}">
          <img src="{esc(logo_src)}" alt="{esc(SITE_NAME)}" width="160" height="64" loading="lazy" onerror="this.hidden=true">
          <span class="footer-logo__text">{esc(SITE_NAME)}</span>
        </a>
        <div class="footer-social">{social_html}</div>
        <div class="footer-newsletter">
          <h2 class="footer-heading">{esc(nl["title"])}</h2>
          <p>{esc(nl["description"])}</p>
          <form action="#" method="post" data-newsletter-form>
            <input type="email" name="email" placeholder="{esc(nl["email_placeholder"])}" required aria-label="{esc(nl["email_aria"])}">
            <label class="footer-newsletter__consent">
              <input type="checkbox" name="consent" value="1" required aria-required="true">
              <span>{esc(nl["consent_before"])} <a href="{esc(route_href(nl["consent_href"], depth))}">{esc(nl["consent_link"])}</a>.</span>
            </label>
            <button type="submit" class="btn-primary-sm" data-newsletter-submit disabled>{esc(nl["submit"])}</button>
          </form>
        </div>
      </div>
      <div class="footer-grid__col">
        <h2 class="footer-heading">{esc(sections["institucional"])}</h2>
        <ul class="footer-links">{link_list("institucional")}</ul>
      </div>
      <div class="footer-grid__col">
        <h2 class="footer-heading">{esc(sections["recursos"])}</h2>
        <ul class="footer-links">{link_list("recursos")}</ul>
      </div>
      <div class="footer-grid__col">
        <h2 class="footer-heading">{esc(sections["suporte"])}</h2>
        <ul class="footer-links">{link_list("suporte")}</ul>
      </div>
    </div>
  </div>
  <div class="site-footer__bottom">
    <div class="section-container footer-bottom-inner">
      <p class="footer-copy">{esc(footer_cfg["copyright"])}</p>
    </div>
  </div>
</footer>"""


def _category_icon(name: str) -> str:
    icons = {
        "calculator": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="2" width="16" height="20" rx="2"/><path d="M8 6h8M8 10h.01M12 10h.01M16 10h.01M8 14h.01M12 14h.01M16 14h.01M8 18h.01M12 18h.01M16 18h.01"/></svg>',
        "clipboard": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/></svg>',
        "book": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>',
        "chart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>',
        "leaf": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z"/></svg>',
        "document": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/></svg>',
        "users": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
        "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
        "brain": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/></svg>',
        "play": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="m10 8 6 4-6 4V8z"/></svg>',
        "lightbulb": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg>',
        "globe": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
        "pill": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m10.5 20.5 10-10a4.95 4.95 0 1 0-7-7l-10 10a4.95 4.95 0 1 0 7 7Z"/><path d="m8.5 8.5 7 7"/></svg>',
        "message": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
        "hardhat": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 18a1 1 0 0 0 1 1h18a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1H3a1 1 0 0 0-1 1v2Z"/><path d="M10 10V5a2 2 0 0 1 4 0v5"/><path d="M4 15v-3a8 8 0 0 1 16 0v3"/></svg>',
        "file-badge": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><circle cx="12" cy="15" r="3"/></svg>',
        "file-text": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/></svg>',
        "more": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/></svg>',
    }
    return icons.get(name, icons["calculator"])


def _render_home_link_list(links: list[dict], depth: int) -> str:
    items = []
    for link in links:
        href = route_href(link["href"], depth)
        items.append(
            f'<li><a class="home-pillar__link" href="{esc(href)}">'
            f'<span class="home-pillar__link-icon">{_category_icon(link.get("icon", "document"))}</span>'
            f'{esc(link["label"])}</a></li>'
        )
    return f'<ul class="home-pillar__links">{"".join(items)}</ul>'


def _render_home_dashboard(dashboard: dict) -> str:
    bars = "".join(
        f'<div class="home-dashboard__bar" style="--h:{h}"><span></span></div>'
        for h in (45, 62, 78, 55, 88, 72)
    )
    return f"""
<div class="home-dashboard" aria-hidden="true">
  <div class="home-dashboard__head">{esc(dashboard.get("title", "Indicadores"))}</div>
  <div class="home-dashboard__bars">{bars}</div>
  <div class="home-dashboard__metrics">
    <div class="home-dashboard__donut">
      <div class="home-dashboard__donut-ring" style="--pct:92"><span>{esc(dashboard.get("donut_value", "92%"))}</span></div>
      <small>{esc(dashboard.get("donut_label", "Taxa de adesão"))}</small>
    </div>
    <div class="home-dashboard__trend">
      <span class="home-dashboard__trend-value">{esc(dashboard.get("trend_value", "-18%"))}</span>
      <small>{esc(dashboard.get("trend_label", "Eventos adversos"))}</small>
    </div>
  </div>
</div>"""


def _module_slug_from_href(href: str) -> str:
    clean = href.strip("/").split("?")[0]
    if clean.startswith("../"):
        clean = clean.split("../")[-1]
    return clean.split("/")[0] if clean else "ferramentas"


def _render_home_pillar(block: dict, *, depth: int, variant: str) -> str:
    links_html = _render_home_link_list(block.get("links", []), depth)
    cta = block.get("cta", {})
    cta_href = route_href(cta.get("href", "/"), depth)
    visual = ""
    if variant == "education":
        img = image_href(depth, block.get("image", "homepage-section-001.webp"))
        alt = esc(block.get("image_alt", ""))
        badge = block.get("badge") or {}
        badge_href = route_href(badge.get("href", "/simulados"), depth)
        badge_btn = esc(badge.get("button_label", "Acessar"))
        badge_html = ""
        if badge:
            from icons_lib import lucide_icon

            badge_body = f'<strong>{esc(badge.get("title", ""))}</strong>'
            if badge.get("subtitle"):
                badge_body += f'<span>{esc(badge.get("subtitle", ""))}</span>'
            badge_html = f"""
  <div class="home-pillar__badge">
    <div class="home-pillar__badge-main">
      <span class="home-pillar__badge-icon">{lucide_icon("graduation-cap", size="18")}</span>
      <span class="home-pillar__badge-text">{badge_body}</span>
    </div>
    <a class="home-pillar__badge-btn btn-primary-sm" href="{esc(badge_href)}">{badge_btn}</a>
  </div>"""
        visual = f"""
<div class="home-pillar__visual home-pillar__visual--photo">
  <img src="{esc(img)}" alt="{alt}" width="280" height="220" loading="lazy">
  {badge_html}
</div>"""
    elif variant == "management":
        if block.get("dashboard"):
            visual = f'<div class="home-pillar__visual home-pillar__visual--dashboard">{_render_home_dashboard(block.get("dashboard", {}))}</div>'
        elif block.get("image"):
            img = image_href(depth, block["image"])
            alt = esc(block.get("image_alt", ""))
            visual = f"""
<div class="home-pillar__visual home-pillar__visual--photo">
  <img src="{esc(img)}" alt="{alt}" width="280" height="220" loading="lazy">
</div>"""

    section_attr = 'education' if variant == 'education' else 'management'
    return f"""
<article class="home-pillar home-pillar--{variant}" data-ce-profile-section="{section_attr}">
  <div class="home-pillar__body">
    <h2 class="home-pillar__title">{esc(block.get("title", ""))}</h2>
    <p class="home-pillar__subtitle">{esc(block.get("subtitle", ""))}</p>
    {links_html}
    <a class="home-pillar__cta" href="{esc(cta_href)}">{esc(cta.get("label", "Saiba mais"))} →</a>
  </div>
  {visual}
</article>"""


def _render_home_global_section(section: dict, *, depth: int) -> str:
    cta = section.get("cta", {})
    cta_href = route_href(cta.get("href", "/historia"), depth)
    stats_html = "".join(
        f'<div class="home-global__stat">'
        f'<span class="home-global__stat-icon">{_category_icon(s.get("icon", "globe"))}</span>'
        f'<strong>{esc(s["value"])}</strong>'
        f'<span>{esc(s["label"])}</span></div>'
        for s in section.get("stats", [])
    )
    comm = section.get("community") or {}
    comm_href = route_href(comm.get("href", "/forum"), depth)
    avatars = "".join(
        f'<span class="home-community__avatar" aria-hidden="true">{esc(initials)}</span>'
        for initials in comm.get("avatars", ["A", "B", "C", "D"])
    )
    if comm.get("image"):
        side_img = image_href(depth, comm["image"])
        side_alt = esc(comm.get("image_alt", ""))
        map_html = f"""
    <div class="home-global__side-media">
      <img src="{esc(side_img)}" alt="{side_alt}" width="320" height="240" loading="lazy">
    </div>"""
    else:
        map_html = """
    <div class="home-global__map" aria-hidden="true">
      <svg class="home-global__map-svg" viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="400" cy="200" rx="360" ry="170" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.25"/>
        <ellipse cx="400" cy="200" rx="280" ry="130" fill="none" stroke="currentColor" stroke-width="1" opacity="0.2"/>
        <circle cx="220" cy="160" r="6" fill="currentColor"/><circle cx="380" cy="140" r="6" fill="currentColor"/>
        <circle cx="520" cy="180" r="6" fill="currentColor"/><circle cx="610" cy="220" r="6" fill="currentColor"/>
        <circle cx="300" cy="240" r="6" fill="currentColor"/>
      </svg>
    </div>"""
    community_html = f"""
<aside class="home-community">
  <h3>{esc(comm.get("title", "Comunidade ativa"))}</h3>
  <p>{esc(comm.get("description", ""))}</p>
  <div class="home-community__social">
    <div class="home-community__avatars">{avatars}</div>
    <span class="home-community__count">{esc(comm.get("members_label", "+12k"))}</span>
  </div>
  <a class="home-community__link" href="{esc(comm_href)}">Entrar no fórum →</a>
</aside>"""
    return f"""
<section class="home-global" aria-labelledby="home-global-title">
  <div class="section-container home-global__grid">
    <div class="home-global__content">
      <h2 id="home-global-title">{esc(section.get("title", ""))}</h2>
      <p>{esc(section.get("description", ""))}</p>
      <a class="home-global__cta" href="{esc(cta_href)}">{esc(cta.get("label", "Nossa jornada"))} →</a>
    </div>
    <div class="home-global__stats">{stats_html}</div>
    {map_html}
    {community_html}
  </div>
</section>"""


def _render_daily_tip_card(config: dict, *, depth: int) -> str:
    badge = esc(config.get("badge", "Dica do dia"))
    more_label = esc(config.get("more_label", "Ver mais dicas"))
    more_href = esc(route_href(config.get("more_href", "/dicas"), depth))
    return f"""
<aside class="home-daily-tip" data-daily-tip aria-labelledby="home-daily-tip-title">
  <div class="home-daily-tip__head">
    <span class="home-daily-tip__badge">{badge}</span>
    <time class="home-daily-tip__date" data-daily-tip-date datetime=""></time>
  </div>
  <div class="home-daily-tip__body">
    <div class="home-daily-tip__icon" data-daily-tip-icon aria-hidden="true"></div>
    <div>
      <h2 id="home-daily-tip-title" class="home-daily-tip__title" data-daily-tip-title></h2>
      <p class="home-daily-tip__text" data-daily-tip-text></p>
    </div>
  </div>
  <a class="home-daily-tip__link" href="{more_href}" data-daily-tip-more>{more_label} →</a>
</aside>"""


def _render_tool_ecosystem_section(section: dict, *, depth: int) -> str:
    cards = ""
    for item in section.get("items", []):
        href = route_href(item.get("href", "/ferramentas"), depth)
        mod = _module_slug_from_href(item.get("href", "/ferramentas"))
        cards += f"""
<a class="home-eco-card" href="{esc(href)}" data-ce-profile-module="{esc(mod)}">
  <span class="home-eco-card__icon">{_category_icon(item.get("icon", "calculator"))}</span>
  <span class="home-eco-card__label">{esc(item["title"])}</span>
</a>"""
    if not cards:
        return ""
    return f"""
<section class="home-ecosystem" data-ce-profile-section="ecosystem" aria-labelledby="home-ecosystem-title">
  <div class="section-container">
    <div class="home-ecosystem__header">
      <h2 id="home-ecosystem-title">{esc(section.get("title", "Ecossistema"))}</h2>
      <p>{esc(section.get("subtitle", ""))}</p>
    </div>
    <div class="home-ecosystem__grid">{cards}</div>
  </div>
</section>"""


def render_document(
    *,
    depth: int,
    title: str,
    description: str,
    canonical_path: str,
    main_html: str,
    og_type: str = "website",
    og_image: str | None = None,
    extra_css: list[str] | None = None,
    main_class: str = "site-main",
    json_ld: dict | list[dict] | None = None,
    extra_head: str = "",
) -> str:
    ctx = get_render_locale()
    prefix = rel_prefix(depth)
    canon = canonical_path if canonical_path.startswith("/") else f"/{canonical_path}"
    css = [
        f"{prefix}assets/css/tokens.css",
        f"{prefix}assets/css/layout.css",
        f"{prefix}assets/css/chrome.css",
    ]
    if extra_css:
        css.extend(extra_css)
    css_links = "\n  ".join(f'<link rel="stylesheet" href="{esc(h)}">' for h in css)
    from seo_lib import head_seo

    seo_block = head_seo(
        title, description, canon,
        locale_prefix=ctx["url_prefix"],
        og_type=og_type,
        json_ld=json_ld,
    )
    from chrome_partials import render_chrome_footer_mount, render_chrome_mounts
    from marketing_lib import render_marketing_head, render_marketing_body, render_marketing_ad_rail

    marketing_head = render_marketing_head()
    marketing_body = render_marketing_body(depth)
    marketing_rail = render_marketing_ad_rail()

    return f"""<!DOCTYPE html>
<html lang="{esc(ctx['lang'])}" dir="{esc(ctx['direction'])}" data-ce-prefix="{esc(prefix)}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  {marketing_head}
  <meta name="ce-asset-prefix" content="{esc(prefix)}">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:type" content="{esc(og_type)}">
  <meta property="og:locale" content="{esc(ctx['locale'])}">
  {seo_block}
  {render_head_assets(depth, title, description, canonical_path=canonical_path, og_image=og_image)}
  {css_links}
  {extra_head}
</head>
<body>
<div class="site-shell">
  <a class="skip-link" href="#main-content">{esc(ctx['skip_label'])}</a>
  {render_chrome_mounts(depth)}
  <main id="main-content" class="{esc(main_class)}" tabindex="-1">
    {main_html}
  </main>
  {marketing_rail}
  {render_chrome_footer_mount(depth)}
</div>
{marketing_body}
  <script src="{esc(prefix)}assets/js/chrome-templates.js"></script>
  <script src="{esc(prefix)}assets/js/chrome-loader.js" defer></script>
  <script src="{esc(prefix)}assets/js/user-profile.js" defer></script>
  <script src="{esc(prefix)}assets/js/site.js" defer></script>
</body>
</html>"""


def _home_schema_ge(home: dict, major: int, minor: int, patch: int) -> bool:
    v = home.get("schema_version", "2026.1.0")
    try:
        parts = [int(p) for p in str(v).split(".")[:3]]
        while len(parts) < 3:
            parts.append(0)
        return tuple(parts) >= (major, minor, patch)
    except ValueError:
        return False


def render_home_page(
    home: dict,
    *,
    depth: int,
    title: str,
    description: str,
    slug_map: dict[str, str],
    daily_tips: dict | None = None,
    canonical_path: str = "/",
) -> str:
    if _home_schema_ge(home, 2026, 3, 0):
        from home_render_v203 import render_home_page_v203

        return render_home_page_v203(
            home,
            depth=depth,
            title=title,
            description=description,
            slug_map=slug_map,
            daily_tips=daily_tips,
            canonical_path=canonical_path,
        )

    hero = home["hero"]
    search = home["search"]
    hero_img = image_href(depth, hero.get("image", "homepage-hero.webp"))
    hero_alt = esc(hero.get("image_alt", "Profissional de enfermagem em ambiente clínico"))
    bg = hero.get("background") or {}
    hero_style = ""
    if bg:
        cs = esc(bg.get("color_start", "#002d62"))
        cm = esc(bg.get("color_mid", "#0a1628"))
        ce = esc(bg.get("color_end", "#334e68"))
        hero_style = f' style="--home-hero-bg-start:{cs};--home-hero-bg-mid:{cm};--home-hero-bg-end:{ce};"'

    title_html = esc(hero["title"])
    if hero.get("title_accent"):
        title_html += f' <span class="home-hero__title-accent">{esc(hero["title_accent"])}</span>'

    stats_html = "".join(
        f'<div class="home-stat"><div class="home-stat__value">{esc(s["value"])}</div>'
        f'<div class="home-stat__label">{esc(s["label"])}</div></div>'
        for s in hero.get("stats", [])
    )

    categories_html = ""
    for cat in home.get("categories", []):
        href = route_href(cat["href"], depth)
        categories_html += f"""
<article class="home-category" data-ce-profile-module="{esc(_module_slug_from_href(cat["href"]))}">
  <div class="home-category__icon">{_category_icon(cat.get("icon", "calculator"))}</div>
  <h3 class="home-category__title">{esc(cat["title"])}</h3>
  <p class="home-category__text">{esc(cat["description"])}</p>
  <a class="home-category__link" href="{esc(href)}">{esc(cat["link_label"])} →</a>
</article>"""

    featured = home.get("featured", {})
    featured_cards = ""
    for item in featured.get("items", []):
        if item.get("tool_code") and item["tool_code"] in slug_map:
            href = tool_page_href(slug_map[item["tool_code"]], "root")
        else:
            href = route_href(item.get("href", "/ferramentas"), depth)
        code_attr = f' data-ce-tool-code="{esc(item["tool_code"])}"' if item.get("tool_code") else ""
        featured_cards += f"""
<article class="home-tool-card"{code_attr}>
  <h3>{esc(item["title"])}</h3>
  <p>{esc(item["description"])}</p>
  <a class="home-tool-card__action" href="{esc(href)}">{esc(item["action_label"])}</a>
</article>"""

    cta_primary = hero.get("cta_primary", {})
    cta_secondary = hero.get("cta_secondary", {})
    actions_html = ""
    if cta_primary:
        actions_html += f'<a class="btn-primary-lg" href="{esc(route_href(cta_primary.get("href", "/ferramentas"), depth))}">{esc(cta_primary.get("label", "Explorar"))} →</a>'
    if cta_secondary:
        actions_html += f'<a class="btn-outline-lg" href="{esc(route_href(cta_secondary.get("href", "/sobre"), depth))}">{esc(cta_secondary.get("label", "Conhecer"))}</a>'

    solutions_html = ""
    sol = home.get("solutions")
    if sol:
        sol_cards = ""
        for item in sol.get("items", []):
            sol_cards += f"""
<article class="home-category">
  <div class="home-category__icon">{_category_icon(item.get("icon", "leaf"))}</div>
  <h3 class="home-category__title">{esc(item["title"])}</h3>
  <p class="home-category__text">{esc(item["description"])}</p>
  <a class="home-category__link" href="{esc(route_href(item["href"], depth))}">Saiba mais →</a>
</article>"""
        solutions_html = f"""
<section class="home-solutions" aria-labelledby="home-solutions-title">
  <div class="section-container">
    <div class="home-solutions__header">
      <h2 id="home-solutions-title">{esc(sol.get("title", "Soluções"))}</h2>
      <p>{esc(sol.get("subtitle", ""))}</p>
    </div>
    <div class="home-solutions__grid">{sol_cards}</div>
  </div>
</section>"""

    pillars_html = ""
    edu = home.get("education_block")
    mgmt = home.get("management_block")
    if edu or mgmt:
        pillar_cards = ""
        if edu:
            pillar_cards += _render_home_pillar(edu, depth=depth, variant="education")
        if mgmt:
            pillar_cards += _render_home_pillar(mgmt, depth=depth, variant="management")
        pillars_html = f"""
<section class="home-pillars" aria-label="Educação e gestão">
  <div class="section-container home-pillars__grid">{pillar_cards}</div>
</section>"""

    global_html = ""
    if home.get("global_platform"):
        global_html = _render_home_global_section(home["global_platform"], depth=depth)

    daily_tip_cfg = home.get("daily_tip") or {}
    daily_tip_html = _render_daily_tip_card(daily_tip_cfg, depth=depth) if daily_tips else ""

    tips_payload: dict[str, Any] = {"tips": [], "slug_map": slug_map}
    if daily_tips:
        tips_list = []
        for tip in daily_tips.get("tips", []):
            entry = dict(tip)
            code = entry.pop("tool_code", None)
            if code and code in slug_map:
                entry["tool_slug"] = slug_map[code]
            tips_list.append(entry)
        tips_payload = {
            "tips": tips_list,
            "more_link": daily_tips.get("more_link") or {},
        }
    tips_json = json.dumps(tips_payload, ensure_ascii=False).replace("<", "\\u003c")

    ecosystem_html = ""
    eco = home.get("tool_ecosystem")
    if eco:
        ecosystem_html = _render_tool_ecosystem_section(eco, depth=depth)

    prefix = rel_prefix(depth)
    main = f"""
<section class="home-hero"{hero_style} aria-labelledby="home-hero-title">
  <div class="section-container home-hero__grid">
    <div class="home-hero__content">
      <h1 id="home-hero-title" class="home-hero__title">{title_html}</h1>
      <p class="home-hero__subtitle" data-ce-profile-hero-subtitle>{esc(hero["subtitle"])}</p>
      <div class="home-hero__stats">{stats_html}</div>
      {f'<div class="home-hero__actions">{actions_html}</div>' if actions_html else ''}
    </div>
    <div class="home-hero__media">
      {daily_tip_html}
      <img src="{esc(hero_img)}" alt="{hero_alt}" width="480" height="420" loading="eager" decoding="async">
    </div>
  </div>
</section>
<div class="home-search-wrap">
  <div class="section-container">
    <form class="home-search" role="search" data-home-search>
      <label class="home-search__label" for="home-search-input" data-ce-profile-search-label>{esc(search["label"])}</label>
      <div class="home-search__row">
        <div class="home-search__input-wrap">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          <input id="home-search-input" type="search" name="q" placeholder="{esc(search["placeholder"])}" autocomplete="off" data-home-search-input data-ce-profile-search-input>
        </div>
        <button type="submit" class="home-search__btn">{esc(search["button"])}</button>
      </div>
      <div class="home-search__results" data-home-search-results aria-live="polite"></div>
    </form>
    <div class="ce-profile-strip" data-ce-profile-strip hidden>
      <span data-ce-profile-strip-label></span>
      <div class="ce-profile-strip__links" data-ce-profile-quick-links></div>
      <button type="button" class="ce-profile-strip__change" data-profile-change>Alterar perfil</button>
    </div>
  </div>
</div>
{solutions_html}
{ecosystem_html}
<section class="home-section" aria-labelledby="home-categories">
  <div class="section-container">
    <div class="home-categories" id="home-categories">{categories_html}</div>
  </div>
</section>
<section class="home-section" data-ce-profile-section="featured" aria-labelledby="home-featured-title">
  <div class="section-container">
    <div class="home-featured-header">
      <h2 id="home-featured-title">{esc(featured.get("title", "Mais utilizadas"))}</h2>
      <a href="{esc(route_href(featured.get("view_all_href", "/ferramentas"), depth))}">{esc(featured.get("view_all_label", "Ver todas"))} →</a>
    </div>
    <div class="home-featured-grid">{featured_cards}</div>
  </div>
</section>{pillars_html}{global_html}
<script type="application/json" id="daily-tips-data">{tips_json}</script>"""

    return render_document(
        depth=depth,
        title=title,
        description=description,
        canonical_path=canonical_path,
        main_html=main,
        extra_css=[f"{prefix}assets/css/home.css", f"{prefix}assets/css/institutional.css"],
        main_class="site-main home-main",
    )


def render_page(
    *,
    depth: int,
    title: str,
    description: str,
    canonical_path: str,
    hero_title: str,
    hero_subtitle: str,
    breadcrumbs: list[tuple[str, str | None]],
    body: str,
    og_type: str = "website",
    json_ld: dict | list[dict] | None = None,
) -> str:
    body_block = f"""
    <div class="page-hero">
      <div class="section-container">
        <h1>{esc(hero_title)}</h1>
        <p>{esc(hero_subtitle)}</p>
      </div>
    </div>
    <div class="section-container">
      {render_breadcrumbs(breadcrumbs, depth)}
    </div>
    {body}"""
    return render_document(
        depth=depth,
        title=title,
        description=description,
        canonical_path=canonical_path,
        main_html=body_block,
        og_type=og_type,
        json_ld=json_ld,
    )


def render_hub_section(title: str, cards: list[tuple[str, str, str, str]]) -> str:
    """Reusable hub grid: (title, description, badge, href)."""
    items = []
    for ct, desc, badge, href in cards:
        items.append(f"""
<article class="card">
  <span class="badge">{esc(badge)}</span>
  <h3><a href="{esc(href)}">{esc(ct)}</a></h3>
  <p>{esc(desc)}</p>
</article>""")
    return f"""
<section class="section section-container" aria-labelledby="{esc(slugify(title))}">
  <h2 id="{esc(slugify(title))}">{esc(title)}</h2>
  <div class="card-grid">{"".join(items)}</div>
</section>"""


def render_list_section(title: str, rows: list[tuple[str, str]]) -> str:
    lis = "".join(f"<li><strong>{esc(a)}</strong> — {esc(b)}</li>" for a, b in rows[:200])
    extra = f"<li><em>… e mais {len(rows) - 200} registros na plataforma.</em></li>" if len(rows) > 200 else ""
    return f"""
<section class="section section-container">
  <h2>{esc(title)}</h2>
  <ul class="meta-list">{lis}{extra}</ul>
</section>"""


def render_tool_page(tool: dict, definition: dict | None, depth: int, path_slug: str) -> str:
    acronym = tool.get("acronym") or tool["tool_code"].replace("TOOL.", "")
    params_html = ""
    if definition and definition.get("parameters"):
        fields = []
        for p in definition["parameters"][:8]:
            ptype = p.get("type", "number")
            if ptype == "boolean":
                fields.append(f'<label><input type="checkbox" name="{esc(p["code"])}"> {esc(p.get("label", p["code"]))}</label>')
            elif ptype in ("integer", "number"):
                fields.append(
                    f'<label for="{esc(p["code"])}">{esc(p.get("label", p["code"]))}</label>'
                    f'<input id="{esc(p["code"])}" name="{esc(p["code"])}" type="number" min="{esc(p.get("min", 0))}">'
                )
            else:
                fields.append(f'<label for="{esc(p["code"])}">{esc(p.get("label", p["code"]))}</label><input id="{esc(p["code"])}" name="{esc(p["code"])}" type="text">')
        bands = definition.get("interpretation_bands") or []
        band_rows = "".join(
            f"<li>{esc(b.get('label_pt', ''))}: {esc(b.get('min', ''))}–{esc(b.get('max', ''))} — {esc(b.get('action_pt', ''))}</li>"
            for b in bands[:5]
        )
        params_html = f"""
<section class="section section-container">
  <div class="card">
    <h2>Calculadora — {esc(tool['name'])}</h2>
    <p><strong>Fórmula:</strong> {esc(definition.get('formula', 'N/A'))}</p>
    <form class="tool-form" data-calc-form>
      {''.join(fields)}
      <button class="btn" type="submit">Calcular</button>
      <p data-calc-result aria-live="polite"></p>
    </form>
  </div>
  {f'<h3>Interpretação</h3><ul class="meta-list">{band_rows}</ul>' if band_rows else ''}
</section>"""
    seo_title = f"{tool['name']} ({acronym}) | {SITE_NAME}"
    desc = f"Ferramenta clínica {tool['name']} — Calculadoras de Enfermagem 2026, edição {tool.get('edition', '2026')}."
    body = params_html or f'<section class="section section-container"><div class="card"><p>{esc(desc)}</p></div></section>'
    return render_page(
        depth=depth,
        title=seo_title,
        description=desc,
        canonical_path=f"/ferramentas/{path_slug}",
        hero_title=tool["name"],
        hero_subtitle=f"{acronym} · {tool.get('tool_type', 'clinical')} · {tool.get('category', '')}",
        breadcrumbs=[
            ("Ferramentas", "../index.html" if depth >= 2 else "index.html"),
            (tool["name"], None),
        ],
        body=body,
    )


def write_page(out_dir: Path, rel_path: str, html_content: str) -> Path:
    fp = out_dir / rel_path
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(html_content, encoding="utf-8", newline="\n")
    return fp


def seo_lookup(seo_records: list[dict], path: str, fallback_title: str) -> tuple[str, str]:
    path_norm = path if path.startswith("/") else f"/{path}"
    for r in seo_records:
        if r.get("canonical_path") == path_norm:
            return brand_text(r.get("title", fallback_title)), brand_text(r.get("description", fallback_title))
    for r in seo_records:
        if r.get("canonical_path", "").rstrip("/") == path_norm.rstrip("/"):
            return brand_text(r.get("title", fallback_title)), brand_text(r.get("description", fallback_title))
    return f"{fallback_title} | {SITE_NAME}", f"Conteúdo clínico e educacional — {fallback_title}. {BRAND_FRAMEWORK}."
