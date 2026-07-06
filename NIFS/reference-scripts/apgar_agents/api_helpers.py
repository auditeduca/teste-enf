"""Resolve credenciais DeepSeek — mesmo contrato do Code Review / Graph AI."""
from __future__ import annotations

import os

DEFAULT_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash")


def resolve_deepseek(payload: dict | None = None) -> tuple[str | None, str]:
    """api_key do body (app localStorage) > DEEPSEEK_API_KEY env."""
    payload = payload or {}
    key = (payload.get("api_key") or os.environ.get("DEEPSEEK_API_KEY") or "").strip()
    model = (payload.get("model") or os.environ.get("DEEPSEEK_MODEL") or DEFAULT_MODEL).strip()
    return (key or None), model


def llm_enabled(payload: dict | None = None) -> bool:
    payload = payload or {}
    if payload.get("no_llm") or payload.get("llm") is False:
        return False
    key, _ = resolve_deepseek(payload)
    return bool(key) and payload.get("use_llm", True) is not False
