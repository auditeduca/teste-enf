# -*- coding: utf-8 -*-
"""
Padroniza o chrome compartilhado de todas as páginas HTML na raiz PT-BR.

NÃO reescreve o conteúdo principal (main) — só elementos comuns:
  skip link, header, lang, footer, body.cko-cart-page, data-cko-template,
  assets CKO (cart / shell / templates), remoção de CDNs legados.

Uso:
  python tools/standardize_page_chrome.py
  python tools/standardize_page_chrome.py --dry-run
  python tools/standardize_page_chrome.py --report
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from migrate_content_shell import wrap_main  # noqa: E402

CATALOG_PATH = ROOT / "data" / "cko-shell-pages.json"

EXCLUDE = {
    "footer.html",
    "menu-global.html",
    "global-body-elements.html",
    "lang-selector.html",
    "_language_selector.html",
    "cookies.html",
    "404.html",
}

INSTITUTIONAL = {
    "missao",
    "objetivo",
    "politica",
    "termos",
    "mapa-do-site",
    "fale",
    "conteudos-do-site",
    "conteudos_da_pagina",
}

TOOL = {
    "downloads",
    "downloads.template",
    "flashcards_quiz",
    "flashcards-srs",
    "valorizacao-profissional",
    "geradordir",
    "formulario-saep-enfermagem",
    "forum-enfermagem",
    "album_enfermagem",
    "risktools",
    "matriz-de-risco",
    "genogramaeecomapa",
    "instrumentais-cirurgicos",
    "equipamentoscc",
    "guia_rapido_dispositivos",
    "elisabeth-marques-plataforma-completa",
    "biblioteca-carinho-de-emergencia",
    "biblioteca-cirurgica",
    "biblioteca-curativo",
    "biblioteca-provas",
    "biblioteca-seringa",
}

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
    "integracoes_calculadora_de_gasometria", "meem",
}

CART_CSS = '<link href="/css/pages/cart-emergencia.css" rel="stylesheet">'
SHELL_CSS = '<link href="/css/pages/cko-page-shell.css" rel="stylesheet">'
TPL_CSS = '<link href="/css/pages/cko-page-templates.css" rel="stylesheet">'
SHELL_JS = '<script src="/js/cko-page-shell.js" defer></script>'
TPL_JS = '<script src="/js/cko-page-templates.js" defer></script>'

CDN_SCRIPT_RE = re.compile(
    r'<script[^>]+src=["\']https?://cdn\.tailwindcss\.com[^"\']*["\'][^>]*>\s*</script>\s*',
    re.I,
)
GOOGLE_FONT_LINK_RE = re.compile(
    r'<link[^>]+href=["\']https?://fonts\.googleapis\.com[^"\']*["\'][^>]*/?>\s*',
    re.I,
)
GOOGLE_FONT_CSS_RE = re.compile(
    r'<link[^>]+href=["\']https?://fonts\.gstatic\.com[^"\']*["\'][^>]*/?>\s*',
    re.I,
)
LUCIDE_CDN_RE = re.compile(
    r'<script[^>]+src=["\']https?://unpkg\.com/lucide[^"\']*["\'][^>]*>\s*</script>\s*',
    re.I,
)


def stem_of(name: str) -> str:
    return Path(name).stem.lower()


def classify(name: str, html: str) -> str:
    stem = stem_of(name)
    if name == "index.html" or 'data-cko-template="home"' in html:
        return "home"
    if stem in INSTITUTIONAL:
        return "institutional"
    if stem in TOOL or stem.startswith("biblioteca"):
        return "tool"
    if stem in CALC_SLUGS:
        return "calculator"
    if "data-cko-content" in html or "cko-content-engine" in html:
        return "content"
    # shell pages that are protocols/guides
    if any(
        k in stem
        for k in (
            "protocolo",
            "guia",
            "checklist",
            "legisl",
            "teoria",
            "metas",
            "principio",
            "nanda",
            "sinan",
            "notificacao",
            "lista-de-doencas",
            "paradacardio",
            "resposta-rapida",
            "suporte-avancado",
            "checagem",
            "vigilancia",
            "regrasmedic",
            "nr1",
            "copsoq",
            "entenda",
            "lei8080",
            "tabelas-vacinas",
            "adequar",
            "normas",
            "simulado",
        )
    ):
        return "content"
    if "cko-page-shell.js" in html or "data-cko-slot" in html:
        return "content"
    return "content"


def needs_shell(tpl: str) -> bool:
    return tpl in {"institutional", "calculator", "tool", "content"}


def insert_after_stylesheet(html: str, marker: str, link: str) -> str:
    if link.split('href="')[1].split('"')[0] in html:
        return html
    if marker in html:
        return html.replace(marker, marker + "\n" + link, 1)
    return html.replace("</head>", link + "\n</head>", 1)


def insert_after_script(html: str, marker_src: str, script: str) -> str:
    src = script.split('src="')[1].split('"')[0]
    if src in html:
        return html
    # find defer script with marker
    pat = re.compile(
        rf'(<script[^>]+src="{re.escape(marker_src)}"[^>]*>\s*</script>)',
        re.I,
    )
    m = pat.search(html)
    if m:
        return html.replace(m.group(1), m.group(1) + "\n" + script, 1)
    return html.replace("</head>", script + "\n</head>", 1)


def ensure_assets(html: str, tpl: str) -> str:
    # cart
    if "/css/pages/cart-emergencia.css" not in html:
        if 'href="/global-styles.css" rel="stylesheet">' in html:
            html = html.replace(
                'href="/global-styles.css" rel="stylesheet">',
                'href="/global-styles.css" rel="stylesheet">\n' + CART_CSS,
                1,
            )
        elif 'href="/public/output.css" rel="stylesheet">' in html:
            html = html.replace(
                'href="/public/output.css" rel="stylesheet">',
                'href="/public/output.css" rel="stylesheet">\n'
                '<link href="/global-styles.css" rel="stylesheet">\n' + CART_CSS,
                1,
            )
        else:
            html = html.replace("</head>", CART_CSS + "\n</head>", 1)

    # shell css
    if needs_shell(tpl) and "/css/pages/cko-page-shell.css" not in html:
        if "/css/pages/cart-emergencia.css" in html:
            html = html.replace(CART_CSS, CART_CSS + "\n" + SHELL_CSS, 1)
            if "/css/pages/cko-page-shell.css" not in html:
                html = html.replace(
                    'href="/css/pages/cart-emergencia.css" rel="stylesheet">',
                    'href="/css/pages/cart-emergencia.css" rel="stylesheet">\n' + SHELL_CSS,
                    1,
                )
        else:
            html = html.replace("</head>", SHELL_CSS + "\n</head>", 1)

    # templates css
    if "/css/pages/cko-page-templates.css" not in html:
        anchor = (
            'href="/css/pages/cko-page-shell.css" rel="stylesheet">'
            if "/css/pages/cko-page-shell.css" in html
            else 'href="/css/pages/cart-emergencia.css" rel="stylesheet">'
        )
        if anchor in html:
            html = html.replace(anchor, anchor + "\n" + TPL_CSS, 1)
        else:
            html = html.replace("</head>", TPL_CSS + "\n</head>", 1)

    # shell js
    if needs_shell(tpl) and "/js/cko-page-shell.js" not in html:
        if 'src="/lang-selector.js"' in html:
            html = re.sub(
                r'(<script[^>]+src="/lang-selector\.js"[^>]*>\s*</script>)',
                r"\1\n" + SHELL_JS,
                html,
                count=1,
                flags=re.I,
            )
        elif 'src="/global-scripts.js"' in html:
            html = re.sub(
                r'(<script[^>]+src="/global-scripts\.js"[^>]*>\s*</script>)',
                r"\1\n" + SHELL_JS,
                html,
                count=1,
                flags=re.I,
            )
        else:
            html = html.replace("</head>", SHELL_JS + "\n</head>", 1)

    # templates js
    if "/js/cko-page-templates.js" not in html:
        if "/js/cko-page-shell.js" in html:
            html = re.sub(
                r'(<script[^>]+src="/js/cko-page-shell\.js"[^>]*>\s*</script>)',
                r"\1\n" + TPL_JS,
                html,
                count=1,
                flags=re.I,
            )
        elif 'src="/lang-selector.js"' in html:
            html = re.sub(
                r'(<script[^>]+src="/lang-selector\.js"[^>]*>\s*</script>)',
                r"\1\n" + TPL_JS,
                html,
                count=1,
                flags=re.I,
            )
        else:
            html = html.replace("</head>", TPL_JS + "\n</head>", 1)

    return html


def ensure_body(html: str, tpl: str) -> str:
    # body class + data-cko-template
    def body_repl(m: re.Match) -> str:
        attrs = m.group(1) or ""
        # class
        cm = re.search(r'\bclass="([^"]*)"', attrs, re.I)
        classes = cm.group(1) if cm else ""
        parts = classes.split()
        if "cko-cart-page" not in parts:
            parts.append("cko-cart-page")
        tpl_class = f"cko-tpl-{tpl}" if tpl != "home" else "cko-tpl-home"
        # keep one tpl class
        parts = [p for p in parts if not p.startswith("cko-tpl-")]
        parts.append(tpl_class)
        new_class = " ".join(parts)
        if cm:
            attrs = re.sub(r'\bclass="[^"]*"', f'class="{new_class}"', attrs, count=1, flags=re.I)
        else:
            attrs = f' class="{new_class}"' + attrs

        if re.search(r"\bdata-cko-template=", attrs, re.I):
            attrs = re.sub(
                r'\bdata-cko-template="[^"]*"',
                f'data-cko-template="{tpl}"',
                attrs,
                count=1,
                flags=re.I,
            )
        else:
            attrs = attrs + f' data-cko-template="{tpl}"'
        return f"<body{attrs}>"

    html = re.sub(r"<body([^>]*)>", body_repl, html, count=1, flags=re.I)

    if 'href="#main-content">Ir para o conteúdo' not in html and 'href="#main-content"' not in html:
        html = re.sub(
            r"(<body[^>]*>)",
            r'\1\n<a class="sr-only focus:not-sr-only" href="#main-content">Ir para o conteúdo</a>',
            html,
            count=1,
            flags=re.I,
        )
    return html


def ensure_global_mounts(html: str) -> str:
    """Ensure header / lang / footer placeholders exist."""
    if 'id="global-header-container"' not in html:
        # insert before main if possible
        html = re.sub(
            r"(<main\b)",
            '<div id="global-header-container"></div>\n'
            '<div id="language-selector-placeholder"></div>\n\\1',
            html,
            count=1,
            flags=re.I,
        )
    elif 'id="language-selector-placeholder"' not in html:
        html = html.replace(
            'id="global-header-container"></div>',
            'id="global-header-container"></div>\n<div id="language-selector-placeholder"></div>',
            1,
        )
    if 'id="footer-placeholder"' not in html:
        html = re.sub(
            r"</body>",
            '<div id="footer-placeholder"></div>\n</body>',
            html,
            count=1,
            flags=re.I,
        )
    # normalize main id
    if 'id="main-content"' not in html and re.search(r"<main\b", html, re.I):
        html = re.sub(r"<main\b", '<main id="main-content"', html, count=1, flags=re.I)
    return html


GOOGLE_DNS_PREFETCH_RE = re.compile(
    r'<link[^>]+href=["\']//fonts\.googleapis\.com["\'][^>]*/?>\s*',
    re.I,
)


def strip_legacy_cdns(html: str) -> str:
    html = CDN_SCRIPT_RE.sub("", html)
    html = GOOGLE_FONT_LINK_RE.sub("", html)
    html = GOOGLE_FONT_CSS_RE.sub("", html)
    html = LUCIDE_CDN_RE.sub("", html)
    html = GOOGLE_DNS_PREFETCH_RE.sub("", html)
    return html


def ensure_shell_slots(html: str, page_id: str) -> str:
    """If page already has cko-layout but missing chrome/hero/sidebar, inject missing mounts."""
    if "cko-layout" not in html and "data-cko-slot" not in html:
        return html

    # ensure chrome+hero before cko-layout
    if f'data-cko-page="{page_id}"' not in html:
        # try to rewrite existing page ids? skip if unknown
        m = re.search(r'data-cko-page="([^"]+)"', html)
        if m:
            page_id = m.group(1)

    if 'data-cko-slot="chrome"' not in html:
        html = re.sub(
            r'(<main[^>]*>)',
            rf'\1\n<div data-cko-page="{page_id}" data-cko-slot="chrome"></div>\n'
            rf'<div data-cko-page="{page_id}" data-cko-slot="hero"></div>\n',
            html,
            count=1,
            flags=re.I,
        )
    elif 'data-cko-slot="hero"' not in html:
        html = re.sub(
            r'(data-cko-slot="chrome"></div>)',
            rf'\1\n<div data-cko-page="{page_id}" data-cko-slot="hero"></div>',
            html,
            count=1,
            flags=re.I,
        )

    if 'data-cko-slot="sidebar"' not in html and "cko-layout" in html:
        # add side column if missing
        if "cko-layout__side" not in html:
            html = re.sub(
                r'(</div>\s*)(</div>\s*</main>|</main>)',
                rf'\1<aside class="cko-layout__side" data-cko-page="{page_id}" '
                r'data-cko-slot="sidebar" aria-label="Recursos da página"></aside>\n\2',
                html,
                count=1,
                flags=re.I,
            )
    return html


def catalog_page_id(name: str, html: str) -> str:
    m = re.search(r'data-cko-page="([^"]+)"', html)
    if m:
        return m.group(1)
    s = stem_of(name)
    s = re.sub(r"[^a-z0-9_-]+", "-", s).strip("-")
    return s[:64] or "page"


def ensure_catalog_entry(catalog: dict, page_id: str, title: str, lead: str, tpl: str) -> bool:
    pages = catalog.setdefault("pages", {})
    if page_id in pages:
        return False
    nav = {
        "home": "Início",
        "institutional": "Institucional",
        "calculator": "Calculadoras",
        "tool": "Ferramentas",
        "content": "Conteúdos",
    }.get(tpl, "Conteúdos")
    pages[page_id] = {
        "navSet": "conteudos" if tpl != "home" else "home",
        "breadcrumb": [
            {"label": "Início", "href": "/"},
            {"label": nav},
            {"label": title},
        ],
        "actions": [
            {"label": "Início", "href": "/", "primary": True},
            {"label": "Mapa do site", "href": "/mapa-do-site.html"},
        ],
        "hero": {
            "eyebrow": "Calculadoras de Enfermagem",
            "title": title,
            "lead": lead,
            "chips": ["Padronizado CKO"],
        },
        "aside": False,
        "sidebar": {
            "feedback": True,
            "tools": [
                {"label": "Início", "href": "/", "primary": True},
                {"label": "Mapa do site", "href": "/mapa-do-site.html"},
            ],
        },
        "navLabel": nav,
    }
    return True


def extract_title(html: str, fallback: str) -> str:
    m = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
    if m:
        t = unescape(re.sub(r"\s+", " ", m.group(1))).strip()
        t = re.split(r"\s*\|\s*", t)[0].strip()
        t = re.sub(r"\s*-\s*Calculadoras.*$", "", t, flags=re.I).strip()
        if t:
            return t[:120]
    return fallback


def extract_description(html: str) -> str:
    m = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]+)"', html, re.I)
    if not m:
        m = re.search(r'<meta[^>]+content="([^"]+)"[^>]+name="description"', html, re.I)
    if m:
        return unescape(m.group(1)).strip()[:220]
    return "Conteúdo educativo de enfermagem — adapte ao protocolo e POP da sua instituição."


def process_file(path: Path, catalog: dict, dry: bool) -> dict:
    html0 = path.read_text(encoding="utf-8", errors="ignore")
    html = html0
    name = path.name
    tpl = classify(name, html)
    page_id = catalog_page_id(name, html)
    changes = []

    new_html = strip_legacy_cdns(html)
    if new_html != html:
        changes.append("cdn")
        html = new_html

    new_html = ensure_assets(html, tpl)
    if new_html != html:
        changes.append("assets")
        html = new_html

    new_html = ensure_body(html, tpl)
    if new_html != html:
        changes.append("body")
        html = new_html

    new_html = ensure_global_mounts(html)
    if new_html != html:
        changes.append("mounts")
        html = new_html

    if needs_shell(tpl) and "cko-layout" not in html:
        wrapped = wrap_main(html, page_id)
        if wrapped != html and "cko-layout" in wrapped:
            html = wrapped
            changes.append("wrap")
        else:
            new_html = ensure_shell_slots(html, page_id)
            if new_html != html:
                changes.append("slots")
                html = new_html
    elif needs_shell(tpl):
        new_html = ensure_shell_slots(html, page_id)
        if new_html != html:
            changes.append("slots")
            html = new_html

    title = extract_title(html, page_id)
    lead = extract_description(html)
    if needs_shell(tpl) and ensure_catalog_entry(catalog, page_id, title, lead, tpl):
        changes.append("catalog")

    changed = html != html0
    if changed and not dry:
        path.write_text(html, encoding="utf-8", newline="\n")

    return {
        "file": name,
        "tpl": tpl,
        "page_id": page_id,
        "changes": changes,
        "changed": changed,
        "has_shell": "cko-page-shell.js" in html or "data-cko-slot" in html,
        "has_template": "data-cko-template=" in html,
        "has_layout": "cko-layout" in html,
    }


def report(paths: list[Path]) -> None:
    counts = {"home": 0, "institutional": 0, "calculator": 0, "tool": 0, "content": 0}
    with_tpl = 0
    with_shell = 0
    with_layout = 0
    with_cdn = 0
    missing_layout = []
    for p in paths:
        t = p.read_text(encoding="utf-8", errors="ignore")
        tpl = classify(p.name, t)
        counts[tpl] = counts.get(tpl, 0) + 1
        if "data-cko-template=" in t:
            with_tpl += 1
        if "cko-page-shell.js" in t or "data-cko-slot" in t:
            with_shell += 1
        if "cko-layout" in t:
            with_layout += 1
        elif needs_shell(tpl):
            missing_layout.append(p.name)
        if "cdn.tailwindcss.com" in t or "fonts.googleapis.com" in t:
            with_cdn += 1
    print("REPORT root PT pages")
    print(f"  total={len(paths)}")
    print(f"  with_data-cko-template={with_tpl}")
    print(f"  with_shell={with_shell}")
    print(f"  with_cko-layout={with_layout}")
    print(f"  leftover_cdn={with_cdn}")
    print(f"  shell_missing_layout={len(missing_layout)}")
    for k, v in counts.items():
        print(f"  classify.{k}={v}")
    if missing_layout[:15]:
        print("  missing_layout_sample:")
        for n in missing_layout[:15]:
            print(f"    - {n}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    paths = sorted(
        p for p in ROOT.glob("*.html") if p.name not in EXCLUDE and p.is_file()
    )

    if args.report:
        report(paths)
        return 0

    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    stats = {"changed": 0, "files": 0}
    by_change: dict[str, int] = {}
    for p in paths:
        stats["files"] += 1
        res = process_file(p, catalog, args.dry_run)
        if res["changed"]:
            stats["changed"] += 1
            print(f"{'[dry] ' if args.dry_run else ''}UPDATE {res['file']} tpl={res['tpl']} {res['changes']}")
            for c in res["changes"]:
                by_change[c] = by_change.get(c, 0) + 1

    if not args.dry_run:
        CATALOG_PATH.write_text(
            json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    print("---")
    print(f"files={stats['files']} changed={stats['changed']} dry={args.dry_run}")
    print("changes:", by_change)
    report(paths)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
