"""Roteador de tarefas → melhor provedor LLM."""
from __future__ import annotations

import json
import re
from typing import Any

from llm_router.config import provider_for_task, providers_status, resolve_api_key, resolve_model
from llm_router.providers import chat_complete


def parse_json_response(text: str) -> Any:
    text = (text or "").strip()
    if not text:
        raise ValueError("Resposta LLM vazia")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        return json.loads(fence.group(1).strip())
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return json.loads(text[start : end + 1])
    start = text.find("[")
    end = text.rfind("]")
    if start >= 0 and end > start:
        return json.loads(text[start : end + 1])
    raise ValueError(f"JSON não encontrado: {text[:400]}...")


def route_chat(
    messages: list[dict],
    *,
    task: str = "default",
    provider: str | None = None,
    payload: dict | None = None,
    temperature: float = 0.2,
    max_tokens: int = 4096,
) -> dict:
    """Chat com roteamento automático por tipo de tarefa."""
    payload = payload or {}
    chosen = provider or provider_for_task(task, payload)
    content = chat_complete(
        messages,
        provider=chosen,
        temperature=temperature,
        max_tokens=max_tokens,
        payload=payload,
    )
    return {
        "provider": chosen,
        "model": resolve_model(chosen, payload),
        "task": task,
        "content": content,
    }


def route_chat_json(
    messages: list[dict],
    *,
    task: str = "default",
    provider: str | None = None,
    payload: dict | None = None,
    temperature: float = 0.2,
    max_tokens: int = 8192,
) -> dict:
    result = route_chat(
        messages,
        task=task,
        provider=provider,
        payload=payload,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    result["parsed"] = parse_json_response(result["content"])
    return result


def llm_status() -> dict:
    """Status de todos os provedores + roteamento."""
    return {
        "providers": providers_status(),
        "task_routing": {
            "graph_validation": "claude",
            "clinical_decision_content": "claude",
            "translation": "deepseek",
            "code_review": "deepseek",
            "fast_check": "groq",
        },
        "any_configured": any(p["configured"] for p in providers_status().values()),
    }


def llm_enabled(payload: dict | None = None) -> bool:
    payload = payload or {}
    import os
    if os.environ.get("NKOS_NO_LLM", "").strip() in ("1", "true", "yes"):
        return False
    if payload.get("no_llm") or payload.get("llm") is False:
        return False
    if payload.get("use_llm") is False:
        return False
    for provider in ("claude", "deepseek", "groq", "cursor"):
        if resolve_api_key(provider, payload):
            return True
    return False
