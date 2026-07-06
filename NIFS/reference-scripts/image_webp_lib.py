"""Convert raster images to WebP for web delivery."""
from __future__ import annotations

from pathlib import Path

RASTER_EXT = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff"}
SKIP_NAMES = frozenset({"favicon.ico"})


def _require_pillow():
    try:
        from PIL import Image  # type: ignore
        return Image
    except ImportError as exc:
        raise SystemExit(
            "Pillow required for WebP conversion.\n"
            "  pip install Pillow\n"
            "  or: pip install -r requirements-build.txt"
        ) from exc


def convert_image_to_webp(
    src: Path,
    dst: Path | None = None,
    *,
    quality: int = 82,
    method: int = 6,
    max_width: int | None = None,
    max_height: int | None = None,
    lossless: bool = False,
) -> dict:
    """Convert one image to WebP. Returns size stats."""
    Image = _require_pillow()
    src = Path(src)
    if not src.is_file():
        raise FileNotFoundError(src)

    out = Path(dst) if dst else src.with_suffix(".webp")
    before = src.stat().st_size

    with Image.open(src) as im:
        im.load()
        if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
            im = im.convert("RGBA")
        elif im.mode != "RGB":
            im = im.convert("RGB")

        w, h = im.size
        if max_width or max_height:
            mw = max_width or w
            mh = max_height or h
            im.thumbnail((mw, mh), Image.Resampling.LANCZOS)

        save_kw = {"format": "WEBP", "method": max(0, min(6, method))}
        if lossless:
            save_kw["lossless"] = True
        else:
            save_kw["quality"] = max(1, min(100, quality))

        out.parent.mkdir(parents=True, exist_ok=True)
        im.save(out, **save_kw)

    after = out.stat().st_size
    saved = before - after
    return {
        "src": str(src),
        "dst": str(out),
        "before_bytes": before,
        "after_bytes": after,
        "saved_bytes": saved,
        "saved_pct": round(saved / before * 100, 1) if before else 0,
        "width": im.size[0],
        "height": im.size[1],
    }


def convert_tree_to_webp(
    src_dir: Path,
    *,
    quality: int = 82,
    max_width: int | None = 1920,
    delete_source: bool = False,
    skip_existing: bool = True,
) -> list[dict]:
    """Convert all raster images under src_dir to sibling .webp files."""
    results: list[dict] = []
    for path in sorted(src_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in RASTER_EXT:
            continue
        if path.name.lower() in SKIP_NAMES:
            continue

        out = path.with_suffix(".webp")
        if skip_existing and out.exists() and out.stat().st_mtime >= path.stat().st_mtime:
            results.append({
                "src": str(path),
                "dst": str(out),
                "skipped": True,
                "reason": "webp newer or exists",
            })
            continue

        stat = convert_image_to_webp(
            path, out, quality=quality, max_width=max_width,
        )
        stat["skipped"] = False
        results.append(stat)

        if delete_source and out.exists():
            path.unlink()

    return results


def format_bytes(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n / (1024 * 1024):.2f} MB"
