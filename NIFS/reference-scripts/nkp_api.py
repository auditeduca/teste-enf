"""REST API for Calculadoras de Enfermagem Knowledge Platform admin UI.

Serves CRUD + graph endpoints over JSON datasets (datasets/).

Usage:
  pip install flask flask-cors
  python scripts/nkp_api.py
  # -> http://127.0.0.1:8787

CORS enabled for Vite dev server (platform/ on :5175).
"""
from __future__ import annotations

import json
import os
import threading
import uuid
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

from dataset_io import (
    find_record,
    iter_records,
    paginate_records,
    read_envelope,
    record_count,
    write_envelope,
)
from content_paths import content_path, content_rel
from agent_common.agent_import import prepare_agent_package  # noqa: E402
from agent_common.env_loader import load_project_env  # noqa: E402
from partition_lib import (
    COUNTRY_FRAMEWORKS,
    LOCALE_ENTITY_FILES,
    SITE_LOCALES,
    SUPPORTED_COUNTRIES,
    country_entity_rel,
    locale_content_rel,
    locale_entity_rel,
    normalize_locale,
    resolve_entity_path,
)

ROOT = Path(__file__).resolve().parent.parent
DATASETS = ROOT / "datasets"

load_project_env()

app = Flask(__name__)
_CORS_PORTS = range(5173, 5200)
CORS(app, resources={r"/api/*": {"origins": [
    *(f"http://127.0.0.1:{p}" for p in _CORS_PORTS),
    *(f"http://localhost:{p}" for p in _CORS_PORTS),
]}})

NOW = lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

ENTITY_REGISTRY: dict[str, dict] = {
    "Country": {
        "path": "global/countries.json",
        "pk": "country_code",
        "label": "name",
        "partition": "global",
    },
    "Language": {
        "path": "global/languages.json",
        "pk": "language_code",
        "label": "name",
        "partition": "global",
    },
    "Locale": {
        "path": "global/locales.json",
        "pk": "locale_code",
        "label": "locale_code",
        "partition": "global",
    },
    "Taxonomy": {
        "path": "clinical/taxonomy.json",
        "pk": "taxonomy_code",
        "label": "name",
        "partition": "global",
    },
    "DesignToken": {
        "path": "metadata/design_tokens.json",
        "pk": "token_code",
        "label": "token_code",
        "partition": "global",
    },
    "MasterEntity": {
        "path": "master/master_entities.json",
        "pk": "entity_code",
        "label": "name",
        "partition": "global",
    },
    "EntityRelation": {
        "path": "master/entity_relations.json",
        "pk": "relation_code",
        "partition": "global",
    },
    "Asset": {"path": "metadata/assets.json", "pk": "asset_code", "label": "asset_code", "partition": "global"},
    "PageTemplate": {
        "path": "metadata/templates.json",
        "pk": "template_code",
        "label": "name",
        "partition": "global",
    },
    "Section": {"path": "metadata/sections.json", "pk": "section_code", "partition": "global"},
    "Component": {
        "path": "metadata/components.json",
        "pk": "component_code",
        "label": "name",
        "partition": "global",
    },
    "ComplianceRule": {
        "path": "metadata/compliance_rules.json",
        "pk": "compliance_code",
        "label": "framework",
        "partition": "country",
    },
    "ContentRequest": {
        "path": content_rel("content_requests"),
        "pk": "request_code",
        "partition": "country",
    },
    "Workflow": {"path": "ai/workflows.json", "pk": "workflow_code", "partition": "locale"},
    "Translation": {
        "path": content_rel("translations"),
        "pk": "translation_code",
        "label": "content_code",
        "partition": "locale",
    },
    "Content": {
        "path": content_rel("contents"),
        "pk": "content_code",
        "label": "title_pt",
    },
    "ContentFragment": {
        "path": content_rel("content_fragments"),
        "pk": "fragment_code",
        "label": "body_pt",
    },
    "ContentVersion": {
        "path": content_rel("content_versions"),
        "pk": "version_code",
        "label": "content_code",
    },
}

SCOPE_COUNTRIES = [
    {"code": "BR", "label": "Brasil", "default_locale": "pt-BR", "frameworks": ["LGPD"]},
    {"code": "PT", "label": "Portugal", "default_locale": "pt-PT", "frameworks": ["RGPD"]},
    {"code": "US", "label": "Estados Unidos", "default_locale": "en-US", "frameworks": ["HIPAA"]},
    {"code": "ES", "label": "Espanha", "default_locale": "es-ES", "frameworks": ["RGPD"]},
    {"code": "FR", "label": "França", "default_locale": "fr-FR", "frameworks": ["RGPD"]},
    {"code": "DE", "label": "Alemanha", "default_locale": "de-DE", "frameworks": ["DSGVO"]},
    {"code": "IT", "label": "Itália", "default_locale": "it-IT", "frameworks": ["GDPR"]},
    {"code": "JP", "label": "Japão", "default_locale": "ja-JP", "frameworks": ["APPI"]},
]


def _request_country(body: dict | None = None) -> str:
    cc = request.args.get("country", "").strip().upper()
    if cc:
        return cc
    if body:
        return str(body.get("country_code", "")).strip().upper()
    return ""


def _request_locale(body: dict | None = None) -> str:
    loc = request.args.get("locale", "").strip()
    if not loc:
        loc = request.args.get("language", "").strip()
    if loc:
        return normalize_locale(loc)
    if body:
        loc = body.get("locale") or body.get("language") or body.get("language_code") or ""
        if loc:
            return normalize_locale(str(loc))
    return normalize_locale("pt-BR")


def _entity_dataset_path(
    entity_key: str,
    country: str | None = None,
    locale: str | None = None,
) -> str:
    meta = ENTITY_REGISTRY[entity_key]
    cc = (country or _request_country()).strip().upper()
    loc = locale or _request_locale()
    return resolve_entity_path(entity_key, meta, country=cc, locale=loc)


def _load_entity(key: str, country: str | None = None, locale: str | None = None) -> dict:
    """Full envelope load — use only for writes and imports."""
    if key not in ENTITY_REGISTRY:
        raise KeyError(key)
    return read_envelope(_entity_dataset_path(key, country, locale))


def _save_entity(key: str, env: dict, country: str | None = None, locale: str | None = None) -> None:
    write_envelope(_entity_dataset_path(key, country, locale), env)


def _record_id(rec: dict, pk: str) -> str:
    return str(rec.get("uuid") or rec.get(pk) or rec.get("id", ""))


def _build_list_predicate(entity_key: str, meta: dict, search: str):
    search_l = search.lower()

    def predicate(rec: dict) -> bool:
        if not _record_matches_filters(rec, entity_key):
            return False
        if search_l:
            parts = [str(rec.get(meta["pk"], "")), str(rec.get(meta.get("label") or "", ""))]
            if not any(search_l in p.lower() for p in parts if p):
                return False
        return True

    return predicate


def _record_matches_filters(rec: dict, entity_key: str) -> bool:
    return rec in _apply_extra_filters([rec], entity_key)


def _normalize_relation(rec: dict) -> dict:
    """Map EntityRelation records -> graph UI shape."""
    return {
        "id": _record_id(rec, "relation_code"),
        "source_entity": rec.get("source_code") or rec.get("source_entity", ""),
        "target_entity": rec.get("target_code") or rec.get("target_entity", ""),
        "relation_type": _map_relation_type(rec.get("relation_type", "RELATES_TO")),
        "strength": int(min(10, max(1, round(float(rec.get("weight") or rec.get("strength") or 5) * 10)))),
        "status": rec.get("status", "active"),
        "_raw": rec,
    }


def _map_relation_type(rt: str) -> str:
    m = {
        "assesses": "RELATES_TO",
        "classified_in": "RELATES_TO",
        "uses": "USES_COMPONENT",
        "has_asset": "HAS_ASSET",
        "depends_on": "DEPENDS_ON",
    }
    return m.get(rt, rt.upper() if rt.islower() else rt)


def _normalize_language(rec: dict) -> dict:
    active = rec.get("is_active", True)
    return {
        "id": _record_id(rec, "language_code"),
        "language_code": rec.get("language_code", ""),
        "name": rec.get("name", ""),
        "native_name": rec.get("native_name", ""),
        "rtl": rec.get("rtl", False),
        "status": "active" if active else "archived",
        "_raw": rec,
    }


def _normalize_locale(rec: dict) -> dict:
    return {
        "id": _record_id(rec, "locale_code"),
        "locale_code": rec.get("locale_code", ""),
        "language_code": rec.get("language_code", ""),
        "country_code": rec.get("country_code", ""),
        "fallback_locale": rec.get("fallback_locale", ""),
        "currency": rec.get("currency", ""),
        "timezone": rec.get("timezone", ""),
        "direction": rec.get("direction", "ltr"),
        "status": rec.get("status", "active"),
        "_raw": rec,
    }


def _normalize_taxonomy(rec: dict) -> dict:
    active = rec.get("is_active", True)
    return {
        "id": _record_id(rec, "taxonomy_code"),
        "taxonomy_code": rec.get("taxonomy_code", ""),
        "name": rec.get("name", ""),
        "slug": rec.get("slug", ""),
        "parent_code": rec.get("parent_code", ""),
        "level": rec.get("level", 0),
        "path": rec.get("path", ""),
        "description": rec.get("description", ""),
        "status": "active" if active else "archived",
        "_raw": rec,
    }


def _normalize_design_token(rec: dict) -> dict:
    return {
        "id": _record_id(rec, "token_code"),
        "token_code": rec.get("token_code", ""),
        "token_type": rec.get("token_type", ""),
        "name": rec.get("name", ""),
        "value": rec.get("value", ""),
        "description": rec.get("description", ""),
        "status": rec.get("status", "active"),
        "_raw": rec,
    }


def _normalize_country(rec: dict) -> dict:
    return {
        "id": _record_id(rec, "country_code"),
        "country_code": rec.get("country_code", ""),
        "name": rec.get("name", ""),
        "name_local": rec.get("name_local", ""),
        "who_region": rec.get("who_region", ""),
        "income_level": rec.get("income_level", ""),
        "regulatory_zone": rec.get("regulatory_zone", ""),
        "currency": rec.get("currency", ""),
        "timezone": rec.get("timezone", ""),
        "measurement_system": rec.get("measurement_system", ""),
        "is_active": rec.get("is_active", True),
        "status": "active" if rec.get("is_active", True) else "archived",
        "_raw": rec,
    }


def _normalize_master(rec: dict) -> dict:
    return {
        "id": _record_id(rec, "entity_code"),
        "master_code": rec.get("entity_code", ""),
        "title": rec.get("name") or rec.get("title", ""),
        "slug": rec.get("slug", ""),
        "domain": rec.get("taxonomy_code", "").split(".")[0].lower() if rec.get("taxonomy_code") else "clinical",
        "entity_type": rec.get("entity_type", "concept"),
        "parent_entity_code": rec.get("parent_entity_code", ""),
        "taxonomy_code": rec.get("taxonomy_code", ""),
        "description": rec.get("description", ""),
        "status": rec.get("status", "active"),
        "_raw": rec,
    }


def _normalize_asset(rec: dict) -> dict:
    return {
        "id": _record_id(rec, "asset_code"),
        "asset_code": rec.get("asset_code", ""),
        "title": rec.get("title") or rec.get("asset_code", ""),
        "asset_type": (rec.get("asset_type") or "IMAGE").upper(),
        "category": rec.get("category", ""),
        "file_url": rec.get("file_url") or rec.get("path", ""),
        "alt_text": rec.get("alt_text", ""),
        "license": rec.get("license", "proprietary"),
        "status": rec.get("status", "active"),
        "version": rec.get("version", 1),
        "_raw": rec,
    }


def _normalize_translation(rec: dict) -> dict:
    text = rec.get("translated_text", "")
    return {
        "id": _record_id(rec, "translation_code"),
        "translation_code": rec.get("translation_code", ""),
        "content_code": rec.get("content_code", ""),
        "target_locale": rec.get("target_locale", ""),
        "language_code": rec.get("language_code", ""),
        "field_name": rec.get("field_name", ""),
        "translated_text": text,
        "text_preview": (text[:120] + "…") if len(text) > 120 else text,
        "content_scope": rec.get("content_scope", ""),
        "status": rec.get("status", "reviewed"),
        "_raw": rec,
    }


def _normalize_content(rec: dict) -> dict:
    title = rec.get("title_pt") or rec.get("title") or ""
    return {
        "id": _record_id(rec, "content_code"),
        "content_code": rec.get("content_code", ""),
        "title_pt": title,
        "slug": rec.get("slug", ""),
        "content_type": rec.get("content_type", ""),
        "locale_code": rec.get("locale_code", ""),
        "route_path": rec.get("route_path", ""),
        "source_entity": rec.get("source_entity", ""),
        "source_code": rec.get("source_code", ""),
        "status": rec.get("status", "published"),
        "edition": rec.get("edition", ""),
        "_raw": rec,
    }


def _normalize_content_fragment(rec: dict) -> dict:
    body = rec.get("body_pt") or ""
    return {
        "id": _record_id(rec, "fragment_code"),
        "fragment_code": rec.get("fragment_code", ""),
        "content_code": rec.get("content_code", ""),
        "fragment_type": rec.get("fragment_type", ""),
        "sequence": rec.get("sequence"),
        "body_preview": (body[:120] + "…") if len(body) > 120 else body,
        "locale_code": rec.get("locale_code", ""),
        "_raw": rec,
    }


def _normalize_content_version(rec: dict) -> dict:
    return {
        "id": _record_id(rec, "version_code"),
        "version_code": rec.get("version_code", ""),
        "content_code": rec.get("content_code", ""),
        "version_number": rec.get("version_number"),
        "snapshot_label": rec.get("snapshot_label", ""),
        "locale_code": rec.get("locale_code", ""),
        "published_at": rec.get("published_at", ""),
        "_raw": rec,
    }


NORMALIZERS = {
    "Country": _normalize_country,
    "Language": _normalize_language,
    "Locale": _normalize_locale,
    "Taxonomy": _normalize_taxonomy,
    "DesignToken": _normalize_design_token,
    "MasterEntity": _normalize_master,
    "EntityRelation": _normalize_relation,
    "Asset": _normalize_asset,
    "Translation": _normalize_translation,
    "Content": _normalize_content,
    "ContentFragment": _normalize_content_fragment,
    "ContentVersion": _normalize_content_version,
}


def _filter_records(records: list, search: str, pk: str, label_key: str | None) -> list:
    if not search:
        return records
    q = search.lower()
    out = []
    for r in records:
        parts = [str(r.get(pk, "")), str(r.get(label_key or "", ""))]
        if any(q in p.lower() for p in parts if p):
            out.append(r)
    return out


def _apply_extra_filters(records: list, entity_key: str) -> list:
    parent = request.args.get("parent", "").strip()
    entity_type = request.args.get("entity_type", "").strip()
    status = request.args.get("status", "").strip()
    category = request.args.get("category", "").strip()
    framework = request.args.get("framework", "").strip()
    asset_type = request.args.get("asset_type", "").strip()
    relation_type = request.args.get("relation_type", "").strip()
    template_code = request.args.get("template_code", "").strip()
    layout_code = request.args.get("layout_code", "").strip()
    language = request.args.get("language", "").strip()
    country = request.args.get("country", "").strip()
    locale = request.args.get("locale", "").strip()
    edition = request.args.get("edition", "").strip()
    content_source = request.args.get("content_source", "").strip()
    content_code = request.args.get("content_code", "").strip()
    content_type = request.args.get("content_type", "").strip()
    domain = request.args.get("domain", "").strip()
    who_region = request.args.get("who_region", "").strip()
    income_level = request.args.get("income_level", "").strip()
    language_code = request.args.get("language_code", "").strip()
    token_type = request.args.get("token_type", "").strip()
    level = request.args.get("level", "").strip()
    is_active = request.args.get("is_active", "").strip()

    if parent:
        records = [
            r for r in records
            if (r.get("parent_entity_code") or r.get("parent_code") or "") == parent
        ]
    if entity_type:
        records = [r for r in records if (r.get("entity_type") or "") == entity_type]
    if status:
        records = [r for r in records if str(r.get("status", "")).lower() == status.lower()]
    if category:
        records = [r for r in records if (r.get("category") or "").lower() == category.lower()]
    if framework:
        records = [r for r in records if (r.get("framework") or "").lower() == framework.lower()]
    if asset_type:
        records = [
            r for r in records
            if str(r.get("asset_type", "")).lower().replace("_", "") == asset_type.lower().replace("_", "")
        ]
    if relation_type:
        records = [r for r in records if (r.get("relation_type") or "") == relation_type]
    if template_code:
        records = [r for r in records if (r.get("template_code") or r.get("template") or "") == template_code]
    if layout_code:
        records = [r for r in records if (r.get("layout_code") or "") == layout_code]
    if edition:
        records = [r for r in records if str(r.get("edition", "")) == edition]
    if content_source:
        records = [r for r in records if (r.get("content_source") or "") == content_source]
    if content_code:
        records = [r for r in records if (r.get("content_code") or "") == content_code]
    if content_type:
        records = [r for r in records if (r.get("content_type") or "") == content_type]
    if language:
        lang = language.lower()
        records = [
            r for r in records
            if lang in str(r.get("language", "")).lower()
            or lang in str(r.get("language_code", "")).lower()
            or lang in str(r.get("locale", "")).lower()
            or lang in str(r.get("locale_code", "")).lower()
        ]
    if locale:
        loc = locale.lower()
        records = [
            r for r in records
            if loc in str(r.get("locale", "")).lower()
            or loc in str(r.get("locale_code", "")).lower()
            or loc in str(r.get("language", "")).lower()
            or loc in str(r.get("language_code", "")).lower()
            or loc in str(r.get("target_locale", "")).lower()
        ]
    if country:
        cc = country.upper()
        records = [
            r for r in records
            if str(r.get("country_code", "")).upper() == cc
            or cc in str(r.get("locale_code", "")).upper()
            or cc in str(r.get("locale", "")).upper()
        ]
    country_code_filter = request.args.get("country_code", "").strip()
    if country_code_filter:
        cc = country_code_filter.upper()
        records = [r for r in records if str(r.get("country_code", "")).upper() == cc]
    if domain:
        d = domain.lower()
        records = [
            r for r in records
            if d in (r.get("taxonomy_code") or "").lower()
            or d in (r.get("entity_code") or "").lower()
            or d in (r.get("domain") or "").lower()
        ]
    if who_region:
        wr = who_region.upper()
        records = [r for r in records if str(r.get("who_region", "")).upper() == wr]
    if income_level:
        il = income_level.lower()
        records = [r for r in records if str(r.get("income_level", "")).lower() == il]
    if language_code:
        lc = language_code.lower()
        records = [r for r in records if str(r.get("language_code", "")).lower() == lc]
    if token_type:
        tt = token_type.upper()
        records = [r for r in records if str(r.get("token_type", "")).upper() == tt]
    if level != "":
        records = [r for r in records if str(r.get("level", "")) == level]
    if is_active != "":
        want = is_active.lower() in ("true", "1", "yes")
        records = [r for r in records if bool(r.get("is_active", True)) == want]
    return records


@app.get("/")
def index():
    """Evita 404 ao abrir :8787 no browser — a UI React roda em :5175."""
    return jsonify({
        "service": "CALENF-NKD Knowledge Platform API",
        "ui": "http://127.0.0.1:5175",
        "code_review": "http://127.0.0.1:5175/code-review",
        "health": "/api/health",
        "review_rules": "/api/review/rules",
        "note": "Rotas da plataforma (ex. /code-review) são do Vite, não desta API.",
    })


@app.get("/api/health")
def health():
    entities = list(ENTITY_REGISTRY.keys())
    return jsonify({
        "ok": True,
        "datasets_root": str(DATASETS),
        "api_version": "2026.6.20",
        "entity_count": len(entities),
        "entities": entities,
    })


@app.get("/api/monitor/progress")
def monitor_progress():
    import sys

    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    from monitor_progress import collect  # noqa: WPS433

    refresh = request.args.get("refresh", "").strip() in ("1", "true", "yes")
    return jsonify(collect(refresh_resource=refresh))


@app.get("/api/stats")
def stats():
    country = _request_country()
    counts = {}
    for key, meta in ENTITY_REGISTRY.items():
        try:
            if meta.get("partition") == "country":
                if country:
                    counts[key] = record_count(_entity_dataset_path(key, country))
                else:
                    total = 0
                    for cc in SUPPORTED_COUNTRIES:
                        rel = country_entity_rel(key, cc)
                        if (DATASETS / rel).exists():
                            total += record_count(rel)
                    counts[key] = total
            elif meta.get("partition") == "locale":
                loc = _request_locale()
                if request.args.get("locale") or request.args.get("language"):
                    counts[key] = record_count(_entity_dataset_path(key, locale=loc))
                elif key not in LOCALE_ENTITY_FILES:
                    counts[key] = record_count(meta["path"])
                else:
                    total = 0
                    for loc_code in SITE_LOCALES:
                        rel = locale_entity_rel(key, loc_code)
                        if (DATASETS / rel).exists():
                            total += record_count(rel)
                    counts[key] = total
            else:
                counts[key] = record_count(meta["path"])
        except OSError:
            counts[key] = 0
    return jsonify(counts)


@app.get("/api/scopes")
def scopes():
    by_partition: dict[str, list[str]] = {"global": [], "locale": [], "country": []}
    for key, meta in ENTITY_REGISTRY.items():
        tier = meta.get("partition", "global")
        by_partition.setdefault(tier, []).append(key)

    return jsonify({
        "strategy": "physical_v4",
        "lazy_io": True,
        "default_page_size": 40,
        "physical_layout": {
            "country": "datasets/by-country/{CC}/",
            "locale": "datasets/by-locale/{locale}/",
        },
        "supported_countries": SUPPORTED_COUNTRIES,
        "country_frameworks": COUNTRY_FRAMEWORKS,
        "tiers": {
            "global": {
                "label": "Global — conhecimento clínico e design system",
                "entities": by_partition.get("global", []),
                "load": "hierarchy + pagination",
                "path": "datasets/master/, datasets/metadata/",
            },
            "locale": {
                "label": "Locale — idioma e workflows de conteúdo",
                "entities": by_partition.get("locale", []),
                "load": "reads by-locale/{locale}/ only",
                "path": "datasets/by-locale/{locale}/",
                "site_locales": SITE_LOCALES,
            },
            "country": {
                "label": "País — compliance e content factory",
                "entities": by_partition.get("country", []),
                "load": "requires country scope — reads by-country/{CC}/ only",
                "path": "datasets/by-country/{CC}/",
            },
        },
        "countries": SCOPE_COUNTRIES,
        "site_locales": ["pt-BR", "en", "es", "fr", "de", "it", "ja"],
    })


@app.get("/api/scopes/<country_code>")
def scope_country(country_code: str):
    cc = country_code.strip().upper()
    if cc not in SUPPORTED_COUNTRIES:
        return jsonify({"error": "unsupported country"}), 404
    entities = {}
    for key in ("ComplianceRule", "ContentRequest"):
        rel = country_entity_rel(key, cc)
        path = DATASETS / rel
        entities[key] = {
            "path": rel,
            "exists": path.exists(),
            "count": record_count(rel) if path.exists() else 0,
        }
    return jsonify({
        "country": cc,
        "frameworks": COUNTRY_FRAMEWORKS.get(cc, []),
        "entities": entities,
    })


@app.get("/api/scopes/locale/<locale_code>")
def scope_locale(locale_code: str):
    loc = normalize_locale(locale_code)
    if loc not in SITE_LOCALES:
        return jsonify({"error": "unsupported locale", "supported": SITE_LOCALES}), 404
    home_rel = locale_content_rel("home_page", loc)
    wf_rel = locale_entity_rel("Workflow", loc)
    tr_rel = locale_entity_rel("Translation", loc)
    return jsonify({
        "locale": loc,
        "content": {
            "home_page": {
                "path": home_rel,
                "exists": (DATASETS / home_rel).exists(),
            },
        },
        "entities": {
            "Workflow": {
                "path": wf_rel,
                "exists": (DATASETS / wf_rel).exists(),
                "count": record_count(wf_rel) if (DATASETS / wf_rel).exists() else 0,
            },
            "Translation": {
                "path": tr_rel,
                "exists": (DATASETS / tr_rel).exists(),
                "count": record_count(tr_rel) if (DATASETS / tr_rel).exists() else 0,
            },
        },
    })


@app.get("/api/entities/<entity_key>")
def list_entities(entity_key: str):
    if entity_key not in ENTITY_REGISTRY:
        return jsonify({"error": "unknown entity"}), 404
    meta = ENTITY_REGISTRY[entity_key]
    search = request.args.get("search", "")
    limit = min(int(request.args.get("limit", 50)), 2000)
    offset = int(request.args.get("offset", 0))
    partition = meta.get("partition", "global")
    country = request.args.get("country", "").strip()
    locale = _request_locale()

    if partition == "country" and not country:
        return jsonify({
            "error": "country_required",
            "message": "Selecione um país na barra de escopo para carregar este módulo.",
            "partition": partition,
            "total": 0,
            "offset": offset,
            "limit": limit,
            "records": [],
        }), 400

    predicate = _build_list_predicate(entity_key, meta, search)
    dataset_path = _entity_dataset_path(entity_key, country, locale)
    total, page = paginate_records(dataset_path, predicate, offset=offset, limit=limit)
    norm = NORMALIZERS.get(entity_key)
    if norm:
        page = [norm(r) for r in page]
    return jsonify({
        "total": total,
        "offset": offset,
        "limit": limit,
        "partition": partition,
        "country": country or None,
        "locale": locale,
        "dataset_path": dataset_path,
        "lazy": True,
        "records": page,
    })


@app.get("/api/entities/<entity_key>/<record_id>")
def get_entity(entity_key: str, record_id: str):
    if entity_key not in ENTITY_REGISTRY:
        return jsonify({"error": "unknown entity"}), 404
    meta = ENTITY_REGISTRY[entity_key]
    cc = _request_country()
    loc = _request_locale()
    rec = find_record(_entity_dataset_path(entity_key, cc, loc), meta["pk"], record_id)
    if not rec:
        return jsonify({"error": "not found"}), 404
    norm = NORMALIZERS.get(entity_key)
    return jsonify(norm(rec) if norm else rec)


@app.post("/api/entities/<entity_key>")
def create_entity(entity_key: str):
    if entity_key not in ENTITY_REGISTRY:
        return jsonify({"error": "unknown entity"}), 404
    meta = ENTITY_REGISTRY[entity_key]
    body = request.get_json(force=True) or {}
    cc = _request_country(body)
    loc = _request_locale(body)
    if meta.get("partition") == "country" and not cc:
        return jsonify({"error": "country_required"}), 400
    env = _load_entity(entity_key, cc, loc)
    pk = meta["pk"]
    if not body.get(pk):
        return jsonify({"error": f"missing {pk}"}), 400
    body.setdefault("uuid", str(uuid.uuid4()))
    body.setdefault("created_at", NOW())
    body.setdefault("updated_at", NOW())
    body.setdefault("status", body.get("status", "draft"))
    if meta.get("partition") == "country":
        body.setdefault("country_code", cc)
    if meta.get("partition") == "locale":
        body.setdefault("locale", loc)
    env.setdefault("records", []).append(body)
    env["count"] = len(env["records"])
    _save_entity(entity_key, env, cc, loc)
    return jsonify(body), 201


@app.put("/api/entities/<entity_key>/<record_id>")
def update_entity(entity_key: str, record_id: str):
    if entity_key not in ENTITY_REGISTRY:
        return jsonify({"error": "unknown entity"}), 404
    meta = ENTITY_REGISTRY[entity_key]
    cc = _request_country()
    loc = _request_locale()
    env = _load_entity(entity_key, cc, loc)
    body = request.get_json(force=True) or {}
    for i, r in enumerate(env.get("records", [])):
        if _record_id(r, meta["pk"]) == record_id or r.get(meta["pk"]) == record_id:
            merged = {**r, **body, "updated_at": NOW()}
            env["records"][i] = merged
            _save_entity(entity_key, env, cc, loc)
            return jsonify(merged)
    return jsonify({"error": "not found"}), 404


@app.post("/api/entities/<entity_key>/import")
def import_entities(entity_key: str):
    if entity_key not in ENTITY_REGISTRY:
        return jsonify({"error": "unknown entity"}), 404
    meta = ENTITY_REGISTRY[entity_key]
    pk = meta["pk"]
    body = request.get_json(force=True) or {}
    cc = _request_country(body)
    loc = _request_locale(body)
    if meta.get("partition") == "country" and not cc:
        return jsonify({"error": "country_required"}), 400
    incoming = body.get("records") or []
    mode = (body.get("mode") or "merge").lower()
    if not isinstance(incoming, list) or not incoming:
        return jsonify({"error": "records array required"}), 400

    env = _load_entity(entity_key, cc, loc)
    existing = env.get("records", [])
    by_pk = {str(r.get(pk, "")): r for r in existing if r.get(pk)}

    created = updated = skipped = 0
    for rec in incoming:
        if not isinstance(rec, dict) or not rec.get(pk):
            skipped += 1
            continue
        code = str(rec[pk])
        rec.setdefault("uuid", str(uuid.uuid4()))
        rec.setdefault("created_at", NOW())
        rec["updated_at"] = NOW()
        if meta.get("partition") == "country":
            rec.setdefault("country_code", cc)
        if meta.get("partition") == "locale":
            rec.setdefault("locale", loc)
        if code in by_pk:
            if mode == "replace":
                by_pk[code] = {**by_pk[code], **rec}
                updated += 1
            elif mode == "merge":
                by_pk[code] = {**by_pk[code], **rec}
                updated += 1
            else:
                skipped += 1
        else:
            by_pk[code] = rec
            created += 1

    env["records"] = list(by_pk.values())
    env["count"] = len(env["records"])
    _save_entity(entity_key, env, cc, loc)
    return jsonify({"ok": True, "created": created, "updated": updated, "skipped": skipped, "total": env["count"]})


@app.get("/api/content/home-preview")
def home_preview():
    locale = _request_locale()
    rel = locale_content_rel("home_page", locale)
    path = DATASETS / rel
    if not path.exists():
        path = content_path("home_page")
    if not path.exists():
        return jsonify({"error": "home_page.json not found"}), 404
    data = json.loads(path.read_text(encoding="utf-8"))
    data["_dataset_path"] = str(path.relative_to(DATASETS)).replace("\\", "/")
    return jsonify(data)


@app.get("/api/translations/summary")
def translations_summary():
    """Per-locale translation counts without scanning 160k global records."""
    manifest_path = DATASETS / "by-locale" / "translations_manifest.json"
    if manifest_path.exists():
        return jsonify(json.loads(manifest_path.read_text(encoding="utf-8")))
    locales = {}
    for loc in SITE_LOCALES:
        rel = locale_entity_rel("Translation", loc)
        if (DATASETS / rel).exists():
            locales[loc] = {"path": rel, "count": record_count(rel)}
    return jsonify({
        "strategy": "physical_v4",
        "source": content_rel("translations"),
        "locales": locales,
    })


@app.get("/api/locales/summary")
def locales_summary():
    path = DATASETS / "global" / "locales.json"
    if not path.exists():
        return jsonify({"languages": [], "countries": [], "site_locales": ["pt-BR", "en", "es", "fr", "de", "it", "ja"]})
    env = json.loads(path.read_text(encoding="utf-8"))
    langs = sorted({r.get("language_code") for r in env.get("records", []) if r.get("language_code")})
    countries = sorted({r.get("country_code") for r in env.get("records", []) if r.get("country_code")})
    return jsonify({
        "languages": langs[:50],
        "countries": countries[:50],
        "total_locales": len(env.get("records", [])),
        "site_locales": ["pt-BR", "en", "es", "fr", "de", "it", "ja"],
    })


@app.get("/api/graph/relations")
def graph_relations():
    limit = min(int(request.args.get("limit", 120)), 500)
    offset = int(request.args.get("offset", 0))
    search = request.args.get("search", "").lower()
    meta = ENTITY_REGISTRY["EntityRelation"]

    def predicate(rec: dict) -> bool:
        if not search:
            return True
        return (
            search in (rec.get("source_code") or "").lower()
            or search in (rec.get("target_code") or "").lower()
        )

    total, page = paginate_records(meta["path"], predicate, offset=offset, limit=limit)
    relations = [_normalize_relation(r) for r in page]
    for rel in relations:
        rel.pop("_raw", None)
    return jsonify({"total": total, "offset": offset, "limit": limit, "lazy": True, "relations": relations})


@app.get("/api/graph/mindmap")
def mindmap():
    limit_m = min(int(request.args.get("master_limit", 30)), 100)
    domain = request.args.get("domain", "")
    mmeta = ENTITY_REGISTRY["MasterEntity"]
    rmeta = ENTITY_REGISTRY["EntityRelation"]

    def master_predicate(rec: dict) -> bool:
        if not domain:
            return True
        return domain in (rec.get("taxonomy_code") or "").lower()

    _, masters_raw = paginate_records(mmeta["path"], master_predicate, offset=0, limit=limit_m)
    masters = [_normalize_master(m) for m in masters_raw]
    codes = {m.get("master_code") for m in masters}

    relations = []
    for rec in iter_records(rmeta["path"]):
        if rec.get("source_code") in codes or rec.get("target_code") in codes:
            rel = _normalize_relation(rec)
            rel.pop("_raw", None)
            relations.append(rel)
            if len(relations) >= 200:
                break

    return jsonify({"masters": masters, "relations": relations, "lazy": True})


@app.get("/api/graph/entity-options")
def graph_entity_options():
    """Searchable entity codes for graph forms (master + tools + protocols)."""
    q = (request.args.get("q") or "").strip().lower()
    limit = min(int(request.args.get("limit", 50)), 200)
    options: list[dict] = []

    def matches(code: str, label: str) -> bool:
        if not q:
            return True
        blob = f"{code} {label}".lower()
        return q in blob

    def add_option(code: str, label: str, typ: str) -> bool:
        if not code:
            return False
        if not matches(code, label):
            return False
        options.append({"code": code, "label": label or code, "type": typ})
        return len(options) >= limit

    mmeta = ENTITY_REGISTRY["MasterEntity"]

    def master_pred(rec: dict) -> bool:
        code = rec.get("entity_code") or ""
        name = rec.get("name") or ""
        return matches(code, name)

    _, masters = paginate_records(mmeta["path"], master_pred, offset=0, limit=limit)
    for rec in masters:
        add_option(rec.get("entity_code", ""), rec.get("name", ""), "master")
        if len(options) >= limit:
            break

    if len(options) < limit:
        try:
            tools_env = read_envelope("clinical/clinical_tools_catalog.json")
            for rec in tools_env.get("records") or []:
                code = rec.get("tool_code") or ""
                name = rec.get("name") or rec.get("name_pt") or ""
                if add_option(code, name, "tool"):
                    break
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            pass

    if len(options) < limit:
        try:
            protos = read_envelope("clinical/institutional_protocols.json")
            for rec in protos.get("records") or []:
                code = rec.get("protocol_code") or ""
                name = rec.get("title_pt") or rec.get("title") or ""
                if add_option(code, name, "protocol"):
                    break
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            pass

    if len(options) < limit:
        try:
            contents_env = read_envelope(content_rel("contents"))
            for rec in contents_env.get("records") or []:
                code = rec.get("content_code") or ""
                name = rec.get("title_pt") or rec.get("title") or ""
                if add_option(code, name, "content"):
                    break
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            pass

    return jsonify({"q": q, "limit": limit, "count": len(options), "options": options})


# ---------------------------------------------------------------------------
# Audit pipeline (full project audit with live progress)
# ---------------------------------------------------------------------------
_audit_lock = threading.Lock()
_audit_running = False

AUDIT_REPORT = DATASETS / "metadata" / "full_audit_report.json"
AUDIT_PROGRESS = DATASETS / "metadata" / "audit_progress.json"


def _audit_bg(payload: dict) -> None:
    global _audit_running
    try:
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from audit_lib import run_full_audit
        run_full_audit(
            skip_website_audit=bool(payload.get("skip_website", False)),
            skip_a11y=bool(payload.get("skip_a11y", False)),
            mode=payload.get("mode") or "full",
            domains=payload.get("domains"),
        )
    finally:
        with _audit_lock:
            _audit_running = False


@app.get("/api/audit/progress")
def audit_progress():
    if AUDIT_PROGRESS.exists():
        return jsonify(json.loads(AUDIT_PROGRESS.read_text(encoding="utf-8")))
    return jsonify({"status": "idle", "progress_pct": 0})


@app.get("/api/audit/execution-plan")
def audit_execution_plan():
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from audit_lib import AUDIT_STAGES
    from audit_orchestrator import get_execution_plan

    mode = request.args.get("mode", "full")
    domains = request.args.getlist("domain") or None
    return jsonify(get_execution_plan(
        AUDIT_STAGES,
        mode=mode,
        domains=domains,
        skip_website=request.args.get("skip_website") == "1",
        skip_a11y=request.args.get("skip_a11y") == "1",
    ))


@app.get("/api/audit/monitor")
def audit_monitor():
    """Real-time dashboard snapshot — all domain tiles."""
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from audit_orchestrator import build_monitor_snapshot

    progress = json.loads(AUDIT_PROGRESS.read_text(encoding="utf-8")) if AUDIT_PROGRESS.exists() else None
    full = json.loads(AUDIT_REPORT.read_text(encoding="utf-8")) if AUDIT_REPORT.exists() else None
    return jsonify(build_monitor_snapshot(progress, full))


@app.get("/api/audit/domains/<domain_id>")
def audit_domain_status(domain_id: str):
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from audit_orchestrator import DOMAIN_META, load_domain_status

    if domain_id not in DOMAIN_META:
        return jsonify({"error": f"Domínio desconhecido: {domain_id}"}), 404
    data = load_domain_status(domain_id)
    if not data:
        meta = DOMAIN_META[domain_id]
        return jsonify({"domain": domain_id, "label": meta["label"], "status": "idle", "compliance_pct": None})
    return jsonify(data)


@app.get("/api/audit/free-apis")
def audit_free_apis():
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from audit_external import pagespeed_available
    from audit_orchestrator import FREE_AUDIT_APIS

    apis = []
    for api in FREE_AUDIT_APIS:
        row = dict(api)
        if row.get("env_key"):
            import os
            row["configured"] = bool(os.environ.get(row["env_key"], "").strip())
        else:
            row["configured"] = True
        apis.append(row)
    return jsonify({"apis": apis, "pagespeed_ready": pagespeed_available()})


@app.get("/api/audit/report")
def audit_report():
    if not AUDIT_REPORT.exists():
        return jsonify({
            "status": "empty",
            "message": "Nenhum relatório. Execute POST /api/audit/run.",
            "summary": None,
            "gaps": [],
        })
    data = json.loads(AUDIT_REPORT.read_text(encoding="utf-8"))
    if "framework" not in data:
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from audit_framework import enrich_audit_report
        data = enrich_audit_report(data)
    return jsonify(data)


@app.get("/api/audit/frameworks")
def audit_frameworks():
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from audit_framework import list_frameworks, FRAMEWORK_VERSION
    return jsonify({"version": FRAMEWORK_VERSION, "frameworks": list_frameworks()})


@app.get("/api/audit/report/export")
def audit_report_export():
    fmt = request.args.get("format", "md")
    if not AUDIT_REPORT.exists():
        return jsonify({"error": "Nenhum relatório disponível"}), 404
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from audit_framework import enrich_audit_report, export_report

    data = json.loads(AUDIT_REPORT.read_text(encoding="utf-8"))
    if "framework" not in data:
        data = enrich_audit_report(data)
    try:
        content, mime, filename = export_report(data, fmt)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    from flask import Response
    return Response(
        content,
        mimetype=mime,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/api/audit/suggest")
def audit_suggest():
    import os
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from audit_ai_suggest import suggest_fix
    from audit_framework import enrich_audit_report

    body = request.get_json(silent=True) or {}
    finding = body.get("finding")
    if not finding or not finding.get("message"):
        return jsonify({"error": "Campo 'finding' obrigatório"}), 400
    api_key = (body.get("api_key") or os.environ.get("DEEPSEEK_API_KEY") or "").strip()
    if not api_key:
        return jsonify({"error": "api_key ou DEEPSEEK_API_KEY obrigatória"}), 400

    context = ""
    if AUDIT_REPORT.exists():
        report = json.loads(AUDIT_REPORT.read_text(encoding="utf-8"))
        if "framework" not in report:
            report = enrich_audit_report(report)
        fw = report.get("framework") or {}
        context = f"Compliance geral: {fw.get('overall_compliance_pct')}%"

    try:
        suggestion = suggest_fix(
            finding,
            api_key=api_key,
            model=body.get("model") or "deepseek-v4-flash",
            report_context=context,
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 502

    finding_id = finding.get("id")
    if finding_id and AUDIT_REPORT.exists():
        report = json.loads(AUDIT_REPORT.read_text(encoding="utf-8"))
        for f in report.get("findings") or []:
            if f.get("id") == finding_id:
                f["suggestion"] = suggestion
                break
        AUDIT_REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    return jsonify({"suggestion": suggestion, "finding_id": finding_id})


@app.post("/api/audit/run")
def audit_run():
    global _audit_running
    body = request.get_json(silent=True) or {}
    with _audit_lock:
        if _audit_running:
            return jsonify({"error": "Auditoria já em execução"}), 409
        _audit_running = True
    t = threading.Thread(target=_audit_bg, args=(body,), daemon=True)
    t.start()
    return jsonify({
        "started": True,
        "mode": body.get("mode") or "full",
        "domains": body.get("domains"),
        "skip_website": bool(body.get("skip_website", False)),
        "skip_a11y": bool(body.get("skip_a11y", False)),
    })


# ---------------------------------------------------------------------------
# AI proxy — Groq (Llama) + Cursor-compatible OpenAI endpoint
# Keys sent from client localStorage (local admin only).
# ---------------------------------------------------------------------------
AI_ENDPOINTS = {
    "groq": "https://api.groq.com/openai/v1/chat/completions",
    "cursor": "https://api.cursor.com/v1/chat/completions",
    "deepseek": "https://api.deepseek.com/v1/chat/completions",
    "claude": "https://api.anthropic.com/v1/messages",
    "anthropic": "https://api.anthropic.com/v1/messages",
}

DEFAULT_MODELS = {
    "groq": "llama-3.3-70b-versatile",
    "cursor": "gpt-4o",
    "deepseek": "deepseek-v4-flash",
    "claude": "claude-sonnet-4-6",
    "anthropic": "claude-sonnet-4-6",
}


@app.post("/api/ai/complete")
def ai_complete():
    body = request.get_json(silent=True) or {}
    provider = (body.get("provider") or "groq").lower()
    if provider == "anthropic":
        provider = "claude"
    messages = body.get("messages") or []
    temperature = float(body.get("temperature", 0.2))
    max_tokens = int(body.get("max_tokens", 4096))

    if provider not in AI_ENDPOINTS:
        return jsonify({"error": f"Provider desconhecido: {provider}"}), 400
    if not messages:
        return jsonify({"error": "messages obrigatório"}), 400

    model = (body.get("model") or DEFAULT_MODELS.get(provider, "")).strip()

    # Claude/Anthropic e demais via llm_router unificado
    if provider in ("claude", "deepseek", "groq", "cursor"):
        try:
            import sys
            scripts = ROOT / "scripts"
            if str(scripts) not in sys.path:
                sys.path.insert(0, str(scripts))
            from llm_router import chat_complete as llm_chat, resolve_api_key

            api_key = resolve_api_key(provider, body)
            if not api_key:
                return jsonify({"error": "api_key obrigatória (localStorage ou env)"}), 400
            content = llm_chat(
                messages,
                provider=provider,
                api_key=api_key,
                model=model or None,
                temperature=temperature,
                max_tokens=max_tokens,
                payload=body,
            )
            return jsonify({
                "provider": provider,
                "model": model or DEFAULT_MODELS.get(provider, ""),
                "content": content,
            })
        except Exception as exc:
            return jsonify({"error": str(exc)[:2000]}), 502

    api_key = (body.get("api_key") or "").strip()
    if not api_key:
        env_keys = {
            "deepseek": "DEEPSEEK_API_KEY",
            "groq": "GROQ_API_KEY",
            "cursor": "CURSOR_API_KEY",
            "claude": "ANTHROPIC_API_KEY",
        }
        api_key = (os.environ.get(env_keys.get(provider, "")) or "").strip()
    if not api_key:
        return jsonify({"error": "api_key obrigatória (localStorage ou env)"}), 400

    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }).encode("utf-8")

    req = urllib.request.Request(
        AI_ENDPOINTS[provider],
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        from review.ssl_utils import ssl_setup_hint, urlopen_request

        with urlopen_request(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        return jsonify({"error": f"HTTP {exc.code}", "detail": err_body[:2000]}), 502
    except urllib.error.URLError as exc:
        hint = ssl_setup_hint(exc)
        return jsonify({"error": f"{exc.reason}.{hint}"}), 502

    choice = (data.get("choices") or [{}])[0]
    content = (choice.get("message") or {}).get("content", "")
    return jsonify({
        "provider": provider,
        "model": model,
        "content": content,
        "usage": data.get("usage"),
        "raw": data,
    })


@app.get("/api/ai/templates")
def ai_templates():
    """Built-in prompt templates for validators and generation."""
    templates_path = ROOT / "datasets" / "metadata" / "ai_prompt_templates.json"
    if templates_path.exists():
        return jsonify(json.loads(templates_path.read_text(encoding="utf-8")))
    return jsonify({"templates": []})


@app.get("/api/llm/status")
def llm_status_route():
    """Status de todos os provedores LLM e roteamento por tarefa."""
    import sys
    scripts = ROOT / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from agent_common.env_loader import env_status
    from llm_router import llm_status

    return jsonify({
        **llm_status(),
        "env": env_status(),
    })


@app.post("/api/llm/route")
def llm_route():
    """Chat com roteamento automático por task (claude/deepseek/groq)."""
    body = request.get_json(silent=True) or {}
    messages = body.get("messages") or []
    if not messages:
        return jsonify({"error": "messages obrigatório"}), 400
    import sys
    scripts = ROOT / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from llm_router import route_chat, route_chat_json

    task = body.get("task") or "default"
    as_json = bool(body.get("json"))
    try:
        if as_json:
            result = route_chat_json(
                messages,
                task=task,
                provider=body.get("provider"),
                payload=body,
                temperature=float(body.get("temperature", 0.2)),
                max_tokens=int(body.get("max_tokens", 8192)),
            )
        else:
            result = route_chat(
                messages,
                task=task,
                provider=body.get("provider"),
                payload=body,
                temperature=float(body.get("temperature", 0.2)),
                max_tokens=int(body.get("max_tokens", 4096)),
            )
        return jsonify(result)
    except Exception as exc:
        return jsonify({"error": str(exc)[:2000]}), 502


# ---------------------------------------------------------------------------
# LangGraph code review — DeepSeek, skips node_modules / nodes / large files
# ---------------------------------------------------------------------------
REVIEW_REPORT = ROOT / "datasets" / "metadata" / "code_review_report.json"
REVIEW_CHANGES = ROOT / "datasets" / "metadata" / "code_review_changes.jsonl"
_review_lock = threading.Lock()
_review_running = False
_apply_running = False


def _review_bg(payload: dict) -> None:
    global _review_running
    import os
    from review.cancel import reset_cancel
    from review.graph import run_review_graph
    from review.progress import reset_progress, set_progress

    reset_cancel()
    reset_progress()
    set_progress(phase="starting")
    api_key = (payload.get("api_key") or os.environ.get("DEEPSEEK_API_KEY") or "").strip()
    out = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "error",
        "paths": payload.get("paths") or ["scripts", "platform/src"],
        "model": payload.get("model") or "deepseek-v4-flash",
    }
    try:
        if not api_key:
            raise ValueError("api_key ou DEEPSEEK_API_KEY obrigatória")
        result = run_review_graph(
            root=ROOT,
            target_paths=out["paths"],
            api_key=api_key,
            model=out["model"],
            focus=(payload.get("focus") or ""),
        )
        out.update(result)
        if "cancelada" in (result.get("error") or "").lower():
            out["status"] = "cancelled"
        else:
            out["status"] = "complete" if not result.get("error") else "partial"

        if payload.get("auto_apply") and out.get("report") and api_key:
            from review.apply import apply_fixes_from_report

            apply_result = apply_fixes_from_report(
                root=ROOT,
                report_md=out["report"],
                api_key=api_key,
                model=out["model"],
                run_id=out["generated_at"],
            )
            out["apply"] = apply_result
            if apply_result.get("applied"):
                out["apply_summary"] = f"{len(apply_result['applied'])} arquivo(s) corrigido(s)"
    except Exception as exc:
        out["error"] = str(exc)
        out["report"] = ""
    finally:
        REVIEW_REPORT.parent.mkdir(parents=True, exist_ok=True)
        REVIEW_REPORT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        reset_progress()
        with _review_lock:
            _review_running = False


@app.delete("/api/review/report")
@app.post("/api/review/clear")
def review_clear():
    """Remove relatório persistido em datasets/metadata/code_review_report.json."""
    with _review_lock:
        if _review_running:
            return jsonify({"error": "Aguarde o fim da revisão em execução"}), 409
    if REVIEW_REPORT.exists():
        REVIEW_REPORT.unlink()
    return jsonify({"cleared": True})


@app.get("/api/review/report")
def review_report():
    if not REVIEW_REPORT.exists():
        return jsonify({
            "status": "empty",
            "message": "Nenhum relatório. Execute POST /api/review/run.",
        })
    return jsonify(json.loads(REVIEW_REPORT.read_text(encoding="utf-8")))


@app.get("/api/review/status")
def review_status():
    from review.progress import get_progress

    with _review_lock:
        running = _review_running
    has = REVIEW_REPORT.exists()
    last = None
    last_status = None
    if has:
        data = json.loads(REVIEW_REPORT.read_text(encoding="utf-8"))
        last = data.get("generated_at")
        last_status = data.get("status")
    progress = get_progress()
    last_apply = None
    if has:
        data = json.loads(REVIEW_REPORT.read_text(encoding="utf-8"))
        last_apply = data.get("last_apply")
    return jsonify({
        "running": running,
        "apply_running": _apply_running,
        "has_report": has,
        "last_run": last,
        "last_status": last_status,
        "last_apply": last_apply,
        "progress": progress,
    })


@app.post("/api/review/stop")
def review_stop():
    from review.cancel import request_cancel

    with _review_lock:
        if not _review_running:
            return jsonify({"stopped": False, "message": "Nenhuma revisão em execução."})
        request_cancel()
    return jsonify({"stopping": True, "message": "Cancelamento solicitado — aguardando fim do lote atual."})


@app.post("/api/review/run")
def review_run():
    global _review_running
    body = request.get_json(silent=True) or {}
    with _review_lock:
        if _review_running:
            return jsonify({"error": "Revisão já em execução"}), 409
        _review_running = True
    t = threading.Thread(target=_review_bg, args=(body,), daemon=True)
    t.start()
    return jsonify({
        "started": True,
        "paths": body.get("paths") or ["scripts", "platform/src"],
        "auto_apply": bool(body.get("auto_apply")),
        "note": "Ignora node_modules, nodes, shards e arquivos >48KB. auto_apply grava alterações em code_review_changes.jsonl",
    })


def _apply_bg(payload: dict) -> None:
    global _apply_running
    import os
    from review.apply import apply_fixes_from_report
    from review.change_log import read_changes

    api_key = (payload.get("api_key") or os.environ.get("DEEPSEEK_API_KEY") or "").strip()
    result = {"applied": [], "skipped": [], "error": ""}
    try:
        if not api_key:
            raise ValueError("api_key ou DEEPSEEK_API_KEY obrigatória")
        if not REVIEW_REPORT.exists():
            raise ValueError("Nenhum relatório. Execute a revisão primeiro.")
        report_data = json.loads(REVIEW_REPORT.read_text(encoding="utf-8"))
        report_md = report_data.get("report") or ""
        if not report_md.strip():
            raise ValueError("Relatório vazio.")
        run_id = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        result = apply_fixes_from_report(
            root=ROOT,
            report_md=report_md,
            api_key=api_key,
            model=payload.get("model") or report_data.get("model") or "deepseek-v4-flash",
            paths=payload.get("paths"),
            log_path=REVIEW_CHANGES,
            run_id=run_id,
        )
        report_data["last_apply"] = {
            "at": run_id,
            "applied_count": len(result.get("applied") or []),
            "skipped_count": len(result.get("skipped") or []),
            "error": result.get("error") or "",
        }
        REVIEW_REPORT.write_text(json.dumps(report_data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as exc:
        result["error"] = str(exc)
    finally:
        with _review_lock:
            _apply_running = False
        result["changes_log"] = str(REVIEW_CHANGES.relative_to(ROOT))
        result["recent_log"] = read_changes(REVIEW_CHANGES, limit=20)


@app.post("/api/review/apply")
def review_apply():
    """Aplica correções sugeridas pelo último relatório (DeepSeek) com log de alterações."""
    global _apply_running
    body = request.get_json(silent=True) or {}
    with _review_lock:
        if _review_running:
            return jsonify({"error": "Aguarde o fim da revisão em execução"}), 409
        if _apply_running:
            return jsonify({"error": "Aplicação já em execução"}), 409
        _apply_running = True
    t = threading.Thread(target=_apply_bg, args=(body,), daemon=True)
    t.start()
    return jsonify({
        "started": True,
        "log": "datasets/metadata/code_review_changes.jsonl",
        "note": "Correções são gravadas com hash antes/depois; paths restritos a scripts, platform/src, docs",
    })


@app.get("/api/review/changes")
def review_changes():
    from review.change_log import read_changes

    limit = min(int(request.args.get("limit", 50)), 200)
    return jsonify({
        "log_path": str(REVIEW_CHANGES.relative_to(ROOT)),
        "entries": read_changes(REVIEW_CHANGES, limit=limit),
    })


@app.get("/api/review/rules")
def review_rules():
    from review.config import (
        MAX_FILE_BYTES,
        MAX_FILE_LINES,
        MAX_FILES_TO_REVIEW,
        SKIP_DIR_NAMES,
        SKIP_PATH_PREFIXES,
    )
    return jsonify({
        "skip_dirs": sorted(SKIP_DIR_NAMES),
        "skip_prefixes": list(SKIP_PATH_PREFIXES),
        "max_file_bytes": MAX_FILE_BYTES,
        "max_file_lines": MAX_FILE_LINES,
        "max_files": MAX_FILES_TO_REVIEW,
    })


# ---------------------------------------------------------------------------
# APGAR Master Data pilot — LangGraph + DeepSeek (api_key do app)
# ---------------------------------------------------------------------------
def _apgar_sys_path() -> None:
    import sys

    scripts = ROOT / "scripts"
    agents = scripts / "apgar_agents"
    for p in (str(scripts), str(agents)):
        if p not in sys.path:
            sys.path.insert(0, p)


@app.get("/api/apgar/status")
def apgar_status():
    _apgar_sys_path()
    from apgar.field_registry import modules  # noqa: WPS433

    mod = modules()
    report_path = ROOT / "datasets" / "master-data" / "apgar" / "validation_report.json"
    report = {}
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
    return jsonify({
        "concept_code": "APGAR",
        "completion_pct": mod.get("overall_completion_pct"),
        "status": mod.get("status"),
        "last_validation": report.get("generated_at"),
        "validation_pass_rate": report.get("pass_rate"),
        "errors": report.get("errors", []),
        "deepseek_env": bool(os.environ.get("DEEPSEEK_API_KEY")),
        "note": "Envie api_key no body (deepseekApiKey do app) como em /api/review/run",
    })


@app.post("/api/apgar/validate")
def apgar_validate():
    _apgar_sys_path()
    from apgar.validate_apgar import run_validation  # noqa: WPS433

    rep = run_validation()
    return jsonify({
        "ok": len(rep.errors) == 0,
        "checks": rep.checks,
        "passed": len(rep.passed),
        "warnings": len(rep.warnings),
        "errors": rep.errors,
    })


@app.post("/api/apgar/field/run")
def apgar_field_run():
    body = request.get_json(silent=True) or {}
    field_id = (body.get("field_id") or "").strip()
    if not field_id:
        return jsonify({"error": "field_id obrigatório"}), 400

    _apgar_sys_path()
    from api_helpers import llm_enabled, resolve_deepseek  # noqa: WPS433
    from graph import run_field  # noqa: WPS433

    api_key, model = resolve_deepseek(body)
    use_llm = llm_enabled(body)
    if use_llm and not api_key:
        return jsonify({"error": "api_key obrigatória (deepseekApiKey do app ou DEEPSEEK_API_KEY)"}), 400

    try:
        result = run_field(field_id, api_key=api_key, model=model, use_llm=use_llm)
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    return jsonify({
        "ok": bool((result.get("validation") or {}).get("validation_passed")),
        "llm_enabled": result.get("llm_enabled"),
        "model": result.get("model"),
        "result": result,
    })


@app.post("/api/apgar/translation/run")
def apgar_translation_run():
    body = request.get_json(silent=True) or {}
    _apgar_sys_path()
    from api_helpers import llm_enabled, resolve_deepseek  # noqa: WPS433

    api_key, model = resolve_deepseek(body)
    use_llm = llm_enabled(body)
    write = bool(body.get("write", True))

    if use_llm and not api_key:
        return jsonify({"error": "api_key obrigatória (deepseekApiKey do app ou DEEPSEEK_API_KEY)"}), 400

    try:
        if use_llm and api_key:
            from translation_graph import run_translation_graph  # noqa: WPS433

            out = run_translation_graph(
                api_key=api_key,
                model=model,
                use_llm=True,
                refresh_tier=body.get("refresh_tier") or "machine_from_en",
                write=write,
            )
        else:
            from translation_agent import run_deterministic_pipeline  # noqa: WPS433

            out = run_deterministic_pipeline(write=write)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    return jsonify({"ok": out.get("ok"), "llm_enabled": out.get("llm_enabled"), "result": out})


@app.post("/api/apgar/phases/run")
def apgar_phases_run():
    body = request.get_json(silent=True) or {}
    phase = (body.get("phase") or "").strip().upper()
    all_phases = bool(body.get("all"))

    _apgar_sys_path()
    from phases.registry import PHASE_AGENTS  # noqa: WPS433
    from api_helpers import llm_enabled, resolve_deepseek  # noqa: WPS433

    api_key, model = resolve_deepseek(body)
    use_llm = llm_enabled(body)

    if phase == "M11" and use_llm:
        if not api_key:
            return jsonify({"error": "api_key obrigatória para M11 com LLM"}), 400
        from translation_graph import run_translation_graph  # noqa: WPS433

        out = run_translation_graph(api_key=api_key, model=model, use_llm=True, write=bool(body.get("write")))
        return jsonify({"ok": out.get("ok"), "phase": "M11", "result": out})

    agents = PHASE_AGENTS
    if phase:
        agents = [a for a in PHASE_AGENTS if a.phase_id == phase]
        if not agents:
            return jsonify({"error": f"Fase desconhecida: {phase}"}), 404

    import dataclasses

    results = [dataclasses.asdict(a.run()) for a in agents]
    ok = all(r.get("ok") for r in results)
    return jsonify({"ok": ok, "results": results})


# ---------------------------------------------------------------------------
# Content Pending Master Data — FLA, SIM, MMP, PRT, PKT, FAQ
# ---------------------------------------------------------------------------
def _content_sys_path() -> None:
    import sys

    scripts = ROOT / "scripts"
    agents = scripts / "content_agents"
    for p in (str(scripts), str(agents)):
        if p not in sys.path:
            sys.path.insert(0, p)


@app.get("/api/content-pending/status")
def content_pending_status():
    _content_sys_path()
    from content.field_registry import modules, pending_items  # noqa: WPS433
    from content.queue_stats import compute_queue_stats  # noqa: WPS433

    mod = modules()
    pending = pending_items()
    stats = compute_queue_stats(pending)
    report_path = ROOT / "datasets" / "master-data" / "content-pending" / "validation_report.json"
    report = {}
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))

    from content.workflow_store import list_workflows  # noqa: WPS433

    awaiting = list_workflows(status="awaiting_approval", limit=50)
    awaiting_brief = [
        {
            "workflow_id": w.get("workflow_id"),
            "pending_id": w.get("pending_id"),
            "entity_code": w.get("entity_code"),
            "artifact_type": w.get("artifact_type"),
            "title_pt": (w.get("pending_item") or {}).get("title_pt"),
            "status": w.get("status"),
        }
        for w in awaiting
    ]
    return jsonify({
        "program_code": "CONTENT_PENDING",
        "completion_pct": stats["overall_completion_pct"],
        "overall_completion_pct": stats["overall_completion_pct"],
        "status": stats["program_status"],
        "catalog_status": pending.get("status"),
        "catalog_total": stats["catalog_total"],
        "pending_count": stats["pending_count"],
        "applied_count": stats["applied_count"],
        "pending_total": stats["pending_count"],
        "counts_by_status": stats["counts_by_status"],
        "counts_by_type": pending.get("counts_by_type"),
        "pending_items": pending.get("items", [])[:200],
        "awaiting_approval_count": len(awaiting),
        "awaiting_approval": awaiting_brief,
        "last_validation": report.get("generated_at"),
        "pass_rate": report.get("pass_rate"),
        "errors": report.get("errors", []),
        "note": "Gerar → awaiting_approval → Aprovar grava no dataset. Doc 14 é gate separado (/code-sequence).",
    })


@app.post("/api/content-pending/validate")
def content_pending_validate():
    _content_sys_path()
    from content.validate_content import run_validation  # noqa: WPS433

    rep = run_validation()
    return jsonify({
        "ok": len(rep.errors) == 0,
        "checks": rep.checks,
        "passed": len(rep.passed),
        "warnings": len(rep.warnings),
        "errors": rep.errors,
    })


@app.post("/api/content-pending/catalog/rebuild")
def content_pending_catalog_rebuild():
    _content_sys_path()
    from content.pending_catalog import build_pending_queue  # noqa: WPS433

    doc = build_pending_queue()
    out = ROOT / "datasets" / "master-data" / "content-pending" / "pending_items.json"
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return jsonify({"ok": True, "total": doc["total"], "counts_by_type": doc["counts_by_type"]})


@app.post("/api/content-pending/field/run")
def content_pending_field_run():
    body = request.get_json(silent=True) or {}
    field_id = (body.get("field_id") or "").strip()
    if not field_id:
        return jsonify({"error": "field_id obrigatório"}), 400

    _content_sys_path()
    import sys

    if str(ROOT / "scripts" / "content_agents") not in sys.path:
        sys.path.insert(0, str(ROOT / "scripts" / "content_agents"))
    if str(ROOT / "scripts" / "apgar_agents") not in sys.path:
        sys.path.insert(1, str(ROOT / "scripts" / "apgar_agents"))
    from api_helpers import llm_enabled, resolve_deepseek  # noqa: WPS433
    import graph as content_graph  # noqa: WPS433

    api_key, model = resolve_deepseek(body)
    use_llm = llm_enabled(body)
    if use_llm and not api_key:
        return jsonify({"error": "api_key obrigatória"}), 400

    try:
        result = content_graph.run_field(field_id, api_key=api_key, model=model, use_llm=use_llm)
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    from agent_common.sanitize import sanitize_agent_result  # noqa: WPS433

    result = sanitize_agent_result(result)
    return jsonify({
        "ok": bool((result.get("validation") or {}).get("validation_passed")),
        "llm_enabled": result.get("llm_enabled"),
        "result": result,
    })


@app.post("/api/content-pending/phases/run")
def content_pending_phases_run():
    body = request.get_json(silent=True) or {}
    phase = (body.get("phase") or "").strip().upper()

    _content_sys_path()
    from phases.registry import PHASE_AGENTS  # noqa: WPS433

    agents = PHASE_AGENTS
    if phase:
        agents = [a for a in PHASE_AGENTS if a.phase_id == phase]
        if not agents:
            return jsonify({"error": f"Fase desconhecida: {phase}"}), 404

    import dataclasses

    results = [dataclasses.asdict(a.run()) for a in agents]
    ok = all(r.get("ok") for r in results)
    return jsonify({"ok": ok, "results": results})


@app.get("/api/content-pending/workflow")
def content_pending_workflow_list():
    _content_sys_path()
    from content.workflow_store import list_workflows  # noqa: WPS433

    status = (request.args.get("status") or "").strip() or None
    limit = min(int(request.args.get("limit", 50)), 200)
    workflows = list_workflows(status=status, limit=limit)
    return jsonify({"workflows": workflows, "count": len(workflows)})


@app.get("/api/content-pending/workflow/<workflow_id>")
def content_pending_workflow_get(workflow_id: str):
    _content_sys_path()
    from content.workflow_store import load_workflow  # noqa: WPS433
    from agent_common.sanitize import sanitize_agent_result  # noqa: WPS433

    try:
        wf = load_workflow(workflow_id)
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    return jsonify(sanitize_agent_result(wf))


@app.post("/api/content-pending/workflow/run")
def content_pending_workflow_run():
    body = request.get_json(silent=True) or {}
    _content_sys_path()
    import sys

    if str(ROOT / "scripts" / "content_agents") not in sys.path:
        sys.path.insert(0, str(ROOT / "scripts" / "content_agents"))
    if str(ROOT / "scripts" / "apgar_agents") not in sys.path:
        sys.path.insert(1, str(ROOT / "scripts" / "apgar_agents"))
    from api_helpers import llm_enabled, resolve_deepseek  # noqa: WPS433
    from content.workflow_runner import run_bulk, run_pending_item  # noqa: WPS433
    from agent_common.sanitize import sanitize_agent_result  # noqa: WPS433

    api_key, model = resolve_deepseek(body)
    use_llm = llm_enabled(body)
    mode = (body.get("mode") or "individual").strip().lower()

    if use_llm and not api_key:
        return jsonify({"error": "api_key obrigatória para LLM"}), 400

    try:
        if mode == "bulk":
            out = run_bulk(
                artifact_type=(body.get("artifact_type") or "").strip().upper() or None,
                limit=min(int(body.get("limit", 5)), 20),
                api_key=api_key,
                model=model,
                use_llm=use_llm,
            )
            out["results"] = [sanitize_agent_result(r) for r in out.get("results", [])]
            return jsonify(out)
        pending_id = (body.get("pending_id") or "").strip()
        if not pending_id:
            return jsonify({"error": "pending_id obrigatório no modo individual"}), 400
        wf = run_pending_item(pending_id, api_key=api_key, model=model, use_llm=use_llm)
        return jsonify({"ok": True, "workflow": sanitize_agent_result(wf)})
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.post("/api/content-pending/workflow/approve")
def content_pending_workflow_approve():
    body = request.get_json(silent=True) or {}
    workflow_id = (body.get("workflow_id") or "").strip()
    if not workflow_id:
        return jsonify({"error": "workflow_id obrigatório"}), 400

    _content_sys_path()
    from content.workflow_runner import approve_workflow  # noqa: WPS433
    from agent_common.sanitize import sanitize_agent_result  # noqa: WPS433

    try:
        out = approve_workflow(workflow_id)
        return jsonify({"ok": True, **sanitize_agent_result(out)})
    except (KeyError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.post("/api/content-pending/workflow/reject")
def content_pending_workflow_reject():
    body = request.get_json(silent=True) or {}
    workflow_id = (body.get("workflow_id") or "").strip()
    if not workflow_id:
        return jsonify({"error": "workflow_id obrigatório"}), 400

    _content_sys_path()
    from content.workflow_runner import reject_workflow  # noqa: WPS433

    reason = (body.get("reason") or "").strip()
    wf = reject_workflow(workflow_id, reason=reason)
    return jsonify({"ok": True, "workflow": wf})


@app.post("/api/content-pending/archive/prepare")
def content_pending_archive_prepare():
    body = request.get_json(silent=True) or {}
    _content_sys_path()
    from content.apply_proposal import archive_legacy_datasets  # noqa: WPS433

    dry_run = body.get("dry_run", True) is not False
    result = archive_legacy_datasets(dry_run=dry_run)
    return jsonify({"ok": True, **result})


@app.post("/api/content-factory/sync")
def content_factory_sync():
    """Populate ContentRequest kanban from content-pending queue."""
    body = request.get_json(silent=True) or {}
    country = (body.get("country") or request.args.get("country") or "BR").strip().upper()
    try:
        from content_factory_sync import sync_content_requests  # noqa: WPS433
    except ImportError:
        import sys
        scripts = str(ROOT / "scripts")
        if scripts not in sys.path:
            sys.path.insert(0, scripts)
        from content_factory_sync import sync_content_requests  # noqa: WPS433
    try:
        result = sync_content_requests(country)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"ok": True, **result})


@app.get("/api/pending/inventory")
def pending_inventory():
    import sys
    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    from agent_common.pending_inventory import collect  # noqa: WPS433
    return jsonify(collect())


@app.post("/api/pending/run")
def pending_run():
    """Executa agentes apenas nas pendências detectadas."""
    body = request.get_json(silent=True) or {}
    use_llm = body.get("llm") is True
    import sys
    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    from run_pending_agents import run_pending  # noqa: WPS433
    report = run_pending(use_llm=use_llm)
    return jsonify(report)


def _daily_agent_sys_path() -> None:
    import sys

    for p in (str(ROOT / "scripts"), str(ROOT / "scripts" / "daily_agent")):
        if p not in sys.path:
            sys.path.insert(0, p)


@app.get("/api/daily-agent/status")
def daily_agent_status():
    _daily_agent_sys_path()
    state_path = ROOT / "datasets" / "metadata" / "daily_agent_state.json"
    report_path = ROOT / "datasets" / "metadata" / "daily_agent_report.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else {}
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else {}
    from agent_common.pending_inventory import collect  # noqa: WPS433

    inv = collect()
    return jsonify({
        "state": state,
        "last_report": report,
        "pending_actions": len(inv.get("actions", [])),
        "platform_complete": state.get("platform_complete", False),
        "next_run_at": state.get("next_run_at"),
        "single_command": "python scripts/run_daily_loop.py --stop-when-complete",
        "interval_default": "24h",
    })


@app.post("/api/daily-agent/run")
def daily_agent_run():
    body = request.get_json(silent=True) or {}
    _daily_agent_sys_path()
    from orchestrator import run_daily_cycle  # noqa: WPS433

    try:
        report = run_daily_cycle(
            use_llm=body.get("llm") is True,
            med_limit=int(body.get("med_limit", 25)),
            asset_limit=int(body.get("asset_limit", 50)),
            full_audit=body.get("full_audit") is True,
            rebuild_site=body.get("rebuild_site") is True,
            no_ssl_verify=body.get("no_ssl_verify", True) is not False,
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    if report.get("locked"):
        return jsonify(report), 409
    return jsonify(report)


# ---------------------------------------------------------------------------
# Site Full — orquestrador único zero→100%
# ---------------------------------------------------------------------------
def _site_full_sys_path() -> None:
    import sys

    for sub in ("site_agents", "site_full", "content_agents", "apgar_agents", "content"):
        p = str(ROOT / "scripts" / sub)
        if p not in sys.path:
            sys.path.insert(0, p)


@app.get("/api/site-full/manifest")
def site_full_manifest():
    _site_full_sys_path()
    from site_full.field_registry import manifest  # noqa: WPS433

    return jsonify(manifest())


@app.get("/api/site-full/status")
def site_full_status():
    _site_full_sys_path()
    from site_full.field_registry import manifest  # noqa: WPS433

    mods = manifest().get("modules", [])
    avg = round(sum(m.get("completion_pct", 0) for m in mods) / len(mods), 1) if mods else 0
    return jsonify({
        "program_code": "SITE_FULL",
        "modules": len(mods),
        "overall_completion_pct": avg,
        "single_command": "python scripts/site_agents/run_site_full.py --all",
        "gaps": manifest().get("gaps_user_should_add", []),
    })


@app.post("/api/site-full/run")
def site_full_run():
    body = request.get_json(silent=True) or {}
    _site_full_sys_path()
    from api_helpers import llm_enabled, resolve_deepseek  # noqa: WPS433
    from orchestrator import run_all  # noqa: WPS433

    api_key, model = resolve_deepseek(body)
    use_llm = llm_enabled(body)
    module_ids = body.get("modules")
    if isinstance(module_ids, str):
        module_ids = [x.strip() for x in module_ids.split(",") if x.strip()]

    report = run_all(
        module_ids=module_ids,
        api_key=api_key,
        model=model,
        use_llm=use_llm,
        bulk_limit=min(int(body.get("bulk_limit", 5)), 20),
        approve=bool(body.get("approve")),
        build=body.get("build", True) is not False,
        archive_dry_run=body.get("archive_dry_run", True) is not False,
    )
    return jsonify(report)


# ---------------------------------------------------------------------------
# Global expansion — países, idiomas, fusos, perfis
# ---------------------------------------------------------------------------
def _global_expansion_sys_path() -> None:
    import sys

    for sub in ("global_expansion_agents", "global_expansion", "content_agents", "apgar_agents", "content"):
        p = str(ROOT / "scripts" / sub)
        if p not in sys.path:
            sys.path.insert(0, p)


@app.get("/api/global-expansion/status")
def global_expansion_status():
    _global_expansion_sys_path()
    from global_expansion.validate_global import run_validation  # noqa: WPS433

    exp = ROOT / "datasets" / "master-data" / "global-expansion"
    cov = {}
    i18n_cov = {}
    if (exp / "coverage_report.json").exists():
        cov = json.loads((exp / "coverage_report.json").read_text(encoding="utf-8"))
    if (exp / "i18n_coverage_report.json").exists():
        i18n_cov = json.loads((exp / "i18n_coverage_report.json").read_text(encoding="utf-8"))
    from global_expansion.update_progress import persist_global_progress  # noqa: WPS433

    prog = persist_global_progress()
    rep = run_validation()
    return jsonify({
        "program_code": "GLOBAL_EXPANSION",
        "coverage": cov,
        "i18n_coverage": i18n_cov,
        "overall_completion_pct": prog.get("overall_completion_pct", cov.get("overall_completion_pct", 0)),
        "progress_segments": prog.get("segments", {}),
        "validation_ok": len(rep.errors) == 0,
        "errors": rep.errors,
        "single_command": "python scripts/global_expansion_agents/run_global.py --all --rebuild",
    })


@app.post("/api/global-expansion/run")
def global_expansion_run():
    body = request.get_json(silent=True) or {}
    _global_expansion_sys_path()
    from api_helpers import llm_enabled, resolve_deepseek  # noqa: WPS433
    from orchestrator import run_global  # noqa: WPS433

    api_key, _model = resolve_deepseek(body)
    use_llm = llm_enabled(body)
    profiles = body.get("profiles")
    if isinstance(profiles, str):
        profiles = [x.strip() for x in profiles.split(",") if x.strip()]

    report = run_global(
        profiles=profiles,
        api_key=api_key,
        use_llm=use_llm,
        rebuild=body.get("rebuild", True) is not False,
        careers_limit=int(body.get("careers_limit", 195 if body.get("all") else 10)),
        i18n_limit=int(body.get("i18n_limit", 30 if body.get("all") else 10)),
        model=body.get("model"),
    )
    return jsonify(report)


@app.get("/api/careers/status")
def careers_status():
    careers = ROOT / "datasets" / "master-data" / "careers"
    cov = {}
    if (careers / "coverage_report.json").exists():
        cov = json.loads((careers / "coverage_report.json").read_text(encoding="utf-8"))
    return jsonify({
        "program_code": "CAREERS_GLOBAL",
        "coverage": cov,
        "single_command": "python scripts/career_agents/run_careers.py --all --rebuild",
    })


@app.post("/api/careers/run")
def careers_run():
    body = request.get_json(silent=True) or {}
    _global_expansion_sys_path()
    import importlib.util
    from api_helpers import llm_enabled, resolve_deepseek  # noqa: WPS433

    path = ROOT / "scripts" / "career_agents" / "orchestrator.py"
    spec = importlib.util.spec_from_file_location("career_orchestrator", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)

    api_key, _model = resolve_deepseek(body)
    use_llm = llm_enabled(body)
    countries = body.get("countries")
    if isinstance(countries, str):
        countries = [x.strip().upper() for x in countries.split(",") if x.strip()]

    report = mod.run_careers(
        countries=countries,
        limit=int(body.get("limit", 195 if body.get("all") else 10)),
        api_key=api_key,
        use_llm=use_llm,
        model=body.get("model"),
        rebuild=body.get("rebuild", True) is not False,
    )
    return jsonify(report)


# ---------------------------------------------------------------------------
# Resource expansion — CV, escalas, indicadores, dicionário, biblioteca, slides, games
# ---------------------------------------------------------------------------
def _resource_expansion_sys_path() -> None:
    import sys

    for sub in ("resource_expansion_agents", "resource_expansion", "apgar_agents", "content_agents"):
        p = str(ROOT / "scripts" / sub)
        if p not in sys.path:
            sys.path.insert(0, p)


@app.get("/api/resource-expansion/status")
def resource_expansion_status():
    _resource_expansion_sys_path()
    from validate_resources import run_validation  # noqa: WPS433
    from update_progress import persist_progress  # noqa: WPS433

    res = ROOT / "datasets" / "master-data" / "resource-expansion"
    refresh = request.args.get("refresh", "").strip() in ("1", "true", "yes")

    if refresh:
        progress = persist_progress()
    else:
        reg_path = res / "modules_registry.json"
        cov_path = res / "coverage_report.json"
        reg = json.loads(reg_path.read_text(encoding="utf-8")) if reg_path.is_file() else {"modules": []}
        cov = json.loads(cov_path.read_text(encoding="utf-8")) if cov_path.is_file() else {}
        progress = {
            "overall_completion_pct": cov.get("overall_completion_pct", 0),
            "modules": reg.get("modules", []),
            "module_progress": cov.get("module_progress", {}),
        }

    cov = {}
    if (res / "coverage_report.json").exists():
        cov = json.loads((res / "coverage_report.json").read_text(encoding="utf-8"))

    lib_stats = {}
    lib_path = ROOT / "datasets" / "content" / "library" / "library_visual_assets.json"
    if lib_path.is_file():
        lib = json.loads(lib_path.read_text(encoding="utf-8"))
        stats = lib.get("sync_stats") or {}
        downloaded = sum(1 for r in lib.get("records", []) if r.get("status") == "downloaded")
        lib_stats = {
            "total": lib.get("total_assets", len(lib.get("records", []))),
            "downloaded": downloaded,
            "last_sync_at": lib.get("last_sync_at"),
            "last_sync": stats,
        }

    blockers = []
    for mod in progress.get("modules", []):
        gaps = mod.get("gaps") or []
        pct = mod.get("completion_pct", 0)
        if pct >= 100:
            continue
        if gaps:
            blockers.append({"module_id": mod.get("module_id"), "pct": pct, "gaps": gaps, "status": mod.get("status")})
        elif mod.get("module_id") == "M23_library_assets":
            blockers.append({
                "module_id": "M23_library_assets",
                "pct": pct,
                "gaps": [f"Assets baixados: {lib_stats.get('downloaded', 0)}/{lib_stats.get('total', '?')} — URLs produção frequentemente 404"],
                "status": mod.get("status"),
            })
        elif mod.get("module_id") == "M22_dictionary":
            med = cov.get("medication_dictionary") or {}
            nd_path = ROOT / "datasets" / "master" / "nursing_dictionary.json"
            nd_n = 0
            nd_defs = 0
            if nd_path.is_file():
                nd_doc = json.loads(nd_path.read_text(encoding="utf-8"))
                nd_recs = nd_doc.get("records", [])
                nd_n = len(nd_recs)
                nd_defs = sum(1 for r in nd_recs if r.get("definition_pt") or r.get("definition"))
            blockers.append({
                "module_id": "M22_dictionary",
                "pct": pct,
                "gaps": [
                    f"Enfermagem: {nd_defs}/{nd_n} definições",
                    (
                        f"Medicamentos: {med.get('with_definition', 0)}/{med.get('total_drug_references', 500)} "
                        "vinculados a DrugReference (parent_entity_code)"
                    ),
                ],
                "status": mod.get("status"),
            })

    rep = run_validation()
    return jsonify({
        "program_code": "RESOURCE_EXPANSION",
        "coverage": cov,
        "modules": progress.get("modules", []),
        "overall_completion_pct": progress.get("overall_completion_pct", cov.get("overall_completion_pct", 0)),
        "module_progress": progress.get("module_progress", {}),
        "library_sync": lib_stats,
        "blockers": blockers,
        "progress_updated_at": cov.get("generated_at"),
        "validation_ok": len(rep.errors) == 0,
        "errors": rep.errors,
        "medication_dictionary": cov.get("medication_dictionary"),
        "single_command": "python scripts/resource_expansion_agents/run_resources.py --all",
        "note": "Conclusão ~40% é esperada até dicionário, assets e CV avançarem. Use Executar ou ?refresh=1.",
    })


@app.post("/api/resource-expansion/run")
def resource_expansion_run():
    body = request.get_json(silent=True) or {}
    _resource_expansion_sys_path()
    import importlib.util
    from api_helpers import llm_enabled, resolve_deepseek  # noqa: WPS433

    api_key, _model = resolve_deepseek(body)
    use_llm = llm_enabled(body)

    path = ROOT / "scripts" / "resource_expansion_agents" / "orchestrator.py"
    spec = importlib.util.spec_from_file_location("resource_orchestrator", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    try:
        spec.loader.exec_module(mod)
        report = mod.run_resources(
            rebuild=body.get("rebuild", True) is not False,
            sync_assets=body.get("sync_assets", True) is not False,
            build_slides=body.get("build_slides", True) is not False,
            asset_limit=int(body.get("asset_limit", 30)),
            api_key=api_key,
            use_llm=use_llm,
            run_medication_dictionary=body.get("run_medication_dictionary", True) is not False,
            medication_dict_limit=int(body.get("medication_dict_limit", 10)),
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    return jsonify(report)


# ---------------------------------------------------------------------------
# Medication dictionary — entradas DICT vinculadas a DrugReference (doc 14)
# ---------------------------------------------------------------------------
def _medication_dictionary_sys_path() -> None:
    prepare_agent_package("medication_dictionary_agents")


@app.get("/api/medication-dictionary/status")
def medication_dictionary_status():
    _medication_dictionary_sys_path()
    from status import collect_status  # noqa: WPS433

    return jsonify(collect_status())


@app.post("/api/medication-dictionary/catalog/rebuild")
def medication_dictionary_catalog_rebuild():
    body = request.get_json(silent=True) or {}
    _medication_dictionary_sys_path()
    from catalog import build_queue  # noqa: WPS433

    limit = body.get("limit")
    result = build_queue(limit=int(limit) if limit is not None else None)
    return jsonify(result)


@app.post("/api/medication-dictionary/run")
def medication_dictionary_run():
    body = request.get_json(silent=True) or {}
    _medication_dictionary_sys_path()
    from api_helpers import llm_enabled, resolve_deepseek  # noqa: WPS433
    from graph import run_batch, run_item  # noqa: WPS433

    api_key, _model = resolve_deepseek(body)
    use_llm = llm_enabled(body)
    pending_id = (body.get("pending_id") or "").strip()

    try:
        if pending_id:
            result = run_item(
                pending_id,
                api_key=api_key,
                use_llm=use_llm,
                apply=body.get("apply", True) is not False,
            )
        else:
            result = run_batch(
                limit=int(body.get("limit", 10)),
                api_key=api_key,
                use_llm=use_llm,
                apply=body.get("apply", True) is not False,
            )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    return jsonify(result)


# ---------------------------------------------------------------------------
# Notificação compulsória — legislação BR nacional + estadual (doc 14)
# ---------------------------------------------------------------------------
def _compulsory_notification_sys_path() -> None:
    prepare_agent_package("compulsory_notification_agents")


@app.get("/api/compulsory-notifications/status")
def compulsory_notifications_status():
    _compulsory_notification_sys_path()
    from status import collect_status  # noqa: WPS433

    return jsonify(collect_status())


@app.post("/api/compulsory-notifications/scrape")
def compulsory_notifications_scrape():
    body = request.get_json(silent=True) or {}
    _compulsory_notification_sys_path()
    from graph import run_scrape  # noqa: WPS433

    limit = body.get("limit")
    try:
        result = run_scrape(limit=int(limit) if limit is not None else None)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    return jsonify(result)


@app.post("/api/compulsory-notifications/catalog/rebuild")
def compulsory_notifications_catalog_rebuild():
    body = request.get_json(silent=True) or {}
    _compulsory_notification_sys_path()
    from catalog import build_queue  # noqa: WPS433

    if body.get("scrape_first"):
        from graph import run_scrape  # noqa: WPS433

        run_scrape(limit=body.get("scrape_limit"))
    limit = body.get("limit")
    result = build_queue(limit=int(limit) if limit is not None else None)
    return jsonify(result)


@app.post("/api/compulsory-notifications/run")
def compulsory_notifications_run():
    body = request.get_json(silent=True) or {}
    _compulsory_notification_sys_path()
    from api_helpers import llm_enabled, resolve_deepseek  # noqa: WPS433
    from graph import run_batch, run_item  # noqa: WPS433

    api_key, _model = resolve_deepseek(body)
    use_llm = llm_enabled(body)
    pending_id = (body.get("pending_id") or "").strip()

    try:
        if pending_id:
            result = run_item(
                pending_id,
                api_key=api_key,
                use_llm=use_llm,
                apply=body.get("apply", True) is not False,
            )
        else:
            result = run_batch(
                limit=int(body.get("limit", 10)),
                api_key=api_key,
                use_llm=use_llm,
                apply=body.get("apply", True) is not False,
                scrape_first=body.get("scrape_first", False) is True,
                scrape_limit=body.get("scrape_limit"),
            )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    return jsonify(result)


@app.post("/api/compulsory-notifications/validate")
def compulsory_notifications_validate():
    _compulsory_notification_sys_path()
    from validate_program import run_validation  # noqa: WPS433

    rep = run_validation()
    return jsonify({"ok": rep.ok, "errors": rep.errors, "warnings": rep.warnings})


# ---------------------------------------------------------------------------
# Legislação brasileira — CF, LOSUS, profissional, vínculos ferramentas (doc 14)
# ---------------------------------------------------------------------------
def _brazilian_legislation_sys_path() -> None:
    prepare_agent_package("brazilian_legislation_agents")


@app.get("/api/brazilian-legislation/status")
def brazilian_legislation_status():
    _brazilian_legislation_sys_path()
    from status import collect_status  # noqa: WPS433

    return jsonify(collect_status())


@app.post("/api/brazilian-legislation/discover")
def brazilian_legislation_discover():
    body = request.get_json(silent=True) or {}
    _brazilian_legislation_sys_path()
    from discover import discover  # noqa: WPS433

    limit = body.get("limit")
    return jsonify(discover(limit=int(limit) if limit is not None else None))


@app.post("/api/brazilian-legislation/fetch")
def brazilian_legislation_fetch():
    body = request.get_json(silent=True) or {}
    _brazilian_legislation_sys_path()
    from fetch_stage import fetch_all  # noqa: WPS433

    limit = body.get("limit")
    return jsonify(fetch_all(
        limit=int(limit) if limit is not None else None,
        only_stale=body.get("only_stale", True) is not False,
    ))


@app.post("/api/brazilian-legislation/refresh")
def brazilian_legislation_refresh():
    body = request.get_json(silent=True) or {}
    _brazilian_legislation_sys_path()
    from graph import run_pipeline  # noqa: WPS433

    try:
        result = run_pipeline(
            limit=int(body.get("limit", 10)),
            only_stale=body.get("only_stale", True) is not False,
            skip_fetch=body.get("skip_fetch", False) is True,
            apply=body.get("apply", True) is not False,
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    return jsonify(result)


@app.post("/api/brazilian-legislation/validate")
def brazilian_legislation_validate():
    _brazilian_legislation_sys_path()
    from validate_program import run_validation  # noqa: WPS433

    rep = run_validation()
    return jsonify({"ok": rep.ok, "errors": rep.errors, "warnings": rep.warnings})


# ---------------------------------------------------------------------------
# ANVISA open data — dados.gov.br / dados.anvisa.gov.br (atualização mensal)
# ---------------------------------------------------------------------------
def _anvisa_open_data_sys_path() -> None:
    prepare_agent_package("anvisa_open_data_agents")


@app.get("/api/anvisa-open-data/status")
def anvisa_open_data_status():
    _anvisa_open_data_sys_path()
    from status import collect_status  # noqa: WPS433

    return jsonify(collect_status())


@app.post("/api/anvisa-open-data/sync-catalog")
def anvisa_open_data_sync_catalog():
    body = request.get_json(silent=True) or {}
    _anvisa_open_data_sys_path()
    from catalog import sync_catalog  # noqa: WPS433

    return jsonify(sync_catalog(verify_ssl=body.get("verify_ssl", True) is not False))


@app.post("/api/anvisa-open-data/discover")
def anvisa_open_data_discover():
    body = request.get_json(silent=True) or {}
    _anvisa_open_data_sys_path()
    from discover import discover  # noqa: WPS433

    limit = body.get("limit")
    return jsonify(discover(limit=int(limit) if limit is not None else None))


@app.post("/api/anvisa-open-data/fetch")
def anvisa_open_data_fetch():
    body = request.get_json(silent=True) or {}
    _anvisa_open_data_sys_path()
    from fetch_stage import fetch_all  # noqa: WPS433

    limit = body.get("limit")
    return jsonify(fetch_all(
        limit=int(limit) if limit is not None else None,
        only_stale=body.get("only_stale", True) is not False,
        verify_ssl=body.get("verify_ssl", True) is not False,
    ))


@app.post("/api/anvisa-open-data/monthly")
def anvisa_open_data_monthly():
    body = request.get_json(silent=True) or {}
    _anvisa_open_data_sys_path()
    from graph import run_pipeline  # noqa: WPS433

    try:
        result = run_pipeline(
            limit=int(body.get("limit", 5)),
            only_stale=body.get("only_stale", True) is not False,
            skip_fetch=body.get("skip_fetch", False) is True,
            sync_catalog_first=body.get("sync_catalog", True) is not False,
            apply=body.get("apply", True) is not False,
            verify_ssl=body.get("verify_ssl", True) is not False,
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    return jsonify(result)


@app.post("/api/anvisa-open-data/validate")
def anvisa_open_data_validate():
    _anvisa_open_data_sys_path()
    from validate_program import run_validation  # noqa: WPS433

    rep = run_validation()
    return jsonify({"ok": rep.ok, "errors": rep.errors, "warnings": rep.warnings})


# ---------------------------------------------------------------------------
# Doc 14 — aprovação master_code_sequence_proposal
# ---------------------------------------------------------------------------
def _code_sequence_sys_path() -> None:
    import sys

    p = str(ROOT / "scripts" / "code_sequence")
    if p not in sys.path:
        sys.path.insert(0, p)


@app.get("/api/code-sequence/status")
def code_sequence_status():
    _code_sequence_sys_path()
    from approval import get_status  # noqa: WPS433

    return jsonify(get_status())


@app.post("/api/code-sequence/approve")
def code_sequence_approve():
    body = request.get_json(silent=True) or {}
    _code_sequence_sys_path()
    from approval import approve  # noqa: WPS433

    checklist = body.get("checklist") or {}
    try:
        return jsonify(approve(
            approver=(body.get("approver") or "").strip(),
            checklist=checklist,
            notes=(body.get("notes") or "").strip(),
        ))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/code-sequence/reject")
def code_sequence_reject():
    body = request.get_json(silent=True) or {}
    _code_sequence_sys_path()
    from approval import reject  # noqa: WPS433

    try:
        return jsonify(reject(
            approver=(body.get("approver") or "").strip(),
            reason=(body.get("reason") or "").strip(),
        ))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


# ---------------------------------------------------------------------------
# Visual Intelligence — VEIP (OG generation, VGA audit, prompt DNA)
# ---------------------------------------------------------------------------
def _visual_intelligence_sys_path() -> None:
    prepare_agent_package("visual_intelligence_agents")


@app.get("/api/visual-intelligence/status")
def visual_intelligence_status():
    _visual_intelligence_sys_path()
    from status import collect_status  # noqa: WPS433

    return jsonify(collect_status())


@app.post("/api/visual-intelligence/generate")
def visual_intelligence_generate():
    body = request.get_json(silent=True) or {}
    _visual_intelligence_sys_path()
    from og_generator import generate_all, generate_og  # noqa: WPS433

    template = body.get("template") or body.get("page")
    locale = body.get("locale", "pt-BR")
    persona = body.get("persona")
    if body.get("all"):
        return jsonify(generate_all(locale=locale))
    if not template:
        return jsonify({"error": "template or page required"}), 400
    try:
        return jsonify(generate_og(template, locale=locale, persona=persona))
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404


@app.post("/api/visual-intelligence/audit")
def visual_intelligence_audit():
    body = request.get_json(silent=True) or {}
    _visual_intelligence_sys_path()
    from vga_audit import audit_image, audit_manifest_entry  # noqa: WPS433

    canonical = body.get("canonical_path")
    if canonical:
        rep = audit_manifest_entry(canonical)
        if not rep:
            return jsonify({"error": "No manifest entry for path"}), 404
        return jsonify(rep.to_dict())
    path = body.get("image_path") or body.get("image_url")
    if not path:
        return jsonify({"error": "image_path or canonical_path required"}), 400
    rep = audit_image(
        path,
        country=body.get("country", "BR"),
        page_type=body.get("page_type", "sustainability"),
        persona=body.get("persona", "profissional"),
        template_key=body.get("template"),
    )
    return jsonify(rep.to_dict())


@app.post("/api/visual-intelligence/prompt-dna")
def visual_intelligence_prompt_dna():
    body = request.get_json(silent=True) or {}
    _visual_intelligence_sys_path()
    from prompt_dna import build_prompt, build_visual_dna  # noqa: WPS433

    dna = build_visual_dna(
        locale=body.get("locale", "pt-BR"),
        persona=body.get("persona", "profissional"),
        tool=body.get("tool"),
        page=body.get("page"),
        mode=body.get("mode", "study"),
        theme=body.get("theme", "light"),
    )
    asset_type = body.get("asset_type", "og")
    return jsonify({"dna": dna, "prompt": build_prompt(dna, asset_type=asset_type)})


# ---------------------------------------------------------------------------
# Clinical Article Factory — artigos problema/solução por ferramenta
# ---------------------------------------------------------------------------
def _clinical_article_sys_path() -> None:
    prepare_agent_package("clinical_article_agents")


@app.get("/api/clinical-articles/status")
def clinical_articles_status():
    _clinical_article_sys_path()
    from status import collect_status  # noqa: WPS433

    return jsonify(collect_status())


@app.post("/api/clinical-articles/generate")
def clinical_articles_generate():
    body = request.get_json(silent=True) or {}
    _clinical_article_sys_path()
    from article_builder import build_pair  # noqa: WPS433
    from merge import merge_articles  # noqa: WPS433
    from paths import load_tools_catalog  # noqa: WPS433

    pilot = ["TOOL.INFUSION", "TOOL.CAPURRO", "TOOL.APGAR", "TOOL.BRADEN", "TOOL.GCS", "TOOL.BMI", "TOOL.MCG_KG_MIN", "TOOL.INSULIN"]
    if body.get("all"):
        tools = [t["tool_code"] for t in load_tools_catalog()]
    elif body.get("tool"):
        tools = [body["tool"]]
    else:
        tools = pilot

    records = []
    errors = []
    for tc in tools:
        try:
            records.extend(build_pair(tc))
        except Exception as exc:
            errors.append({"tool": tc, "error": str(exc)})

    if body.get("apply", True):
        merge_result = merge_articles(records)
        return jsonify({"ok": not errors, "generated": len(records), "errors": errors, **merge_result})
    return jsonify({"ok": not errors, "generated": len(records), "errors": errors, "records": records})


# ---------------------------------------------------------------------------
# Nursing OS Global — orquestrador de domínios
# ---------------------------------------------------------------------------
def _nursing_os_sys_path() -> None:
    import sys

    p = str(ROOT / "scripts" / "nursing_os")
    if p not in sys.path:
        sys.path.insert(0, p)


@app.get("/api/nursing-os/status")
def nursing_os_status():
    _nursing_os_sys_path()
    from status import collect_status  # noqa: WPS433

    return jsonify(collect_status())


@app.get("/api/nursing-os/domains")
def nursing_os_domains():
    path = ROOT / "datasets" / "master-data" / "nursing-os" / "domains.json"
    if not path.exists():
        return jsonify({"domains": []})
    import json

    return jsonify(json.loads(path.read_text(encoding="utf-8")))


@app.post("/api/nursing-os/context/resolve")
def nursing_os_context_resolve():
    body = request.get_json(silent=True) or {}
    _nursing_os_sys_path()
    from status import resolve_context  # noqa: WPS433

    return jsonify(resolve_context(body))


@app.get("/api/nursing-ai-agents/status")
def nursing_ai_agents_status():
    import json

    reg = ROOT / "datasets" / "master-data" / "nursing-ai-agents" / "agents_registry.json"
    canon = ROOT / "datasets" / "master-data" / "nursing-ai-agents" / "canonical.json"
    agents = json.loads(reg.read_text(encoding="utf-8")) if reg.exists() else {}
    meta = json.loads(canon.read_text(encoding="utf-8")) if canon.exists() else {}
    return jsonify({"program": meta.get("program_code"), "agents": agents.get("agents", []), "routing_rules": agents.get("routing_rules", [])})


# ---------------------------------------------------------------------------
# Nursing Professional Intelligence Hub — legislação + carreira + contexto
# ---------------------------------------------------------------------------
def _professional_intelligence_sys_path() -> None:
    prepare_agent_package("professional_intelligence_agents")


@app.get("/api/professional-intelligence/status")
def professional_intelligence_status():
    _professional_intelligence_sys_path()
    from status import collect_status  # noqa: WPS433

    return jsonify(collect_status())


@app.get("/api/professional-intelligence/tool-context")
def professional_intelligence_tool_context():
    tool = request.args.get("tool_code") or request.args.get("tool")
    if not tool:
        return jsonify({"ok": False, "error": "tool_code required"}), 400
    _professional_intelligence_sys_path()
    from tool_context import resolve_tool_context  # noqa: WPS433

    return jsonify(resolve_tool_context(
        tool,
        persona=request.args.get("persona", "profissional"),
        country=request.args.get("country", "BR"),
        clinical_result=request.args.get("clinical_result"),
    ))


@app.post("/api/professional-intelligence/regulatory/query")
def professional_intelligence_regulatory_query():
    body = request.get_json(silent=True) or {}
    question = body.get("question") or body.get("q")
    if not question:
        return jsonify({"ok": False, "error": "question required"}), 400
    _professional_intelligence_sys_path()
    from regulatory_agent import query_regulatory  # noqa: WPS433

    return jsonify(query_regulatory(
        question,
        country=body.get("country", "BR"),
        state=body.get("state"),
        role=body.get("role", "enfermeiro"),
        formation=body.get("formation"),
    ))


@app.post("/api/professional-intelligence/exam-plan")
def professional_intelligence_exam_plan():
    body = request.get_json(silent=True) or {}
    goal = body.get("goal") or body.get("position") or "Enfermeiro"
    _professional_intelligence_sys_path()
    from exam_planner import build_exam_plan  # noqa: WPS433

    return jsonify(build_exam_plan(
        goal,
        days=int(body.get("days", 30)),
        country=body.get("country", "BR"),
        position=body.get("position"),
    ))


@app.get("/api/professional-intelligence/career-map")
def professional_intelligence_career_map():
    country = request.args.get("country", "BR")
    _professional_intelligence_sys_path()
    from paths import career_maps  # noqa: WPS433

    maps = career_maps().get("countries", {})
    entry = maps.get(country)
    if not entry:
        return jsonify({"ok": False, "error": "country_not_found", "available": list(maps.keys())}), 404
    return jsonify({"ok": True, "country": country, "career_map": entry})


# ---------------------------------------------------------------------------
# Nursing AI Factory — plataforma interna de desenvolvimento autônomo
# ---------------------------------------------------------------------------
def _ai_factory_sys_path() -> None:
    prepare_agent_package("ai_factory_agents")


@app.get("/api/ai-factory/status")
def ai_factory_status():
    _ai_factory_sys_path()
    from status import collect_status  # noqa: WPS433

    return jsonify(collect_status())


@app.get("/api/ai-factory/agents")
def ai_factory_agents():
    import json

    path = ROOT / "datasets/master-data/ai-factory/agents_registry.json"
    if not path.exists():
        return jsonify({"agents": [], "phase1_priority": []})
    data = json.loads(path.read_text(encoding="utf-8"))
    return jsonify(data)


@app.get("/api/ai-factory/workflows")
def ai_factory_workflows():
    import json

    path = ROOT / "datasets/master-data/ai-factory/workflows.json"
    if not path.exists():
        return jsonify({"workflows": {}})
    return jsonify(json.loads(path.read_text(encoding="utf-8")))


@app.get("/api/ai-factory/tools")
def ai_factory_tools():
    _ai_factory_sys_path()
    from catalog import list_tools  # noqa: WPS433

    return jsonify(list_tools(
        search=request.args.get("search", ""),
        category=request.args.get("category", ""),
        tool_type=request.args.get("tool_type", ""),
        status=request.args.get("status", ""),
        pipeline_status=request.args.get("pipeline_status", ""),
        limit=min(int(request.args.get("limit", 100)), 500),
        offset=int(request.args.get("offset", 0)),
    ))


@app.post("/api/ai-factory/run")
def ai_factory_run():
    body = request.get_json(silent=True) or {}
    brief = body.get("brief") or body.get("input") or ""
    tool_code = body.get("tool_code")
    if not brief and not tool_code:
        return jsonify({"ok": False, "error": "brief or tool_code required"}), 400
    _ai_factory_sys_path()
    from workflow_runner import run_workflow  # noqa: WPS433

    return jsonify(run_workflow(
        brief,
        tool_code=tool_code,
        tool_name=body.get("tool_name"),
        workflow_id=body.get("workflow_id", "new_clinical_tool"),
        phase1_only=body.get("phase1_only", True),
        country=body.get("country", "BR"),
        persona=body.get("persona", "profissional"),
        persist=body.get("persist", True),
    ))


@app.post("/api/ai-factory/run-batch")
def ai_factory_run_batch():
    body = request.get_json(silent=True) or {}
    _ai_factory_sys_path()
    from workflow_runner import run_batch  # noqa: WPS433

    return jsonify(run_batch(
        tool_codes=body.get("tool_codes"),
        all_tools=bool(body.get("all_tools")),
        limit=int(body.get("limit", 10)),
        search=body.get("search", ""),
        category=body.get("category", ""),
        tool_type=body.get("tool_type", ""),
        workflow_id=body.get("workflow_id", "new_clinical_tool"),
        phase1_only=body.get("phase1_only", True),
        country=body.get("country", "BR"),
        persona=body.get("persona", "profissional"),
        persist=body.get("persist", True),
    ))


@app.post("/api/ai-factory/evaluate")
def ai_factory_evaluate():
    body = request.get_json(silent=True) or {}
    agent_id = body.get("agent_id")
    scores = body.get("scores") or {}
    if not agent_id or not scores:
        return jsonify({"ok": False, "error": "agent_id and scores required"}), 400
    _ai_factory_sys_path()
    from paths import evaluations_schema  # noqa: WPS433

    types = evaluations_schema().get("evaluation_types", {})
    spec = types.get(agent_id, types.get("code_reviewer", {}))
    threshold = spec.get("pass_threshold", 85)
    dims = spec.get("dimensions", list(scores.keys()))
    dim_scores = {d: scores.get(d, 0) for d in dims if d in scores}
    avg = sum(dim_scores.values()) / len(dim_scores) if dim_scores else 0
    passed = avg >= threshold
    return jsonify({
        "ok": True,
        "agent_id": agent_id,
        "scores": dim_scores,
        "average": round(avg, 1),
        "pass_threshold": threshold,
        "passed": passed,
    })


@app.post("/api/nursing-ai-agents/route")
def nursing_ai_agents_route():
    body = request.get_json(silent=True) or {}
    intent = body.get("intent", "clinical_question")
    persona = body.get("persona", "profissional")
    import json

    reg = json.loads((ROOT / "datasets/master-data/nursing-ai-agents/agents_registry.json").read_text(encoding="utf-8"))
    agent_id = "clinical"
    for rule in reg.get("routing_rules", []):
        if rule.get("intent") == intent:
            p = rule.get("persona")
            if not p or persona in p or rule.get("persona_any"):
                agent_id = rule["agent"]
                break
    agent = next((a for a in reg.get("agents", []) if a["agent_id"] == agent_id), None)
    return jsonify({"intent": intent, "persona": persona, "agent_id": agent_id, "agent": agent})


# ---------------------------------------------------------------------------
# Nursing Knowledge API — Gateway /api/v1
# ---------------------------------------------------------------------------
def _nursing_knowledge_api_sys_path() -> None:
    import sys

    p = str(ROOT / "scripts" / "nursing_knowledge_api")
    if p not in sys.path:
        sys.path.insert(0, p)


def _register_nursing_knowledge_api() -> None:
    _nursing_knowledge_api_sys_path()
    from register_routes import register_v1_routes  # noqa: WPS433

    register_v1_routes(app)


@app.get("/api/nursing-knowledge-api/status")
def nursing_knowledge_api_admin_status():
    _nursing_knowledge_api_sys_path()
    from status import collect_status  # noqa: WPS433

    return jsonify(collect_status())


@app.get("/api/nursing-knowledge-api/services")
def nursing_knowledge_api_services():
    import json

    path = ROOT / "datasets/master-data/nursing-knowledge-api/services_registry.json"
    return jsonify(json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"services": {}})


_register_nursing_knowledge_api()


# ---------------------------------------------------------------------------
# Nursing Studio — grafo + agentes + gerador redes sociais
# ---------------------------------------------------------------------------
def _nursing_studio_sys_path() -> None:
    import sys

    p = str(ROOT / "scripts" / "nursing_studio_agents")
    if p not in sys.path:
        sys.path.insert(0, p)


@app.get("/api/studio/status")
def studio_status():
    _nursing_studio_sys_path()
    from status import collect_status  # noqa: WPS433

    return jsonify(collect_status())


@app.get("/api/studio/formats")
def studio_formats():
    _nursing_studio_sys_path()
    from paths import formats  # noqa: WPS433

    return jsonify({"formats": formats()})


@app.get("/api/studio/blocks")
def studio_blocks():
    _nursing_studio_sys_path()
    from paths import editing_blocks, templates  # noqa: WPS433

    return jsonify({"blocks": editing_blocks(), "templates": templates()})


@app.get("/api/graph/studio/context")
def graph_studio_context():
    _nursing_studio_sys_path()
    from graph_context import resolve_graph_context  # noqa: WPS433

    return jsonify(resolve_graph_context(
        entity_code=request.args.get("entity_code"),
        tool_code=request.args.get("tool_code"),
        topic=request.args.get("topic"),
        country=request.args.get("country", "BR"),
        persona=request.args.get("persona", "profissional"),
    ))


@app.post("/api/studio/generate")
def studio_generate():
    body = request.get_json(silent=True) or {}
    _nursing_studio_sys_path()
    from workflow_runner import run_studio_pipeline  # noqa: WPS433

    return jsonify(run_studio_pipeline(
        tool_code=body.get("tool_code"),
        topic=body.get("topic"),
        entity_code=body.get("entity_code"),
        format_id=body.get("format", "instagram_post"),
        persona=body.get("persona", "profissional"),
        country=body.get("country", "BR"),
        template_id=body.get("template_id"),
        edits=body.get("edits"),
    ))


@app.post("/api/studio/evaluate")
def studio_evaluate():
    body = request.get_json(silent=True) or {}
    _nursing_studio_sys_path()
    from studio_agents import evaluate_publication  # noqa: WPS433

    return jsonify(evaluate_publication(
        template_spec=body.get("template_spec", body),
        persona=body.get("persona", "profissional"),
        country=body.get("country", "BR"),
        format_id=body.get("format", "instagram_post"),
    ))


@app.post("/api/studio/review")
def studio_review():
    body = request.get_json(silent=True) or {}
    _nursing_studio_sys_path()
    from studio_agents import review_image  # noqa: WPS433

    return jsonify(review_image(
        evaluation=body.get("evaluation", body),
        format_id=body.get("format", "instagram_post"),
    ))


@app.get("/api/studio/asset/<path:filename>")
def studio_asset(filename):
    p = ROOT / "website" / "assets" / "images" / "studio" / filename
    if not p.exists() or ".." in filename:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return send_file(p, mimetype="image/svg+xml")


# ---------------------------------------------------------------------------
# Graph Intelligence — validação Claude + screening Groq + conteúdo clínico
# ---------------------------------------------------------------------------
def _graph_intelligence_sys_path() -> None:
    prepare_agent_package("graph_intelligence_agents")


@app.get("/api/graph-intelligence/status")
def graph_intelligence_status():
    _graph_intelligence_sys_path()
    from status import collect_status  # noqa: WPS433

    return jsonify(collect_status())


@app.get("/api/graph-intelligence/inventory")
def graph_intelligence_inventory():
    _graph_intelligence_sys_path()
    from graph_snapshot import build_inventory_stats  # noqa: WPS433

    return jsonify(build_inventory_stats())


@app.get("/api/graph-intelligence/criteria")
def graph_intelligence_criteria():
    _graph_intelligence_sys_path()
    from paths import criteria  # noqa: WPS433

    return jsonify(criteria())


@app.get("/api/graph-intelligence/review-plan")
def graph_intelligence_review_plan():
    _graph_intelligence_sys_path()
    from paths import review_plan  # noqa: WPS433

    return jsonify(review_plan())


@app.post("/api/graph-intelligence/validate")
def graph_intelligence_validate():
    body = request.get_json(silent=True) or {}
    _graph_intelligence_sys_path()
    from validator_agent import validate_graph  # noqa: WPS433

    return jsonify(validate_graph(
        tool_codes=body.get("tool_codes"),
        use_llm=body.get("use_llm", True) and not body.get("no_llm"),
        provider=body.get("provider"),
        payload=body,
    ))


@app.post("/api/graph-intelligence/fast-screen")
def graph_intelligence_fast_screen():
    body = request.get_json(silent=True) or {}
    _graph_intelligence_sys_path()
    from validator_agent import fast_screen  # noqa: WPS433

    return jsonify(fast_screen(payload=body))


@app.post("/api/graph-intelligence/generate-content")
def graph_intelligence_generate_content():
    body = request.get_json(silent=True) or {}
    entity = body.get("entity_code") or body.get("tool_code")
    if not entity:
        return jsonify({"ok": False, "error": "entity_code or tool_code required"}), 400
    _graph_intelligence_sys_path()
    from content_agent import generate_clinical_content  # noqa: WPS433

    return jsonify(generate_clinical_content(
        entity,
        entity_type=body.get("entity_type", "ClinicalTool"),
        country=body.get("country", "BR"),
        persona=body.get("persona", "profissional"),
        use_llm=body.get("use_llm", True) and not body.get("no_llm"),
        payload=body,
    ))


@app.post("/api/graph-intelligence/cross-tool")
def graph_intelligence_cross_tool():
    body = request.get_json(silent=True) or {}
    tool = body.get("tool_code")
    if not tool:
        return jsonify({"ok": False, "error": "tool_code required"}), 400
    _graph_intelligence_sys_path()
    from content_agent import generate_cross_tool_intelligence  # noqa: WPS433

    return jsonify(generate_cross_tool_intelligence(tool, payload=body))


# ---------------------------------------------------------------------------
# Database Sync — DeepSeek validation + Supabase/Firebase upload
# ---------------------------------------------------------------------------
def _database_sync_sys_path() -> None:
    prepare_agent_package("database_sync_agents")


@app.get("/api/database-sync/status")
def database_sync_status():
    _database_sync_sys_path()
    from status import collect_status  # noqa: WPS433

    return jsonify(collect_status())


@app.post("/api/database-sync/validate")
def database_sync_validate():
    body = request.get_json(silent=True) or {}
    _database_sync_sys_path()
    from api_helpers import llm_enabled  # noqa: WPS433
    from orchestrator import run_pipeline  # noqa: WPS433

    return jsonify(run_pipeline(
        entity_keys=body.get("entities"),
        tier=body.get("tier"),
        target=body.get("target", "supabase"),
        use_llm=llm_enabled(body),
        validate_only=True,
        payload=body,
    ))


@app.post("/api/database-sync/schema")
def database_sync_schema():
    _database_sync_sys_path()
    from schema_builder import generate_supabase_ddl, write_schema_file  # noqa: WPS433

    path = write_schema_file()
    return jsonify({"ok": True, "schema_path": path, "ddl": generate_supabase_ddl()})


@app.post("/api/database-sync/upload")
def database_sync_upload():
    body = request.get_json(silent=True) or {}
    _database_sync_sys_path()
    from config import resolve_entities  # noqa: WPS433
    from uploader_firebase import upload_entities as upload_firebase  # noqa: WPS433
    from uploader_supabase import upload_entities as upload_supabase  # noqa: WPS433

    entities = resolve_entities(body.get("entities"))
    if body.get("tier"):
        from config import ENTITY_TIERS  # noqa: WPS433
        keys = [e["entity_key"] for e in ENTITY_TIERS.get(body["tier"], [])]
        entities = resolve_entities(keys)

    target = body.get("target", "supabase")
    dry_run = body.get("dry_run", True) is not False
    if body.get("live") is True:
        dry_run = False

    result = {"ok": True, "dry_run": dry_run, "uploads": {}}
    if target in ("supabase", "both"):
        result["uploads"]["supabase"] = upload_supabase(entities, dry_run=dry_run)
    if target in ("firebase", "both"):
        result["uploads"]["firebase"] = upload_firebase(
            entities,
            dry_run=dry_run,
            use_function=body.get("use_firebase_function", True),
        )
    result["ok"] = all(u.get("ok") for u in result["uploads"].values())
    return jsonify(result)


@app.post("/api/database-sync/sync")
def database_sync_sync():
    """Pipeline completo: validar (DeepSeek) → upload Supabase/Firebase."""
    body = request.get_json(silent=True) or {}
    _database_sync_sys_path()
    from api_helpers import llm_enabled  # noqa: WPS433
    from orchestrator import run_pipeline  # noqa: WPS433

    dry_run = body.get("dry_run", True) is not False
    if body.get("live") is True:
        dry_run = False

    return jsonify(run_pipeline(
        entity_keys=body.get("entities"),
        tier=body.get("tier"),
        target=body.get("target", "supabase"),
        use_llm=llm_enabled(body),
        dry_run=dry_run,
        validate_only=False,
        payload=body,
    ))


@app.post("/api/database-sync/backup")
def database_sync_backup():
    body = request.get_json(silent=True) or {}
    _database_sync_sys_path()
    from backup import create_security_backup, list_backups, restore_backup  # noqa: WPS433

    if body.get("restore"):
        return jsonify(restore_backup(
            body["restore"],
            dry_run=body.get("dry_run", True) is not False and body.get("live") is not True,
        ))

    if body.get("list"):
        return jsonify({"ok": True, "backups": list_backups(int(body.get("limit", 20)))})

    return jsonify(create_security_backup(
        full=bool(body.get("full")),
        tiers=body.get("tiers"),
        label=body.get("label", "api_backup"),
    ))


@app.post("/api/database-sync/finalize")
def database_sync_finalize():
    """DeepSeek: ler → interpretar → planejar → executar (backup obrigatório)."""
    body = request.get_json(silent=True) or {}
    _database_sync_sys_path()
    from api_helpers import llm_enabled  # noqa: WPS433
    from backup import create_security_backup  # noqa: WPS433
    from executor_agent import execute_plan  # noqa: WPS433
    from planner_agent import plan_finalize  # noqa: WPS433

    tiers = body.get("tiers") or ["tier1_core", "tier2_clinical", "tier3_content"]
    target = body.get("target", "supabase")
    plan_only = body.get("plan_only", False) is True
    use_llm = llm_enabled(body)
    payload = {**body, "live": body.get("live") is True}

    if plan_only:
        from finalize_graph import run_finalize_graph  # noqa: WPS433
        return jsonify(run_finalize_graph(
            tiers=tiers,
            target=target,
            use_llm=use_llm,
            live=False,
            force=bool(body.get("force")),
            min_score=float(body.get("min_score", 95)),
            execute_enabled=False,
            validate_only=True,
        ))

    use_langgraph = body.get("legacy") is not True
    if use_langgraph:
        from finalize_graph import run_finalize_graph  # noqa: WPS433
        return jsonify(run_finalize_graph(
            tiers=tiers,
            target=target,
            api_key=(body.get("api_key") or "").strip() or None,
            use_llm=use_llm,
            live=payload.get("live") is True,
            force=bool(body.get("force")),
            min_score=float(body.get("min_score", 95)),
            execute_enabled=not body.get("validate_only"),
            validate_only=bool(body.get("validate_only")),
        ))

    backup = create_security_backup(
        full=bool(body.get("full_backup")),
        tiers=tiers,
        label="api_pre_finalize",
    )
    plan = plan_finalize(tiers=tiers, target=target, use_llm=use_llm, payload=payload)

    blockers = plan.get("blockers_before_execute") or []
    if blockers and not body.get("force"):
        return jsonify({
            "ok": False,
            "error": "blockers_detected",
            "backup_id": backup.get("backup_id"),
            "blockers": blockers,
            "plan": {k: v for k, v in plan.items() if k != "context"},
        }), 409

    report = execute_plan(plan, payload=payload, stop_on_error=not body.get("force"))
    report["backup_id"] = backup.get("backup_id")
    plan_summary = {k: v for k, v in plan.items() if k != "context"}
    return jsonify({"ok": report.get("ok"), "backup": backup, "plan": plan_summary, "execution": report})


# ---------------------------------------------------------------------------
# Task Center — executar agentes reais (medicamentos, conteúdo, AI Factory…)
# ---------------------------------------------------------------------------
def _task_center_sys_path() -> None:
    import sys

    for p in (
        str(ROOT / "scripts" / "task_center"),
        str(ROOT / "scripts" / "apgar_agents"),
        str(ROOT / "scripts"),
    ):
        if p not in sys.path:
            sys.path.insert(0, p)


@app.get("/api/tasks/status")
def tasks_status():
    _task_center_sys_path()
    from status import collect_status  # noqa: WPS433

    return jsonify(collect_status())


@app.get("/api/tasks/list")
def tasks_list():
    _task_center_sys_path()
    from registry import list_tasks  # noqa: WPS433

    status = request.args.get("status", "all")
    limit = min(int(request.args.get("limit", 200)), 500)
    return jsonify(list_tasks(status=status, limit=limit))


@app.post("/api/tasks/sync")
def tasks_sync():
    _task_center_sys_path()
    from registry import sync_registry  # noqa: WPS433

    return jsonify(sync_registry())


@app.post("/api/tasks/run")
def tasks_run():
    body = request.get_json(silent=True) or {}
    _task_center_sys_path()
    from api_helpers import llm_enabled  # noqa: WPS433
    from runner import run_task  # noqa: WPS433

    task_id = body.get("task_id")
    if not task_id:
        return jsonify({"ok": False, "error": "task_id_required"}), 400
    return jsonify(run_task(
        task_id,
        use_llm=llm_enabled(body),
        limit=int(body.get("limit", 10)),
    ))


@app.post("/api/tasks/run-batch")
def tasks_run_batch():
    body = request.get_json(silent=True) or {}
    _task_center_sys_path()
    from api_helpers import llm_enabled  # noqa: WPS433
    from registry import list_tasks, sync_registry  # noqa: WPS433
    from runner import run_batch_tasks  # noqa: WPS433

    task_ids = body.get("task_ids")
    if not task_ids:
        sync_registry()
        pending = list_tasks(status="pending", limit=int(body.get("limit", 20)))
        task_ids = [t["id"] for t in pending.get("tasks", [])]
    if not task_ids:
        return jsonify({"ok": True, "total": 0, "succeeded": 0, "results": [], "note": "no_pending_tasks"})
    return jsonify(run_batch_tasks(task_ids, use_llm=llm_enabled(body)))


@app.post("/api/tasks/run-pending-agents")
def tasks_run_pending_agents():
    """Executa run_pending_agents.py — todos os agentes com pendência no inventário."""
    body = request.get_json(silent=True) or {}
    _database_sync_sys_path()
    from agent_executor import run_pending_agents  # noqa: WPS433
    from api_helpers import llm_enabled  # noqa: WPS433

    return jsonify(run_pending_agents(
        use_llm=llm_enabled(body),
        agents=body.get("agents"),
    ))


if __name__ == "__main__":
    print("Knowledge Platform API — datasets:", DATASETS)
    print("Entities:", ", ".join(ENTITY_REGISTRY))
    app.run(host="127.0.0.1", port=8787, debug=False)
