#!/usr/bin/env python3
"""Extract and bind every known CKO/NIFS/NKP API as POLICY_MASTER HOLD.

Sources: shared DeepSeek/API-first conversation, LYR-SEC control hashes,
live Supabase readback, NIFS-800 catalogs, nkp_api.py, site admin.
MD/REG completion is the next task — not asserted here.
DOCUMENTADO ≠ IMPLANTADO ≠ ASSURED. Release remains HOLD / NOT_RELEASED.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cko_policy_contract import CASCADE, FAIL_CLOSED_ID, POLICY_MASTER_ID, specialize

GATE = Path(__file__).resolve().parents[1]
REPO = GATE.parent
SITE = REPO / "reference-website"
NKP_API = REPO / "NIFS" / "reference-scripts" / "nkp_api.py"
NIFS_REST = REPO / "NIFS" / "800-INTEROPERABILITY" / "800-05-rest.md"
NIFS_FHIR = REPO / "NIFS" / "800-INTEROPERABILITY" / "800-01-fhir.md"
SEC_MANIFEST = SITE / "data" / "cko" / "layers" / "LYR-SEC-001" / "package" / "FINAL_MANIFEST.json"

OUT_POLICY = GATE / "public" / "policies" / "api-catalog.json"
OUT_SITE = SITE / "data" / "cko" / "api-catalog.json"
OUT_CASCADE = SITE / "data" / "cko" / "cascade" / "api-catalog.json"

SHARED_DEEPSEEK = [
    {
        "slug": "cko-deepseek-gateway",
        "version": "v4",
        "hash": "f7d2a0936ca358c4b904120066fff85ac75e823d0d5d92844e6ee27d1a69f7b0",
        "role": "gateway",
        "canonical_authority": False,
        "note": "Tarefas estruturadas; resultado exige validação downstream",
    },
    {
        "slug": "cko-deepseek-regulatory-extract",
        "version": "v7",
        "hash": "40203dd95ff3b79b8e935723207371d7b8c82e773cabfc5f0850a1ab822e7942",
        "role": "regulatory_extractor",
        "canonical_authority": False,
        "next_task": "MD_REG_COMPLETE",
        "note": "Prioritário para corpus normativo; MD/REG completa na próxima tarefa",
    },
    {
        "slug": "cko-deepseek-health",
        "version": "NOT_IN_LAYER_HASH",
        "hash": None,
        "role": "health",
        "canonical_authority": False,
        "note": "HTTP 200 isolado não prova configured=true",
    },
]

LIVE_READBACK = [
    {"slug": "extrair-questoes-enfermagem", "version": 2, "project": "aevqrmkdhffmursdtcmo"},
    {"slug": "recover-cko-artifact", "version": 1, "project": "aevqrmkdhffmursdtcmo"},
    {"slug": "invoke-recover-cko-artifact-once", "version": 3, "project": "aevqrmkdhffmursdtcmo"},
    {"slug": "santos-study-renderer", "version": 3, "project": "aevqrmkdhffmursdtcmo"},
    {"slug": "santos-study-export-once", "version": 2, "project": "aevqrmkdhffmursdtcmo"},
    {"slug": "cko-deepseek-gateway", "version": 1, "project": "aevqrmkdhffmursdtcmo", "drift": "layer_hash_is_v4"},
    {"slug": "calculadoras-smart-deepseek-gateway", "version": 1, "project": "aevqrmkdhffmursdtcmo"},
]

ALTERNATE = [
    {"id": "NIFS-800-04", "name": "SMART on FHIR", "status": "DESIGN_HOLD"},
    {"id": "NIFS-800-06", "name": "GraphQL", "status": "DESIGN_HOLD"},
    {"id": "NIFS-800-07", "name": "gRPC", "status": "DESIGN_HOLD"},
    {"id": "NIFS-800-08", "name": "Webhooks", "status": "DESIGN_HOLD"},
    {"id": "NIFS-900-08", "name": "API Gateway", "status": "DESIGN_HOLD"},
]


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_nkp_routes() -> list[dict]:
    text = NKP_API.read_text(encoding="utf-8")
    rows = []
    for method, path in re.findall(r"@app\.(get|post|put|delete|patch)\(\"([^\"]+)\"\)", text):
        if path == "/":
            continue
        rows.append(
            {
                "method": method.upper(),
                "path": path,
                "source": "NIFS/reference-scripts/nkp_api.py",
                "operational": "NOT_ASSERTED",
                "release": "HOLD / NOT_RELEASED",
            }
        )
    return rows


def parse_nifs_rest() -> list[dict]:
    text = NIFS_REST.read_text(encoding="utf-8")
    rows = []
    for method, path, purpose in re.findall(r"\| (GET|POST|PUT|DELETE) \| (`[^`]+`|/api/[^|]+) \| ([^|]+) \|", text):
        path = path.strip().strip("`")
        rows.append(
            {
                "method": method,
                "path": path,
                "purpose": purpose.strip(),
                "source": "NIFS-800-05",
                "operational": "NOT_ASSERTED",
                "clinical": "PAUSED" if "/calculators" in path else "NOT_ASSERTED",
                "modality": "MUST_NOT" if "/calculators" in path and "calculate" in path else "HOLD",
            }
        )
    return rows


def parse_fhir() -> list[dict]:
    text = NIFS_FHIR.read_text(encoding="utf-8")
    rows = []
    for path, methods, purpose in re.findall(r"\| (`/fhir/[^`]+`) \| ([^|]+) \| ([^|]+) \|", text):
        rows.append(
            {
                "path": path.strip("`"),
                "methods": methods.strip(),
                "purpose": purpose.strip(),
                "source": "NIFS-800-01",
                "operational": "NOT_ASSERTED",
            }
        )
    return rows


def edge_from_manifest() -> list[dict]:
    manifest = json.loads(SEC_MANIFEST.read_text(encoding="utf-8"))
    rows = []
    for key, digest in (manifest.get("current_control_hashes") or {}).items():
        slug, _, version = key.partition("@")
        rows.append(
            {
                "slug": slug,
                "version": version or "unknown",
                "hash": digest,
                "source": "LYR-SEC-001/FINAL_MANIFEST",
                "operational": "NOT_ASSERTED",
            }
        )
    return rows


def family(
    family_id: str,
    name: str,
    policy_type: str,
    objective: str,
    deny_if: str,
    layers: list[str],
    authority: list[str],
    extra: dict,
) -> dict:
    policy_id = f"POL-CKO-{family_id}-1.0.0"
    body = {
        "id": policy_id,
        "kind": "policy-as-code",
        "family_id": family_id,
        "document_id": family_id,
        "document_version": "1.0.0",
        "policy_type": policy_type,
        "name": name,
        "parent": POLICY_MASTER_ID,
        "specializes": POLICY_MASTER_ID,
        "inherits": [FAIL_CLOSED_ID, POLICY_MASTER_ID],
        "starts_at": "policy-as-code",
        "status": "CONTROLLED_API_HOLD",
        "active": False,
        "implantado": False,
        "assured": False,
        "release": "HOLD / NOT_RELEASED",
        "release_allowed": False,
        "published": False,
        "operational": "NOT_ASSERTED",
        "modality": "MUST_NOT",
        "blocking_inspect": False,
        "blocking_release": True,
        "contract": specialize(
            policy_id=policy_id,
            policy_name=name,
            policy_type="API",
            objective=objective,
            deny_if=deny_if,
            layers=layers,
            authority=authority,
            extra_identity={"family_id": family_id},
        ),
    }
    body.update(extra)
    return body


def build() -> dict:
    nkp = parse_nkp_routes()
    rest = parse_nifs_rest()
    fhir = parse_fhir()
    edge = edge_from_manifest()
    families = [
        family(
            "API-SHARED-DEEPSEEK",
            "APIs da conversa compartilhada DeepSeek/API-first",
            "SHARED_CONVERSATION",
            "bind_shared_deepseek_apis_without_claiming_operational",
            "nursePalm == ASSERTED or deepseek.result == canonical",
            ["CKO-REG", "LYR-SEC-001"],
            ["CKO — Bootstrap DeepSeek API Worker v1.0.0", "CKO — START HERE Multiagent Shared Blackboard v1.0.1"],
            {
                "endpoints": SHARED_DEEPSEEK,
                "endpoint_count": len(SHARED_DEEPSEEK),
                "precedence": ["SPECIALIZED_GOVERNED_EDGE", "CKO_DEEPSEEK_GATEWAY", "DIRECT_PROVIDER_CALL"],
                "supabase_project_shared": "pgsybzggewhinaniybiy",
                "supabase_project_readable": "aevqrmkdhffmursdtcmo",
            },
        ),
        family(
            "API-EDGE-CONTROLLED",
            "Edge functions com hash de controlo LYR-SEC-001",
            "EDGE_HASH",
            "keep_layer_hashed_edge_functions_hold",
            "edge.canonical_promotion == true",
            ["LYR-SEC-001"],
            ["ART-H12-SECURITY-FINAL-CONTROLLED"],
            {"endpoints": edge, "endpoint_count": len(edge)},
        ),
        family(
            "API-EDGE-LIVE-READBACK",
            "Readback das Edge Functions no projeto Supabase acessível",
            "LIVE_READBACK",
            "document_live_readback_without_promoting_canonical",
            "live.ACTIVE == platform.ACTIVE",
            ["LYR-SEC-001"],
            ["Supabase list_edge_functions", "NO_FACT_WITHOUT_EVIDENCE"],
            {
                "endpoints": LIVE_READBACK,
                "endpoint_count": len(LIVE_READBACK),
                "note": "ACTIVE no projeto acessível ≠ ACTIVE da plataforma CKO. Gateway live v1 ≠ hash v4.",
            },
        ),
        family(
            "API-NIS-REST",
            "Catálogo REST NIFS-800-05",
            "NIS_DESIGN",
            "keep_nifs_rest_design_hold_calculators_paused",
            "POST /api/v1/calculators/*/calculate without PAUSED",
            ["LYR-CLIN-CALC-001", "LYR-TERM-001"],
            ["NIFS-800-05"],
            {"endpoints": rest, "endpoint_count": len(rest)},
        ),
        family(
            "API-NIS-FHIR",
            "Catálogo FHIR NIFS-800-01",
            "NIS_DESIGN",
            "keep_fhir_design_hold",
            "fhir.operational == ASSERTED",
            ["LYR-TERM-001", "CKO-REG"],
            ["NIFS-800-01"],
            {"endpoints": fhir, "endpoint_count": len(fhir)},
        ),
        family(
            "API-NIS-ALTERNATE",
            "GraphQL, gRPC, Webhooks, SMART, Gateway",
            "NIS_DESIGN",
            "keep_alternate_interop_design_hold",
            "alternate.implantado == true",
            ["LYR-RUN-001"],
            ["NIFS-800-04", "NIFS-800-06", "NIFS-800-07", "NIFS-800-08", "NIFS-900-08"],
            {"endpoints": ALTERNATE, "endpoint_count": len(ALTERNATE)},
        ),
        family(
            "API-NKP-ADMIN",
            "NKP admin API extraída de nkp_api.py",
            "ADMIN_CODE",
            "bind_nkp_admin_routes_as_hold_not_production",
            "nkp_api.production == true",
            ["LYR-RUN-001"],
            ["NIFS/reference-scripts/nkp_api.py"],
            {"endpoints": nkp, "endpoint_count": len(nkp)},
        ),
        family(
            "API-SITE-ADMIN",
            "Admin API do site hospedado",
            "SITE_ADMIN",
            "keep_site_admin_api_hold",
            "adminApi.unauthenticated == true and action == mutate",
            ["LYR-SEC-001"],
            ["reference-website/js/admin-engine.js"],
            {
                "endpoints": [
                    {
                        "method": "POST",
                        "path": "/api/functions/adminApi",
                        "source": "reference-website/js/admin-engine.js",
                        "operational": "NOT_ASSERTED",
                    }
                ],
                "endpoint_count": 1,
            },
        ),
        family(
            "API-MD-REG-NEXT",
            "MD/REG via API — próxima tarefa",
            "NEXT_TASK",
            "forbid_claiming_md_reg_complete_in_this_catalog",
            "md_reg_complete == true",
            ["CKO-MD", "CKO-REG"],
            ["CKO-MD", "CKO-REG", "cko-deepseek-regulatory-extract"],
            {
                "endpoints": [
                    {
                        "slug": "cko-deepseek-regulatory-extract",
                        "next_task": "MD_REG_COMPLETE",
                        "classified_md_fields": 2496,
                        "classified_reg_bindings": 10913,
                        "materialized_field_bindings": False,
                        "corpus_denominator": 0,
                    }
                ],
                "endpoint_count": 1,
                "md_reg_complete": False,
                "note": "Classificado ≠ extraído clause-level ≠ implantado. Completar MD/REG é a próxima tarefa.",
            },
        ),
    ]
    endpoint_total = sum(f["endpoint_count"] for f in families)
    return {
        "id": "POL-CKO-API-CATALOG-1.0.0",
        "kind": "policy-as-code",
        "mode": "fail-closed",
        "root": False,
        "starts_at": "policy-as-code",
        "parent": POLICY_MASTER_ID,
        "specializes": POLICY_MASTER_ID,
        "inherits": [FAIL_CLOSED_ID, POLICY_MASTER_ID],
        "document_id": "CKO-POL-API-001",
        "document_version": "1.0.0",
        "status": "CONTROLLED_API_HOLD",
        "frozen": True,
        "active": False,
        "cascade": CASCADE,
        "release": "HOLD / NOT_RELEASED",
        "release_allowed": False,
        "published": False,
        "operational": "NOT_ASSERTED",
        "canonical_promotion": False,
        "documentado": True,
        "implantado": False,
        "assured": False,
        "new_architectural_root": False,
        "family_count": len(families),
        "endpoint_total": endpoint_total,
        "md_reg_complete": False,
        "md_reg_next_task": True,
        "families": families,
        "rule": "Todas as APIs da conversa compartilhada, NIFS-800, NKP e readback live estão extraídas e ligadas a policy-as-code. Nenhuma é operacional canónica. MD/REG completa na próxima tarefa.",
        "evaluation": {
            "verdict": "API_HOLD_EXTRACTED_NOT_OPERATIONAL",
            "documentado": True,
            "implantado": False,
            "assured": False,
            "active": False,
            "md_reg_complete": False,
            "findings": [
                {
                    "id": "API-F-SHARED-BOUND",
                    "severity": "HOLD",
                    "text": "cko-deepseek-gateway / regulatory-extract / health ligados. Gateway não tem autoridade canónica.",
                },
                {
                    "id": "API-F-VERSION-DRIFT",
                    "severity": "HOLD",
                    "text": "Hash LYR-SEC gateway@v4 ≠ readback live gateway@v1 no projeto acessível. Drift ≠ promoção.",
                },
                {
                    "id": "API-F-MD-REG-NEXT",
                    "severity": "HOLD",
                    "text": "MD 2496 e REG 10913 permanecem classificados. Completar extração/amarração MD/REG é a próxima tarefa.",
                },
            ],
        },
    }


def generate() -> dict:
    policy = build()
    if policy["family_count"] != 9:
        raise SystemExit(f"expected 9 API families, got {policy['family_count']}")
    if policy["md_reg_complete"] is not False:
        raise SystemExit("md_reg_complete must stay false")
    for dest in (OUT_POLICY, OUT_SITE, OUT_CASCADE):
        write_json(dest, policy)
    return policy


if __name__ == "__main__":
    doc = generate()
    print(
        f"wrote {OUT_POLICY} families={doc['family_count']} endpoints={doc['endpoint_total']} status={doc['status']}"
    )
