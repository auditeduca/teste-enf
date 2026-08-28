"""Carrega .env da raiz do repositório para os agentes NKOS."""
from __future__ import annotations

import os
import sys
from pathlib import Path

_LOADED = False
_LOADED_FROM: Path | None = None
# NIFS/reference-scripts/agent_common -> NIFS
NIFS_ROOT = Path(__file__).resolve().parent.parent.parent
WORKSPACE_ROOT = NIFS_ROOT.parent

_SCRIPTS = WORKSPACE_ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from env_paths import env_candidates  # noqa: E402


def project_root() -> Path:
    return NIFS_ROOT


def _env_candidates() -> list[Path]:
    return env_candidates(WORKSPACE_ROOT, nifs=NIFS_ROOT, include_home=False)


def load_project_env(*, force: bool = False) -> dict[str, str]:
    """Parse .env e injeta em os.environ (sem sobrescrever vars já definidas)."""
    global _LOADED, _LOADED_FROM
    if _LOADED and not force:
        return {}

    loaded: dict[str, str] = {}
    env_path = None
    for candidate in _env_candidates():
        if candidate.is_file():
            env_path = candidate
            break

    if not env_path:
        _LOADED = True
        _LOADED_FROM = None
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
    _LOADED_FROM = env_path
    return loaded


def env_status() -> dict:
    """Quais chaves de agente estão configuradas (sem expor valores)."""
    load_project_env()
    env_path = _LOADED_FROM
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
        "env_file": str(env_path) if env_path else "",
        "env_file_exists": env_path is not None,
        "keys": {k: bool((os.environ.get(k) or "").strip()) for k in keys},
    }
