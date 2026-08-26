"""Dual-render parity: fetch and inline pages must share the same text content."""

from __future__ import annotations

import re
from pathlib import Path

from engine.paths import FETCH_DIR, INLINE_DIR


_TAG = re.compile(r"<[^>]+>")
_SPACE = re.compile(r"\s+")
_STYLE = re.compile(r"<style\b[^>]*>.*?</style>", re.IGNORECASE | re.DOTALL)
_SCRIPT = re.compile(r"<script\b[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
_LINK = re.compile(r"<link\b[^>]*>", re.IGNORECASE)


def _text(html: str) -> str:
    html = _STYLE.sub(" ", html)
    html = _SCRIPT.sub(" ", html)
    html = _LINK.sub(" ", html)
    return _SPACE.sub(" ", _TAG.sub(" ", html)).strip()


def check_parity(fetch_dir: Path | None = None, inline_dir: Path | None = None) -> dict:
    fetch_dir = fetch_dir or FETCH_DIR
    inline_dir = inline_dir or INLINE_DIR
    findings = []
    if not fetch_dir.exists() or not inline_dir.exists():
        return {"status": "HOLD", "findings": [{"id": "RENDER_MISSING", "reason": "Árvores fetch/inline ainda não geradas."}]}

    fetch_pages = {path.relative_to(fetch_dir): path for path in fetch_dir.rglob("*.html")}
    inline_pages = {path.relative_to(inline_dir): path for path in inline_dir.rglob("*.html")}
    if set(fetch_pages) != set(inline_pages):
        findings.append({
            "id": "PAGE_SET_MISMATCH",
            "reason": f"fetch={sorted(map(str, fetch_pages))} inline={sorted(map(str, inline_pages))}",
        })
    for rel in sorted(set(fetch_pages) & set(inline_pages)):
        fetch_text = _text(fetch_pages[rel].read_text(encoding="utf-8"))
        inline_text = _text(inline_pages[rel].read_text(encoding="utf-8"))
        if fetch_text != inline_text:
            findings.append({
                "id": "TEXT_MISMATCH",
                "reason": str(rel),
            })
    return {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "pagesCompared": len(set(fetch_pages) & set(inline_pages)),
    }
