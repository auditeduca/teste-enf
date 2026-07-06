"""Single source of truth for datasets/content/ file locations.

All build loaders, validators, and bootstrap scripts should import paths from
here instead of hardcoding ``content/*.json`` at the datasets root.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ROOT / "datasets"
CONTENT_ROOT = DATASETS / "content"

# Paths relative to datasets/
CONTENT_PATHS: dict[str, str] = {
    # Site — páginas públicas e experiência do usuário
    "home_page": "content/site/home_page.json",
    "institutional_pages": "content/site/institutional_pages.json",
    "privacy_center": "content/site/privacy_center.json",
    "sustainability_center": "content/site/sustainability_center.json",
    "institutional_hubs": "content/site/institutional_hubs.json",
    "user_profile_experience": "content/site/user_profile_experience.json",
    # Chrome — navegação, shell e marketing
    "chrome_navigation": "content/chrome/chrome_navigation.json",
    "chrome_shell": "content/chrome/chrome_shell.json",
    "marketing_config": "content/chrome/marketing_config.json",
    # Hubs — templates e orquestrador
    "hub_templates": "content/hubs/hub_templates.json",
    "hub_orchestrator": "content/hubs/hub_orchestrator.json",
    # Tools — UI de calculadoras e escalas
    "tool_templates": "content/tools/tool_templates.json",
    "tool_ui_bindings": "content/tools/tool_ui_bindings.json",
    "calculator_scale_options": "content/tools/calculator_scale_options.json",
    # Editorial — artigos, templates e dicas
    "articles": "content/editorial/articles.json",
    "template_pages": "content/editorial/template_pages.json",
    "labor_calculators": "content/editorial/labor_calculators.json",
    "daily_tips": "content/editorial/daily_tips.json",
    # NKOS — entidades de conteúdo (fase 7)
    "contents": "content/nkos/contents.json",
    "content_fragments": "content/nkos/content_fragments.json",
    "content_versions": "content/nkos/content_versions.json",
    "community_translations": "content/nkos/community_translations.json",
    "content_requests": "content/nkos/content_requests.json",
    "content_review_cycles": "content/nkos/content_review_cycles.json",
    # i18n — traduções globais (sharded)
    "translations": "content/i18n/translations.json",
}

# Subpastas lógicas (para documentação e validação)
CONTENT_LAYERS: dict[str, list[str]] = {
    "site": [
        "home_page",
        "institutional_pages",
        "privacy_center",
        "sustainability_center",
        "institutional_hubs",
        "user_profile_experience",
    ],
    "chrome": ["chrome_navigation", "chrome_shell", "marketing_config"],
    "hubs": ["hub_templates", "hub_orchestrator"],
    "tools": ["tool_templates", "tool_ui_bindings", "calculator_scale_options"],
    "editorial": ["articles", "template_pages", "labor_calculators", "daily_tips"],
    "nkos": [
        "contents",
        "content_fragments",
        "content_versions",
        "community_translations",
        "content_requests",
        "content_review_cycles",
    ],
    "i18n": ["translations"],
}


def content_rel(key: str) -> str:
    """Dataset-relative POSIX path (e.g. ``content/site/home_page.json``)."""
    try:
        return CONTENT_PATHS[key]
    except KeyError as exc:
        raise KeyError(f"Unknown content key: {key!r}") from exc


def content_path(key: str) -> Path:
    """Absolute path under ``datasets/``."""
    return DATASETS / content_rel(key)


def legacy_content_path(filename: str) -> Path:
    """Old flat ``content/{filename}`` — for one-off migration checks only."""
    name = Path(filename).name
    if name != filename or ".." in Path(filename).parts:
        raise ValueError(f"Caminho inválido para legacy_content_path: {filename!r}")
    resolved = (CONTENT_ROOT / name).resolve()
    if not str(resolved).startswith(str(CONTENT_ROOT.resolve())):
        raise ValueError(f"Caminho fora de CONTENT_ROOT: {filename!r}")
    return resolved
