"""Tradução de home e perfis via DeepSeek — Grau A, 30 idiomas."""
from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
EXP = ROOT / "datasets" / "master-data" / "global-expansion"
BY_LOCALE = ROOT / "datasets" / "by-locale"
CANONICAL = ROOT / "datasets" / "content" / "site" / "home_page.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _scaffold_locales() -> list[str]:
    from site_locales import SITE_LOCALES

    out = []
    for loc in SITE_LOCALES:
        path = BY_LOCALE / loc / "home_page.json"
        if not path.is_file():
            out.append(loc)
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        if doc.get("i18n_status") not in ("translated", "reviewed"):
            out.append(loc)
    return out


def _extract_translatable(home: dict) -> dict:
    hero = home.get("hero", {})
    search = home.get("search", {})
    solutions = home.get("solutions", {})
    return {
        "hero_title": hero.get("title"),
        "hero_title_accent": hero.get("title_accent"),
        "hero_subtitle": hero.get("subtitle"),
        "hero_image_alt": hero.get("image_alt"),
        "cta_primary": hero.get("cta_primary", {}).get("label"),
        "cta_secondary": hero.get("cta_secondary", {}).get("label"),
        "search_label": search.get("label"),
        "search_placeholder": search.get("placeholder"),
        "search_button": search.get("button"),
        "solutions_title": solutions.get("title"),
        "solutions_subtitle": solutions.get("subtitle"),
        "solution_items": [
            {"title": i.get("title"), "description": i.get("description")}
            for i in (solutions.get("items") or [])[:5]
        ],
    }


def _apply_translation(home: dict, tr: dict, locale: str) -> dict:
    out = deepcopy(home)
    out["locale"] = locale
    out["i18n_status"] = "translated"
    out["translated_at"] = _now()
    out["translation_engine"] = "deepseek"
    if tr.get("hero_title"):
        out.setdefault("hero", {})["title"] = tr["hero_title"]
    if tr.get("hero_title_accent"):
        out.setdefault("hero", {})["title_accent"] = tr["hero_title_accent"]
    if tr.get("hero_subtitle"):
        out.setdefault("hero", {})["subtitle"] = tr["hero_subtitle"]
    if tr.get("hero_image_alt"):
        out.setdefault("hero", {})["image_alt"] = tr["hero_image_alt"]
    if tr.get("cta_primary"):
        out.setdefault("hero", {}).setdefault("cta_primary", {})["label"] = tr["cta_primary"]
    if tr.get("cta_secondary"):
        out.setdefault("hero", {}).setdefault("cta_secondary", {})["label"] = tr["cta_secondary"]
    for key in ("search_label", "search_placeholder", "search_button"):
        field = key.replace("search_", "")
        if tr.get(key):
            out.setdefault("search", {})[field if field != "button" else "button"] = tr[key]
    if tr.get("solutions_title"):
        out.setdefault("solutions", {})["title"] = tr["solutions_title"]
    if tr.get("solutions_subtitle"):
        out.setdefault("solutions", {})["subtitle"] = tr["solutions_subtitle"]
    items = tr.get("solution_items") or []
    sol_items = out.get("solutions", {}).get("items") or []
    for idx, item in enumerate(items):
        if idx < len(sol_items):
            if item.get("title"):
                sol_items[idx]["title"] = item["title"]
            if item.get("description"):
                sol_items[idx]["description"] = item["description"]
    return out


def translate_home_locale(locale: str, *, api_key: str, model: str | None = None) -> dict:
    import sys

    sys.path.insert(0, str(ROOT / "scripts" / "apgar_agents"))
    from apgar_agents.llm import chat_json, resolve_model  # noqa: WPS433

    from site_locales import SITE_LOCALE_META

    path = BY_LOCALE / locale / "home_page.json"
    if locale == "pt-BR":
        return {"locale": locale, "skipped": True, "ok": True}
    source = json.loads(CANONICAL.read_text(encoding="utf-8"))
    if path.is_file():
        source = json.loads(path.read_text(encoding="utf-8"))
    payload = _extract_translatable(source)
    meta = SITE_LOCALE_META.get(locale, {})
    lang_name = meta.get("language_code", locale)

    messages = [
        {
            "role": "system",
            "content": (
                "Você traduz conteúdo de site de enfermagem para o locale indicado. "
                "Responda APENAS JSON válido com as mesmas chaves recebidas. "
                "Adapte tom e preferências culturais do público local. "
                "Inclua evidence_grade: A e sources: [] (array de {citation, doi_or_url, organization, year}) "
                "com 1-2 referências WHO/OECD ou diretriz nacional quando relevante."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {"target_locale": locale, "language_code": lang_name, "fields": payload},
                ensure_ascii=False,
            ),
        },
    ]
    tr = chat_json(messages, api_key=api_key, model=resolve_model(model), max_tokens=8192)
    if isinstance(tr, dict) and "fields" in tr:
        tr = tr["fields"]
    translated = _apply_translation(source, tr if isinstance(tr, dict) else {}, locale)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(translated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"locale": locale, "ok": True, "path": str(path.relative_to(ROOT))}


def run_i18n_batch(*, api_key: str, model: str | None = None, limit: int = 10) -> dict:
    locales = _scaffold_locales()[:limit]
    results = []
    for loc in locales:
        try:
            results.append(translate_home_locale(loc, api_key=api_key, model=model))
        except Exception as exc:
            results.append({"locale": loc, "ok": False, "error": str(exc)})

    # Atualiza coverage
    from build_i18n_world import build_locale_profile_overrides, ensure_locale_homes, sync_user_profile_config

    home_status = ensure_locale_homes()
    for r in results:
        if r.get("ok") and not r.get("skipped"):
            home_status[r["locale"]] = "translated"
    locale_profiles = build_locale_profile_overrides(home_status)
    sync_user_profile_config(locale_profiles)

    cov_path = EXP / "i18n_coverage_report.json"
    cov = json.loads(cov_path.read_text(encoding="utf-8")) if cov_path.is_file() else {}
    translated = sum(1 for s in home_status.values() if s in ("translated", "reviewed"))
    cov.update({
        "generated_at": _now(),
        "home_translated": translated,
        "home_scaffold": len(home_status) - translated,
        "last_llm_batch": len(results),
    })
    cov_path.write_text(json.dumps(cov, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "module": "i18n_world",
        "processed": len(results),
        "ok_count": sum(1 for r in results if r.get("ok")),
        "results": results,
        "home_translated": translated,
        "ok": all(r.get("ok") for r in results) if results else True,
    }
