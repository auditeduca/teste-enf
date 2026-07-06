"""Roteador LLM unificado — Claude, DeepSeek, Groq (Llama), Cursor."""
from agent_common.env_loader import load_project_env

load_project_env()

from llm_router.config import PROVIDERS, provider_for_task, providers_status, resolve_api_key, resolve_model
from llm_router.providers import chat_complete
from llm_router.router import llm_enabled, llm_status, parse_json_response, route_chat, route_chat_json

__all__ = [
    "PROVIDERS",
    "chat_complete",
    "llm_enabled",
    "llm_status",
    "parse_json_response",
    "provider_for_task",
    "providers_status",
    "resolve_api_key",
    "resolve_model",
    "route_chat",
    "route_chat_json",
]
