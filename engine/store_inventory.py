"""Drive / Supabase recover → compare → fronts plan.

MAKER (inventory) ≠ CHECKER (compare). Agents replay persisted MCP listings.
They do not call Drive/Supabase MCP, do not unzip mega dumps, and do not
promote HTML or invent schema.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from .paths import ROOT, TOOLS_DIR

DRIVE_PARENT_ID = "0AFNnC8Uinv0BUk9PVA"
MEGA_BYTES = 20_000_000

ALREADY_IN_CKO_IDS = {
    "1HEOd0k5i_iBtereT_ob_T1q8qI9MzKKU": "site-shell zip ingested to cko_inbox/drive/site_shell",
    "1LmEcVDsi2-MTUObRr7SIsSLgWWXeftEO": "locales.zip → MD-LOCALE-REG-001 SOURCE_DERIVED",
    "1tJ-AEv3_KpEQxNa3lMuY7A80skFtw4IK": "pages_full.zip inventory SOURCE_DERIVED; HTML not in data/tools",
    "1JmiD4RuQ9was5X5Vdzr8Al56OjPo5VfJ": "regulatory canonical delta already compared into GitHub MD/REG",
    "1BlJcgdqn93-JyVkPTw9-QmHnpjTpUH0x": "header logo copied as DS rendition",
    "1Tez0sazlumxO8EeapH30Xw6bF4KpGGnh": "footer logo copied as DS rendition",
}

QUARANTINE_IDS = {
    "1OUlaOO-hvxKk7IHoiBoKWuJRg26hP3uC": "Parecer 360 documental FAIL; 0/24 implementação evidenciada",
    "1JQEfMVlnlN1llmbAnvJOUb4WTs5U9skw": "braden.html Drive ≠ objeto MD",
}

CANDIDATE_GAP_IDS = {
    "1QGdvsnUhKSr2XTQ03sJzWowKp8lQUxZf": (
        "site-shell-completo.zip (296119 B) vs ingested site-shell 82453 B. COMPARE_ONLY; do not unzip into data/tools."
    ),
    "1E9OB0AKR0m2Hbeknf43Htwo-fXob6cP9": (
        "Vacinas zip PATTERN_CANDIDATE COMPARE. 15 CAL-VAC observados. Não copiar para data/tools."
    ),
    "1h4Lu0dDFoNNwJ-Q0e3FUCUYOksUhvIli": (
        "recuperado_insulina_consolidado.zip COMPARE_ONLY. Não unzip para data/tools. Sem inventar dose."
    ),
    "1Iucn9BiW9HQNOnyn5zpxyx5dSFupu-TR": (
        "recuperado_insulina_package.zip COMPARE_ONLY. Não unzip para data/tools. Sem inventar dose."
    ),
    "1mTJ0LQh2azuI3Nm0nnYbC6PUCXQIDG7D": (
        "guia-metadados-avancado HTML COMPARE. 32 critérios SEO ≠ 32 bibliotecas. CDN fonts FORBIDDEN; não copiar HTML para render/."
    ),
    "152MrVMQHG76G8nVN0wMMqedvTpHzfEB-": (
        "Dicionario clinico.zip COMPARE. Campos/códigos SOURCE_DERIVED. Sem promover escalas nem UUIDv4. PDF/DOCX não são cláusula."
    ),
}

FOLDER_NOTES = {
    "1b0ORWmyAaYk6b_bW112RVcuARtWwRd0T": (
        "Menu COMPARE (Auditoria-Menu-MetaDados). 151 destinos SOURCE_DERIVED no Drive. "
        "Não ligar mega-menu/Braden no chrome público."
    ),
    "1GRoNBScNVf4UsnHL0YSY17J6jsGLAyJW": (
        "OG cards Drive COMPARE. 151 WebP 1200×630 reivindicados. Não copiar cartões de /braden.html. "
        "CKO usa OG first-party default."
    ),
    "1dbC8M3TOAivaa9iwWRg0O6gI8ryKr0Qs": (
        "Passarinho-Vai-Lá COMPARE. Zips de brand/vila/design + imagens ChatGPT. Sem unzip mega; imagens SKIP."
    ),
    "1ZcE8AK0hVnrmMuuKISJ9t02t0w5QcJ0x": (
        "Classificações Médicas COMPARE. Pastas ICPC-2/UMLS/UCUM/LOINC/RxNorm/MeSH. Zip 99 MB SKIP. Sem dump licenciado."
    ),
    "1UpgQAuPUvF_8iGY31-k2W7EXGcY1S7eQ": (
        "Pasta anvisa FOLDER_OBSERVED. Filhos listing vazio neste ciclo. Sem unzip dump de medicamentos."
    ),
    "1_SQqd5Xx_6seeOklBPqfWTW2juEnwQJw": (
        "Pasta anvisa-open-data FOLDER_OBSERVED. Filhos listing vazio neste ciclo. Sem dump."
    ),
    "1PC-6ZLimaugUTvgBj7tEDWvmf5oGvmMc": (
        "Pasta anvisa_open_data_agents FOLDER_OBSERVED. Filhos listing vazio neste ciclo. Sem promover agentes Drive."
    ),
}

PII_IDS = {
    "1hGjFWE2ZuX0roApGgL-qoyNRNb8KLTLkuT6Zh1l28AU": "spreadsheet title is an email; do not project",
}

SKIP_UNZIP_IDS = {
    "1TPmIPtXeMbsjJEiG_19W5bt8JZPJMhDF": (
        "CKO_Medicamentos_ANVISA_Completo.zip listing COMPARE. Não unzip. "
        "Claimed 17231 na descrição Drive = SOURCE_DERIVED, não população hashed."
    ),
}


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


def _int_size(value) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def classify_drive_file(item: dict) -> dict:
    """Deterministic class. Never promotes to MD."""
    file_id = str(item.get("id") or "")
    title = str(item.get("title") or "")
    mime = str(item.get("mimeType") or "")
    size = _int_size(item.get("fileSize") or item.get("bytes"))
    record = {
        "id": file_id,
        "title": "[REDACTED_PII]" if file_id in PII_IDS else title,
        "mimeType": mime,
        "bytes": size or None,
        "promotes_to_md": False,
    }
    if file_id in PII_IDS:
        record.update({
            "classification": "SKIP_PII",
            "reason": PII_IDS[file_id],
        })
        return record
    if file_id in ALREADY_IN_CKO_IDS:
        record.update({
            "classification": "ALREADY_IN_CKO",
            "reason": ALREADY_IN_CKO_IDS[file_id],
        })
        return record
    if file_id in QUARANTINE_IDS:
        record.update({
            "classification": "DISCOVERY_QUARANTINE",
            "reason": QUARANTINE_IDS[file_id],
        })
        return record
    if file_id in CANDIDATE_GAP_IDS:
        record.update({
            "classification": "CANDIDATE_GAP",
            "reason": CANDIDATE_GAP_IDS[file_id],
            "action": "COMPARE_ONLY",
        })
        return record
    if file_id in SKIP_UNZIP_IDS:
        record.update({
            "classification": "SKIP_BINARY_DUMP",
            "reason": SKIP_UNZIP_IDS[file_id],
            "action": "COMPARE_ONLY",
        })
        return record
    if mime == "application/vnd.google-apps.folder":
        record.update({
            "classification": "FOLDER_OBSERVED",
            "reason": FOLDER_NOTES.get(file_id) or "Pasta observada. Filhos HTML não são identidade MD.",
        })
        return record
    if (
        mime.startswith("image/")
        or title.startswith("ChatGPT Image")
        or "Gemini_Generated_Image" in title
    ):
        record.update({
            "classification": "SKIP_BINARY_DUMP",
            "reason": "Imagem/gerado. Não é objeto canônico.",
        })
        return record
    if size >= MEGA_BYTES:
        record.update({
            "classification": "SKIP_BINARY_DUMP",
            "reason": f"Binário ≥ {MEGA_BYTES} bytes. Não unzip neste ciclo.",
        })
        return record
    lowered = title.lower()
    if lowered.endswith(".html") or mime == "text/html" or "lei8080" in lowered:
        record.update({
            "classification": "DISCOVERY_QUARANTINE",
            "reason": "HTML Drive. Ads/escalas não publicadas não entram em data/tools.",
        })
        return record
    if "parecer-360" in lowered or "parecer_360" in lowered:
        record.update({
            "classification": "DISCOVERY_QUARANTINE",
            "reason": "Workbook Parecer 360. GAP-PARECER-360 QUARANTINE.",
        })
        return record
    if any(token in lowered for token in ("nifs", "nkos", "nurse_palm", "nurse-palm")):
        record.update({
            "classification": "DISCOVERY_QUARANTINE",
            "reason": "Dump NIFS/NKOS. IDs LEG.BR.* não substituem business_key CKO.",
        })
        return record
    record.update({
        "classification": "DISCOVERY_QUARANTINE",
        "reason": "Drive = descoberta. RECOVER → COMPARE → GAP ONLY antes de rebuild.",
    })
    return record


def _github_md_keys() -> list[str]:
    keys: list[str] = []
    md_dir = ROOT / "cko_md"
    if not md_dir.exists():
        return keys
    for path in sorted(md_dir.glob("*.json")):
        payload = _load(path)
        key = payload.get("business_key")
        if key:
            keys.append(str(key))
        for group in (
            payload.get("instruments"),
            payload.get("resources"),
            payload.get("agencies"),
            payload.get("living_gaps"),
        ):
            for item in group or []:
                nested = item.get("business_key") or item.get("id")
                if nested:
                    keys.append(str(nested))
    return sorted(set(keys))


def _pilot_slugs() -> list[str]:
    return sorted(path.stem for path in TOOLS_DIR.glob("*.json"))


def inventory_drive() -> dict:
    """AG-INVENTORY-DRIVE — classify persisted Drive listing. No MCP, no unzip."""
    raw_path = ROOT / "cko_inbox" / "extracted" / "drive_listing_raw.json"
    dest = ROOT / "cko_inbox" / "extracted" / "drive_inventory.json"
    raw = _load(raw_path)
    files = [classify_drive_file(item) for item in (raw.get("files") or [])]
    local_dirs = []
    drive_inbox = ROOT / "cko_inbox" / "drive"
    if drive_inbox.exists():
        for child in sorted(drive_inbox.iterdir()):
            if child.is_dir():
                local_dirs.append(child.name)
    counts = Counter(item["classification"] for item in files)
    payload = {
        "business_key": "IPE-DRIVE-INV-001",
        "uuid": None,
        "status": "SOURCE_DERIVED",
        "epistemic_status": "OBSERVED",
        "parent_id": raw.get("parent_id") or DRIVE_PARENT_ID,
        "captured_at": raw.get("captured_at") or _now(),
        "classified_at": _now(),
        "promotes_to_md": False,
        "quarantine": True,
        "pagination": raw.get("pagination") or {},
        "folders": raw.get("folders") or [],
        "subfolder_html": raw.get("subfolder_html") or {},
        "image_dump": raw.get("image_dump") or {},
        "local_inbox_dirs": local_dirs,
        "files": files,
        "counts": dict(counts),
        "population": len(files),
        "rule": "Drive/NIFS = descoberta/quarentena. HTML e mega-zip não viram golden MD.",
    }
    _dump(dest, payload)
    return {
        "agent_id": "AG-INVENTORY-DRIVE",
        "class": "DISCOVERY",
        "role": "MAKER",
        "status": "OBSERVED" if files else "EVIDENCE_PENDING",
        "promotes_to_md": False,
        "writes_to": "cko_inbox/extracted/drive_inventory.json",
        "population": len(files),
        "counts": dict(counts),
        "pagination_complete": bool((raw.get("pagination") or {}).get("complete")),
        "do_not_unzip": True,
    }


def inventory_supabase() -> dict:
    """AG-INVENTORY-SUPABASE — persisted projects/functions. Schema stays EVIDENCE_PENDING."""
    raw_path = ROOT / "cko_inbox" / "extracted" / "supabase_listing_raw.json"
    dest = ROOT / "cko_inbox" / "extracted" / "supabase_inventory.json"
    raw = _load(raw_path)
    mcp = _load(ROOT / "cko_inbox" / "extracted" / "supabase_mcp_probe.json")
    sql = dict(raw.get("sql") or {})
    schema_status = sql.get("schema_status") or "EVIDENCE_PENDING"
    projects = list(raw.get("projects") or [])
    mcp_ref = mcp.get("project_ref")
    if mcp_ref and not any(item.get("ref") == mcp_ref for item in projects):
        projects.append({
            "ref": mcp_ref,
            "name": mcp.get("project_name") or "UNKNOWN",
            "region": mcp.get("region") or "UNKNOWN",
            "status": mcp.get("project_status") or "OBSERVED_GATEWAY",
            "sql": mcp.get("sql_status") or "MCP permission denied",
        })
    if mcp:
        sql["mcp"] = {
            "read_only": mcp.get("read_only"),
            "project_ref": mcp_ref,
            "get_project": "PERMISSION_DENIED",
            "list_tables": "PERMISSION_DENIED",
            "auth_settings_http": ((mcp.get("probes") or {}).get("auth_v1_settings_publishable") or {}).get("http_status"),
            "config_paths": mcp.get("mcp_config_paths") or [],
        }
    payload = {
        "business_key": "IPE-SUPABASE-INV-001",
        "uuid": None,
        "status": "SOURCE_DERIVED",
        "epistemic_status": "OBSERVED" if projects else "EVIDENCE_PENDING",
        "schema": schema_status,
        "promotes_to_md": False,
        "do_not_invent": [
            "table names",
            "column lists",
            "172 entities",
            "row counts",
        ],
        "projects": projects,
        "sql": sql,
        "mcp": {
            "ref": "IPE-SUPABASE-MCP-001",
            "read_only": True,
            "url": mcp.get("mcp_url"),
            "oauth_this_agent": "PERMISSION_DENIED",
        },
        "edge_functions": raw.get("edge_functions") or [],
        "project_url": raw.get("project_url"),
        "rule": "SQL 28P01 / MCP -32600 → schema UNKNOWN. Edge function slugs are names only; source not fetched; LLM gateway HOLD. Publishable key not committed.",
        "classified_at": _now(),
    }
    _dump(dest, payload)
    return {
        "agent_id": "AG-INVENTORY-SUPABASE",
        "class": "DISCOVERY",
        "role": "MAKER",
        "status": "EVIDENCE_PENDING" if schema_status == "EVIDENCE_PENDING" else "OBSERVED",
        "promotes_to_md": False,
        "writes_to": "cko_inbox/extracted/supabase_inventory.json",
        "schema": schema_status,
        "projects_observed": len(payload["projects"]),
        "edge_functions_observed": len(payload["edge_functions"]),
        "sql_blocked": True,
        "llm_gateway": "HOLD",
    }


def compare_stores() -> dict:
    """AG-COMPARE-STORES — Drive/Supabase vs GitHub MD/REG. Gaps only."""
    dest = ROOT / "cko_inbox" / "extracted" / "compare_stores.json"
    drive = _load(ROOT / "cko_inbox" / "extracted" / "drive_inventory.json")
    supabase = _load(ROOT / "cko_inbox" / "extracted" / "supabase_inventory.json")
    method = _load(ROOT / "cko_md" / "operating_method.json")
    md_keys = _github_md_keys()
    pilots = _pilot_slugs()
    drive_files = drive.get("files") or []
    candidate_gaps = [item for item in drive_files if item.get("classification") == "CANDIDATE_GAP"]
    quarantine = [item for item in drive_files if item.get("classification") == "DISCOVERY_QUARANTINE"]
    already = [item for item in drive_files if item.get("classification") == "ALREADY_IN_CKO"]
    parecer = next((item for item in drive_files if item.get("id") == "1OUlaOO-hvxKk7IHoiBoKWuJRg26hP3uC"), None)
    living = method.get("living_gaps") or []
    gaps = []
    for item in living:
        gaps.append({
            "id": item.get("id"),
            "status": item.get("status"),
            "source": "MD-OPS-METHOD-001",
            "reason": item.get("reason") or item.get("evidence"),
        })
    if candidate_gaps:
        gaps.append({
            "id": "GAP-DRIVE-SHELL-COMPLETO",
            "status": "COMPARE_ONLY",
            "source": "IPE-DRIVE-INV-001",
            "reason": candidate_gaps[0].get("reason"),
        })
    if supabase.get("schema") == "EVIDENCE_PENDING":
        if not any(item.get("id") == "GAP-SUPABASE-READ" for item in gaps):
            gaps.append({
                "id": "GAP-SUPABASE-READ",
                "status": "BLOCKED",
                "source": "IPE-SUPABASE-INV-001",
                "reason": "MCP Cursor JSON read_only DOCUMENTADO. OAuth deste agente: permission denied no ref yskgekcjzndptzmnjfke. 28P01 no ref aevqrmkdhffmursdtcmo. Schema not observed.",
            })
    payload = {
        "business_key": "IPE-COMPARE-STORES-001",
        "uuid": None,
        "status": "SOURCE_DERIVED",
        "epistemic_status": "OBSERVED",
        "promotes_to_md": False,
        "compared_at": _now(),
        "github_md_keys": md_keys,
        "github_md_key_count": len(md_keys),
        "pilots_in_data_tools": pilots,
        "braden_in_data_tools": (TOOLS_DIR / "braden.json").exists(),
        "drive": {
            "population": drive.get("population") or 0,
            "already_in_cko": len(already),
            "quarantine": len(quarantine),
            "candidate_gap": len(candidate_gaps),
            "parecer_360": "QUARANTINE" if parecer else "NOT_IN_LISTING",
        },
        "supabase": {
            "schema": supabase.get("schema") or "EVIDENCE_PENDING",
            "projects": len(supabase.get("projects") or []),
        },
        "gaps": gaps,
        "rule": "Não promover Drive/Supabase a identidade. Chat não é fonte. Reconstrução é último recurso.",
    }
    _dump(dest, payload)
    return {
        "agent_id": "AG-COMPARE-STORES",
        "class": "MONITORING",
        "role": "CHECKER",
        "status": "OBSERVED",
        "promotes_to_md": False,
        "writes_to": "cko_inbox/extracted/compare_stores.json",
        "gap_count": len(gaps),
        "braden_in_data_tools": payload["braden_in_data_tools"],
        "supabase_schema": payload["supabase"]["schema"],
    }


def plan_fronts() -> dict:
    """AG-PLAN-FRONTS — living fronts bound to existing agents. Not a waterfall."""
    dest = ROOT / "cko_md" / "fronts_plan.json"
    compare = _load(ROOT / "cko_inbox" / "extracted" / "compare_stores.json")
    method = _load(ROOT / "cko_md" / "operating_method.json")
    drive = _load(ROOT / "cko_inbox" / "extracted" / "drive_inventory.json")
    supabase = _load(ROOT / "cko_inbox" / "extracted" / "supabase_inventory.json")
    gap_by_id = {item.get("id"): item for item in (compare.get("gaps") or [])}
    fronts = [
        {
            "id": "F1",
            "name": "Inventário Drive",
            "status": "REGISTERED",
            "agents": ["AG-INVENTORY-DRIVE", "AG-COMPARE-STORES"],
            "gap": "GAP-DRIVE-INVENTORY",
            "action": "Classificar listing persistido. Não unzip Abelha/grok/pages_full/nkos.",
            "population": drive.get("population"),
            "pagination_complete": bool((drive.get("pagination") or {}).get("complete")),
        },
        {
            "id": "F2",
            "name": "Leitura Supabase",
            "status": "HOLD",
            "agents": ["AG-INVENTORY-SUPABASE"],
            "gap": "GAP-SUPABASE-READ",
            "action": "Dono HOLD. MCP .cursor/mcp.json read_only DOCUMENTADO. Schema SQL EVIDENCE_PENDING. Sem coletar SUPABASE_DB_PASSWORD. Sem list_tables. Sem inventar 172 entidades.",
            "schema": supabase.get("schema") or "EVIDENCE_PENDING",
            "owner_decision": "HOLD",
        },
        {
            "id": "F3",
            "name": "Catálogo federal incremental",
            "status": "REGISTERED",
            "agents": ["AG-PROBE-CONGRESS-API", "AG-FETCH-FEDERAL-LEGISLATION", "AG-LIBRARY-CATALOG"],
            "gap": "GAP-DEC-7508",
            "action": "Só LCP/lei/DEC-n. Não misturar portaria de órgão neste tubo.",
        },
        {
            "id": "F4",
            "name": "PGDADOS restante",
            "status": "REGISTERED",
            "agents": ["AG-FETCH-GOV-SOURCES", "AG-LIBRARY-CATALOG"],
            "gap": "GAP-PGDADOS",
            "action": "Parte 3 PDF e cartilhas 4–5 EVIDENCE_PENDING. ABNT/mwpt ignorado.",
        },
        {
            "id": "F5",
            "name": "Atos de órgão",
            "status": "HOLD",
            "agents": ["AG-FETCH-REGULATED"],
            "gap": "GAP-ORGAN-ACTS",
            "action": "Portaria MS / Resolução COFEN = segundo tubo. Não ingestão em massa via Congresso.",
        },
        {
            "id": "F6",
            "name": "COFEN REST",
            "status": "EVIDENCE_PENDING",
            "agents": ["AG-API-PROBE", "AG-FETCH-REGULATED"],
            "gap": "GAP-COFEN-REST",
            "action": "HTML observado. REST sem HTTP 200. Não inventar adapter. COREN CLOSED_NOT_OBSERVED.",
        },
        {
            "id": "F7",
            "name": "Dimensionamento",
            "status": "HOLD",
            "agents": ["AG-LINK-MD"],
            "gap": "GAP-DIMENSIONAMENTO",
            "action": "Cinco pilotos. Dimensionamento permanece HOLD.",
        },
        {
            "id": "F8",
            "name": "Parecer 360",
            "status": "QUARANTINE",
            "agents": ["AG-INVENTORY-DRIVE", "AG-COMPARE-STORES"],
            "gap": "GAP-PARECER-360",
            "action": "Não promover workbook a golden MD.",
        },
        {
            "id": "F9",
            "name": "L30/L40 pages_full + institucionais",
            "status": "REGISTERED",
            "agents": ["AG-PARSE-PAGES-FULL", "AG-COMPARE-STORES"],
            "gap": "GAP-L30-L40-PAGES-FULL",
            "action": "COMPARE stems (index/missão/política/termos + calculadoras) vs 5 pilotos. Catálogo de pendências REG (MD-PAGES-REG-PEND-001). Sem unzip em data/tools.",
        },
        {
            "id": "F10",
            "name": "L60 bibliotecas + vacinas",
            "status": "COMPARE_ONLY",
            "agents": ["AG-INVENTORY-DRIVE", "AG-LIBRARY-CATALOG"],
            "gap": "GAP-L60-LIBRARIES",
            "owner_decision": "COMPARE_ACCEPTED",
            "action": (
                "COMPARE_ACCEPTED: persistir 11 device + 24 objetos clínicos + 15 CAL-VAC. "
                "Claimed 32 permanece EVIDENCE_PENDING. Sem inventar 32 adapters; "
                "sem promover CAL-VAC/Braden/NNN; sem somar conjuntos heterogéneos."
            ),
        },
        {
            "id": "F11",
            "name": "L80/L90/L100 API onde possível",
            "status": "EVIDENCE_PENDING",
            "agents": ["AG-API-PROBE"],
            "gap": "GAP-L80-L120-API",
            "action": "Probe só HTTP 200. Sem dump LOINC/UMLS/classificacoes_medicas.zip.",
        },
        {
            "id": "F12",
            "name": "NANDA/NIC/NOC rights-safe",
            "status": "REGISTERED",
            "agents": ["AG-PLAN-FRONTS", "AG-RIGHTS-BIND"],
            "gap": "GAP-NNN-RIGHTS",
            "action": "Dono B: identidade+código+deep-link. Sem texto NANDA/NIC/NOC. nanda-00046.json permanece QUARANTINE.",
            "owner_decision": "B",
        },
        {
            "id": "F13",
            "name": "L140/L150 API + pesquisa",
            "status": "REGISTERED",
            "agents": ["AG-API-PROBE", "AG-LIBRARY-CATALOG"],
            "gap": "GAP-L140-L150-API-RESEARCH",
            "action": "Crossref/NCBI observados como busca. Resposta API ≠ canônico sem snapshot/hash/MD/REG.",
        },
        {
            "id": "F14",
            "name": "L150/L160 guia por conceito",
            "status": "REGISTERED",
            "agents": ["AG-CONTENT-CURRICULUM"],
            "gap": "GAP-L150-L160-CONCEPT-RENDERER",
            "action": "Um conceito → uma identidade → renderer. LLM FORBIDDEN no canônico.",
        },
        {
            "id": "F15",
            "name": "ISO 8000 + PGDADOS explícito",
            "status": "REGISTERED",
            "agents": ["AG-ISO8000-PROFILE", "AG-LIBRARY-CATALOG"],
            "gap": "GAP-ISO8000-PGDADOS",
            "action": "URL PGDADOS /pgdados persistida no perfil ISO. Não substitui cláusula licenciada. Sem certificação.",
        },
        {
            "id": "F16",
            "name": "Escalas: busca PubMed/COFEN/OMS",
            "status": "REGISTERED",
            "agents": ["AG-API-PROBE", "AG-RIGHTS-BIND"],
            "gap": "GAP-SCALE-LITERATURE",
            "action": "Busca bibliográfica HTTP. SciELO 403 EVIDENCE_PENDING. Não republicar Braden/Norton/Glasgow.",
        },
        {
            "id": "F17",
            "name": "pages_full catálogo de pendências REG",
            "status": "REGISTERED",
            "agents": ["AG-PARSE-PAGES-FULL", "AG-CONTENT-CURRICULUM"],
            "gap": "GAP-PAGES-REG-PEND",
            "action": "Owner override: inventário demonstra gaps MD+REG+rights. Extração clínica em massa FORBIDDEN.",
        },
        {
            "id": "F18",
            "name": "L280/L290/L300 OG+SEO+JSON-LD",
            "status": "COMPARE_ONLY",
            "agents": ["AG-INVENTORY-DRIVE"],
            "gap": "GAP-OG-SEO-JSONLD",
            "action": "Drive 151 cards COMPARE. OG first-party 1200×630 no site piloto. JSON-LD WebSite/Organization. Sem MedicalOrganization.",
        },
        {
            "id": "F19",
            "name": "Menu Drive COMPARE",
            "status": "COMPARE_ONLY",
            "agents": ["AG-INVENTORY-DRIVE"],
            "gap": "GAP-MENU-DRIVE",
            "action": "151 destinos no menu.json Drive. Não promover mega-menu/Braden ao chrome público.",
        },
        {
            "id": "F20",
            "name": "L310 i18n WHO/OMS",
            "status": "REGISTERED",
            "agents": ["AG-WHO-I18N", "AG-ISO8000-PROFILE"],
            "gap": "GAP-WHO-I18N",
            "action": "Dono APPROVED chave who.en+local.pt-BR nos 5 pilotos. translation_gate HOLD. Seletor não ligado. Sem dump ICD/ICNP/GHO. Sem inventar strings EN.",
            "owner_decision": "APPROVED",
        },
        {
            "id": "F21",
            "name": "Dicionário clínico Drive + códigos piloto",
            "status": "COMPARE_ONLY",
            "agents": ["AG-CLIN-DICT", "AG-ISO8000-PROFILE"],
            "gap": "GAP-CLIN-DICT",
            "action": "Dono enviou Dicionario clinico.zip (já observado). Sheets Content_Schemas/Meta_Schemas MISSING. Só FLD-* existentes. Sem Braden. UUIDv4 não adotado.",
            "owner_decision": "RECEIVED",
        },
        {
            "id": "F22",
            "name": "MD+REG 44 camadas faseadas",
            "status": "REGISTERED",
            "agents": ["AG-LAYER-PHASE", "AG-ISO8000-PROFILE"],
            "gap": "GAP-LAYER-MD-REG",
            "action": "Envelope MD+REG completo nas 44 (P0–P5). EXISTS≠POPULATED≠ASSURED. Sem certificação. Sem Braden.",
        },
        {
            "id": "F23",
            "name": "UCP v2.0 COMPARE",
            "status": "COMPARE_ONLY",
            "agents": ["AG-UCP-V2-COMPARE", "AG-PLAN-FRONTS"],
            "gap": "GAP-UCP-V2",
            "action": "11 schemas 2020-12 + 2 CSV COMPARE. Não copiar para schemas/. CONTROLLED_CANDIDATE ≠ ASSURED. Modelos/piloto do registo EVIDENCE_PENDING.",
        },
        {
            "id": "F24",
            "name": "L70 API ANVISA + dump Drive",
            "status": "COMPARE_ONLY",
            "agents": ["AG-L70-ANVISA-COMPARE", "AG-API-PROBE", "AG-INVENTORY-DRIVE"],
            "gap": "GAP-L70-ANVISA",
            "action": (
                "Usar Portal APIs ANVISA. SPA HTML 200 ≠ REST JSON de produto. "
                "Zip Drive 59.8 MB SKIP_BINARY_DUMP; 17231 não verificado. "
                "openFDA não substitui bula. Sem data/tools/insulina.json."
            ),
        },
    ]
    for front in fronts:
        living = gap_by_id.get(front["gap"]) or {}
        if living.get("status"):
            front["gap_status"] = living["status"]
    payload = {
        "business_key": "MD-FRONTS-PLAN-001",
        "uuid": None,
        "status": "DOCUMENTADO",
        "implemented": True,
        "publication": "HOLD",
        "assured": False,
        "method_ref": "MD-OPS-METHOD-001",
        "layer_intent_ref": "MD-LAYER-INTENT-001",
        "nnn_rights_ref": "MD-NNN-RIGHTS-001",
        "owner_unblock_ref": "MD-OWNER-UNBLOCK-001",
        "library_api_map_ref": "MD-LIB-API-MAP-001",
        "concept_renderer_ref": "MD-CONCEPT-RENDER-001",
        "method": method.get("method") or "RECOVER → COMPARE → GAP ONLY → REPERFORM → CLOSE",
        "plan_policy": "Plano vivo em JSON. Agentes atuam nas frentes; não criam autoridade nem identidade REG.",
        "maker_neq_checker": True,
        "llm_authority": False,
        "fronts": fronts,
        "next_executable": [
            "F1 replay offline a cada extract",
            "F2 HOLD: MCP read_only DOCUMENTADO; schema SQL EVIDENCE_PENDING; sem senha neste ciclo",
            "F9 COMPARE pages_full vs pilotos; catálogo de pendências REG; sem unzip",
            "F10 COMPARE_ACCEPTED 11+24+15; claimed 32 EVIDENCE_PENDING; sem promover CAL-VAC",
            "F12 NNN OPT-B REGISTERED: códigos+deep-link; texto licenciado withheld",
            "F15 PGDADOS /pgdados explícito no perfil ISO (não certificação)",
            "F18 OG first-party LinkedIn; 151 cards Drive não copiados",
            "F20 chave who.en+local.pt-BR APPROVED; seletor HOLD; sem dump",
            "F21 zip recebido COMPARE; sheets Content_Schemas/Meta_Schemas MISSING",
            "F22 envelope MD+REG das 44 camadas P0–P5; sem claim 100% completo",
            "F23 UCP v2 COMPARE; sem promover schemas 2020-12",
            "F24 L70 Portal APIs ANVISA COMPARE; dump Drive não unzip; REST JSON HOLD até credencial",
            "F3/F4 só com evidência HTTP/Congress já no tubo",
        ],
        "updated_at": _now(),
    }
    _dump(dest, payload)
    method["fronts_plan_ref"] = "MD-FRONTS-PLAN-001"
    method["stores"] = method.get("stores") or {}
    if "drive" in method["stores"]:
        method["stores"]["drive"]["inventory_ref"] = "IPE-DRIVE-INV-001"
        method["stores"]["drive"]["status"] = "OBSERVED"
    if "supabase" in method["stores"]:
        method["stores"]["supabase"]["inventory_ref"] = "IPE-SUPABASE-INV-001"
        method["stores"]["supabase"]["schema"] = supabase.get("schema") or "EVIDENCE_PENDING"
        method["stores"]["supabase"]["edge_functions_observed"] = [
            item.get("slug") for item in (supabase.get("edge_functions") or [])
        ]
    extra = [
        {
            "id": "GAP-DRIVE-INVENTORY",
            "status": "REGISTERED",
            "reason": "Listing Drive classificado. Paginação de imagens ChatGPT incompleta. Não promover HTML.",
        },
        {
            "id": "GAP-DRIVE-SHELL-COMPLETO",
            "status": "COMPARE_ONLY",
            "reason": "site-shell-completo.zip maior que o zip já ingerido. COMPARE_ONLY; sem unzip em data/tools.",
        },
        {
            "id": "GAP-L30-L40-PAGES-FULL",
            "status": "REGISTERED",
            "reason": "pages_full+locales já inventariados. COMPARE stems institucionais e calculadoras vs 5 pilotos. HTML ≠ MD.",
        },
        {
            "id": "GAP-L60-LIBRARIES",
            "status": "COMPARE_ONLY",
            "reason": (
                "Owner COMPARE_ACCEPTED. Observados 11 device + 24 tipos clínicos + 15 CAL-VAC. "
                "Claimed 32 APIs permanece EVIDENCE_PENDING. Sem promover CAL-VAC/Braden/NNN."
            ),
        },
        {
            "id": "GAP-L80-L120-API",
            "status": "EVIDENCE_PENDING",
            "reason": "API só com HTTP 200 JSON. LOINC/UMLS/classificacoes_medicas.zip não entram no GitHub.",
        },
        {
            "id": "GAP-NNN-RIGHTS",
            "status": "REGISTERED",
            "reason": "Owner B: identity catalog codes+URI+deep-link. Labels withheld. nanda-00046.json Drive QUARANTINE.",
        },
        {
            "id": "GAP-L140-L150-API-RESEARCH",
            "status": "REGISTERED",
            "reason": "Crossref e NCBI E-utilities como busca. Não republicar abstract como canônico.",
        },
        {
            "id": "GAP-L150-L160-CONCEPT-RENDERER",
            "status": "REGISTERED",
            "reason": "Guia/questão por conceito único via renderer. LLM FORBIDDEN. Currículo já DOCUMENTADO.",
        },
        {
            "id": "GAP-ISO8000-PGDADOS",
            "status": "REGISTERED",
            "reason": "PGDADOS /pgdados é a referência BR explícita do perfil ISO 8000 CKO. Não substitui cláusula ISO.",
        },
        {
            "id": "GAP-SCALE-LITERATURE",
            "status": "REGISTERED",
            "reason": "PubMed/COFEN/OMS busca. SciELO EVIDENCE_PENDING. Instrumento de terceiros não republicado.",
        },
        {
            "id": "GAP-PAGES-REG-PEND",
            "status": "REGISTERED",
            "reason": "1516 HTML demonstram pendências REG. Extração em massa de fórmula clínica FORBIDDEN.",
        },
        {
            "id": "GAP-OG-SEO-JSONLD",
            "status": "COMPARE_ONLY",
            "reason": "W3C não ingerido. eMAG/LBI nomeados. OG default first-party. 151 cards Drive não copiados.",
        },
        {
            "id": "GAP-MENU-DRIVE",
            "status": "COMPARE_ONLY",
            "reason": "Menu Drive 151 destinos. Chrome público permanece 5 pilotos. Sem Braden no header.",
        },
        {
            "id": "GAP-WHO-I18N",
            "status": "REGISTERED",
            "reason": "Owner APPROVED who.en+local.pt-BR. Seletor não ligado. Variantes pt-PT/pt-AO HOLD. Sem dump ICD/ICNP/GHO. translation_gate HOLD.",
        },
        {
            "id": "GAP-CLIN-DICT",
            "status": "COMPARE_ONLY",
            "reason": "Owner sent Dicionario clinico.zip. Sheets Content_Schemas/Meta_Schemas MISSING. Só FLD existentes. Sem promover Braden. UUIDv4 não adotado.",
        },
        {
            "id": "GAP-LAYER-MD-REG",
            "status": "REGISTERED",
            "reason": "Envelope MD+REG das 44 faseado. EXISTS≠POPULATED≠ASSURED. publication HOLD. Sem Braden.",
        },
        {
            "id": "GAP-UCP-V2",
            "status": "COMPARE_ONLY",
            "reason": "UCP v2.0 CONTROLLED_CANDIDATE. 11 schemas hashed. Não copiar para schemas/. Modelos/piloto ausentes EVIDENCE_PENDING.",
        },
        {
            "id": "GAP-L70-ANVISA",
            "status": "COMPARE_ONLY",
            "reason": (
                "Portal APIs ANVISA HTML 200. REST JSON de produto NOT_OBSERVED sem Gov.br Client ID/Secret. "
                "Dump Drive 59.8 MB SKIP_BINARY_DUMP. Claimed 17231 EVIDENCE_PENDING. openFDA ≠ bula ANVISA."
            ),
        },
    ]
    living_gaps = list(method.get("living_gaps") or [])
    by_id = {item.get("id"): item for item in living_gaps}
    for item in extra:
        by_id[item["id"]] = item
    method["living_gaps"] = list(by_id.values())
    method["layer_intent_ref"] = "MD-LAYER-INTENT-001"
    method["nnn_rights_ref"] = "MD-NNN-RIGHTS-001"
    method["owner_unblock_ref"] = "MD-OWNER-UNBLOCK-001"
    method["library_api_map_ref"] = "MD-LIB-API-MAP-001"
    method["concept_renderer_ref"] = "MD-CONCEPT-RENDER-001"
    _dump(ROOT / "cko_md" / "operating_method.json", method)
    return {
        "agent_id": "AG-PLAN-FRONTS",
        "class": "ORCHESTRATOR",
        "role": "MD",
        "status": "DOCUMENTADO",
        "promotes_to_md": False,
        "writes_to": "cko_md/fronts_plan.json",
        "front_count": len(fronts),
        "publication": "HOLD",
        "blocked": [],
        "hold": ["F2", "F5", "F7", "F8"],
    }
