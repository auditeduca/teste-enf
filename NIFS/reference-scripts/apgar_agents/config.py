"""Configuração do pipeline de agentes APGAR (piloto) — LangGraph + DeepSeek."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
APGAR_DIR = ROOT / "datasets" / "master-data" / "apgar"
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
AGENT_RUNS_DIR = APGAR_DIR / "agent_runs"

DEFAULT_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash")
