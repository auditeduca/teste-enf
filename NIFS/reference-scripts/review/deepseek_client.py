"""DeepSeek chat client (OpenAI-compatible)."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from review.config import DEEPSEEK_BASE_URL, DEFAULT_DEEPSEEK_MODEL
from review.ssl_utils import ssl_setup_hint, urlopen_request

CHAT_URL = f"{DEEPSEEK_BASE_URL}/chat/completions"


def chat_complete(
    messages: list[dict],
    *,
    api_key: str | None = None,
    model: str = DEFAULT_DEEPSEEK_MODEL,
    temperature: float = 0.2,
    max_tokens: int = 4096,
) -> str:
    key = (api_key or os.environ.get("DEEPSEEK_API_KEY") or "").strip()
    if not key:
        raise ValueError("DEEPSEEK_API_KEY ou api_key obrigatória")

    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }).encode("utf-8")

    req = urllib.request.Request(
        CHAT_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
        method="POST",
    )
    try:
        with urlopen_request(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:2000]
        raise RuntimeError(f"DeepSeek HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        hint = ssl_setup_hint(exc)
        raise RuntimeError(f"DeepSeek unreachable: {exc.reason}.{hint}") from exc

    choice = (data.get("choices") or [{}])[0]
    return (choice.get("message") or {}).get("content", "")
