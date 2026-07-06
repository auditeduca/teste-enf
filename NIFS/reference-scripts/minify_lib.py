"""CSS and JavaScript minifiers for static assets.

Uses csscompressor / rjsmin when installed; falls back to safe pure-Python
reducers so the pipeline works without optional deps.
"""
from __future__ import annotations

import re
from pathlib import Path

CSS_EXT = {".css"}
JS_EXT = {".js"}


def _try_csscompressor(text: str) -> str | None:
    try:
        import csscompressor  # type: ignore
        return csscompressor.compress(text)
    except Exception:
        return None


def _try_rjsmin(text: str) -> str | None:
    try:
        import rjsmin  # type: ignore
        return rjsmin.jsmin(text)
    except Exception:
        return None


def minify_css(text: str) -> str:
    compressed = _try_csscompressor(text)
    if compressed is not None:
        return compressed
    # Fallback: strip block comments, collapse whitespace
    out = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    out = re.sub(r"\s+", " ", out)
    out = re.sub(r"\s*([{}:;,>+~])\s*", r"\1", out)
    return out.strip()


def minify_js(text: str) -> str:
    compressed = _try_rjsmin(text)
    if compressed is not None:
        return compressed
    # Fallback: remove line comments and collapse whitespace (conservative)
    lines = []
    for line in text.splitlines():
        stripped = re.sub(r"(^|[^:])//.*", r"\1", line)
        lines.append(stripped.strip())
    return re.sub(r"\n{2,}", "\n", "\n".join(l for l in lines if l))


def minify_text(text: str, *, kind: str) -> str:
    if kind == "css":
        return minify_css(text)
    if kind == "js":
        return minify_js(text)
    raise ValueError(f"Unsupported kind: {kind}")


def minify_file(src: Path, dst: Path, *, kind: str | None = None) -> dict:
    """Minify one file; returns before/after byte sizes."""
    ext = src.suffix.lower()
    inferred = "css" if ext in CSS_EXT else "js" if ext in JS_EXT else None
    k = kind or inferred
    if not k:
        raise ValueError(f"Cannot infer kind for {src}")

    raw = src.read_text(encoding="utf-8")
    before = len(raw.encode("utf-8"))
    mini = minify_text(raw, kind=k)
    after = len(mini.encode("utf-8"))

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(mini, encoding="utf-8", newline="\n")

    saved = before - after
    return {
        "src": str(src),
        "dst": str(dst),
        "kind": k,
        "before_bytes": before,
        "after_bytes": after,
        "saved_bytes": saved,
        "saved_pct": round(saved / before * 100, 1) if before else 0,
    }


def minify_tree(
    src_dir: Path,
    dst_dir: Path | None = None,
    *,
    in_place: bool = False,
    suffix: str = ".min",
) -> list[dict]:
    """Minify all .css and .js under src_dir."""
    results: list[dict] = []
    for path in sorted(src_dir.rglob("*")):
        if not path.is_file():
            continue
        ext = path.suffix.lower()
        if ext not in CSS_EXT | JS_EXT:
            continue
        if suffix and f"{suffix}." in path.name:
            continue

        if in_place:
            out = path.with_name(f"{path.stem}{suffix}{path.suffix}")
        elif dst_dir:
            rel = path.relative_to(src_dir)
            stem = path.stem
            out = dst_dir / rel.parent / f"{stem}{suffix}{path.suffix}"
        else:
            out = path.with_name(f"{path.stem}{suffix}{path.suffix}")

        if not in_place and out == path:
            continue
        results.append(minify_file(path, out, kind="css" if ext == ".css" else "js"))
    return results
