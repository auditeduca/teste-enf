"""Configuração central de provedores LLM — variáveis de ambiente."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderConfig:
    provider_id: str
    env_key: str
    default_model: str
    base_url: str
    api_style: str  # openai | anthropic


PROVIDERS: dict[str, ProviderConfig] = {
    "claude": ProviderConfig(
        provider_id="claude",
        env_key="ANTHROPIC_API_KEY",
        default_model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
        base_url="https://api.anthropic.com/v1/messages",
        api_style="anthropic",
    ),
    "deepseek": ProviderConfig(
        provider_id="deepseek",
        env_key="DEEPSEEK_API_KEY",
        default_model=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        base_url="https://api.deepseek.com/v1/chat/completions",
        api_style="openai",
    ),
    "groq": ProviderConfig(
        provider_id="groq",
        env_key="GROQ_API_KEY",
        default_model=os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
        base_url="https://api.groq.com/openai/v1/chat/completions",
        api_style="openai",
    ),
    "cursor": ProviderConfig(
        provider_id="cursor",
        env_key="CURSOR_API_KEY",
        default_model=os.environ.get("CURSOR_MODEL", "gpt-4o"),
        base_url="https://api.cursor.com/v1/chat/completions",
        api_style="openai",
    ),
}

# Tarefa → provedor preferido (estratégia combinada)
TASK_DEFAULT_PROVIDER: dict[str, str] = {
    "graph_validation": "claude",
    "clinical_decision_content": "claude",
    "graph_content_dense": "claude",
    "reasoning_chain": "claude",
    "code_review": "deepseek",
    "translation": "deepseek",
    "bulk_content": "deepseek",
    "database_validation": "deepseek",
    "seo": "deepseek",
    "fast_check": "groq",
    "classification": "groq",
    "summarize": "groq",
    "default": "deepseek",
}


def resolve_api_key(provider: str, payload: dict | None = None) -> str | None:
    """Body api_key > env específica > env genérica LLM_API_KEY."""
    payload = payload or {}
    explicit = (payload.get("api_key") or payload.get(f"{provider}_api_key") or "").strip()
    if explicit:
        return explicit
    cfg = PROVIDERS.get(provider)
    if cfg:
        key = (os.environ.get(cfg.env_key) or "").strip()
        if key:
            return key
    return (os.environ.get("LLM_API_KEY") or "").strip() or None


def resolve_model(provider: str, payload: dict | None = None) -> str:
    payload = payload or {}
    model = (payload.get("model") or "").strip()
    if model:
        return model
    cfg = PROVIDERS.get(provider)
    if not cfg:
        return "deepseek-v4-flash"
    env_model = os.environ.get(f"{provider.upper()}_MODEL") or os.environ.get(
        f"{cfg.env_key.replace('_API_KEY', '_MODEL')}"
    )
    return (env_model or cfg.default_model).strip()


def provider_for_task(task: str, payload: dict | None = None) -> str:
    payload = payload or {}
    override = (payload.get("provider") or "").strip().lower()
    if override and override in PROVIDERS:
        return override
    return TASK_DEFAULT_PROVIDER.get(task, TASK_DEFAULT_PROVIDER["default"])


def providers_status() -> dict:
    out = {}
    for pid, cfg in PROVIDERS.items():
        out[pid] = {
            "configured": bool((os.environ.get(cfg.env_key) or "").strip()),
            "env_key": cfg.env_key,
            "default_model": cfg.default_model,
            "api_style": cfg.api_style,
        }
    return out
