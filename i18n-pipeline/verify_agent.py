#!/usr/bin/env python3
"""Agente de verificação de tradução — assegura 100% de cobertura.

Ciclo por página (pt original × página gerada no idioma alvo):
  1. DETECTA: unidades de texto que ficaram IDÊNTICAS ao português
     (nós de texto do corpo + strings do tool-config + metas).
  2. TRIAGEM local: descarta o que obviamente pode ficar igual
     (nomes próprios de escalas, códigos, números, URLs, sem letras).
  3. JULGA via LLM (DeepSeek): para cada string restante, decide
     `keep` (cognato/citação/nome — correta ficar igual) ou
     `translate` (ficou sem tradução) — e nesse caso já traduz.
  4. CORRIGE: aplica as traduções na página e grava as decisões em
     translations/{lang}/_verify_fixes.json (overlay do dicionário
     global; decisões `keep` não são re-julgadas em execuções futuras).
  5. RELATA cobertura: unidades totais, traduzidas, iguais legítimas,
     corrigidas, irredutíveis.

Uso:
  python verify_agent.py --lang es --pages abcd2.html          # relatório+fix
  python verify_agent.py --lang es --all --report-only
  python verify_agent.py --lang es --all --limit 20
"""

import argparse
import json
import re
import sys
from pathlib import Path

from scanner_deep import TextCollector
from translate_clinical import (
    LANG_NAMES, PIPELINE, SITE, collect_strings, deepseek_judge,
    load_env, load_global_tm, replace_bounded, replace_text,
)

CFG_RX = re.compile(r'<script[^>]*id=["\']tool-config["\'][^>]*>(.*?)</script>', re.S)

# o parser converte entidades (&lt; -> <); para substituir no HTML bruto,
# cada caractere convertível precisa casar com sua forma literal OU entidade
ENTITY_FORMS = {
    "<": "(?:<|&lt;)", ">": "(?:>|&gt;)", "&": "(?:&|&amp;)",
    '"': '(?:"|&quot;)', "'": "(?:'|&#39;|&apos;)", "\xa0": "(?:\xa0|&nbsp;)",
}


def entity_tolerant_sub(html: str, src: str, dst: str) -> tuple[str, int]:
    pat = "".join(ENTITY_FORMS.get(c, re.escape(c)) for c in src)
    rx = re.compile(r"(?<![A-Za-zÀ-ÿ])" + pat + r"(?![A-Za-zÀ-ÿ])")
    dst_esc = (dst.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
               .replace("\\", "\\\\"))
    return rx.subn(dst_esc, html)
CODEY = re.compile(r"^[\dA-Z()\[\]{}Α-Ωα-ω .,:;+*/%=<>≤≥±°'\"-]+$")
URLISH = re.compile(r"https?://|www\.|@|\.html?\b")
REF_HINT = re.compile(r"\b(19|20)\d{2}\b.*\.|;\s*v\. \d|\bet al\b|\bed\.\b")


def page_units(html: str) -> list[str]:
    tc = TextCollector()
    tc.feed(html)
    units = tc.texts + tc.attrs
    m = CFG_RX.search(html)
    if m:
        try:
            units += collect_strings(json.loads(m.group(1)))
        except Exception:
            pass
    return [u for u in dict.fromkeys(units) if len(u.strip()) >= 4]


def local_triage(s: str, proper: list[str]) -> str | None:
    """Retorna motivo de 'keep' local, ou None (segue para o juiz)."""
    if not re.search(r"[A-Za-zÀ-ÿ]", s):
        return "sem letras"
    if CODEY.match(s):
        return "código/fórmula"
    if URLISH.search(s):
        return "URL/arquivo"
    low = s.lower()
    for p in proper:
        if low == p.lower():
            return "nome próprio (lista)"
    if REF_HINT.search(s) and len(s) > 60:
        return "citação bibliográfica"
    return None


def fixes_path(lang: str) -> Path:
    return PIPELINE / "translations" / lang / "_verify_fixes.json"


def load_fixes(lang: str) -> dict:
    p = fixes_path(lang)
    if p.is_file():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"lang": lang, "keep": {}, "translate": {}}


def save_fixes(lang: str, fixes: dict) -> None:
    p = fixes_path(lang)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(fixes, ensure_ascii=False, indent=1), encoding="utf-8")


def verify_page(name: str, lang: str, proper: list[str], tm: dict,
                fixes: dict, fix: bool) -> dict:
    root_f = SITE / f"{name}.html"
    tgt_f = SITE / lang / f"{name}.html"
    stats = {"page": name, "units": 0, "identical": 0, "keep_local": 0,
             "keep_prior": 0, "keep_judge": 0, "fixed": 0, "residual": 0}
    if not root_f.is_file() or not tgt_f.is_file():
        stats["error"] = "página ausente"
        return stats

    root_units = set(page_units(root_f.read_text(encoding="utf-8")))
    tgt_html = tgt_f.read_text(encoding="utf-8")
    tgt_units = page_units(tgt_html)
    stats["units"] = len(root_units)

    identical = [u for u in tgt_units if u in root_units]
    stats["identical"] = len(identical)

    to_judge = []
    for s in identical:
        if s in fixes["keep"]:
            stats["keep_prior"] += 1
        elif s in fixes["translate"]:
            pass  # já tem tradução conhecida; vai direto para aplicação
        elif local_triage(s, proper):
            stats["keep_local"] += 1
        else:
            to_judge.append(s)

    if to_judge:
        verdicts = deepseek_judge(to_judge, LANG_NAMES.get(lang, lang), proper)
        for s, v in verdicts.items():
            t = (v.get("translation") or "").strip()
            if v.get("action") == "translate" and t and t != s.strip():
                fixes["translate"][s] = v["translation"]
            else:
                # inclui o caso "tradução idêntica" — cognato exato no idioma alvo
                fixes["keep"][s] = v.get("reason", "juiz: forma idêntica correta")
                stats["keep_judge"] += 1

    pending = [(s, fixes["translate"][s]) for s in identical if s in fixes["translate"]]
    if fix and pending:
        tgt_html, n1 = replace_bounded(tgt_html, pending)
        tgt_html, n2 = replace_text(tgt_html, [(s, t) for s, t in pending if len(s) >= 15])
        for s, t in pending:  # fallback: nós de texto com entidades HTML
            tgt_html, _ = entity_tolerant_sub(tgt_html, s, t)
        tgt_f.write_text(tgt_html, encoding="utf-8", newline="")
        still = [s for s, _ in pending if s in page_units(tgt_html)]
        stats["fixed"] = len(pending) - len(still)
        stats["residual"] = len(still)
    else:
        stats["residual"] = len(pending)
    return stats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", required=True)
    ap.add_argument("--pages", nargs="*", default=[])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--report-only", action="store_true")
    args = ap.parse_args()
    load_env()

    pages = [p[:-5] if p.endswith(".html") else p for p in args.pages]
    if args.all:
        pages = sorted(f.stem for f in (PIPELINE / "extracted" / "pages").glob("*.json"))
    if args.limit:
        pages = pages[:args.limit]
    if not pages:
        ap.error("informe --pages ou --all")

    proper = []
    pn = PIPELINE / "extracted" / "common_proper_nouns.json"
    if pn.is_file():
        data = json.loads(pn.read_text(encoding="utf-8"))
        proper = data if isinstance(data, list) else list(data)

    tm = load_global_tm(args.lang)
    fixes = load_fixes(args.lang)
    tot = {"units": 0, "identical": 0, "fixed": 0, "residual": 0,
           "keep": 0}
    for name in pages:
        s = verify_page(name, args.lang, proper, tm, fixes, not args.report_only)
        save_fixes(args.lang, fixes)
        keep = s["keep_local"] + s["keep_prior"] + s["keep_judge"]
        tot["units"] += s["units"]; tot["identical"] += s["identical"]
        tot["fixed"] += s["fixed"]; tot["residual"] += s["residual"]
        tot["keep"] += keep
        cover = 100.0 * (1 - s["residual"] / s["units"]) if s["units"] else 100.0
        print(f"[{name}] unidades={s['units']} iguais={s['identical']} "
              f"legítimas={keep} corrigidas={s['fixed']} "
              f"pendentes={s['residual']} cobertura={cover:.1f}%")

    cov = 100.0 * (1 - tot["residual"] / tot["units"]) if tot["units"] else 100.0
    print(f"\n[{args.lang}] TOTAL: {tot['units']} unidades | {tot['identical']} iguais "
          f"| {tot['keep']} legítimas | {tot['fixed']} corrigidas | "
          f"{tot['residual']} pendentes | cobertura {cov:.1f}%")
    sys.exit(1 if tot["residual"] else 0)


if __name__ == "__main__":
    main()
