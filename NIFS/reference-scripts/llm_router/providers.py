"""Clientes HTTP unificados — OpenAI-compatible + Anthropic Messages API."""
from __future__ import annotations

import json
import urllib.error
import urllib.request

from llm_router.config import PROVIDERS, resolve_api_key, resolve_model


def _openai_chat(
    messages: list[dict],
    *,
    provider: str,
    api_key: str,
    model: str,
    temperature: float,
    max_tokens: int,
) -> str:
    cfg = PROVIDERS[provider]
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }).encode("utf-8")
    req = urllib.request.Request(
        cfg.base_url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    from review.ssl_utils import ssl_setup_hint, urlopen_request

    try:
        with urlopen_request(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:2000]
        raise RuntimeError(f"{provider} HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        hint = ssl_setup_hint(exc)
        raise RuntimeError(f"{provider} unreachable: {exc.reason}.{hint}") from exc

    choice = (data.get("choices") or [{}])[0]
    return (choice.get("message") or {}).get("content", "")


def _anthropic_chat(
    messages: list[dict],
    *,
    api_key: str,
    model: str,
    temperature: float,
    max_tokens: int,
) -> str:
    system_parts: list[str] = []
    chat_messages: list[dict] = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            system_parts.append(content)
        else:
            chat_messages.append({"role": role, "content": content})

    body: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": chat_messages or [{"role": "user", "content": "Continue."}],
    }
    if system_parts:
        body["system"] = "\n\n".join(system_parts)

    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        PROVIDERS["claude"].base_url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    from review.ssl_utils import ssl_setup_hint, urlopen_request

    try:
        with urlopen_request(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:2000]
        raise RuntimeError(f"claude HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        hint = ssl_setup_hint(exc)
        raise RuntimeError(f"claude unreachable: {exc.reason}.{hint}") from exc

    blocks = data.get("content") or []
    parts = [b.get("text", "") for b in blocks if b.get("type") == "text"]
    return "".join(parts)


def chat_complete(
    messages: list[dict],
    *,
    provider: str = "deepseek",
    api_key: str | None = None,
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 4096,
    payload: dict | None = None,
) -> str:
    """Completa chat via provedor indicado."""
    payload = payload or {}
    provider = (provider or "deepseek").lower()
    if provider not in PROVIDERS:
        raise ValueError(f"Provedor desconhecido: {provider}")

    key = api_key or resolve_api_key(provider, payload)
    if not key:
        cfg = PROVIDERS[provider]
        raise ValueError(f"{cfg.env_key} ou api_key obrigatória para {provider}")

    resolved_model = model or resolve_model(provider, payload)
    cfg = PROVIDERS[provider]

    if cfg.api_style == "anthropic":
        return _anthropic_chat(
            messages,
            api_key=key,
            model=resolved_model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    return _openai_chat(
        messages,
        provider=provider,
        api_key=key,
        model=resolved_model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
