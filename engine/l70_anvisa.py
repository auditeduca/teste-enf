"""COMPARE L70 Medications against the official ANVISA API and Drive listing.

Does not unzip CKO_Medicamentos_ANVISA_Completo.zip.
Does not copy insulina HTML/PNG into data/tools.
Does not treat Drive description 17.231 as a hashed population.
Does not treat openFDA as an ANVISA leaflet.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .paths import ROOT, TOOLS_DIR

CATALOG_PATH = ROOT / "cko_md" / "l70_anvisa_compare.json"
BUSINESS_KEY = "MD-L70-ANVISA-001"
DRIVE_ZIP_ID = "1TPmIPtXeMbsjJEiG_19W5bt8JZPJMhDF"
DRIVE_PARENT_ID = "0AFNnC8Uinv0BUk9PVA"
CLAIMED_COUNT_DRIVE_DESCRIPTION = 17231

DRIVE_FOLDERS_MCP = (
    {
        "id": "1UpgQAuPUvF_8iGY31-k2W7EXGcY1S7eQ",
        "title": "anvisa",
        "classification": "FOLDER_OBSERVED",
        "children_listing": "NOT_OBSERVED",
        "note": "search_files parentId devolveu vazio neste ciclo. Sem unzip.",
    },
    {
        "id": "1_SQqd5Xx_6seeOklBPqfWTW2juEnwQJw",
        "title": "anvisa-open-data",
        "classification": "FOLDER_OBSERVED",
        "children_listing": "NOT_OBSERVED",
        "note": "search_files parentId devolveu vazio neste ciclo. Sem dump.",
    },
    {
        "id": "1PC-6ZLimaugUTvgBj7tEDWvmf5oGvmMc",
        "title": "anvisa_open_data_agents",
        "classification": "FOLDER_OBSERVED",
        "children_listing": "NOT_OBSERVED",
        "note": "search_files parentId devolveu vazio neste ciclo. Sem promover agentes Drive.",
    },
)

INSULINA_COMPARE = (
    {
        "id": "1h4Lu0dDFoNNwJ-Q0e3FUCUYOksUhvIli",
        "title": "recuperado_insulina_consolidado.zip",
        "bytes": 7486,
        "classification": "CANDIDATE_GAP",
        "action": "COMPARE_ONLY",
        "note": "Zip pequeno no mesmo parent. Não unzip para data/tools.",
    },
    {
        "id": "1Iucn9BiW9HQNOnyn5zpxyx5dSFupu-TR",
        "title": "recuperado_insulina_package.zip",
        "bytes": 5338,
        "classification": "CANDIDATE_GAP",
        "action": "COMPARE_ONLY",
        "note": "Zip pequeno no mesmo parent. Não unzip para data/tools.",
    },
)

INSULINA_SKIP = (
    {"id": "1613nwK_tve_ti4wECkvSPojeNUOOv_cN", "title": "insulina.webp", "classification": "SKIP_BINARY"},
    {"id": "1cp_z87Y24ZNpGRfxnwe195gZl2UflKrg", "title": "insulina.html", "classification": "DISCOVERY_QUARANTINE"},
    {"id": "1dfMMfHAbatE2zEWtaJ01H3SNA_DuKPjv", "title": "insulina.html", "classification": "DISCOVERY_QUARANTINE"},
    {"id": "1vHSZmqWylbn7jLr1KI_Yc3IIB7ChujIa", "title": "insulina.html", "classification": "DISCOVERY_QUARANTINE"},
    {"id": "1QsVr8UrpktVwQHKWdz0Rut3h3-_l06sz", "title": "insulina.html", "classification": "DISCOVERY_QUARANTINE"},
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _dump(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _adapter(probe: dict, key: str) -> dict:
    for item in probe.get("adapters") or []:
        if item.get("business_key") == key:
            return item
    return {}


def _upsert_library_api_map(portal: dict, consultas: dict, ckan: dict, openfda: dict) -> None:
    path = ROOT / "cko_md" / "library_api_map.json"
    libmap = _load(path)
    if not libmap:
        return
    rows = list(libmap.get("api_where_possible") or [])
    prev_row = next((item for item in rows if item.get("layer") == "L70"), {})
    http_status = portal.get("http_status")
    if http_status is None:
        http_status = prev_row.get("http_status")
    epistemic = portal.get("epistemic_status") or prev_row.get("epistemic_status") or "EVIDENCE_PENDING"
    consultas_status = consultas.get("http_status")
    if consultas_status is None:
        consultas_status = "403"
    ckan_status = ckan.get("http_status")
    if ckan_status is None:
        ckan_status = "401"
    openfda_status = openfda.get("http_status")
    if openfda_status is None:
        openfda_status = "200"
    row = {
        "layer": "L70",
        "intent": "API oficial ANVISA para medicamentos e soluções",
        "adapter": "API-ANVISA-PORTAL",
        "http_status": http_status,
        "epistemic_status": epistemic,
        "note": (
            "Portal APIs ANVISA HTML 200 (SPA Gov.br). "
            f"REST JSON de produto NOT_OBSERVED (consultas HTTP {consultas_status}; "
            f"CKAN anvisa HTTP {ckan_status}). "
            "Zip Drive 59.8 MB SKIP_BINARY_DUMP. Claimed 17231 = descrição Drive, não hashed. "
            f"openFDA HTTP {openfda_status} JSON = fallback US. Não substitui bula ANVISA."
        ),
    }
    replaced = False
    out = []
    for item in rows:
        if item.get("layer") == "L70":
            out.append(row)
            replaced = True
        else:
            out.append(item)
    if not replaced:
        out.insert(0, row)
    libmap["api_where_possible"] = out
    libmap["l70_anvisa_compare_ref"] = BUSINESS_KEY
    _dump(path, libmap)


def compare_l70_anvisa() -> dict:
    """AG-L70-ANVISA-COMPARE — official API first; Drive dump listing-only."""
    probe = _load(ROOT / "cko_inbox" / "extracted" / "api_probe.json")
    drive = _load(ROOT / "cko_inbox" / "extracted" / "drive_inventory.json")
    zip_row = next(
        (item for item in (drive.get("files") or []) if item.get("id") == DRIVE_ZIP_ID),
        {},
    )
    portal = _adapter(probe, "API-ANVISA-PORTAL")
    consultas = _adapter(probe, "API-ANVISA-CONSULTAS-MEDICAMENTOS")
    ckan = _adapter(probe, "API-CKAN-DADOSGOV-ANVISA")
    openfda = _adapter(probe, "API-OPENFDA-DRUGLABEL")
    insulina_tool = (TOOLS_DIR / "insulina.json").exists()
    dump_extracted = any(
        path.name.lower().startswith("cko_medicamentos")
        for path in TOOLS_DIR.glob("*")
    )
    catalog = {
        "business_key": BUSINESS_KEY,
        "uuid": None,
        "status": "SOURCE_DERIVED",
        "implemented": False,
        "publication": "HOLD",
        "assured": False,
        "promotes_to_md": False,
        "copied_into_data_tools": False,
        "unzipped": False,
        "layer": "L70",
        "frente": "F24",
        "method": "RECOVER → COMPARE → GAP ONLY",
        "rule": (
            "L70 usa a API oficial da ANVISA. Resposta HTML do portal ≠ REST JSON de produto. "
            "Dump Drive não entra em data/tools. openFDA não substitui bula ANVISA. "
            "DOCUMENTADO ≠ IMPLEMENTADO ≠ VALIDADO ≠ ASSURED ≠ PUBLICADO."
        ),
        "official_api": {
            "portal": {
                "business_key": "API-ANVISA-PORTAL",
                "url": "https://api.anvisa.gov.br/",
                "kind": "PORTAL_SPA",
                "http_status": portal.get("http_status"),
                "epistemic_status": portal.get("epistemic_status") or "EVIDENCE_PENDING",
                "rest_json": bool(portal.get("rest_json")),
                "base_url": portal.get("base_url"),
                "online": bool(portal.get("online")),
                "auth": "Gov.br OAuth Client ID + Client Secret",
                "note": "SPA HTML 200 observado. Product REST NOT_OBSERVED sem credencial.",
            },
            "consultas_medicamentos": {
                "business_key": "API-ANVISA-CONSULTAS-MEDICAMENTOS",
                "url": "https://consultas.anvisa.gov.br/api/consulta/medicamentos",
                "kind": "PRODUCT_CONSULTA",
                "http_status": consultas.get("http_status"),
                "epistemic_status": consultas.get("epistemic_status") or "EVIDENCE_PENDING",
                "rest_json": bool(consultas.get("rest_json")),
                "base_url": consultas.get("base_url"),
                "note": "HTTP 403 neste ambiente. Não extrair token do JavaScript do portal.",
            },
            "ckan_dadosgov": {
                "business_key": "API-CKAN-DADOSGOV-ANVISA",
                "url": "https://dados.gov.br/api/3/action/package_search?q=anvisa&rows=5",
                "http_status": ckan.get("http_status"),
                "epistemic_status": ckan.get("epistemic_status") or "EVIDENCE_PENDING",
                "note": "CKAN package_search q=anvisa. HTTP 401 neste lote.",
            },
            "openfda_fallback": {
                "business_key": "API-OPENFDA-DRUGLABEL",
                "url": "https://api.fda.gov/drug/label.json?limit=1",
                "http_status": openfda.get("http_status"),
                "epistemic_status": openfda.get("epistemic_status") or "EVIDENCE_PENDING",
                "rest_json": bool(openfda.get("rest_json")) or bool(openfda.get("online")),
                "replaces_anvisa_leaflet": False,
                "note": "Fallback US gov. Não substitui bula ANVISA.",
            },
            "product_rest": "NOT_OBSERVED",
            "production_api": False,
        },
        "drive": {
            "parent_id": DRIVE_PARENT_ID,
            "zip": {
                "id": DRIVE_ZIP_ID,
                "title": zip_row.get("title") or "CKO_Medicamentos_ANVISA_Completo.zip",
                "bytes": zip_row.get("bytes") or 59854232,
                "mimeType": zip_row.get("mimeType") or "application/zip",
                "classification": zip_row.get("classification") or "SKIP_BINARY_DUMP",
                "promotes_to_md": False,
                "description_claim": (
                    "Base completa de medicamentos ANVISA enriquecida — 17.231 medicamentos "
                    "ativos com conhecimento clínico, rastreabilidade e schema CKO v1.0.0"
                ),
                "claimed_count_drive_description": CLAIMED_COUNT_DRIVE_DESCRIPTION,
                "verified_population": "EVIDENCE_PENDING",
                "unzipped": False,
                "copied_into_data_tools": False,
                "source": "DRIVE_LISTING_PLUS_MCP_METADATA",
            },
            "folders_mcp_this_cycle": list(DRIVE_FOLDERS_MCP),
            "insulina_compare": list(INSULINA_COMPARE),
            "insulina_skip": list(INSULINA_SKIP),
        },
        "pilot": {
            "identity": "PILOT-CKO-INSULINA",
            "data_tools_insulina_json": insulina_tool,
            "status": "HOLD",
        },
        "dump_extracted_into_data_tools": dump_extracted,
        "claimed_count_drive_description": CLAIMED_COUNT_DRIVE_DESCRIPTION,
        "verified_population": "EVIDENCE_PENDING",
        "owner_unblock": "UNBLOCK-ANVISA-API-CREDENTIALS",
        "gaps": [
            {
                "id": "GAP-L70-ANVISA-REST-JSON",
                "status": "EVIDENCE_PENDING",
                "reason": (
                    "Portal APIs ANVISA é SPA HTML. REST JSON de produto não observado "
                    "sem Gov.br Client ID/Secret."
                ),
            },
            {
                "id": "GAP-L70-DRIVE-DUMP",
                "status": "COMPARE_ONLY",
                "reason": (
                    "CKO_Medicamentos_ANVISA_Completo.zip 59.8 MB = SKIP_BINARY_DUMP. "
                    "Claimed 17231 é descrição Drive, não população hashed."
                ),
            },
            {
                "id": "GAP-L70-INSULINA-TOOL",
                "status": "HOLD",
                "reason": "Sem data/tools/insulina.json. PNG/HTML Drive não ligam no chrome.",
            },
        ],
        "do_not": [
            "Unzip CKO_Medicamentos_ANVISA_Completo.zip em data/tools.",
            "Tratar 17231 como população verificada.",
            "Copiar insulina.html / insulina.webp / medicamentos.html para o chrome.",
            "Inventar dose, bula ou adapter REST.",
            "Usar openFDA como substituto de bula ANVISA.",
            "Extrair token/segredo do JavaScript de consultas.anvisa.gov.br.",
        ],
        "evaluated_at": _now(),
    }
    _dump(CATALOG_PATH, catalog)
    _upsert_library_api_map(portal, consultas, ckan, openfda)
    return {
        "agent_id": "AG-L70-ANVISA-COMPARE",
        "class": "MONITORING",
        "role": "CHECKER",
        "status": "COMPARE_ONLY",
        "promotes_to_md": False,
        "copied_into_data_tools": False,
        "unzipped": False,
        "publication": "HOLD",
        "assured": False,
        "writes_to": "cko_md/l70_anvisa_compare.json",
        "business_key": BUSINESS_KEY,
        "product_rest": "NOT_OBSERVED",
        "verified_population": "EVIDENCE_PENDING",
    }
