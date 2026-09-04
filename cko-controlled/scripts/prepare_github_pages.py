#!/usr/bin/env python3
"""Stage the CALENF runtime (reference-website) for GitHub Pages.

GitHub Pages is enabled on this repo but currently publishes the git root of
`main`, which has no site index. The runtime is `reference-website/`. This
script copies that tree, drops locale/admin/report paths (same ignore as
Firebase), injects <base href="/teste-enf/"> and rewrites root-absolute
asset URLs so the project site at https://auditeduca.github.io/teste-enf/
loads CSS/JS/partials.

Does not close B9. Does not claim production release. Does not mutate Drive.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "reference-website"
DEFAULT_OUT = ROOT / "_site"
DEFAULT_BASE = "/teste-enf"

SKIP_DIRS = {
    "ar", "bg", "cs", "da", "de", "en", "es", "fi", "fr", "hi", "hr", "hu",
    "id", "it", "ja", "ko", "nl", "no", "pl", "ro", "ru", "sl", "sr", "sv",
    "th", "tr", "uk", "vi", "zh", "docs", "docs-internos", "cdn-cgi",
    "scripts", "templates", "tools", "node_modules", ".git",
}
SKIP_FILES = {
    "cko-relatorio-tecnico-final.html",
    "grafo-clinico.html",
    "admin.html",
    "ativar-admin.html",
}
TEXT_SUFFIXES = {".html", ".css", ".js", ".mjs", ".svg", ".xml"}
ROOT_ABS = re.compile(r'(["\'])/(?!/)')
URL_ABS = re.compile(r"url\((['\"]?)/(?!/)")
FETCH_ABS = re.compile(r"fetch\((['\"])/(?!/)")
HEAD_OPEN = re.compile(r"(<head\b[^>]*>)", re.I)


def normalize_base(base: str) -> str:
    base = (base or DEFAULT_BASE).strip() or DEFAULT_BASE
    if not base.startswith("/"):
        base = "/" + base
    return base.rstrip("/") or "/"


def rewrite_text(text: str, base: str) -> str:
    if base == "/":
        return text
    text = ROOT_ABS.sub(rf"\1{base}/", text)
    text = URL_ABS.sub(rf"url(\1{base}/", text)
    text = FETCH_ABS.sub(rf"fetch(\1{base}/", text)
    return text


def inject_base(html: str, base: str) -> str:
    if base == "/":
        return html
    if re.search(r"<base\b", html, re.I):
        return html
    tag = f'<base href="{base}/">'
    if HEAD_OPEN.search(html):
        return HEAD_OPEN.sub(rf"\1\n{tag}", html, count=1)
    return tag + "\n" + html


def copy_filtered(src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    def ignore(directory: str, names: list[str]) -> set[str]:
        skipped = set()
        dir_path = Path(directory)
        for name in names:
            if name in SKIP_DIRS and (dir_path / name).is_dir():
                skipped.add(name)
            if name in SKIP_FILES:
                skipped.add(name)
        return skipped

    shutil.copytree(src, dest, dirs_exist_ok=True, ignore=ignore)


def rewrite_tree(dest: Path, base: str) -> int:
    n = 0
    for path in dest.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        original = path.read_text(encoding="utf-8", errors="replace")
        updated = rewrite_text(original, base)
        if path.suffix.lower() == ".html":
            updated = inject_base(updated, base)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            n += 1
    return n


def write_meta(dest: Path, base: str, rewritten: int) -> None:
    (dest / ".nojekyll").write_text("", encoding="utf-8")
    src_404 = ROOT / "cko-controlled" / "public" / "404.html"
    if src_404.is_file():
        html = inject_base(rewrite_text(src_404.read_text(encoding="utf-8"), base), base)
        (dest / "404.html").write_text(html, encoding="utf-8")
    elif (dest / "index.html").is_file():
        shutil.copyfile(dest / "index.html", dest / "404.html")
    payload = {
        "id": "CKO-GITHUB-PAGES-HOLD-1.0.0",
        "kind": "github-pages-runtime",
        "source": "reference-website",
        "base": base,
        "rewritten_files": rewritten,
        "release": "HOLD / NOT_RELEASED",
        "release_allowed": False,
        "url": f"https://auditeduca.github.io{base}/",
    }
    (dest / "cko-pages.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--base", default=DEFAULT_BASE)
    args = parser.parse_args()
    if not SITE.is_dir():
        raise SystemExit(f"missing CALENF runtime: {SITE}")
    base = normalize_base(args.base)
    dest = Path(args.out).resolve()
    copy_filtered(SITE, dest)
    rewritten = rewrite_tree(dest, base)
    write_meta(dest, base, rewritten)
    print(
        json.dumps(
            {
                "out": str(dest),
                "base": base,
                "rewritten": rewritten,
                "index": (dest / "index.html").is_file(),
                "aldrete": (dest / "aldrete.html").is_file(),
                "release": "HOLD / NOT_RELEASED",
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
