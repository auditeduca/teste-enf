"""Remove credenciais e segredos de outputs de agentes antes de persistir ou exibir."""
from __future__ import annotations

import copy
import re
from typing import Any

SECRET_KEYS = frozenset({
    "api_key",
    "apikey",
    "apiKey",
    "deepseekApiKey",
    "deepseek_api_key",
    "DEEPSEEK_API_KEY",
    "authorization",
    "Authorization",
    "bearer",
    "Bearer",
    "token",
    "access_token",
    "secret",
})

SK_PATTERN = re.compile(r"\bsk-[a-zA-Z0-9_-]{16,}\b")
BEARER_PATTERN = re.compile(r"\bBearer\s+[a-zA-Z0-9._-]+\b", re.I)


def _redact_string(value: str) -> str:
    out = SK_PATTERN.sub("[REDACTED_API_KEY]", value)
    out = BEARER_PATTERN.sub("Bearer [REDACTED]", out)
    return out


def sanitize_value(value: Any, *, depth: int = 0) -> Any:
    if depth > 32:
        return value
    if isinstance(value, dict):
        cleaned: dict[str, Any] = {}
        for key, item in value.items():
            if key in SECRET_KEYS or key.lower() in {k.lower() for k in SECRET_KEYS}:
                cleaned[key] = "[REDACTED]"
                continue
            cleaned[key] = sanitize_value(item, depth=depth + 1)
        return cleaned
    if isinstance(value, list):
        return [sanitize_value(item, depth=depth + 1) for item in value]
    if isinstance(value, str):
        return _redact_string(value)
    return value


def sanitize_agent_result(result: dict[str, Any]) -> dict[str, Any]:
    """Copia segura — nunca muta o estado interno do grafo."""
    cleaned = sanitize_value(copy.deepcopy(result))
    for key in ("api_key", "model"):
        cleaned.pop(key, None)
    return cleaned


def strip_api_from_text(text: str) -> str:
    return _redact_string(text or "")
