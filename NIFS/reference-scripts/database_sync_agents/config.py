"""Config — Database Sync Agent (Supabase + Firebase)."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MD = ROOT / "datasets" / "master-data" / "database-sync"

# Env — carregado via agent_common.env_loader na API/CLI
SUPABASE_URL = lambda: (os.environ.get("SUPABASE_URL") or "").strip().rstrip("/")
SUPABASE_ANON_KEY = lambda: (os.environ.get("SUPABASE_ANON_KEY") or "").strip()
SUPABASE_SERVICE_ROLE_KEY = lambda: (os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or "").strip()

FIREBASE_PROJECT_ID = lambda: (os.environ.get("FIREBASE_PROJECT_ID") or "").strip()
FIREBASE_CREDENTIALS_JSON = lambda: (os.environ.get("FIREBASE_CREDENTIALS_JSON") or "").strip()
FIREBASE_DATABASE_URL = lambda: (os.environ.get("FIREBASE_DATABASE_URL") or "").strip().rstrip("/")
FIREBASE_FUNCTIONS_URL = lambda: (os.environ.get("FIREBASE_FUNCTIONS_URL") or "").strip().rstrip("/")
FIREBASE_SYNC_SECRET = lambda: (os.environ.get("FIREBASE_SYNC_SECRET") or "").strip()

DATABASE_SYNC_BATCH_SIZE = lambda: int(os.environ.get("DATABASE_SYNC_BATCH_SIZE", "200"))
DATABASE_SYNC_DRY_RUN = lambda: (os.environ.get("DATABASE_SYNC_DRY_RUN", "1").strip() not in ("0", "false", "no"))

DEFAULT_MODEL = "deepseek-v4-flash"

# Entidades prioritárias — espelham ENTITY_REGISTRY do nkp_api
ENTITY_TIERS: dict[str, list[dict]] = {
    "tier1_core": [
        {"entity_key": "Country", "path": "global/countries.json", "pk": "country_code", "table": "nkos_countries", "collection": "countries"},
        {"entity_key": "Language", "path": "global/languages.json", "pk": "language_code", "table": "nkos_languages", "collection": "languages"},
        {"entity_key": "Locale", "path": "global/locales.json", "pk": "locale_code", "table": "nkos_locales", "collection": "locales"},
        {"entity_key": "Taxonomy", "path": "clinical/taxonomy.json", "pk": "taxonomy_code", "table": "nkos_taxonomy", "collection": "taxonomy"},
        {"entity_key": "MasterEntity", "path": "master/master_entities.json", "pk": "entity_code", "table": "nkos_master_entities", "collection": "master_entities"},
        {"entity_key": "EntityRelation", "path": "master/entity_relations.json", "pk": "relation_code", "table": "nkos_entity_relations", "collection": "entity_relations"},
    ],
    "tier2_clinical": [
        {"entity_key": "ClinicalToolCatalog", "path": "clinical/clinical_tools_catalog.json", "pk": "tool_code", "table": "nkos_clinical_tools", "collection": "clinical_tools"},
        {"entity_key": "CalculatorDefinition", "path": "clinical/calculator_definitions.json", "pk": "calculator_code", "table": "nkos_calculators", "collection": "calculators"},
    ],
    "tier3_content": [
        {"entity_key": "Content", "path": "content/nkos/contents.json", "pk": "content_code", "table": "nkos_contents", "collection": "contents"},
        {"entity_key": "Translation", "path": "content/translations.json", "pk": "translation_code", "table": "nkos_translations", "collection": "translations"},
        {"entity_key": "Component", "path": "metadata/components.json", "pk": "component_code", "table": "nkos_components", "collection": "components"},
        {"entity_key": "PageTemplate", "path": "metadata/templates.json", "pk": "template_code", "table": "nkos_templates", "collection": "templates"},
    ],
}


def all_entities() -> list[dict]:
    out: list[dict] = []
    for tier in ENTITY_TIERS.values():
        out.extend(tier)
    return out


def resolve_entities(keys: list[str] | None = None) -> list[dict]:
    catalog = all_entities()
    if not keys:
        return catalog
    by_key = {e["entity_key"]: e for e in catalog}
    return [by_key[k] for k in keys if k in by_key]
