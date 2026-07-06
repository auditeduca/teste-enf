#!/usr/bin/env python3
"""Optimize static assets — minify CSS/JS and convert images to WebP.

Usage:
  python scripts/optimize_assets.py --minify
  python scripts/optimize_assets.py --webp
  python scripts/optimize_assets.py --all
  python scripts/optimize_assets.py --webp --quality 85 --max-width 1600
  python scripts/optimize_assets.py --minify --in-place
  python scripts/optimize_assets.py --webp --update-refs
  python scripts/optimize_assets.py --all --apply-build

Writes datasets/metadata/asset_optimization_report.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
ASSETS = ROOT / "website" / "assets"
REPORT = ROOT / "datasets" / "metadata" / "asset_optimization_report.json"
NOW = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

sys.path.insert(0, str(SCRIPTS))

from image_webp_lib import convert_tree_to_webp, format_bytes  # noqa: E402
from minify_lib import minify_tree  # noqa: E402

REF_EXTENSIONS = (".py", ".json", ".html", ".js", ".jsx", ".css", ".md")


def update_png_refs_to_webp(root: Path) -> list[dict]:
    """Rewrite .png/.jpg references to .webp in source files (after conversion)."""
    changes: list[dict] = []
    pattern = re.compile(
        r'([\w./-]+)\.(png|jpe?g)(?=["\'\s>)])',
        re.I,
    )
    scan_roots = [
        ROOT / "scripts",
        ROOT / "datasets",
        ROOT / "website" / "assets",
    ]
    for base in scan_roots:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in REF_EXTENSIONS:
                continue
            if "node_modules" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            new_text, n = pattern.subn(
                lambda m: f"{m.group(1)}.webp" if (ASSETS / "images" / f"{Path(m.group(1)).name}.webp").exists()
                or (ROOT / m.group(1)).with_suffix(".webp").exists()
                else m.group(0),
                text,
            )
            if n:
                path.write_text(new_text, encoding="utf-8", newline="\n")
                changes.append({"file": str(path.relative_to(ROOT)), "replacements": n})
    return changes


def apply_minified_to_build(out_dir: Path) -> int:
    """Replace .css/.js in build output with .min versions when present."""
    assets = out_dir / "assets"
    if not assets.exists():
        return 0
    swapped = 0
    for ext in (".css", ".js"):
        for mini in list(assets.rglob(f"*.min{ext}")):
            base_name = mini.name.replace(f".min{ext}", ext)
            original = mini.parent / base_name
            if original.exists():
                original.write_bytes(mini.read_bytes())
                mini.unlink()
                swapped += 1
    return swapped


def main() -> int:
    ap = argparse.ArgumentParser(description="Minify CSS/JS and convert images to WebP")
    ap.add_argument("--minify", action="store_true", help="Minify CSS and JS")
    ap.add_argument("--webp", action="store_true", help="Convert raster images to WebP")
    ap.add_argument("--all", action="store_true", help="Minify + WebP")
    ap.add_argument("--src", type=Path, default=ASSETS, help="Assets root (default: website/assets)")
    ap.add_argument("--in-place", action="store_true", help="Write .min.css/.min.js alongside sources")
    ap.add_argument("--quality", type=int, default=82, help="WebP quality 1-100")
    ap.add_argument("--max-width", type=int, default=1920, help="Max image width (0 = no resize)")
    ap.add_argument("--delete-source", action="store_true", help="Remove original after WebP")
    ap.add_argument("--update-refs", action="store_true", help="Rewrite .png/.jpg refs to .webp in scripts/datasets")
    ap.add_argument("--apply-build", action="store_true", help="Apply .min files to website/pt/assets after minify")
    args = ap.parse_args()

    if not (args.minify or args.webp or args.all):
        args.all = True

    src = args.src.resolve()
    report: dict = {"ran_at": NOW, "src": str(src.relative_to(ROOT)), "minify": [], "webp": [], "ref_updates": []}

    print("=" * 56)
    print("CALENF-NKD — otimização de assets")
    print(f"  Source: {src}")
    print("=" * 56)

    if args.minify or args.all:
        css_dir = src / "css"
        js_dir = src / "js"
        minify_results: list[dict] = []
        for sub in (css_dir, js_dir):
            if sub.exists():
                minify_results.extend(
                    minify_tree(sub, in_place=args.in_place, suffix=".min")
                )
        report["minify"] = minify_results
        total_before = sum(r["before_bytes"] for r in minify_results)
        total_after = sum(r["after_bytes"] for r in minify_results)
        print(f"\n[minify] {len(minify_results)} ficheiros")
        print(f"  Antes:  {format_bytes(total_before)}")
        print(f"  Depois: {format_bytes(total_after)}")
        print(f"  Poupança: {format_bytes(total_before - total_after)} ({round((total_before - total_after) / max(total_before, 1) * 100, 1)}%)")

        if args.apply_build:
            out = ROOT / "website" / "pt"
            swapped = apply_minified_to_build(out)
            print(f"  Build apply: {swapped} ficheiros substituídos em website/pt/assets")

    if args.webp or args.all:
        img_dir = src / "images"
        if img_dir.exists():
            max_w = args.max_width if args.max_width > 0 else None
            webp_results = convert_tree_to_webp(
                img_dir,
                quality=args.quality,
                max_width=max_w,
                delete_source=args.delete_source,
            )
            report["webp"] = webp_results
            converted = [r for r in webp_results if not r.get("skipped")]
            total_before = sum(r.get("before_bytes", 0) for r in converted)
            total_after = sum(r.get("after_bytes", 0) for r in converted)
            print(f"\n[webp] {len(converted)} convertidos ({len(webp_results) - len(converted)} ignorados)")
            print(f"  Antes:  {format_bytes(total_before)}")
            print(f"  Depois: {format_bytes(total_after)}")
            print(f"  Poupança: {format_bytes(total_before - total_after)}")
        else:
            print(f"\n[webp] pasta não encontrada: {img_dir}")

    if args.update_refs:
        print("\n[refs] Atualizando referências png/jpeg → webp…")
        ref_changes = update_png_refs_to_webp(ROOT)
        report["ref_updates"] = ref_changes
        print(f"  {len(ref_changes)} ficheiros alterados")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"\nRelatório: {REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
