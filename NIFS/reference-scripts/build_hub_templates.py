"""Merge legacy hub_*.json files into datasets/content/hub_templates.json."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from content_paths import ROOT

CONTENT = ROOT / "datasets" / "content"
ARCHIVE = ROOT / "datasets" / "archive" / "content"

LEGACY_FILES = {
    "protocols": "hub_protocols.json",
    "tools": "hub_tools.json",
    "artigos": "hub_artigos.json",
    "simulados": "hub_simulados.json",
    "library": "hub_library.json",
    "flashcards": "hub_flashcards.json",
}


def main() -> int:
    hubs: dict = {}
    for key, filename in LEGACY_FILES.items():
        path = CONTENT / filename
        if path.exists():
            hubs[key] = json.loads(path.read_text(encoding="utf-8"))

    listings_path = CONTENT / "hub_listings.json"
    if listings_path.exists():
        listings = json.loads(listings_path.read_text(encoding="utf-8"))
        hubs.update(listings.get("hubs", {}))

    out = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "schema_version": "2026.2.0",
        "entity": "HubTemplates",
        "description": "Unified hub page chrome; item lists built at runtime from datasets.",
        "hubs": hubs,
    }
    dst = CONTENT / "hubs" / "hub_templates.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {dst} ({len(hubs)} hubs)")

    ARCHIVE.mkdir(parents=True, exist_ok=True)
    manifest = {
        "archived_at": out["generated_at"],
        "reason": "Merged into hub_templates.json — UI chrome only, not entity payloads.",
        "files": list(LEGACY_FILES.values()) + ["hub_listings.json"],
        "replacement": "datasets/content/hubs/hub_templates.json",
        "loader": "scripts/hub_config_lib.py",
    }
    (ARCHIVE / "hub_legacy_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    print(f"Manifest: {ARCHIVE / 'hub_legacy_manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
