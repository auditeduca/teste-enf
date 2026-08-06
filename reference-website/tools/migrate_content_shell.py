# -*- coding: utf-8 -*-
"""
Migra páginas de CONTEÚDO PT-BR para o cluster modular CKO:
  chrome + hero + cko-layout (main + sidebar) + aside

Escalas/calculadoras interativas ficam de fora (PADRAO §escopo).
"""
from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "cko-shell-pages.json"
MENU = ROOT / "menu-global.html"

EXCLUDE_FILES = {
    "index.html",
    "footer.html",
    "menu-global.html",
    "global-body-elements.html",
    "lang-selector.html",
    "404.html",
    "cookies.html",
}

# Heurística: páginas sob menus de conteúdo / biblioteca / simulados / institucionais
CONTENT_HREF_RE = re.compile(
    r'href="(/)?([^"#?]+\.html)"',
    re.I,
)

# Slugs tipicamente calculadora/escala (excluir)
CALC_SLUGS = {
    "imc", "apache", "sofa", "qsofa", "aldrete", "apgar", "asa", "ballard", "barthel",
    "berg", "bishop", "braden", "bps", "cam", "capurro", "cincinnati", "cornell", "cries",
    "curb-65", "gds", "downton", "escalanumerica", "elpo", "flacc", "fast", "four",
    "fugulin", "gosnell", "hamilton", "hendrich", "humpty", "johns", "jouvet", "katz",
    "lachs", "lanss", "lawton", "meem", "meows", "moca", "morse", "news", "nips", "nihss",
    "norton", "ofras", "painad", "pelod", "perroca", "pews", "prism", "ramsay",
    "rancholosamigos", "richmond", "saps", "silverman", "sistema_sinbad", "tinetti",
    "zarit", "waterlow", "downes", "manchester", "gotejamento", "gestacional", "gasometria",
    "balancohidrico", "dimensionamento", "insulina", "medicamentos", "exames_laboratoriais",
    "calculo-de-ferias", "adicional-noturno", "calculo-hora-extra", "calculo-rescisao",
    "calculadoravacina", "classificacao_wifi", "diagnosticosnanda", "sbar",
    "integracoes_calculadora_de_gasometria",
}

SHELL_CSS = (
    '<link href="/css/pages/cart-emergencia.css" rel="stylesheet">\n'
    '<link href="/css/pages/cko-page-shell.css" rel="stylesheet">'
)
SHELL_JS = '<script src="/js/cko-page-shell.js" defer></script>'

RE_BREADCRUMB = re.compile(
    r'<nav[^>]*(?:aria-label="[Bb]readcrumb"|class="breadcrumb")[^>]*>.*?</nav>\s*',
    re.S,
)
RE_TITLE_BAR_HERO = re.compile(
    r'<div class="text-center mb-8">\s*<h1[^>]*>.*?</h1>\s*'
    r'(?:<div class="title-bar[^"]*"></div>\s*)?'
    r'(?:<h2[^>]*>.*?</h2>\s*)?'
    r'</div>\s*',
    re.S,
)
RE_ICON_H1_BLOCK = re.compile(
    r'<div class="flex flex-col items-center[^"]*">\s*'
    r'(?:<!--.*?-->\s*)?'
    r'<div class="flex flex-col md:flex-row[^"]*">\s*'
    r'<img[^>]*>\s*'
    r'<h1[^>]*>.*?</h1>\s*'
    r'</div>\s*'
    r'</div>\s*'
    r'(?:<div class="title-bar[^"]*"></div>\s*)?',
    re.S,
)
RE_HERO_LEGACY = re.compile(
    r'<section class="[^"]*(?:hero-card-navy|meem-card-navy|cko-cart-hero)[^"]*"[^>]*>.*?</section>\s*',
    re.S,
)
RE_LEGACY_SIDEBAR_WRAP = re.compile(
    r'<!--\s*IN[IÍ]CIO DA REESTRUTURAÇÃO COM BARRA LATERAL\s*-->\s*'
    r'<div class="max-w-7xl mx-auto flex flex-col lg:flex-row[^"]*">\s*'
    r'(?:<!--[^>]*-->\s*)?',
    re.S | re.I,
)


def slug_id(filename: str) -> str:
    s = filename.replace(".html", "")
    s = re.sub(r"[^a-zA-Z0-9_-]+", "-", s).strip("-").lower()
    return s[:64] or "page"


def extract_title(html: str, fallback: str) -> str:
    m = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
    if m:
        t = unescape(re.sub(r"\s+", " ", m.group(1))).strip()
        t = re.split(r"\s*\|\s*", t)[0].strip()
        t = re.sub(r"\s*-\s*Calculadoras.*$", "", t, flags=re.I).strip()
        if t:
            return t[:120]
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S | re.I)
    if m:
        t = unescape(re.sub(r"<[^>]+>", "", m.group(1)))
        t = re.sub(r"\s+", " ", t).strip()
        if t:
            return t[:120]
    return fallback


def extract_description(html: str) -> str:
    m = re.search(
        r'<meta[^>]+name="description"[^>]+content="([^"]+)"',
        html,
        re.I,
    )
    if not m:
        m = re.search(
            r'<meta[^>]+content="([^"]+)"[^>]+name="description"',
            html,
            re.I,
        )
    if m:
        return unescape(m.group(1)).strip()[:220]
    return "Conteúdo educativo de enfermagem — adapte ao protocolo e POP da sua instituição."


def collect_content_targets() -> list[Path]:
    """Links do menu (exceto escalas/calculadoras) + bibliotecas + heurística."""
    menu = MENU.read_text(encoding="utf-8", errors="ignore")
    hrefs = set()
    for m in CONTENT_HREF_RE.finditer(menu):
        rel = m.group(2).lstrip("/")
        if "/" in rel:
            # only top-level from menu for mass pass (biblioteca/ handled separately)
            if rel.startswith("biblioteca/"):
                hrefs.add(rel)
            continue
        hrefs.add(rel)

    # Always include top-level content-ish files by name pattern
    for p in ROOT.glob("*.html"):
        name = p.name
        if name in EXCLUDE_FILES:
            continue
        stem = name[:-5].lower()
        if stem in CALC_SLUGS:
            continue
        if any(
            k in stem
            for k in (
                "biblioteca",
                "simulado",
                "protocolo",
                "guia",
                "manual",
                "legisl",
                "teoria",
                "checklist",
                "metas",
                "principio",
                "terminolog",
                "nanda",
                "sinan",
                "notificacao",
                "lista-de-doencas",
                "genograma",
                "paradacardio",
                "resposta-rapida",
                "suporte-avancado",
                "checagem",
                "vigilancia",
                "regrasmedic",
                "nr1",
                "copsoq",
                "entenda",
                "missao",
                "objetivo",
                "politica",
                "termos",
                "mapa-do-site",
                "conteudos",
                "tecnologiaverde",
                "downloads",
                "instrumentais",
                "lei8080",
                "tabelas-vacinas",
                "album",
                "elisabeth",
                "adequar",
            )
        ):
            hrefs.add(name)

    # Force known content
    for name in (
        "time-de-resposta-rapida.html",
        "5-hs-da-paradacardiorespiratoria.html",
        "5-ts-da-paradacardiorespiratoria.html",
        "suporte-avancado-de-vida.html",
        "biblioteca-cirurgica.html",
        "biblioteca-curativo.html",
        "biblioteca-seringa.html",
        "biblioteca-provas.html",
        "biblioteca-carinho-de-emergencia.html",
        "biblioteca/artigo-carrinho-de-emergencia-enfermagem.html",
        "lei8080-sus.html",
        "tabelas-vacinas-crianca.html",
    ):
        hrefs.add(name)

    paths: list[Path] = []
    for rel in sorted(hrefs):
        # skip calc again
        stem = Path(rel).stem.lower()
        if stem in CALC_SLUGS and not rel.startswith("biblioteca"):
            continue
        if Path(rel).name in EXCLUDE_FILES:
            continue
        p = ROOT / rel
        if p.is_file():
            paths.append(p)
    return paths


def ensure_assets(html: str) -> str:
    if "/css/pages/cko-page-shell.css" not in html:
        if 'href="/global-styles.css" rel="stylesheet">' in html:
            html = html.replace(
                'href="/global-styles.css" rel="stylesheet">',
                'href="/global-styles.css" rel="stylesheet">\n' + SHELL_CSS,
                1,
            )
        elif 'href="/public/output.css" rel="stylesheet">' in html:
            html = html.replace(
                'href="/public/output.css" rel="stylesheet">',
                'href="/public/output.css" rel="stylesheet">\n'
                '<link href="/global-styles.css" rel="stylesheet">\n' + SHELL_CSS,
                1,
            )
        else:
            html = html.replace("</head>", SHELL_CSS + "\n</head>", 1)

    if "/js/cko-page-shell.js" not in html:
        if 'src="/lang-selector.js"' in html:
            html = html.replace(
                'src="/lang-selector.js" defer></script>',
                'src="/lang-selector.js" defer></script>\n' + SHELL_JS,
                1,
            )
        elif 'src="/global-scripts.js"' in html:
            html = html.replace(
                'src="/global-scripts.js" defer></script>',
                'src="/global-scripts.js" defer></script>\n' + SHELL_JS,
                1,
            )
        else:
            html = html.replace("</head>", SHELL_JS + "\n</head>", 1)
    return html


def ensure_body_class(html: str) -> str:
    html = re.sub(
        r'<body([^>]*)class="([^"]*)"',
        lambda m: (
            m.group(0)
            if "cko-cart-page" in m.group(2)
            else f'<body{m.group(1)}class="{m.group(2)} cko-cart-page"'
        ),
        html,
        count=1,
        flags=re.I,
    )
    if re.search(r"<body(?![^>]*class=)", html, re.I):
        html = re.sub(r"<body\b", '<body class="cko-cart-page"', html, count=1, flags=re.I)
    if 'href="#main-content">Ir para o conteúdo' not in html:
        html = re.sub(
            r"(<body[^>]*>)",
            r'\1\n<a class="sr-only focus:not-sr-only" href="#main-content">Ir para o conteúdo</a>',
            html,
            count=1,
            flags=re.I,
        )
    return html


def add_h2_ids(html: str) -> str:
    used = set(re.findall(r'id="([^"]+)"', html))

    def slugify(text: str) -> str:
        t = unescape(re.sub(r"<[^>]+>", "", text))
        t = t.lower()
        t = re.sub(r"[áàâã]", "a", t)
        t = re.sub(r"[éê]", "e", t)
        t = re.sub(r"[í]", "i", t)
        t = re.sub(r"[óôõ]", "o", t)
        t = re.sub(r"[ú]", "u", t)
        t = re.sub(r"[ç]", "c", t)
        t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
        return (t or "secao")[:48]

    def repl(m: re.Match) -> str:
        tag, attrs, inner = m.group(1), m.group(2), m.group(3)
        if re.search(r'\bid\s*=', attrs, re.I):
            return m.group(0)
        sid = slugify(inner)
        base = sid
        i = 2
        while sid in used:
            sid = f"{base}-{i}"
            i += 1
        used.add(sid)
        return f"<{tag}{attrs} id=\"{sid}\">{inner}</{tag}>"

    return re.sub(r"<(h2)([^>]*)>(.*?)</h2>", repl, html, flags=re.S | re.I)


def fix_broken_main_close(html: str) -> str:
    """Many legacy pages have corrupted </main> written as </div>in>."""
    if "</div>in>" in html and "</main>" not in html.lower():
        html = html.replace("</div>in>", "</main>", 1)
    elif "</div>in>" in html:
        # Prefer a real </main>; drop the typo if both somehow exist later
        html = html.replace("</div>in>", "</main>", 1)
    return html


def normalize_main_classes(open_tag: str) -> str:
    if 'id="main-content"' not in open_tag:
        open_tag = re.sub(r"<main\b", '<main id="main-content"', open_tag, count=1, flags=re.I)
    desired = "flex-grow p-4 sm:p-8 max-w-7xl mx-auto w-full"
    if re.search(r'\bclass="', open_tag, re.I):
        open_tag = re.sub(
            r'\bclass="([^"]*)"',
            lambda mm: f'class="{desired}"',
            open_tag,
            count=1,
            flags=re.I,
        )
    else:
        open_tag = re.sub(r">\s*$", f' class="{desired}">', open_tag, count=1)
    return open_tag


def find_main_span(html: str) -> tuple[int, int, int, int] | None:
    """
    Return (open_start, open_end, body_end, close_end) for <main>...</main>.
    close_end == body_end when a synthetic close must be inserted (no closer found).
    """
    m_open = re.search(r"<main\b[^>]*>", html, re.I)
    if not m_open:
        return None
    rest = html[m_open.end() :]
    m_close = re.search(r"</main\s*>", rest, re.I)
    if m_close:
        body_end = m_open.end() + m_close.start()
        close_end = m_open.end() + m_close.end()
        return m_open.start(), m_open.end(), body_end, close_end

    # Unclosed main: cut before chrome that must stay outside
    for pat in (
        r"<!--\s*MULTIPLEX_AD_RESERVED_START\s*-->",
        r'<div id="footer-placeholder"',
        r'<div id="global-body-elements-container"',
        r'<button id="backToTopBtn"',
        r"</body\s*>",
    ):
        m_end = re.search(pat, rest, re.I)
        if m_end:
            body_end = m_open.end() + m_end.start()
            return m_open.start(), m_open.end(), body_end, body_end
    return None


def strip_legacy_page_chrome(html: str) -> str:
    """Remove duplicated breadcrumb/title heroes and old sidebar wrappers."""
    html = RE_BREADCRUMB.sub("", html)
    html = RE_TITLE_BAR_HERO.sub("", html)
    html = RE_ICON_H1_BLOCK.sub("", html)
    if 'data-cko-slot="hero"' not in html:
        html = RE_HERO_LEGACY.sub("", html)
    # Unwrap legacy "barra lateral" outer flex that fights cko-layout
    if RE_LEGACY_SIDEBAR_WRAP.search(html) and "cko-layout" in html:
        html = RE_LEGACY_SIDEBAR_WRAP.sub("", html)
        html = re.sub(
            r"(</main>)\s*(?:<!--[^>]*-->\s*)*</div>\s*(?:<!--[^>]*-->\s*)*",
            r"\1\n",
            html,
            count=1,
            flags=re.I,
        )
    return html


def wrap_main(html: str, page_id: str) -> str:
    """Ensure main has mounts + layout. Conservative if already modular with layout."""
    html = fix_broken_main_close(html)
    html = strip_legacy_page_chrome(html)

    if f'data-cko-page="{page_id}"' in html and "cko-layout" in html and 'data-cko-slot="sidebar"' in html:
        html = re.sub(
            r"(<main\b[^>]*>)",
            lambda m: normalize_main_classes(m.group(1)),
            html,
            count=1,
            flags=re.I,
        )
        return html

    # Special: cart product page — inject sidebar alongside root, don't destroy product
    if "cko-cart-root" in html and page_id in ("carinho", "carinho-artigo"):
        if "cko-layout" not in html:
            html = re.sub(
                r'(<div data-cko-page="[^"]+" data-cko-slot="chrome"></div>\s*)',
                r'\1<div data-cko-page="' + page_id + '" data-cko-slot="hero"></div>\n'
                if page_id == "carinho-artigo"
                else r"\1",
                html,
                count=1,
            )
            # wrap cart root + following until aside
            html = re.sub(
                r'(<div id="cko-cart-root"[^>]*>)',
                r'<div class="cko-layout">\n<div class="cko-layout__main">\n\1',
                html,
                count=1,
            )
            # before footer aside mount or cart-live
            if f'data-cko-slot="aside"' in html:
                html = html.replace(
                    f'<div data-cko-page="{page_id}" data-cko-slot="aside"></div>',
                    f'</div>\n<aside class="cko-layout__side" data-cko-page="{page_id}" data-cko-slot="sidebar" aria-label="Recursos da página"></aside>\n</div>\n'
                    f'<div data-cko-page="{page_id}" data-cko-slot="aside"></div>',
                    1,
                )
            else:
                html = html.replace(
                    "</main>",
                    f'</div>\n<aside class="cko-layout__side" data-cko-page="{page_id}" data-cko-slot="sidebar" aria-label="Recursos da página"></aside>\n</div>\n'
                    f'<div data-cko-page="{page_id}" data-cko-slot="aside"></div>\n</main>',
                    1,
                )
        html = re.sub(
            r"(<main\b[^>]*>)",
            lambda m: normalize_main_classes(m.group(1)),
            html,
            count=1,
            flags=re.I,
        )
        # carinho hero comes from renderer — remove shell hero mount if we added empty
        if page_id == "carinho":
            html = re.sub(
                rf'\s*<div data-cko-page="{page_id}" data-cko-slot="hero"></div>\s*',
                "\n",
                html,
            )
        return html

    # Generic content page
    html = strip_legacy_page_chrome(html)

    span = find_main_span(html)
    if not span:
        return html

    open_start, open_end, body_end, close_end = span
    open_tag = normalize_main_classes(html[open_start:open_end])
    body = html[open_end:body_end]
    had_close = close_end > body_end
    close_tag = "</main>" if had_close else "</main>"

    # strip existing shell mounts to rebuild cleanly
    body = re.sub(r'<div data-cko-page="[^"]+" data-cko-slot="[^"]+"[^>]*>\s*</div>\s*', "", body)
    body = re.sub(r'<aside[^>]*data-cko-slot="sidebar"[^>]*>.*?</aside>\s*', "", body, flags=re.S)
    body = re.sub(
        r'<div class="cko-layout">|</div>\s*(?=<aside class="cko-layout__side")|<div class="cko-layout__main">',
        "",
        body,
    )
    body = body.strip()

    new_body = (
        f'\n<div data-cko-page="{page_id}" data-cko-slot="chrome"></div>\n'
        f'<div data-cko-page="{page_id}" data-cko-slot="hero"></div>\n'
        f'<div class="cko-layout">\n'
        f'<div class="cko-layout__main">\n'
        f"{body}\n"
        f"</div>\n"
        f'<aside class="cko-layout__side" data-cko-page="{page_id}" '
        f'data-cko-slot="sidebar" aria-label="Recursos da página"></aside>\n'
        f"</div>\n"
        f'<div data-cko-page="{page_id}" data-cko-slot="aside"></div>\n'
    )
    return html[:open_start] + open_tag + new_body + close_tag + html[close_end:]


def pick_navset(page_id: str, filename: str) -> tuple[str, str | None]:
    if filename.startswith("biblioteca") or page_id.startswith("biblioteca") or page_id in (
        "cirurgica",
        "curativo",
        "seringa",
        "provas",
        "carinho",
        "carinho-artigo",
    ):
        return "materiais", None
    if page_id in ("trr", "5-hs-da-paradacardiorespiratoria", "5-ts-da-paradacardiorespiratoria", "suporte-avancado-de-vida") or "paradacardio" in page_id or "resposta-rapida" in page_id:
        return "protocolos", "Protocolos relacionados"
    if page_id.startswith("simulado"):
        return "conteudos", "Conteúdos"
    if page_id in ("missao", "objetivo", "politica", "termos", "mapa-do-site", "conteudos-do-site", "tecnologiaverde"):
        return "institucional", "Institucional"
    return "conteudos", "Conteúdos"


def build_page_entry(page_id: str, filename: str, title: str, desc: str, existing: dict | None) -> dict:
    if existing and existing.get("hero") is None and page_id in ("carinho", "carinho-artigo"):
        # keep product pages' null hero
        base = dict(existing)
        base.setdefault("sidebar", {"feedback": True})
        if "tools" not in base.get("sidebar", {}):
            base["sidebar"] = {
                **base.get("sidebar", {}),
                "feedback": True,
                "tools": existing.get("actions")
                or [
                    {"label": "Início", "href": "/", "primary": True},
                    {"label": "Carrinho", "href": "/biblioteca-carinho-de-emergencia.html"},
                ],
            }
        return base

    navset, navlabel = pick_navset(page_id, filename)
    crumb = [
        {"label": "Início", "href": "/"},
        {"label": "Conteúdos" if navset == "conteudos" else ("Materiais" if navset == "materiais" else ("Protocolos" if navset == "protocolos" else "Site"))},
        {"label": title[:80]},
    ]
    if existing and existing.get("breadcrumb"):
        crumb = existing["breadcrumb"]

    tools = [
        {"label": "Início", "href": "/", "primary": True},
        {"label": "Mapa do site", "href": "/mapa-do-site.html"},
        {"label": "Carrinho de Emergência", "href": "/biblioteca-carinho-de-emergencia.html"},
    ]
    if navset == "protocolos":
        tools = [
            {"label": "Calculadora NEWS", "href": "/news.html", "primary": True},
            {"label": "TRR", "href": "/time-de-resposta-rapida.html"},
            {"label": "Carrinho", "href": "/biblioteca-carinho-de-emergencia.html"},
        ]

    entry = {
        "navSet": navset,
        "activeNav": page_id if navset == "materiais" and page_id in ("carinho", "cirurgica", "curativo", "seringa", "provas") else None,
        "breadcrumb": crumb,
        "actions": tools[:3],
        "hero": {
            "eyebrow": "Calculadoras de Enfermagem",
            "title": title,
            "lead": desc,
            "chips": ["Conteúdo educativo", "Atualizado"],
        },
        "aside": {
            "notice": "Material educativo — adapte ao POP e protocolos da sua instituição."
        },
        "sidebar": {
            "feedback": True,
            "tools": tools,
        },
    }
    if navlabel:
        entry["navLabel"] = navlabel
    if not entry["activeNav"]:
        entry.pop("activeNav", None)

    # preserve richer existing entries
    if existing:
        for k in ("navSet", "navLabel", "activeNav", "breadcrumb", "actions", "hero", "aside", "sidebar"):
            if k in existing and existing[k] is not None:
                if k == "sidebar" and isinstance(existing[k], dict):
                    merged = {**entry["sidebar"], **existing[k]}
                    entry["sidebar"] = merged
                elif k == "hero" and existing[k] is None:
                    entry["hero"] = None
                else:
                    entry[k] = existing[k]
    return entry


def migrate_file(path: Path, catalog: dict) -> tuple[bool, str]:
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    page_id = {
        "biblioteca-cirurgica.html": "cirurgica",
        "biblioteca-curativo.html": "curativo",
        "biblioteca-seringa.html": "seringa",
        "biblioteca-provas.html": "provas",
        "biblioteca-carinho-de-emergencia.html": "carinho",
        "biblioteca/artigo-carrinho-de-emergencia-enfermagem.html": "carinho-artigo",
        "time-de-resposta-rapida.html": "trr",
    }.get(rel, slug_id(path.name))

    html0 = path.read_text(encoding="utf-8", errors="ignore")
    title = extract_title(html0, path.stem.replace("-", " ").title())
    desc = extract_description(html0)

    catalog["pages"][page_id] = build_page_entry(
        page_id, path.name, title, desc, catalog["pages"].get(page_id)
    )

    html = html0
    html = ensure_assets(html)
    html = ensure_body_class(html)
    html = add_h2_ids(html)
    html = wrap_main(html, page_id)

    if html != html0:
        path.write_text(html, encoding="utf-8", newline="\n")
        return True, page_id
    return False, page_id


def ensure_navsets(catalog: dict) -> None:
    ns = catalog.setdefault("navSets", {})
    if "conteudos" not in ns:
        ns["conteudos"] = [
            {"id": "trr", "href": "/time-de-resposta-rapida.html", "label": "TRR"},
            {"id": "metas", "href": "/metasinternacionais.html", "label": "Metas ISP"},
            {"id": "checagem", "href": "/checagem.html", "label": "Checagem"},
            {"id": "carinho", "href": "/biblioteca-carinho-de-emergencia.html", "label": "Carrinho"},
            {"id": "provas", "href": "/biblioteca-provas.html", "label": "Provas"},
        ]
    if "institucional" not in ns:
        ns["institucional"] = [
            {"id": "missao", "href": "/missao.html", "label": "Missão"},
            {"id": "objetivo", "href": "/objetivo.html", "label": "Objetivo"},
            {"id": "mapa", "href": "/mapa-do-site.html", "label": "Mapa"},
            {"id": "politica", "href": "/politica.html", "label": "Privacidade"},
            {"id": "termos", "href": "/termos.html", "label": "Termos"},
        ]


def main() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    ensure_navsets(catalog)
    targets = collect_content_targets()
    updated = 0
    ids = []
    for p in targets:
        changed, pid = migrate_file(p, catalog)
        ids.append(pid)
        if changed:
            updated += 1
            print("UPDATED", p.relative_to(ROOT))
        else:
            print("OK-keep", p.relative_to(ROOT))

    CATALOG_PATH.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print("---")
    print("targets", len(targets), "updated", updated, "catalog_pages", len(catalog["pages"]))


if __name__ == "__main__":
    main()
