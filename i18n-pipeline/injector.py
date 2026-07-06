#!/usr/bin/env python3
"""
NIFS i18n Injector — Fase 2 (v2, multi-template)
Aplica o common_dictionary traduzido em TODAS as páginas do site, gerando
/{locale}/{slug}.html com: <html lang>, SEO head (title/description/canonical/hreflang recíproco),
e os termos comuns já substituídos no corpo estático.

Cobre os 2 formatos de template encontrados no site:
  A) calculadoras: <link rel="canonical" href="..." /> + blocos <link rel="alternate" hreflang="..." href="...">
  B) artigos/biblioteca: <link href="..." rel="canonical"/> + blocos <link href="..." hreflang="..." rel="alternate"/>

Conteúdo único por página (SAE, evidências, interpretação específica) permanece em pt-BR
neste estágio — é a Fase 3 (tradução clínica por calculadora).
"""
import json, re, os, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "reference-website"
PIPE = Path(__file__).resolve().parent
OUT = PIPE / "extracted"

translations = json.load(open(OUT / "common_translations.json", encoding="utf-8"))
meta = translations.pop("_meta")
LOCALES = meta["locales"]
SITE_URL = "https://www.calculadorasdeenfermagem.com.br"

EXCLUDE_SUBSTR = ["global-body-elements", "menu-global", "calculadora-preview", "calculadora-template",
                  "preview_apgar", "preview_v2", "ativar-admin", "offline.html", "admin.html"]

HREFLANG_BLOCK_A = re.compile(r'(?:\s*<link rel="alternate"[^\n]*\n?)+', re.IGNORECASE)
HREFLANG_BLOCK_B = re.compile(r'(?:<link href="[^"]*" hreflang="[^"]*" rel="alternate"\s*/?>\n?)+', re.IGNORECASE)
CANONICAL_A = re.compile(r'<link rel="canonical" href="[^"]*"\s*/?>')
CANONICAL_B = re.compile(r'<link href="[^"]*" rel="canonical"\s*/?>')


def apply_common_dict(html: str, locale: str) -> str:
    for term, langs in translations.items():
        if locale in langs:
            html = html.replace(f">{term}<", f">{langs[locale]}<")
    return html


def fix_seo_head(html: str, slug: str, locale: str) -> str:
    canon_root = f"{SITE_URL}/{slug}.html"
    prefix = locale.split("-")[0].lower()
    canon_locale = f"{SITE_URL}/{prefix}/{slug}.html"

    html = re.sub(r'<html lang="[^"]*">', f'<html lang="{locale}">', html, count=1)

    hreflang_block_new_a = (
        f'  <link rel="alternate" hreflang="pt-BR" href="{canon_root}" />\n'
        f'  <link rel="alternate" hreflang="{locale}" href="{canon_locale}" />\n'
        f'  <link rel="alternate" hreflang="x-default" href="{canon_root}" />\n'
    )
    hreflang_block_new_b = (
        f'<link href="{canon_root}" hreflang="pt-BR" rel="alternate"/>\n'
        f'<link href="{canon_locale}" hreflang="{locale}" rel="alternate"/>\n'
        f'<link href="{canon_root}" hreflang="x-default" rel="alternate"/>\n'
    )

    if CANONICAL_A.search(html):
        html = CANONICAL_A.sub(f'<link rel="canonical" href="{canon_locale}" />', html, count=1)
        if HREFLANG_BLOCK_A.search(html):
            html = HREFLANG_BLOCK_A.sub(hreflang_block_new_a, html, count=1)
        else:
            html = CANONICAL_A.sub(lambda m: m.group(0) + "\n" + hreflang_block_new_a, html, count=1)
    elif CANONICAL_B.search(html):
        html = CANONICAL_B.sub(f'<link href="{canon_locale}" rel="canonical"/>', html, count=1)
        if HREFLANG_BLOCK_B.search(html):
            html = HREFLANG_BLOCK_B.sub(hreflang_block_new_b, html, count=1)
        else:
            html = CANONICAL_B.sub(lambda m: m.group(0) + "\n" + hreflang_block_new_b, html, count=1)
    # senão: página sem canonical conhecido -> deixa como está (marcada no relatório)

    return html


def fix_relative_links(html: str) -> str:
    html = re.sub(r'href="(?!http|/|#|mailto|\.\./)([a-zA-Z0-9_-]+\.html)', r'href="../\1', html)
    return html


def process(locale: str, files=None):
    prefix = locale.split("-")[0].lower()
    out_dir = BASE / prefix
    out_dir.mkdir(exist_ok=True)
    if files is None:
        files = sorted(BASE.glob("*.html"))
        files = [f for f in files if not any(x in str(f) for x in EXCLUDE_SUBSTR)]
    count = 0
    for fpath in files:
        slug = fpath.stem
        html = fpath.read_text(encoding="utf-8", errors="ignore")
        html = fix_seo_head(html, slug, locale)
        html = apply_common_dict(html, locale)
        html = fix_relative_links(html)
        (out_dir / f"{slug}.html").write_text(html, encoding="utf-8")
        count += 1
    return count


if __name__ == "__main__":
    locale = sys.argv[1] if len(sys.argv) > 1 else "es"
    n = process(locale)
    print(f"Gerado: {n} páginas em /{locale.split('-')[0].lower()}/")
