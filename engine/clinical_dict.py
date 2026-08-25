"""Drive CKO clinical data dictionary + calculator codes. COMPARE only.

Zip: Dicionario clinico.zip (152MrVMQHG76G8nVN0wMMqedvTpHzfEB-).
Namelist and structured names/codes only. No dump of formulas, ABNT/ISO clauses,
NANDA text, or third-party scales into data/tools.
"""

from __future__ import annotations

import hashlib
import io
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from .paths import ROOT, TOOLS_DIR

DRIVE_FILE_ID = "152MrVMQHG76G8nVN0wMMqedvTpHzfEB-"
DRIVE_TITLE = "Dicionario clinico.zip"
DRIVE_PARENT = "0AFNnC8Uinv0BUk9PVA"
ZIP_PATH = ROOT / "cko_inbox" / "drive" / "dicionario_clinico" / "Dicionario-clinico.zip"
CATALOG_PATH = ROOT / "cko_md" / "clinical_dictionary_catalog.json"
IPE_PATH = ROOT / "cko_inbox" / "extracted" / "clinical_dict_inventory.json"
GLOSSARY_URL = (
    "https://www.gov.br/governodigital/pt-br/infraestrutura-nacional-de-dados/"
    "governancadedados/glossario-de-termos-de-dados"
)
PGDADOS_REF = "MD-PGDADOS-001"
OFFICIAL_CATALOG_URL = "https://www.iso.org/standard/80766.html"

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
NSR = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"

PILOT_CODES = {
    "gotejamento": "CALC-GOTEJAMENTO-001",
    "meows": "SCALE-MEOWS-001",
    "cinco-ts-pcr": "GUIDE-5TS-PCR-001",
    "dimensionamento": "CALC-DIMENSIONAMENTO-001",
    "simulado-tecnico": "EXAM-SIMULADO-TEC-001",
}

DRIVE_MD_BLOCKERS = (
    ("FLD-REF-ACCESSED", "accessed_at", "ABNT NBR 6023:2025"),
    ("FLD-REF-TITLE", "title", "ABNT NBR 6023:2025"),
    ("FLD-REF-URI", "source_uri", "ABNT NBR 6023:2025"),
    ("FLD-REF-VERSION", "version_or_edition", "ABNT NBR 6023:2025"),
    ("FLD-RND-CALCPREC", "calculation_precision", "ABNT NBR 5891:2014"),
    ("FLD-RND-DISPPREC", "display_precision", "ABNT NBR 5891:2014"),
    ("FLD-RND-MODE", "rounding_mode", "ABNT NBR 5891:2014"),
    ("FLD-RND-STAGE", "rounding_stage", "ABNT NBR 5891:2014"),
)

THIRD_PARTY_SCALE_TOKENS = frozenset({
    "braden", "norton", "glasgow", "waterlow", "gosnell", "morse", "nihss",
    "sofa", "qsofa", "apache ii", "news", "news2", "mews",
})


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


def clinical_dict_fields() -> list[dict]:
    """Envelope fields observed from pilots + Drive dictionary. ABNT IDs are Drive-named HOLD."""
    common = {
        "iso_catalog_url": OFFICIAL_CATALOG_URL,
        "iso_clause_text": "CLAUSE_TEXT_UNAVAILABLE",
        "pgdados_ref": PGDADOS_REF,
        "pgdados_source_url": GLOSSARY_URL,
        "pgdados_clause_text": "NOT_COPIED_AS_PRODUCT_RULE",
        "clin_dict_ref": "MD-CLIN-DICT-001",
        "certified": False,
        "iso_implemented": False,
        "layer": "L10",
        "iso_test_id": "ISO8000-CKO-CLIN-DICT",
    }
    rows = [
        ("FLD-TOOL-CODE", "tool.code", "Código operacional observado nos pilotos (CALC-/SCALE-/GUIDE-/EXAM-*). Drive usa nomes, não estes códigos.", "Dados Mestres", "PGD-INSTR-POLITICA"),
        ("FLD-TOOL-SLUG", "tool.slug", "Slug kebab-case. Uma identidade MD; HTML/zip não cria slug paralelo.", "Dados Mestres", "PGD-INSTR-POLITICA"),
        ("FLD-CLIN-DICT-CAMPO", "clin_dict.campo", "Nome de campo do dicionário Drive (Foundation/Knowledge). Catálogo COMPARE; não é cláusula clínica.", "Atributos de referência", "PGD-INSTR-POLITICA"),
        ("FLD-ID-SCHEME", "identity.scheme_candidate", "Drive nomeia canonicalId/UUIDv4/v5/VDR/VIR/MD/slug. Operacional CKO permanece CKO-BK-1; UUIDv7 HOLD. UUIDv4 NÃO adotado.", "Dados Mestres", "PGD-INSTR-POLITICA"),
    ]
    fields = [
        {
            "business_key": key,
            "name": name,
            "purpose": purpose,
            "pgdados_term": term,
            "pgdados_instrument": instrument,
            **common,
        }
        for key, name, purpose, term, instrument in rows
    ]
    for key, name, norm in DRIVE_MD_BLOCKERS:
        fields.append({
            "business_key": key,
            "name": f"clin_dict.{name}",
            "purpose": f"Campo HOLD nomeado no zip Drive ({norm}). Texto de cláusula ABNT não ingerido.",
            "pgdados_term": "padronização",
            "pgdados_instrument": "PGD-INSTR-ESTRATEGIA",
            "abnt_norm_named": norm,
            "status": "HOLD",
            **common,
        })
    return fields


def _cell_text(cell: ET.Element) -> str:
    if cell.attrib.get("t") == "inlineStr":
        return "".join((el.text or "") for el in cell.findall(".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"))
    value = cell.find("m:v", NS)
    return (value.text or "") if value is not None else ""


def _col_letter(ref: str) -> str:
    return "".join(ch for ch in ref if ch.isalpha())


def _parse_xlsx(archive: zipfile.ZipFile, name: str) -> dict[str, list[dict]]:
    inner = zipfile.ZipFile(io.BytesIO(archive.read(name)))
    workbook = ET.fromstring(inner.read("xl/workbook.xml"))
    rels = ET.fromstring(inner.read("xl/_rels/workbook.xml.rels"))
    rid = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}
    sheets: dict[str, list[dict]] = {}
    for sheet in workbook.findall("m:sheets/m:sheet", NS):
        sheet_name = sheet.attrib.get("name") or ""
        target = rid[sheet.attrib[NSR + "id"]].lstrip("/")
        if not target.startswith("xl/"):
            target = "xl/" + target
        root = ET.fromstring(inner.read(target))
        rows = []
        for row in root.findall("m:sheetData/m:row", NS):
            cells = {}
            for cell in row.findall("m:c", NS):
                cells[_col_letter(cell.attrib.get("r", ""))] = _cell_text(cell)
            if any(cells.values()):
                rows.append(cells)
        sheets[sheet_name] = rows
    return sheets


def _parse_zip(path: Path) -> dict:
    sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
    archive = zipfile.ZipFile(path)
    names = archive.namelist()
    dd = _parse_xlsx(archive, "CKO-Data-Dictionary-v1.0.xlsx")
    fields = []
    for sheet in ("Foundation_Schemas", "Knowledge_Schemas"):
        for row in dd.get(sheet) or []:
            campo = (row.get("C") or "").strip()
            schema = (row.get("A") or "").strip()
            if campo and campo != "Campo":
                fields.append({
                    "sheet": sheet,
                    "schema": schema,
                    "campo": campo,
                    "tipo": (row.get("D") or "").strip() or None,
                })
    id_schemes = []
    for row in (dd.get("ID_Schemes") or [])[1:]:
        id_schemes.append({
            "tipo": row.get("B"),
            "formato": row.get("C"),
            "geracao": row.get("D"),
            "mutavel": row.get("E"),
            "quando": row.get("G"),
        })
    nf = _parse_xlsx(archive, "CKO_Matriz_Novas_Ferramentas.xlsx")
    tool_names = []
    started = False
    for row in nf.get("Matriz Novas Ferramentas") or []:
        title = (row.get("B") or "").strip()
        if title == "Ferramenta":
            started = True
            continue
        if started and title and title not in {"Legenda:"} and not title.startswith("Matriz"):
            tool_names.append(title)
    groups = []
    for source, book in (
        ("CKO_Matriz_Novas_Ferramentas.xlsx", nf),
        ("CKO_Matriz_Integracao.xlsx", _parse_xlsx(archive, "CKO_Matriz_Integracao.xlsx")),
    ):
        for row in (book.get("Transversal Calculadoras") or [])[2:]:
            grupo = (row.get("C") or "").strip()
            tools = (row.get("D") or "").strip()
            if grupo and tools:
                parts = [item.strip() for item in re.split(r",\s*", tools) if item.strip()]
                groups.append({"grupo": grupo, "ferramentas": parts, "source": source})
    tokens = []
    seen: set[str] = set()
    for group in groups:
        for token in group["ferramentas"]:
            key = token.lower()
            if key not in seen:
                seen.add(key)
                tokens.append(token)
    capabilities = json.loads(archive.read("CKO-21-Platform-Capabilities-Reconciliation-v1.0.json"))
    return {
        "zip_bytes": path.stat().st_size,
        "zip_sha256": sha256,
        "entry_count": len(names),
        "entries": names,
        "dictionary_sheets": list(dd),
        "dictionary_fields": fields,
        "id_schemes": id_schemes,
        "index_claimed_missing_sheets": ["Content_Schemas", "Meta_Schemas"],
        "new_tool_names": tool_names,
        "calculator_groups": groups,
        "calculator_tokens": tokens,
        "platform_capabilities": [
            {"id": item.get("id"), "name": item.get("name")}
            for item in (capabilities.get("platformCapabilities") or [])
        ],
        "capability_count": len(capabilities.get("platformCapabilities") or []),
        "md_blockers": [
            {"field_id": key, "field": name, "norm": norm, "status": "HOLD"}
            for key, name, norm in DRIVE_MD_BLOCKERS
        ],
    }


def _pilot_compare(tokens: list[str], tool_names: list[str]) -> list[dict]:
    blob = " | ".join(item.lower() for item in tokens + tool_names)
    explicit = {
        "gotejamento": (["Gotejamento"], "MATCH_NAME"),
        "meows": (["MEOWS", "Escala MEOWS"], "MATCH_NAME"),
        "dimensionamento": (["Dimensionamento", "Dimensionamento de Enfermagem"], "MATCH_NAME"),
        "simulado-tecnico": (["Simulado Tecnicos 1", "Simulado Tecnicos 2"], "COMPARE_NOT_1TO1"),
        "cinco-ts-pcr": (["Simulado PCR"], "COMPARE_NOT_1TO1"),
    }
    rows = []
    for slug, code in PILOT_CODES.items():
        path = TOOLS_DIR / f"{slug}.json"
        payload = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        names, relation = explicit[slug]
        hits = [name for name in names if name.lower() in blob]
        rows.append({
            "slug": slug,
            "code": payload.get("code") or code,
            "kind": payload.get("kind"),
            "in_data_tools": path.exists(),
            "drive_name_hits": hits,
            "relation": relation,
        })
    return rows


def compose_clinical_dict() -> dict:
    parsed = _parse_zip(ZIP_PATH) if ZIP_PATH.exists() else {}
    existing = _load(CATALOG_PATH)
    source = parsed or existing
    tokens = source.get("calculator_tokens") or []
    tool_names = source.get("new_tool_names") or []
    third_party = sorted(
        token for token in tokens
        if any(scale in token.lower() for scale in THIRD_PARTY_SCALE_TOKENS)
    )
    pilots = _pilot_compare(tokens, tool_names)
    fields = source.get("dictionary_fields") or []
    return {
        "business_key": "MD-CLIN-DICT-001",
        "uuid": None,
        "status": "SOURCE_DERIVED",
        "implemented": True,
        "publication": "HOLD",
        "assured": False,
        "promotes_to_md": False,
        "promoted_to_data_tools": False,
        "drive_file_id": DRIVE_FILE_ID,
        "title": DRIVE_TITLE,
        "parent_id": DRIVE_PARENT,
        "zip_bytes": source.get("zip_bytes") or existing.get("zip_bytes"),
        "zip_sha256": source.get("zip_sha256") or existing.get("zip_sha256"),
        "entry_count": source.get("entry_count") or existing.get("entry_count"),
        "entries": source.get("entries") or existing.get("entries") or [],
        "layer": "L10",
        "related_21_capabilities": source.get("platform_capabilities") or existing.get("related_21_capabilities") or [],
        "related_taxonomy": "REL-TAXONOMY-21-TO-44-001",
        "do_not_merge_21_with_44": True,
        "dictionary_sheets": source.get("dictionary_sheets") or existing.get("dictionary_sheets") or [],
        "index_claimed_missing_sheets": source.get("index_claimed_missing_sheets") or ["Content_Schemas", "Meta_Schemas"],
        "dictionary_field_count": len(fields) or existing.get("dictionary_field_count") or 0,
        "dictionary_fields": fields or existing.get("dictionary_fields") or [],
        "id_schemes": source.get("id_schemes") or existing.get("id_schemes") or [],
        "identity_conflict": {
            "drive_names_uuid_v4": True,
            "cko_operational": "CKO-BK-1",
            "uuid_generator": "UUIDv7 HOLD",
            "adopt_uuid_v4": False,
            "iso_8000_115_116": "NAMED_NOT_IMPLEMENTED",
            "clause_text": "CLAUSE_TEXT_UNAVAILABLE",
        },
        "new_tool_names": tool_names or existing.get("new_tool_names") or [],
        "new_tool_name_count": len(tool_names) or existing.get("new_tool_name_count") or 0,
        "calculator_tokens": tokens or existing.get("calculator_tokens") or [],
        "calculator_groups": source.get("calculator_groups") or existing.get("calculator_groups") or [],
        "pilot_codes": pilots,
        "third_party_scale_tokens": third_party or existing.get("third_party_scale_tokens") or [],
        "md_blockers": source.get("md_blockers") or [
            {"field_id": key, "field": name, "norm": norm, "status": "HOLD"}
            for key, name, norm in DRIVE_MD_BLOCKERS
        ],
        "rules": [
            "Namelist + nomes/códigos COMPARE. Sem unzip de PDF/DOCX como regra de produto.",
            "Não copiar CAL-/escalas de terceiros para data/tools.",
            "UUIDv4 do Drive não substitui CKO-BK-1.",
            "ISO 8000-115/116 e ABNT NBR nomeadas; cláusula NÃO ingerida.",
            "21 capabilities RELATED_TAXONOMY às 44 camadas; não mesclar.",
            "PNGs PILOT-CKO-INSULINA = SKIP_BINARY. Não ligar no chrome.",
        ],
        "evaluated_at": _now(),
    }


def evaluate_clinical_dict() -> dict:
    payload = compose_clinical_dict()
    _dump(CATALOG_PATH, payload)
    ipe = {
        "business_key": "IPE-CLIN-DICT-001",
        "uuid": None,
        "status": "SOURCE_DERIVED",
        "epistemic_status": "OBSERVED" if ZIP_PATH.exists() else payload.get("status"),
        "promotes_to_md": False,
        "quarantine": True,
        "drive_file_id": DRIVE_FILE_ID,
        "title": DRIVE_TITLE,
        "zip_bytes": payload.get("zip_bytes"),
        "zip_sha256": payload.get("zip_sha256"),
        "entry_count": payload.get("entry_count"),
        "dictionary_field_count": payload.get("dictionary_field_count"),
        "new_tool_name_count": payload.get("new_tool_name_count"),
        "pilot_codes": payload.get("pilot_codes"),
        "rule": payload["rules"][0],
        "md_ref": "MD-CLIN-DICT-001",
    }
    _dump(IPE_PATH, ipe)
    libmap_path = ROOT / "cko_md" / "library_api_map.json"
    libmap = _load(libmap_path)
    if libmap:
        drive = dict(libmap.get("drive") or {})
        drive["clinical_dict_zip_id"] = DRIVE_FILE_ID
        libmap["drive"] = drive
        sets = [item for item in (libmap.get("observed_sets") or []) if item.get("id") != "SET-CLIN-DICT-DRIVE"]
        sets.append({
            "id": "SET-CLIN-DICT-DRIVE",
            "count": payload.get("new_tool_name_count"),
            "kind": "drive_new_tool_names",
            "source": "IPE-CLIN-DICT-001",
            "official_api": "NOT_AN_API",
            "note": "Nomes na matriz de novas ferramentas. Códigos piloto CKO permanecem CALC-/SCALE-/GUIDE-/EXAM-*. Sem promover Braden.",
        })
        libmap["observed_sets"] = sets
        _dump(libmap_path, libmap)
    braden = (TOOLS_DIR / "braden.json").exists()
    return {
        "agent_id": "AG-CLIN-DICT",
        "class": "MD",
        "role": "CHECKER",
        "status": "HOLD",
        "publication": "HOLD",
        "wired_to_frontend": False,
        "promotes_to_md": False,
        "promoted_to_data_tools": False,
        "braden_in_data_tools": braden,
        "dictionary_field_count": payload.get("dictionary_field_count"),
        "new_tool_name_count": payload.get("new_tool_name_count"),
        "llm_used": False,
    }
