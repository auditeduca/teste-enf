"""Config — agente notificação compulsória."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CN_DIR = ROOT / "datasets" / "master-data" / "compulsory-notifications"
SCRAPE_SOURCES = CN_DIR / "scrape_sources.json"
JURISDICTIONS = ROOT / "datasets" / "regulatory" / "br" / "jurisdictions.json"
LEGISLATION = ROOT / "datasets" / "regulatory" / "br" / "legislation_instruments.json"
OUTPUT = ROOT / "datasets" / "regulatory" / "br" / "compulsory_notifications.json"
SCRAPE_CACHE = CN_DIR / "scrape_cache"
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
DEFAULT_MODEL = "deepseek-chat"
BASE_LEGISLATION = "LEG.BR.MS.PC4.2017"
