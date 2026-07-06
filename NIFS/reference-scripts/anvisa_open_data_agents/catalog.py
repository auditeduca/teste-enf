"""Catálogo — sincroniza fontes ANVISA + estatísticas do pipeline."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from agent_common.anvisa_fetch import fetch_dados_gov_org_datasets, list_anvisa_csv_catalog  # noqa: E402
from agent_common.json_io import save_json_atomic  # noqa: E402
from config import ANV_DIR, BR_OUT, CATALOG_OUT, MEDICATIONS_OUT, PRICES_OUT, RESTRICTIONS_OUT, PRIORITY_FILENAMES, SCRAPE_SOURCES  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def sync_catalog(*, verify_ssl: bool = True) -> dict:
    """Sincroniza scrape_sources.json a partir de dados.anvisa.gov.br (+ dados.gov.br se disponível)."""
    anvisa = list_anvisa_csv_catalog(verify_ssl=verify_ssl)
    dgov = fetch_dados_gov_org_datasets(verify_ssl=False)
    sources = anvisa.get("datasets", []) if anvisa.get("ok") else []
    for ds in sources:
        ds["priority"] = 1 if ds.get("filename") in PRIORITY_FILENAMES else 2
        ds["parent_entity_code"] = "ORG.ANVISA"
        ds["domain_code"] = "REG.ANVISA.MEDICAMENTOS" if "MEDICAMENT" in ds.get("filename", "").upper() else "REG.ANVISA.GERAL"
    doc = {
        "schema_version": "2026.2.12-anvisa-scrape-sources",
        "generated_at": _now(),
        "organization_slug": "agencia-nacional-de-vigilancia-sanitaria-anvisa",
        "portal_dados_gov": "https://dados.gov.br/dados/organizacoes/visualizar/agencia-nacional-de-vigilancia-sanitaria-anvisa",
        "portal_anvisa_csv": "https://dados.anvisa.gov.br/dados/",
        "sources_total": len(sources),
        "priority_count": sum(1 for s in sources if s.get("priority") == 1),
        "dados_gov_api_ok": dgov.get("ok", False),
        "dados_gov_total": dgov.get("total", 0),
        "sources": sources,
    }
    save_json_atomic(SCRAPE_SOURCES, doc)
    return {
        "ok": len(sources) > 0,
        "sources_total": len(sources),
        "priority_count": doc["priority_count"],
        "dados_gov_api_ok": doc["dados_gov_api_ok"],
        "path": str(SCRAPE_SOURCES.relative_to(ROOT)),
    }


def pipeline_stats() -> dict:
    sources = _load_json(SCRAPE_SOURCES).get("sources", [])
    discover = _load_json(ANV_DIR / "discover_report.json")
    fetch = _load_json(ANV_DIR / "fetch_report.json")
    extract = _load_json(ANV_DIR / "extract_report.json")
    meds = _load_json(MEDICATIONS_OUT)
    prices = _load_json(PRICES_OUT)
    restr = _load_json(RESTRICTIONS_OUT)
    catalog = _load_json(CATALOG_OUT)
    stale = discover.get("stale", 0)
    pending = stale if stale else max(len(sources) - fetch.get("fetched_ok", 0), 0)
    return {
        "sources_total": len(sources),
        "sources_priority": sum(1 for s in sources if s.get("priority") == 1),
        "datasets_catalog": catalog.get("count", len(catalog.get("records", []))),
        "medications": len(meds.get("records", [])),
        "prices": len(prices.get("records", [])),
        "restrictions": len(restr.get("records", [])),
        "stale_sources": stale,
        "last_fetch_ok": fetch.get("fetched_ok", 0),
        "last_extract_rows": extract.get("rows_extracted", 0),
        "pending_refresh": pending,
        "completion_pct": _completion_pct(sources, fetch, meds),
        "last_discover_at": discover.get("generated_at"),
        "last_fetch_at": fetch.get("generated_at"),
        "next_refresh_due": _next_refresh_due(fetch),
    }


def _completion_pct(sources: list, fetch: dict, meds: dict) -> int:
    if not sources:
        return 0
    priority = [s for s in sources if s.get("priority") == 1] or sources[:5]
    ok_ids = {r.get("source_id") for r in fetch.get("results", []) if r.get("ok")}
    fetched_priority = sum(1 for s in priority if s["source_id"] in ok_ids)
    med_bonus = 30 if len(meds.get("records", [])) > 1000 else (15 if meds.get("records") else 0)
    base = round(fetched_priority / max(len(priority), 1) * 70)
    return min(100, base + med_bonus)


def _next_refresh_due(fetch: dict) -> str | None:
    at = fetch.get("generated_at")
    if not at:
        return "due_now"
    try:
        from datetime import timedelta

        dt = datetime.strptime(at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        due = dt + timedelta(days=30)
        if datetime.now(timezone.utc) >= due:
            return "due_now"
        return due.strftime("%Y-%m-%d")
    except ValueError:
        return None
