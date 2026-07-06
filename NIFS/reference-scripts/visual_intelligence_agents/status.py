"""Status collector for Visual Intelligence Platform."""
from __future__ import annotations

from pathlib import Path

from paths import MD, OG_OUT, canonical, og_manifest, og_templates


def collect_status() -> dict:
    canon = canonical()
    manifest = og_manifest()
    entries = manifest.get("entries", {})
    templates = og_templates().get("templates", {})

    og_files = list(OG_OUT.glob("*")) if OG_OUT.exists() else []
    svg_count = sum(1 for f in og_files if f.suffix == ".svg")
    jpg_count = sum(1 for f in og_files if f.suffix in (".jpg", ".jpeg", ".png"))

    audited = 0
    for entry in entries.values():
        asset = entry.get("asset") or entry.get("svg")
        if asset:
            p = Path(__file__).resolve().parent.parent.parent / "website" / "assets" / "images" / asset
            if p.exists():
                audited += 1

    return {
        "program": canon.get("program_code", "VEIP"),
        "schema_version": canon.get("schema_version"),
        "templates_total": len(templates),
        "manifest_entries": len(entries),
        "og_files_svg": svg_count,
        "og_files_raster": jpg_count,
        "assets_on_disk": audited,
        "completion_pct": round(100 * len(entries) / max(len(templates), 1), 1),
        "og_spec": canon.get("og_spec", {}),
        "master_data_path": str(MD),
        "output_path": str(OG_OUT),
        "entries": entries,
    }
