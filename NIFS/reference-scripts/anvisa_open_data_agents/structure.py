"""Etapa structure — normaliza CSV ANVISA para entidades NKOS."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from config import ANV_DIR, SCRAPE_SOURCES


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _slug_code(value: str, *, prefix: str, max_len: int = 32) -> str:
    clean = re.sub(r"[^A-Z0-9]", "_", (value or "UNK").upper())
    clean = re.sub(r"_+", "_", clean).strip("_")[:max_len]
    return f"{prefix}.{clean}" if clean else f"{prefix}.UNK"


def _medication_record(row: dict, *, source_id: str, content_hash: str | None) -> dict:
    reg = row.get("NUMERO_REGISTRO_PRODUTO") or row.get("NUMERO_REGISTRO") or row.get("REGISTRO") or ""
    name = row.get("NOME_PRODUTO") or row.get("PRODUTO") or ""
    entity = _slug_code(reg or name[:20], prefix="ANV.MED")
    return {
        "entity_code": entity,
        "concept_code": entity.replace("ANV.MED.", ""),
        "parent_entity_code": "ORG.ANVISA",
        "parent_entity_type": "Organization",
        "source_id": source_id,
        "content_source": "ANVISA_OPEN_DATA",
        "evidence_grade": "A",
        "product_name": name,
        "registration_number": reg,
        "active_ingredient": row.get("PRINCIPIO_ATIVO") or row.get("PRINCIPIO_ATIVO_PRODUTO"),
        "holder_company": row.get("EMPRESA_DETENTORA_REGISTRO") or row.get("EMPRESA"),
        "registration_status": row.get("SITUACAO_REGISTRO") or row.get("SITUACAO"),
        "therapeutic_class": row.get("CLASSE_TERAPEUTICA"),
        "regulatory_category": row.get("CATEGORIA_REGULATORIA"),
        "product_type": row.get("TIPO_PRODUTO"),
        "expiry_date": row.get("DATA_VENCIMENTO_REGISTRO"),
        "process_number": row.get("NUMERO_PROCESSO"),
        "content_hash": content_hash,
        "updated_at": _now(),
    }


def _price_record(row: dict, *, source_id: str) -> dict | None:
    reg = row.get("REGISTRO") or row.get("NUMERO_REGISTRO_PRODUTO") or row.get("NUMERO_REGISTRO") or ""
    if not reg:
        return None
    entity = _slug_code(reg, prefix="ANV.PRC")
    return {
        "entity_code": entity,
        "parent_entity_code": _slug_code(reg, prefix="ANV.MED"),
        "source_id": source_id,
        "registration_number": reg,
        "product_name": row.get("PRODUTO") or row.get("NOME_PRODUTO"),
        "active_ingredient": row.get("SUBSTANCIA") or row.get("PRINCIPIO_ATIVO"),
        "pf_price": row.get("PF") or row.get("PRECO_FABRICA") or row.get("PF 0%"),
        "pmc_price": row.get("PMC") or row.get("PRECO_MAXIMO"),
        "state": row.get("UF") or row.get("ESTADO"),
        "content_source": "ANVISA_OPEN_DATA_CMED",
        "updated_at": _now(),
    }


def _restriction_record(row: dict, *, source_id: str) -> dict | None:
    reg = row.get("NUMERO_REGISTRO_PRODUTO") or row.get("REGISTRO") or ""
    if not reg:
        return None
    entity = _slug_code(reg, prefix="ANV.RST")
    return {
        "entity_code": entity,
        "parent_entity_code": _slug_code(reg, prefix="ANV.MED"),
        "source_id": source_id,
        "registration_number": reg,
        "restriction_type": row.get("TIPO_RESTRICAO") or row.get("RESTRICAO"),
        "description_pt": row.get("DESCRICAO") or row.get("RESTRICAO_HOSPITALAR"),
        "content_source": "ANVISA_OPEN_DATA",
        "updated_at": _now(),
    }


def _dataset_catalog_entry(source: dict, *, row_count: int, content_hash: str | None) -> dict:
    sid = source["source_id"]
    return {
        "entity_code": sid,
        "filename": source.get("filename"),
        "title_pt": source.get("title") or source.get("filename"),
        "url": source.get("url"),
        "organization": "ANVISA",
        "portal_dados_gov": source.get("portal_url"),
        "fetch_mode": source.get("fetch_mode"),
        "priority": source.get("priority"),
        "record_count": row_count,
        "content_hash": content_hash,
        "parent_entity_code": "ORG.ANVISA",
        "updated_at": _now(),
    }


def structure_from_extract_report(*, limit: int | None = None) -> dict:
    report_path = ANV_DIR / "extract_report.json"
    if not report_path.is_file():
        return {"medications": [], "prices": [], "restrictions": [], "catalog": []}
    report = json.loads(report_path.read_text(encoding="utf-8"))
    sources_meta = json.loads(SCRAPE_SOURCES.read_text(encoding="utf-8")).get("sources", []) if SCRAPE_SOURCES.is_file() else []
    by_id = {s["source_id"]: s for s in sources_meta}
    medications: dict[str, dict] = {}
    prices: dict[str, dict] = {}
    restrictions: dict[str, dict] = {}
    catalog: list[dict] = []
    extracted = report.get("extracted") or []
    if limit:
        extracted = extracted[:limit]
    for item in extracted:
        sid = item.get("source_id")
        source = by_id.get(sid, {"source_id": sid, "filename": item.get("filename")})
        cache = ANV_DIR / "extract_cache" / f"{sid.replace('.', '_')}.json"
        rows = []
        if cache.is_file():
            rows = json.loads(cache.read_text(encoding="utf-8")).get("rows", [])
        fname = (source.get("filename") or "").upper()
        catalog.append(_dataset_catalog_entry(source, row_count=len(rows), content_hash=item.get("content_hash")))
        for row in rows:
            if "DADOS_ABERTOS_MEDICAMENTOS" in fname or (
                "MEDICAMENT" in fname and "PRECO" not in fname and "RESTRIC" not in fname and "VIGIMED" not in fname
            ):
                rec = _medication_record(row, source_id=sid, content_hash=item.get("content_hash"))
                medications[rec["entity_code"]] = rec
            elif "PRECO" in fname:
                rec = _price_record(row, source_id=sid)
                if rec:
                    prices[rec["entity_code"]] = rec
            elif "RESTRIC" in fname:
                rec = _restriction_record(row, source_id=sid)
                if rec:
                    restrictions[rec["entity_code"]] = rec
    structured = {
        "generated_at": _now(),
        "medications": list(medications.values()),
        "prices": list(prices.values()),
        "restrictions": list(restrictions.values()),
        "catalog": catalog,
    }
    out = ANV_DIR / "structure_report.json"
    out.write_text(json.dumps({**structured, "counts": {
        "medications": len(structured["medications"]),
        "prices": len(structured["prices"]),
        "restrictions": len(structured["restrictions"]),
    }}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return structured
