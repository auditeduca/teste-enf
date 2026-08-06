# -*- coding: utf-8 -*-
"""
Valida identidade visual/estrutural das páginas de conteúdo CKO.

Uso:
  python tools/validate_content_identity.py
  python tools/validate_content_identity.py --file time-de-resposta-rapida.html
  python tools/validate_content_identity.py --strict   # warnings viram falha
  python tools/validate_content_identity.py --json report.json

Critérios: data/cko-content-identity.json + presença de shell/layout/módulos.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDENTITY_PATH = ROOT / "data" / "cko-content-identity.json"
SHELL_CATALOG = ROOT / "data" / "cko-shell-pages.json"
CONTENT_DIR = ROOT / "data" / "content"


@dataclass
class Issue:
    severity: str  # error | warn | info
    code: str
    message: str
    file: str


def load_identity() -> dict:
    return json.loads(IDENTITY_PATH.read_text(encoding="utf-8"))


def page_id_for(path: Path) -> str | None:
    rel = path.relative_to(ROOT).as_posix()
    mapping = {
        "biblioteca-cirurgica.html": "cirurgica",
        "biblioteca-curativo.html": "curativo",
        "biblioteca-seringa.html": "seringa",
        "biblioteca-provas.html": "provas",
        "biblioteca-carinho-de-emergencia.html": "carinho",
        "biblioteca/artigo-carrinho-de-emergencia-enfermagem.html": "carinho-artigo",
        "time-de-resposta-rapida.html": "trr",
    }
    if rel in mapping:
        return mapping[rel]
    # data-cko-page first mount
    text = path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r'data-cko-page="([^"]+)"', text)
    if m:
        return m.group(1)
    return path.stem.lower()[:64]


def collect_targets(single: str | None) -> list[Path]:
    if single:
        p = ROOT / single
        if not p.is_file():
            raise SystemExit(f"Arquivo não encontrado: {single}")
        return [p]
    catalog = json.loads(SHELL_CATALOG.read_text(encoding="utf-8"))
    # Prefer HTML files that already reference shell
    targets: list[Path] = []
    for p in sorted(ROOT.glob("*.html")):
        t = p.read_text(encoding="utf-8", errors="ignore")
        if "cko-page-shell.js" in t or "cko-layout" in t:
            targets.append(p)
    art = ROOT / "biblioteca" / "artigo-carrinho-de-emergencia-enfermagem.html"
    if art.is_file() and art not in targets:
        t = art.read_text(encoding="utf-8", errors="ignore")
        if "cko-page-shell.js" in t or "cko-layout" in t:
            targets.append(art)
    # ensure catalog pages with known files
    _ = catalog  # catalog used as scope signal
    return targets


def validate_file(path: Path, identity: dict) -> list[Issue]:
    rel = path.relative_to(ROOT).as_posix()
    text = path.read_text(encoding="utf-8", errors="ignore")
    issues: list[Issue] = []

    def add(sev: str, code: str, msg: str) -> None:
        issues.append(Issue(sev, code, msg, rel))

    # Assets
    for css in identity.get("requiredAssets", {}).get("css", []):
        # content-modules css is required for engine pages; soft for shell-only
        if css.endswith("cko-content-modules.css"):
            if "cko-content-engine.js" in text and css not in text:
                add("error", "css-modules", f"Falta {css}")
            elif css not in text:
                add("warn", "css-modules", f"Ainda sem {css} (módulos A–F)")
            continue
        if css not in text:
            add("error", "css", f"Falta {css}")

    for js in identity.get("requiredAssets", {}).get("js", []):
        if js.endswith("cko-content-engine.js"):
            if js not in text:
                add("warn", "js-engine", f"Ainda sem {js}")
            continue
        if js not in text:
            add("error", "js", f"Falta {js}")

    body_cls = identity.get("requiredBodyClass", "cko-cart-page")
    if body_cls not in text:
        add("error", "body-class", f"body sem classe {body_cls}")

    layout = identity.get("requiredLayout", {})
    if layout.get("wrapper", "cko-layout") not in text:
        add("error", "layout", "cko-layout ausente")
    if layout.get("main", "cko-layout__main") not in text:
        add("error", "layout-main", "cko-layout__main ausente")
    if 'data-cko-slot="sidebar"' not in text and layout.get("side", "cko-layout__side") not in text:
        add("error", "sidebar", "sidebar/slot ausente")

    for slot in identity.get("requiredSlots", []):
        if f'data-cko-slot="{slot}"' not in text:
            # hero optional only for product pages with null hero
            if slot == "hero" and ("cko-cart-root" in text or 'data-cko-page="carinho"' in text):
                add("info", "hero-product", "Hero via produto (carrinho) — ok")
                continue
            add("error", f"slot-{slot}", f"slot {slot} ausente")

    # aside is optional (aviso/copyright card removed by default via hideAside)
    if 'data-cko-slot="aside"' not in text:
        add("info", "aside-optional", "slot aside ausente (ok — hideAside)")

    if 'id="main-content"' not in text and "<main" not in text.lower():
        add("error", "main", "<main id=main-content> ausente")

    if "</main>" not in text.lower():
        add("error", "main-close", "</main> ausente")

    # Forbidden
    for rule in identity.get("forbiddenPatterns", []):
        pat = rule.get("pattern", "")
        if not pat:
            continue
        if re.search(pat, text, re.I):
            add(rule.get("severity", "error"), rule.get("id", "forbidden"), rule.get("message", pat))

    # H2 ids for TOC
    if not re.search(r"<h2[^>]*\bid\s*=", text, re.I):
        add("warn", "h2-ids", "Nenhum H2 com id (TOC automático fica vazio)")

    # Content engine mount + manifest
    pid = page_id_for(path)
    has_mount = bool(re.search(r'data-cko-content="[^"]+"', text))
    if not has_mount:
        add("warn", "content-mount", "Sem mount data-cko-content (módulos FAQ/related/refs)")
    else:
        m = re.search(r'data-cko-content="([^"]+)"', text)
        pid = m.group(1) if m else pid
        man_path = CONTENT_DIR / f"{pid}.json"
        if not man_path.is_file():
            add("error", "manifest-missing", f"Manifesto ausente: data/content/{pid}.json")
        else:
            try:
                man = json.loads(man_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                add("error", "manifest-json", f"JSON inválido em {man_path.name}: {e}")
                man = None
            if man:
                if man.get("pageId") != pid:
                    add("warn", "pageId-mismatch", f"pageId do manifesto ({man.get('pageId')}) ≠ {pid}")
                for mod in identity.get("requiredModules", []):
                    arr = man.get(mod)
                    if not isinstance(arr, list) or not arr:
                        add("error", f"mod-{mod}", f"Manifesto sem módulo {mod}")
                faq = man.get("faq") or []
                if isinstance(faq, list) and len(faq) < 4:
                    add("warn", "faq-min", f"FAQ com {len(faq)} itens (mínimo recomendado: 4)")
                related = man.get("related") or []
                if isinstance(related, list) and len(related) < 3:
                    add("warn", "related-min", f"Relacionados com {len(related)} (mínimo: 3)")
                for i, media in enumerate(man.get("media") or []):
                    if media.get("role") == "protocol-figure" and not media.get("mobile"):
                        add("warn", "media-mobile", f"media[{i}] protocol-figure sem mobile")
                    if not media.get("source") or str(media.get("source", "")).startswith("PENDENTE"):
                        add("warn", "media-source", f"media[{i}] source pendente/ausente")

    # Duplicate H1 in static HTML (hero is injected — H1 in article is legacy)
    # Count h1 tags in source (shell hero not in source)
    h1_count = len(re.findall(r"<h1\b", text, re.I))
    if h1_count > 0:
        add("warn", "static-h1", f"{h1_count} H1 estático(s) — hero shell já injeta H1")

    return issues


def main() -> int:
    ap = argparse.ArgumentParser(description="Valida identidade visual de conteúdo CKO")
    ap.add_argument("--file", help="Validar um HTML relativo à raiz do site")
    ap.add_argument("--strict", action="store_true", help="Warnings contam como falha")
    ap.add_argument("--json", dest="json_out", help="Escrever relatório JSON")
    args = ap.parse_args()

    if not IDENTITY_PATH.is_file():
        print("ERROR: data/cko-content-identity.json não encontrado", file=sys.stderr)
        return 2

    identity = load_identity()
    targets = collect_targets(args.file)
    all_issues: list[Issue] = []
    for p in targets:
        all_issues.extend(validate_file(p, identity))

    errors = [i for i in all_issues if i.severity == "error"]
    warns = [i for i in all_issues if i.severity == "warn"]
    infos = [i for i in all_issues if i.severity == "info"]

    # Group by file for human output
    by_file: dict[str, list[Issue]] = {}
    for i in all_issues:
        by_file.setdefault(i.file, []).append(i)

    print(f"CKO Content Identity Validator — {len(targets)} arquivo(s)")
    print(f"identity v{identity.get('version', '?')} — {IDENTITY_PATH.name}")
    print("---")
    for f, items in sorted(by_file.items()):
        e = sum(1 for x in items if x.severity == "error")
        w = sum(1 for x in items if x.severity == "warn")
        if e == 0 and w == 0:
            continue
        print(f"{f}  errors={e} warns={w}")
        for x in items:
            if x.severity == "info":
                continue
            print(f"  [{x.severity}] {x.code}: {x.message}")

    print("---")
    print(f"totals  files={len(targets)} errors={len(errors)} warns={len(warns)} infos={len(infos)}")

    if args.json_out:
        out = {
            "files": len(targets),
            "errors": len(errors),
            "warns": len(warns),
            "issues": [asdict(i) for i in all_issues],
        }
        Path(args.json_out).write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("wrote", args.json_out)

    if errors:
        return 1
    if args.strict and warns:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
