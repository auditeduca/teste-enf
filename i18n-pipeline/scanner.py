#!/usr/bin/env python3
"""
NIFS i18n Scanner — Fase 1
Varre todas as páginas HTML do site, extrai conteúdo traduzível (SEO + corpo estático + tool-config JSON),
deduplica strings comuns entre páginas (dicionário de termos) e separa o conteúdo único por página.

Saída:
  - common_dictionary.json   → strings que se repetem em >= MIN_REPEAT páginas (chrome, UI, seguranca, disclaimers)
  - pages/<slug>.json        → conteúdo único por página (SEO + tool-config + textos específicos)
  - scan_report.json         → estatísticas da varredura
"""
import json, re, os, sys
from pathlib import Path
from collections import Counter, defaultdict

SITE_DIR = Path(__file__).resolve().parent.parent / "reference-website"
OUT_DIR = Path(__file__).resolve().parent / "extracted"
OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / "pages").mkdir(exist_ok=True)

EXCLUDE_SUBSTR = [
    "global-body-elements", "menu-global", "calculadora-preview", "calculadora-template",
    "preview_apgar", "preview_v2", "ativar-admin", "offline.html", "admin.html",
    "/es/",  # já é output, não input
]

MIN_REPEAT = 5  # string aparece em >=5 páginas -> vai pro dicionário comum

def repair_json(raw: str) -> str:
    """Conserta o bug conhecido: <i class="fa fa"></i> com aspas não escapadas dentro de strings JSON."""
    # Escapa aspas de atributos HTML embutidos em valores de string JSON (padrão <i class="...">)
    raw = re.sub(r'(?<!\\)"(?=[a-z-]+="[^"]*"></i>)', r'\\"', raw)
    raw = re.sub(r'(<i class=\\?")fa fa(\\?"></i>)', r'\1fa fa\2', raw)
    # fallback: escapa qualquer '="..."' dentro de tags <i ...> que não esteja escapado
    def fix_tag(m):
        return m.group(0).replace('"', '\\"')
    raw = re.sub(r'<i class="[^>]*></i>', fix_tag, raw)
    return raw

def extract_tool_config(html: str):
    m = re.search(r'<script type="application/json" id="tool-config">(.*?)</script>', html, re.DOTALL)
    if not m:
        return None
    raw = m.group(1)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        try:
            return json.loads(repair_json(raw))
        except json.JSONDecodeError as e:
            return {"__parse_error__": str(e)}

def extract_seo(html: str):
    title = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
    desc = re.search(r'name="description"\s+content="([^"]*)"', html)
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    subtitle = re.search(r'class="tool-subtitle">(.*?)</p>', html, re.DOTALL)
    return {
        "title": title.group(1).strip() if title else None,
        "description": desc.group(1).strip() if desc else None,
        "h1": re.sub(r'<[^>]+>', '', h1.group(1)).strip() if h1 else None,
        "subtitle": re.sub(r'<[^>]+>', '', subtitle.group(1)).strip() if subtitle else None,
    }

# Padrões de texto visível estático a extrair (heurística por tag+classe conhecida do template)
TEXT_PATTERNS = [
    (r'<label class="field"[^>]*>([^<]+)</label>', 'field_label'),
    (r'<p class="field">([^<]+)</p>', 'field_desc'),
    (r'<h2[^>]*>(?:<svg[^>]*>.*?</svg>\s*)?([^<]+)</h2>', 'section_h2'),
    (r'<h3>([^<]+)</h3>', 'card_h3'),
    (r'<li><svg[^>]*><use[^>]*/></svg>\s*([^<]+)</li>', 'tip_li'),
    (r'<span class="nnn">([^<]+)</span>', 'nnn_label'),
    (r'<summary>([^<]+?)\s*<svg', 'faq_question'),
]

def extract_static_texts(html: str):
    found = []
    for pattern, kind in TEXT_PATTERNS:
        for m in re.finditer(pattern, html, re.DOTALL):
            txt = m.group(1).strip()
            if txt and len(txt) > 1:
                found.append((kind, txt))
    return found

def main():
    files = sorted(SITE_DIR.glob("*.html"))
    files = [f for f in files if not any(x in str(f) for x in EXCLUDE_SUBSTR)]

    string_freq = Counter()
    string_kind = {}
    page_data = {}
    parse_errors = []

    for fpath in files:
        slug = fpath.stem
        html = fpath.read_text(encoding="utf-8", errors="ignore")

        seo = extract_seo(html)
        cfg = extract_tool_config(html)
        texts = extract_static_texts(html)

        if cfg and "__parse_error__" in cfg:
            parse_errors.append(slug)

        for kind, txt in texts:
            string_freq[txt] += 1
            string_kind[txt] = kind

        page_data[slug] = {
            "seo": seo,
            "has_tool_config": cfg is not None and "__parse_error__" not in (cfg or {}),
            "tool_config": cfg if cfg and "__parse_error__" not in cfg else None,
            "static_texts": texts,
        }

    # Separa comuns vs únicas
    common = {s: {"count": c, "kind": string_kind[s]} for s, c in string_freq.items() if c >= MIN_REPEAT}
    common_sorted = dict(sorted(common.items(), key=lambda kv: -kv[1]["count"]))

    (OUT_DIR / "common_dictionary.json").write_text(
        json.dumps(common_sorted, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    for slug, data in page_data.items():
        # marca quais static_texts são "comuns" (já cobertos pelo dicionário) vs únicos da página
        unique_texts = [(k, t) for k, t in data["static_texts"] if t not in common]
        data["unique_texts"] = unique_texts
        del data["static_texts"]
        (OUT_DIR / "pages" / f"{slug}.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    report = {
        "total_pages_scanned": len(files),
        "pages_with_tool_config": sum(1 for d in page_data.values() if d["has_tool_config"]),
        "pages_with_json_parse_error": parse_errors,
        "unique_strings_total": len(string_freq),
        "common_dictionary_entries": len(common),
        "min_repeat_threshold": MIN_REPEAT,
    }
    (OUT_DIR / "scan_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
