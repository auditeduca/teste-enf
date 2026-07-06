"""Country flag asset mapping (ISO 3166-1 alpha-2 → filename in assets/images/flags/)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLAGS_DIR = ROOT / "website" / "assets" / "images" / "flags"

# Filenames that differ from the ISO country code (lowercase).
FLAG_OVERRIDES: dict[str, str] = {
    "GB": "uk",
    "TL": "tp",
}


def flag_slug(country_code: str) -> str:
    cc = (country_code or "").upper()
    if cc in FLAG_OVERRIDES:
        return FLAG_OVERRIDES[cc]
    return cc.lower()


def flag_asset_path(country_code: str) -> str:
    """Relative path from site assets root, e.g. ``images/flags/br.webp``."""
    return f"images/flags/{flag_slug(country_code)}.webp"


def flag_exists(country_code: str) -> bool:
    slug = flag_slug(country_code)
    return (FLAGS_DIR / f"{slug}.webp").is_file()
