"""Carrega .env da raiz do repositório para os agentes NKOS."""
from __future__ import annotations

import os
from pathlib import Path

_LOADED = False
ROOT = Path(__file__).resolve().parent.parent.parent


def project_root() -> Path:
    return ROOT


def load_project_env(*, force: bool = False) -> dict[str, str]:
    """Parse .env na raiz e injeta em os.environ (sem sobrescrever vars já definidas)."""
    global _LOADED
    if _LOADED and not force:
        return {}

    env_path = ROOT / ".env"
    loaded: dict[str, str] = {}
    if not env_path.is_file():
        _LOADED = True
        return loaded

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if not key or not key.replace("_", "").isalnum():
            continue
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        if key not in os.environ:
            os.environ[key] = value
            loaded[key] = value

    _LOADED = True
    return loaded


def env_status() -> dict:
    """Quais chaves de agente estão configuradas (sem expor valores)."""
    load_project_env()
    keys = [
        "ANTHROPIC_API_KEY",
        "DEEPSEEK_API_KEY",
        "GROQ_API_KEY",
        "CURSOR_API_KEY",
        "GOOGLE_PAGESPEED_API_KEY",
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "FIREBASE_PROJECT_ID",
        "FIREBASE_CREDENTIALS_JSON",
        "FIREBASE_FUNCTIONS_URL",
        "FIREBASE_SYNC_SECRET",
        "NKOS_NO_LLM",
    ]
    return {
        "env_file": str(ROOT / ".env"),
        "env_file_exists": (ROOT / ".env").is_file(),
        "keys": {k: bool((os.environ.get(k) or "").strip()) for k in keys},
    }
