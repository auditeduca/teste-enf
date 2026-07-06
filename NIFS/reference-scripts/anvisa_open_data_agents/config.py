"""Config — agentes dados abertos ANVISA (dados.gov.br / dados.anvisa.gov.br)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
ANV_DIR = ROOT / "datasets" / "master-data" / "anvisa-open-data"
SCRAPE_SOURCES = ANV_DIR / "scrape_sources.json"
SCRAPE_CACHE = ANV_DIR / "scrape_cache"
BR_OUT = ROOT / "datasets" / "regulatory" / "br" / "anvisa"
CATALOG_OUT = BR_OUT / "datasets_catalog.json"
MEDICATIONS_OUT = BR_OUT / "medications_registry.json"
PRICES_OUT = BR_OUT / "medication_prices.json"
RESTRICTIONS_OUT = BR_OUT / "medication_restrictions.json"
DRUG_REFS = ROOT / "datasets" / "clinical" / "drug_references.json"
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

# Datasets prioritários enfermagem / medicamentos (sync mensal)
PRIORITY_FILENAMES = {
    "DADOS_ABERTOS_MEDICAMENTOS.csv",
    "TA_PRECOS_MEDICAMENTOS.csv",
    "TA_RESTRICAO_MEDICAMENTO.csv",
    "FILA_ANALISE_MEDICAMENTO.csv",
    "VigiMed_Medicamentos.csv",
}

DEFAULT_MODEL = "deepseek-chat"
