"""Load unified hub page templates and hydrate live counts at build time."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from content_paths import CONTENT_ROOT, content_path

TEMPLATES_PATH = content_path("hub_templates")
_LEGACY_MAP = {
    "protocols": "hub_protocols.json",
    "tools": "hub_tools.json",
    "artigos": "hub_artigos.json",
    "simulados": "hub_simulados.json",
    "library": "hub_library.json",
    "flashcards": "hub_flashcards.json",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_hub_templates() -> dict[str, dict]:
    """Return all hub templates keyed by id (protocols, tools, quiz, …)."""
    if TEMPLATES_PATH.exists():
        data = _load_json(TEMPLATES_PATH)
        return data.get("hubs", data)

    # Fallback: assemble from legacy split files until hub_templates.json is generated.
    content = CONTENT_ROOT
    hubs: dict[str, dict] = {}
    for key, filename in _LEGACY_MAP.items():
        p = content / filename
        if p.exists():
            hubs[key] = _load_json(p)
    listings = _load_json(content / "hub_listings.json") if (content / "hub_listings.json").exists() else {}
    hubs.update(listings.get("hubs", {}))
    return hubs


def load_hub_template(hub_id: str) -> dict:
    hubs = load_hub_templates()
    if hub_id not in hubs:
        raise KeyError(f"Unknown hub template: {hub_id}")
    return deepcopy(hubs[hub_id])


def hydrate_hub_counts(hub: dict, items: list[dict]) -> dict:
    """Replace stale category counts (often 0) with counts from built item lists."""
    hub = deepcopy(hub)
    by_cat: dict[str, int] = {}
    for item in items:
        cid = item.get("category_id") or item.get("theme", "").lower().replace(" ", "-")
        if cid:
            by_cat[cid] = by_cat.get(cid, 0) + 1
    for cat in hub.get("categories") or []:
        if cat.get("id") == "all":
            cat["count"] = len(items)
        elif cat.get("id") in by_cat:
            cat["count"] = by_cat[cat["id"]]
    for theme in hub.get("themes") or []:
        title = (theme.get("title") or "").lower()
        theme["count"] = sum(
            1 for i in items
            if title in (i.get("theme") or "").lower() or title in (i.get("title") or "").lower()
        )
    return hub
