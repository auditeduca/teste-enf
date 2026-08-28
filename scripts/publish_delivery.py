#!/usr/bin/env python3
"""Publica NIFS/DELIVERY para layout de produção (HTML na raiz do site)."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
DELIVERY = WORKSPACE / "NIFS" / "DELIVERY"
SOURCE_HTML = DELIVERY / "html"
ASSET_DIRS = ("css", "js", "partials", "images", "fonts")


def publish(*, dry_run: bool = False) -> dict:
    stats = {"html_copied": 0, "root_files": 0, "skipped": 0}

    if not SOURCE_HTML.is_dir():
        raise SystemExit(f"Pasta fonte não encontrada: {SOURCE_HTML}")

    for html_file in sorted(SOURCE_HTML.glob("*.html")):
        dest = DELIVERY / html_file.name
        if dest.exists() and dest.read_bytes() == html_file.read_bytes():
            stats["skipped"] += 1
            continue
        if not dry_run:
            shutil.copy2(html_file, dest)
        stats["html_copied"] += 1

    for name in ("sitemap.xml", "robots.txt"):
        src = DELIVERY / "root" / name
        if not src.is_file():
            src = DELIVERY / name
        if src.is_file():
            dest = DELIVERY / name
            if not dry_run:
                shutil.copy2(src, dest)
            stats["root_files"] += 1

    if (DELIVERY / "manifest.json").is_file():
        stats["root_files"] += 1

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Publicar DELIVERY para layout de produção")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    stats = publish(dry_run=args.dry_run)
    mode = "DRY-RUN" if args.dry_run else "OK"
    print(
        f"[{mode}] html_copied={stats['html_copied']} "
        f"skipped={stats['skipped']} root_files={stats['root_files']}"
    )
    print(f"Site pronto em: {DELIVERY}")
    print(f"Preview: cd {DELIVERY} && python3 -m http.server 8765")


if __name__ == "__main__":
    main()
