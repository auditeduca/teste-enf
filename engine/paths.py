"""Repository layout. All paths live inside this application tree."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = ROOT / "schemas"
DATA_DIR = ROOT / "data"
TOOLS_DIR = DATA_DIR / "tools"
ASSETS_DIR = ROOT / "assets"
PUBLIC_DIR = ROOT / "public"
RENDER_DIR = ROOT / "render"
FETCH_DIR = RENDER_DIR / "fetch"
INLINE_DIR = RENDER_DIR / "inline"
ADMIN_DIR = ROOT / "admin"
AUDIT_DIR = ROOT / "audit"
REPORTS_DIR = ROOT / "reports"
REGULATORY_DIR = ROOT / "regulatory"
TEMPLATES_DIR = ROOT / "templates"
TOOL_SCHEMA_PATH = SCHEMAS_DIR / "tool.schema.json"
LAYERS_PATH = DATA_DIR / "layers-21.json"
CATALOG_PATH = DATA_DIR / "catalog.json"
