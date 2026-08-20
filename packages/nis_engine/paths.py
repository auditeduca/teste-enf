"""Repository layout helpers."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
TOOLS_DIR = DATA_DIR / "tools"
SCHEMA_PATH = DATA_DIR / "schemas" / "tool.schema.json"
WEB_DIR = ROOT / "apps" / "web"
TOOLS_OUT_DIR = WEB_DIR / "tools"
