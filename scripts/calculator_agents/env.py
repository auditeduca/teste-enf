"""Carregamento unificado de variáveis de ambiente para agentes de calculadoras."""
from __future__ import annotations

import os
import re
from pathlib import Path

_LOADED = False
WORKSPACE = Path(__file__).resolve().parents[2]
REF_SCRIPTS = WORKSPACE / "NIFS" / "reference-scripts"

ENV_CANDIDATES = [
    WORKSPACE / ".env",
    WORKSPACE / "NIFS" / ".env",
    Path(os.environ.get("CALENF_ENV_FILE", "")),
    Path("C:/Github/CALENF-NKD/.env"),
    Path.home() / ".calenf" / ".env",
]


def _parse_env_file(path: Path) -> dict[str, str]:
    loaded: dict[str, str] = {}
    if not path.is_file():
        return loaded
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("export "):
            line = line[7:].strip()
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$", line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        if key not in os.environ:
            os.environ[key] = value
            loaded[key] = value
    return loaded


def load_env(*, force: bool = False) -> dict[str, str]:
    """Carrega .env de múltiplos caminhos sem sobrescrever vars já definidas."""
    global _LOADED
    if _LOADED and not force:
        return {}

    merged: dict[str, str] = {}
    for candidate in ENV_CANDIDATES:
        if str(candidate) and candidate.is_file():
            merged.update(_parse_env_file(candidate))

    # Também usa env_loader do NKOS se disponível
    if REF_SCRIPTS.is_dir():
        import sys

        scripts_path = str(REF_SCRIPTS)
        if scripts_path not in sys.path:
            sys.path.insert(0, scripts_path)
        try:
            from agent_common.env_loader import load_project_env

            merged.update(load_project_env(force=force))
        except ImportError:
            pass

    _LOADED = True
    return merged


def llm_enabled() -> bool:
    load_env()
    if os.environ.get("NKOS_NO_LLM", "").strip().lower() in ("1", "true", "yes"):
        return False
    return bool(os.environ.get("DEEPSEEK_API_KEY", "").strip())


def env_status() -> dict:
    load_env()
    keys = [
        "DEEPSEEK_API_KEY",
        "ANTHROPIC_API_KEY",
        "GROQ_API_KEY",
        "DEEPSEEK_MODEL",
        "NKOS_NO_LLM",
    ]
    env_files = [str(p) for p in ENV_CANDIDATES if str(p) and p.is_file()]
    return {
        "llm_enabled": llm_enabled(),
        "env_files_found": env_files,
        "keys": {k: bool(os.environ.get(k, "").strip()) for k in keys},
        "deepseek_model": os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash"),
    }
