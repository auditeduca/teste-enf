#!/usr/bin/env python3
"""Mark the canonical breadcrumb/hero so the shell does not inject a duplicate.

Does not mutate Drive copies. Does not close B9. Human visual choices stay HOLD.
"""
from __future__ import annotations

import re
from pathlib import Path

GATE = Path(__file__).resolve().parents[1]
SITE = GATE.parent / "reference-website"
DRIVE = (
    GATE / "public" / "drive",
    GATE / "control-plane" / "drive-html",
)

SKIP_DIRS = {
    "ar", "bg", "cs", "da", "de", "en", "es", "fi", "fr", "hi", "hr", "hu",
    "id", "it", "ja", "ko", "nl", "no", "pl", "ro", "ru", "sl", "sr", "sv",
    "th", "tr", "uk", "vi", "zh", "docs", "docs-internos", "cdn-cgi",
}


def assert_not_drive(path: Path) -> None:
    resolved = path.resolve()
    for root in DRIVE:
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            continue
        raise SystemExit(f"refusing Drive write: {path}")


def add_attr(tag: str, name: str, value: str) -> str:
    if re.search(rf"\b{re.escape(name)}\s*=", tag):
        return tag
    return tag[:-1].rstrip() + f' {name}="{value}">'


def stamp_text(html: str) -> str:
    html = re.sub(
        r"<nav\b[^>]*class=\"[^\"]*(?:tpl-breadcrumb|crumbs)[^\"]*\"[^>]*>",
        lambda m: add_attr(m.group(0), "data-cko-static", "breadcrumb"),
        html,
        flags=re.I,
    )
    html = re.sub(
        r"<div\b[^>]*class=\"[^\"]*tool-header[^\"]*\"[^>]*>",
        lambda m: add_attr(m.group(0), "data-cko-static", "hero"),
        html,
        flags=re.I,
    )
    html = re.sub(
        r"<section\b[^>]*class=\"[^\"]*\bhero\b[^\"]*\"[^>]*>",
        lambda m: add_attr(m.group(0), "data-cko-static", "hero"),
        html,
        flags=re.I,
    )
    html = re.sub(
        r"<section\b[^>]*class=\"[^\"]*-card-navy[^\"]*\"[^>]*>",
        lambda m: add_attr(m.group(0), "data-cko-static", "hero"),
        html,
        flags=re.I,
    )
    html = re.sub(
        r"<section\b[^>]*class=\"[^\"]*cko-home-hero[^\"]*\"[^>]*>",
        lambda m: add_attr(m.group(0), "data-cko-static", "hero"),
        html,
        flags=re.I,
    )
    return html


def iter_pages() -> list[Path]:
    pages = []
    for path in sorted(SITE.glob("*.html")):
        pages.append(path)
    for path in sorted((SITE / "templates").glob("*.html")) if (SITE / "templates").is_dir() else []:
        pages.append(path)
    return pages


def main() -> None:
    changed = []
    for path in iter_pages():
        if path.parent.name in SKIP_DIRS:
            continue
        original = path.read_text(encoding="utf-8")
        stamped = stamp_text(original)
        if stamped == original:
            continue
        assert_not_drive(path)
        path.write_text(stamped, encoding="utf-8")
        changed.append(path.name)
    print(
        {
            "stamped": len(changed),
            "pages": [name for name in changed[:24]],
            "release": "HOLD / NOT_RELEASED",
        }
    )


if __name__ == "__main__":
    main()
