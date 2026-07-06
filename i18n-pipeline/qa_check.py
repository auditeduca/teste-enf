#!/usr/bin/env python3
"""QA pós-tradução — valida as páginas geradas de um idioma.

Checa por página:
  - tool-config é JSON válido (quando a raiz tem tool-config);
  - <html lang> correto e bloco hreflang completo (31 alternates);
  - <title> difere do pt (foi traduzido);
  - resíduo de português no texto visível (heurística: contagem de tokens
    tipicamente pt como "ção", "não", "õe") — compara com a página raiz.

Uso: python qa_check.py --lang es [--limit N] [--verbose]
Sai com código 1 se houver falhas estruturais (JSON inválido etc).
"""

import argparse
import json
import re
import sys
from pathlib import Path

PIPELINE = Path(__file__).resolve().parent
SITE = PIPELINE.parent / "reference-website"

PT_TOKENS = re.compile(r"ção|ções|não\b|õe|çã|Avaliação|resultado será exibido", re.I)
TAGS = re.compile(r"<script\b.*?</script>|<style\b.*?</style>|<[^>]+>", re.S | re.I)
CFG_RX = re.compile(r'<script[^>]*id=["\']tool-config["\'][^>]*>(.*?)</script>', re.S)


def visible_text(html: str) -> str:
    return TAGS.sub(" ", html)


def pt_score(html: str) -> int:
    return len(PT_TOKENS.findall(visible_text(html)))


def check_page(name: str, lang: str) -> dict:
    root_f = SITE / f"{name}.html"
    tgt_f = SITE / lang / f"{name}.html"
    r: dict = {"page": name, "errors": [], "warnings": []}
    if not tgt_f.is_file():
        r["errors"].append("página alvo inexistente")
        return r
    root = root_f.read_text(encoding="utf-8")
    tgt = tgt_f.read_text(encoding="utf-8")

    if CFG_RX.search(root):
        m = CFG_RX.search(tgt)
        if not m:
            r["errors"].append("tool-config ausente no alvo")
        else:
            try:
                json.loads(m.group(1))
            except Exception as e:
                r["errors"].append(f"tool-config JSON inválido: {e}")

    if f'lang="{lang}"' not in tgt.split(">", 1)[0] + ">":
        m = re.search(r'<html[^>]*lang="([^"]*)"', tgt)
        if not m or m.group(1) != lang:
            r["errors"].append(f"<html lang> = {m.group(1) if m else '?'}")

    n_alt = len(re.findall(r'rel="alternate"[^>]*hreflang=|hreflang=[^>]*rel="alternate"', tgt))
    if n_alt != 31:
        r["warnings"].append(f"hreflang={n_alt} (esperado 31)")

    rt = re.search(r"<title>(.*?)</title>", root, re.S)
    tt = re.search(r"<title>(.*?)</title>", tgt, re.S)
    if rt and tt and rt.group(1).strip() == tt.group(1).strip():
        r["warnings"].append("title idêntico ao pt (não traduzido)")

    root_pt, tgt_pt = pt_score(root), pt_score(tgt)
    r["pt_residual"] = tgt_pt
    r["pt_root"] = root_pt
    if root_pt and tgt_pt > 0.30 * root_pt:
        r["warnings"].append(f"resíduo pt alto: {tgt_pt}/{root_pt} tokens")
    return r


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    pages = sorted(f.stem for f in (PIPELINE / "extracted" / "pages").glob("*.json"))
    if args.limit:
        pages = pages[:args.limit]

    n_err = n_warn = n_ok = 0
    residuals = []
    for name in pages:
        r = check_page(name, args.lang)
        if r["errors"]:
            n_err += 1
            print(f"ERRO  {name}: {'; '.join(r['errors'])}")
        elif r["warnings"]:
            n_warn += 1
            if args.verbose:
                print(f"aviso {name}: {'; '.join(r['warnings'])}")
        else:
            n_ok += 1
        if "pt_residual" in r:
            residuals.append((r["pt_residual"], r.get("pt_root", 0), name))

    print(f"\n[{args.lang}] OK: {n_ok} | avisos: {n_warn} | erros: {n_err} "
          f"(de {len(pages)} páginas)")
    residuals.sort(reverse=True)
    print("maiores resíduos pt (tokens alvo/raiz):")
    for res, root, name in residuals[:10]:
        print(f"  {name}: {res}/{root}")
    sys.exit(1 if n_err else 0)


if __name__ == "__main__":
    main()
