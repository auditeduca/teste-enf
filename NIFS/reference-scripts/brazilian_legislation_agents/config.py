"""Config — agente legislação brasileira consolidada."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BL_DIR = ROOT / "datasets" / "master-data" / "brazilian-legislation"
SCRAPE_SOURCES = BL_DIR / "scrape_sources.json"
SCRAPE_CACHE = BL_DIR / "scrape_cache"
DOMAINS = ROOT / "datasets" / "regulatory" / "br" / "legislation_domains.json"
INSTRUMENTS = ROOT / "datasets" / "regulatory" / "br" / "legislation_instruments.json"
CORPUS = ROOT / "datasets" / "regulatory" / "br" / "legislation_corpus.json"
PROVISIONS = ROOT / "datasets" / "regulatory" / "br" / "legal_provisions.json"
TOOL_LINKS = ROOT / "datasets" / "regulatory" / "br" / "legislation_tool_links.json"
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
DEFAULT_MODEL = "deepseek-chat"
