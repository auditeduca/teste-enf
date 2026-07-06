"""DeepSeek + helpers JSON para agentes APGAR (LangGraph).

Estratégia combinada: tarefas nobres (grafo, decisão clínica) → Claude via llm_router;
volume/tradução/code review → DeepSeek; checks rápidos → Groq (Llama).
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from review.config import DEFAULT_DEEPSEEK_MODEL
from review.deepseek_client import chat_complete as deepseek_chat_complete

from config import DEFAULT_MODEL, PROMPTS_DIR

_SCRIPTS = Path(__file__).resolve().parent.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

try:
    from api_helpers import resolve_deepseek as _resolve_deepseek
except ImportError:
    from apgar_agents.api_helpers import resolve_deepseek as _resolve_deepseek

try:
    from llm_router import route_chat, route_chat_json as _route_chat_json
    _HAS_ROUTER = True
except ImportError:
    _HAS_ROUTER = False


def get_api_key(explicit: str | None = None, payload: dict | None = None) -> str | None:
    if explicit:
        key = explicit.strip()
        return key or None
    if payload:
        key, _ = _resolve_deepseek(payload)
        if key:
            return key
    key = (os.environ.get("DEEPSEEK_API_KEY") or "").strip()
    return key or None


def resolve_model(model: str | None = None) -> str:
    return model or DEFAULT_MODEL or DEFAULT_DEEPSEEK_MODEL


def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


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
    raise ValueError(f"JSON não encontrado na resposta LLM: {text[:400]}...")


def _resolve_task(payload: dict | None) -> str | None:
    payload = payload or {}
    return payload.get("llm_task") or payload.get("task")


def chat_json(
    messages: list[dict],
    *,
    api_key: str,
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 4096,
    payload: dict | None = None,
    task: str | None = None,
) -> Any:
    task = task or _resolve_task(payload)
    if _HAS_ROUTER and task and task not in ("default", "code_review", "translation", "bulk_content"):
        result = _route_chat_json(
            messages,
            task=task,
            payload={**(payload or {}), "api_key": api_key, "model": model},
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return result.get("parsed")
    content = deepseek_chat_complete(
        messages,
        api_key=api_key,
        model=resolve_model(model),
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return parse_json_response(content)


def chat_text(
    messages: list[dict],
    *,
    api_key: str,
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 4096,
    payload: dict | None = None,
    task: str | None = None,
) -> str:
    task = task or _resolve_task(payload)
    if _HAS_ROUTER and task and task not in ("default", "code_review", "translation", "bulk_content"):
        result = route_chat(
            messages,
            task=task,
            payload={**(payload or {}), "api_key": api_key, "model": model},
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return result.get("content", "")
    return deepseek_chat_complete(
        messages,
        api_key=api_key,
        model=resolve_model(model),
        temperature=temperature,
        max_tokens=max_tokens,
    )
