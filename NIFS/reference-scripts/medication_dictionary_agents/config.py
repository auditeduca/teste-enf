"""Config — agente dicionário de medicamentos."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MD_DIR = ROOT / "datasets" / "master-data" / "medication-dictionary"
QUEUE_PATH = MD_DIR / "pending_queue.json"
DRUG_REFS = ROOT / "datasets" / "clinical" / "drug_references.json"
DRUG_MONO = ROOT / "datasets" / "clinical" / "drug_monographs.json"
OUTPUT = ROOT / "datasets" / "clinical" / "medication_dictionary.json"
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
DEFAULT_MODEL = "deepseek-chat"
