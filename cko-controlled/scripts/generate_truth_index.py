#!/usr/bin/env python3
"""Emit the observed Drive × Supabase catalog. Not a new architectural root.

Live MCP readback 2026-10-14. Drive was listed, never written.
Supabase was queried read-only. Documentado ≠ implantado ≠ ACTIVE ≠ RELEASE.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

GATE = Path(__file__).resolve().parents[1]
SITE = GATE.parent / "reference-website"
STAMP_NAME = "CKO-DRIVE-SUPABASE-TRUTH-INDEX-HOLD.json"

# Observation instant of the MCP readback that produced this catalog.
OBSERVED_AT = "2026-10-14T22:40:00Z"


def payload() -> dict:
    return {
        "id": "CKO-DRIVE-SUPABASE-TRUTH-INDEX-HOLD",
        "title": "Índice único observado Drive × Supabase",
        "kind": "observed_catalog",
        "version": "1.0.0",
        "observed_at": OBSERVED_AT,
        "connector": {
            "drive": "Google-drive MCP search_files + get_file_metadata, read-only",
            "supabase": "Supabase MCP list_organizations + list_projects + list_tables + execute_sql, read-only",
            "drive_writes": 0,
            "supabase_ddl": 0,
        },
        "new_architectural_root": False,
        "replaces_cko_md": False,
        "replaces_cko_reg": False,
        "replaces_source_registry": False,
        "replaces_universe_supabase_ref": False,
        "release": "HOLD / NOT_RELEASED",
        "b9": "HOLD / NOT_RELEASED",
        "release_allowed": False,
        "nursePalmOperational": "NOT_ASSERTED",
        "clinical_promotion": "DENIED",
        "calculators": "PAUSED",
        "scales": "PAUSED",
        "md_reg_complete": False,
        "observed_runtime": False,
        "closes_b9": False,
        "closes_rights_holds": False,
        "closes_clinical_homolog": False,
        "documentado_nao_e_implantado": True,
        "authority": {
            "note": "Identidade canónica continua nos pacotes CKO-MD e CKO-REG. Este índice só cataloga o que os conectores viram.",
            "canonical_ids": ["CKO-MD", "CKO-REG"],
            "packages": [
                {
                    "layer": "CKO-MD",
                    "drive_id": "18yyBskfiiKNAduwNmnp8vHO_09Qg_n-0",
                    "title": "CKO-MASTER-DATA-FINAL-CONTROLLED-v1.0.0.zip",
                    "kind": "application/zip",
                    "bytes": 3223,
                    "parentId": "1U38TaIimt61pwSJNvFBhb4NkR-EfCOJv",
                    "parent_title": "HORIZONTAL",
                    "viewUrl": "https://drive.google.com/file/d/18yyBskfiiKNAduwNmnp8vHO_09Qg_n-0/view",
                },
                {
                    "layer": "CKO-REG",
                    "drive_id": "1EO7Al3_UyEyD9RTQUagMsW4tZjGwmP9J",
                    "title": "CKO-REGULATORY-FINAL-CONTROLLED-v1.0.0.zip",
                    "kind": "application/zip",
                    "bytes": 2574,
                    "parentId": "1U38TaIimt61pwSJNvFBhb4NkR-EfCOJv",
                    "parent_title": "HORIZONTAL",
                    "viewUrl": "https://drive.google.com/file/d/1EO7Al3_UyEyD9RTQUagMsW4tZjGwmP9J/view",
                },
                {
                    "layer": "LYR-CLIN-SCALE-001",
                    "drive_id": "1UM29WGMSQwZPPtpAIMpMoZ4mj04kcGLE",
                    "title": "SCALES-SCORES-FINAL-CONTROLLED-v1.0.0.zip",
                    "kind": "application/zip",
                    "bytes": 3779,
                    "parentId": "1U38TaIimt61pwSJNvFBhb4NkR-EfCOJv",
                    "parent_title": "HORIZONTAL",
                    "runtime": "PAUSED",
                },
                {
                    "layer": "LYR-CLIN-CALC-001",
                    "drive_id": "1Oxb_DGzeNlS070s-_f4nuFGAchaXGHAg",
                    "title": "CLINICAL-CALCULATORS-FINAL-CONTROLLED-v1.0.0.zip",
                    "kind": "application/zip",
                    "bytes": 4508,
                    "parentId": "1YKnmVCjXv3nWoDTC8JCpiXpezoNZ60XJ",
                    "runtime": "PAUSED",
                },
                {
                    "layer": "LYR-PUB-001",
                    "drive_id": "1c3o8yuNMnjyzZI84kLdDqLwCGSJtRb-W",
                    "title": "PUBLICATION-RELEASE-FINAL-CONTROLLED-v1.0.0.zip",
                    "kind": "application/zip",
                    "bytes": 3489,
                    "parentId": "1Ul1GpfF8sRJj5Siu6upjv8pOuKNPFK8C",
                    "runtime": "HOLD / NOT_RELEASED",
                },
            ],
        },
        "drive": {
            "do_not_alter": True,
            "listing_complete": False,
            "my_drive_root": {
                "id": "0AFNnC8Uinv0BUk9PVA",
                "first_page_children": [
                    {"id": "1T0H-BHJCvKbBqMsguPb56GmGCOU7cPrQ", "title": "ImagensGItCE", "kind": "folder"},
                    {"id": "1MpmWQHA69XNHDLnVrz1f4DrN8Q2gPE9h", "title": "Outros", "kind": "folder"},
                    {
                        "id": "14em4ZC6l0cQlxb8Va36vYTH1IQLrGT8r",
                        "title": "Imagens da raiz — organizado em 2026-10-09",
                        "kind": "folder",
                    },
                    {
                        "id": "17Fq18tS6qhK4C0P8Ngh3rhDtNP3h2HCp",
                        "title": "Audit Educa — Consolidado",
                        "kind": "folder",
                    },
                    {
                        "id": "1l519_P-9o6bnQcItydKvEEDpEYeE8R8s",
                        "title": "extracao bruta Grok Bot Danadão",
                        "kind": "folder",
                    },
                ],
                "first_page_has_more": True,
                "note": "A segunda página do root devolveu argumento inválido. O root tem mais itens do que estes cinco.",
            },
            "nursing_root": {
                "id": "1c9vErI_It3XwzAcAFOnbxw9V0Mn6xfB9",
                "title": "Calculadoras-de-Enfermagem",
                "parentId": "0AFNnC8Uinv0BUk9PVA",
                "createdTime": "2026-01-24T21:58:53.541Z",
                "viewUrl": "https://drive.google.com/drive/folders/1c9vErI_It3XwzAcAFOnbxw9V0Mn6xfB9",
                "first_page_children": [
                    {"id": "15v8Nm6H7UxEinHp5W7FRVzZZ2Hi4Ds8S", "title": "00_HANDOFF"},
                    {
                        "id": "1sPNYlbAzKtyS0RNJoDpCEc3xgXR2JJma",
                        "title": "PILOTO_PIPELINE_DETERMINISTICO_COFEN_2026-10-10",
                    },
                    {"id": "1UbPlp0RMgOsw3Ey2V-lwpZvcGKfMcEy0", "title": "Corpus_Canonico_2026-10-03"},
                    {"id": "14stj3zygXRpqt0qJV-ZTI6X13JrJezxc", "title": "01_ORIGINAIS_USUARIO"},
                    {"id": "194ppG1qi_umpSocRyToxIbocpGlEzGw0", "title": "FEDERAL"},
                ],
                "first_page_has_more": True,
            },
            "controlled_spine": [
                {
                    "id": "1p4wnw98c9GkLlVDHtNKC_WZ4pKNhIbB4",
                    "title": "90_FINAL_CONTROLLED",
                    "parentId": "1c9vErI_It3XwzAcAFOnbxw9V0Mn6xfB9",
                },
                {
                    "id": "1U38TaIimt61pwSJNvFBhb4NkR-EfCOJv",
                    "title": "HORIZONTAL",
                    "parentId": "1p4wnw98c9GkLlVDHtNKC_WZ4pKNhIbB4",
                },
            ],
            "cko_named_folders_listed": 52,
            "cko_named_listing_complete": False,
            "duplicate_titles_seen": [
                "CKO Regulatory Project Finals - CLEAN v1.4.0 (várias pastas)",
                "cko-docsys-v1.5.0-governed-content",
                "CKO_GOVERNED_WAVE2_v1.0.0_STABLE",
                "CKO_CANONICAL_REGULATORY_ARCHITECTURE_v0.1.0",
                "assessment-cko",
            ],
            "snapshot_20260902": {
                "id": "ALL-SHA256-MANIFEST-20260902",
                "file_count": 449,
                "is_entire_drive": False,
            },
        },
        "supabase": {
            "organization": {
                "id": "fuffdjignqrldlxlguti",
                "name": "auditeduca's Org",
            },
            "mcp_projects_visible": [
                {
                    "id": "aevqrmkdhffmursdtcmo",
                    "name": "auditeduca's Project",
                    "region": "us-east-2",
                    "status": "ACTIVE_HEALTHY",
                    "created_at": "2026-06-14T21:09:07.734442Z",
                    "readable": True,
                },
                {
                    "id": "bsawvgyideporzailnys",
                    "name": "simulados-para-enfermagem",
                    "region": "sa-east-1",
                    "status": "INACTIVE",
                    "created_at": "2026-08-14T04:31:12.660485Z",
                    "readable": False,
                    "error": "Connection terminated due to connection timeout",
                },
            ],
            "documented_logical_ref": {
                "project_ref": "pgsybzggewhinaniybiy",
                "logical_root": "supabase://pgsybzggewhinaniybiy/cko_governance/controlled_artifacts/",
                "in_mcp_project_list": False,
                "note": "Continua no universe.json como localização lógica. Este run não viu o projecto.",
            },
            "site_forum_ref": {
                "project_ref": "asjkftjfbkuuhilnqonx",
                "used_by": "reference-website/*/forum-enfermagem.html",
                "in_mcp_project_list": False,
            },
            "live_readable": {
                "project_id": "aevqrmkdhffmursdtcmo",
                "schemas_non_system": [
                    "auth",
                    "cko_atlas_lab",
                    "cko_editorial",
                    "extensions",
                    "graphql",
                    "graphql_public",
                    "net",
                    "public",
                    "realtime",
                    "regulatory",
                    "storage",
                    "supabase_migrations",
                    "vault",
                ],
                "cko_governance_schema": False,
                "storage_buckets": 0,
                "tables": {
                    "cko_editorial.resources": {
                        "rows": 80,
                        "by_status": {"inventory": 80},
                        "by_type": {"calculator": 17, "scale": 63},
                    },
                    "cko_editorial.standards": {"rows": 1},
                    "cko_editorial.blueprints": {"rows": 0},
                    "cko_editorial.sections": {"rows": 0},
                    "cko_editorial.generation_jobs": {"rows": 0},
                    "cko_atlas_lab.canonical_atoms": {
                        "rows": 65200,
                        "publication_allowed_true": 0,
                        "publication_allowed_false": 65200,
                        "rls_enabled": False,
                    },
                    "cko_atlas_lab.ingest_log": {"rows": 1, "rls_enabled": False},
                    "cko_atlas_lab.ingest_parts": {"rows": 0, "rls_enabled": False},
                    "regulatory.schema_registry": {
                        "rows": 1,
                        "code": "CKO-REGULATORY",
                        "name": "CKO Regulatory Canonical Contract",
                        "version": "1.0.0",
                        "status": "active",
                    },
                    "regulatory.instruments": {"rows": 0},
                    "regulatory.provisions": {"rows": 0},
                    "regulatory.source_snapshots": {"rows": 0},
                    "regulatory.jurisdictions": {"rows": 0},
                    "public.provas_enfermagem": {"rows": 4},
                    "public.extracoes_enfermagem": {"rows": 4},
                    "public.questoes_enfermagem": {"rows": 26},
                },
            },
        },
        "conflicts": [
            {
                "id": "CONF-SUPABASE-REF-NOT-IN-MCP",
                "statement": "universe.json aponta pgsybzggewhinaniybiy; list_projects deste run não devolveu esse ref.",
            },
            {
                "id": "CONF-FORUM-REF-NOT-IN-MCP",
                "statement": "O fórum do site usa asjkftjfbkuuhilnqonx; esse ref também não está na lista MCP.",
            },
            {
                "id": "CONF-NO-CKO-GOVERNANCE-SCHEMA",
                "statement": "O logical_root documentado usa cko_governance; o projecto legível tem cko_editorial, cko_atlas_lab e regulatory, sem schema cko_governance.",
            },
            {
                "id": "CONF-EDITORIAL-INVENTORY-ONLY",
                "statement": "cko_editorial.resources tem 80 linhas, todas status=inventory. Zero published. Não fecha calculadoras nem escalas.",
            },
            {
                "id": "CONF-REGULATORY-EMPTY",
                "statement": "regulatory.schema_registry existe (1 linha CKO-REGULATORY 1.0.0); instruments, provisions e source_snapshots estão a 0.",
            },
            {
                "id": "CONF-ATLAS-NOT-PUBLISHABLE",
                "statement": "cko_atlas_lab.canonical_atoms tem 65200 linhas e publication_allowed=false em todas. RLS desligado nas 3 tabelas do schema.",
            },
        ],
        "unknowns": [
            {
                "id": "UNK-SUPABASE-PHYSICAL",
                "statement": "IDs Supabase documentados são localizações lógicas; este run não materializou pgsybzggewhinaniybiy nem asjkftjfbkuuhilnqonx.",
            },
            {
                "id": "UNK-DRIVE-LISTING-INCOMPLETE",
                "statement": "Paginação do root, de Calculadoras-de-Enfermagem e das pastas CKO não fechou. Este índice não é o Drive inteiro.",
            },
            {
                "id": "UNK-PITR",
                "statement": "Contagens SQL não equivalem a pg_dump/PITR com restore test.",
            },
            {
                "id": "UNK-DRIVE-OUTSIDE-SNAPSHOT",
                "statement": "O manifesto 2026-09-02 (449 ficheiros) não cobre as pastas de outubro (00_HANDOFF, Corpus_Canonico, FEDERAL, ImagensGItCE).",
            },
        ],
        "findings": [
            {
                "id": "FND-ATLAS-RLS-DISABLED",
                "severity": "critical",
                "statement": "cko_atlas_lab.canonical_atoms, ingest_log e ingest_parts estão sem RLS. Não foi aplicado ALTER TABLE neste run.",
            }
        ],
        "single_base": {
            "what_this_is": "Um único catálogo observado: autoridade (zips CKO-MD/CKO-REG) + Drive vivo + Supabase visível, com conflitos explícitos.",
            "what_this_is_not": [
                "Nova Pedra Fundamental",
                "Substituição de SOURCE_REGISTRY",
                "Projecto Supabase único implantado",
                "Release, ACTIVE operacional ou fecho de B9",
            ],
        },
    }


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def generate() -> dict:
    body = payload()
    raw = json.dumps(body, separators=(",", ":"), ensure_ascii=False, sort_keys=True).encode("utf-8")
    body["materialization"] = {
        "sha256": hashlib.sha256(raw).hexdigest(),
        "generated_by": "cko-controlled/scripts/generate_truth_index.py",
    }
    write_json(GATE / "public" / "data" / STAMP_NAME, body)
    write_json(SITE / "data" / "cko" / STAMP_NAME, body)
    return body


if __name__ == "__main__":
    out = generate()
    print("truth_index", out["id"], out["materialization"]["sha256"])
