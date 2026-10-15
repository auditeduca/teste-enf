#!/usr/bin/env python3
"""Emit the observed Kanban HOLD board.

This is a planning catalog, not Linear, not a 13th runtime page, not release.
Realtime here means: regenerate this stamp; the page re-reads it; an agent
rewrites the canvas on CI or a timer. No Drive/Supabase websocket.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

GATE = Path(__file__).resolve().parents[1]
SITE = GATE.parent / "reference-website"
STAMP_NAME = "CKO-KANBAN-HOLD.json"
RECORDED_AT = "2026-10-14T23:55:00Z"


def load(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def card(cid: str, title: str, note: str, evidence: str) -> dict:
    return {"id": cid, "title": title, "note": note, "evidence": evidence}


def payload() -> dict:
    universe = load(GATE / "public" / "data" / "universe.json")
    human = load(GATE / "public" / "data" / "human-decisions.json")
    truth = load(GATE / "public" / "data" / "CKO-DRIVE-SUPABASE-TRUTH-INDEX-HOLD.json")
    gov = load(GATE / "public" / "data" / "CKO-DIRECTORY-GOVERNANCE-HOLD.json")
    live = (truth.get("supabase") or {}).get("live_readable") or {}
    tables = live.get("tables") or {}
    atlas = tables.get("cko_atlas_lab.canonical_atoms") or {}
    editorial = tables.get("cko_editorial.resources") or {}
    human_ids = [item.get("id") for item in human.get("items") or []]
    rights = next((item for item in human.get("items") or [] if item.get("id") == "HOLD-HUMAN-RIGHTS-CHAIN"), {})

    columns = [
        {
            "id": "blocked",
            "title": "Bloqueado",
            "hint": "Não avança sem evidência nova ou decisão humana.",
            "items": [
                card(
                    "B9",
                    "B9 / release",
                    "HOLD / NOT_RELEASED. release_allowed = false. CI PASS não fecha B9.",
                    "universe.json · fail-closed.json",
                ),
                card(
                    "CLIN",
                    "Promoção clínica",
                    "DENIED. Calculadoras e escalas PAUSED. 0 UTC implementados.",
                    "CKO-POL-UT-001 · universal-tool.json",
                ),
                card(
                    "NP",
                    "Nurse-PaLM operacional",
                    "NOT_ASSERTED. Digital twin observed = false.",
                    "governance.json · HOLD-HUMAN-NURSEPALM-OPS",
                ),
                card(
                    "MDREG",
                    "2496 MD × 10913 REG",
                    "Universos classificados. Bindings não materializados. md_reg_complete = false.",
                    "md-reg-frontend.json",
                ),
            ],
        },
        {
            "id": "doing",
            "title": "Em curso",
            "hint": "Trabalho actual. Documentado ≠ implantado.",
            "items": [
                card(
                    "KANBAN",
                    "Quadro de planeamento HOLD",
                    "Este carimbo e a página cko-kanban.html. A página relê o JSON a cada 30 s. O canvas é reescrito no CI ou no timer de 10 min.",
                    "CKO-KANBAN-HOLD.json",
                ),
            ],
        },
        {
            "id": "cataloged",
            "title": "Catalogado HOLD",
            "hint": "Feito como catálogo. Não é ACTIVE nem RELEASE.",
            "items": [
                card(
                    "SOT",
                    "Índice observado Drive × Supabase",
                    "Uma base observada, não uma raiz nova. CKO-MD e CKO-REG intactos.",
                    truth.get("id") or "CKO-DRIVE-SUPABASE-TRUTH-INDEX-HOLD",
                ),
                card(
                    "GOV",
                    "Registo de governação do diretório",
                    "Escopo só deste diretório. Sem vigência automática. Sem IndiciumFIN.",
                    gov.get("id") or "CKO-DIRECTORY-GOVERNANCE-HOLD",
                ),
                card(
                    "PAGES",
                    "GitHub Pages HOLD",
                    "prepare_github_pages.py e canários /camadas/ + Aldrete no mapa. pageCount continua 12.",
                    "github-pages-hold-site.yml",
                ),
            ],
        },
        {
            "id": "human",
            "title": "Decisão humana",
            "hint": "O agente não fecha sozinho.",
            "items": [
                card(
                    "RIGHTS",
                    "13 RIGHTS_PROVENANCE",
                    rights.get("decision")
                    or "Bucket sem títulos no ledger. Proveniência por média em aberto.",
                    "HOLD-HUMAN-RIGHTS-CHAIN · UNK-RIGHTS-CHAIN",
                ),
                card(
                    "HOMOLOG",
                    "Homologação clínica",
                    "Continua DENIED. Classificação ≠ homologação operacional.",
                    "HOLD-HUMAN-CLINICAL-HOMOLOG",
                ),
                card(
                    "RLS",
                    "RLS do cko_atlas_lab",
                    "3 tabelas sem RLS. Átomos publication_allowed=false. Sem ALTER TABLE neste HOLD.",
                    "FND-ATLAS-RLS-DISABLED",
                ),
                card(
                    "LIN",
                    "Linear como quadro vivo",
                    "MCP Linear precisa de autenticação. Até lá o quadro é este carimbo + canvas.",
                    "namespaceStatus=needsAuth",
                ),
            ],
        },
    ]

    return {
        "id": "CKO-KANBAN-HOLD",
        "title": "Quadro Kanban do estado observado",
        "kind": "observed_kanban",
        "version": "0.1.0",
        "recorded_at": RECORDED_AT,
        "new_architectural_root": False,
        "replaces_cko_md": False,
        "replaces_cko_reg": False,
        "replaces_fail_closed": False,
        "replaces_source_registry": False,
        "replaces_linear": False,
        "promotes_policy": False,
        "assigns_vigencia": False,
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
        "drive_writes": 0,
        "supabase_ddl": 0,
        "this_page_is_not_a_13th_runtime_page": True,
        "runtime_pages_n": 12,
        "authority": {
            "note": "Identidade canónica continua em CKO-MD e CKO-REG. Este quadro só ordena o estado já observado.",
            "canonical_ids": ["CKO-MD", "CKO-REG"],
        },
        "refresh": {
            "mechanism": "stamp_reread",
            "page_poll_seconds": 30,
            "agent_timer_seconds": 600,
            "agent_ci": True,
            "websocket": False,
            "drive_websocket": False,
            "supabase_realtime": False,
            "linear_authenticated": False,
            "note": "A página relê este JSON. O canvas não faz rede. Linear continua needsAuth. Não há websocket ao Drive nem ao Supabase.",
        },
        "observed": {
            "universe_release": (universe.get("baseline") or {}).get("release") or "HOLD / NOT_RELEASED",
            "human_items_n": len(human_ids),
            "human_ids": human_ids,
            "truth_index_id": truth.get("id"),
            "governance_id": gov.get("id"),
            "supabase_live_ref": live.get("project_id") or "aevqrmkdhffmursdtcmo",
            "editorial_inventory": (editorial.get("by_status") or {}).get("inventory") or editorial.get("rows") or 80,
            "atlas_atoms": atlas.get("rows") or 65200,
            "atlas_publication_allowed_true": atlas.get("publication_allowed_true") or 0,
        },
        "columns": columns,
        "single_base": {
            "what_this_is": "Um único quadro HOLD do planeamento observado, com releitura do carimbo. Não é Linear autenticado.",
            "what_this_is_not": [
                "Websocket ao Drive ou ao Supabase",
                "Quadro Linear autenticado",
                "13.ª página institucional",
                "Release, ACTIVE operacional ou fecho de B9",
                "Promoção clínica ou Nurse-PaLM operacional",
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
        "generated_by": "cko-controlled/scripts/generate_kanban.py",
    }
    write_json(GATE / "public" / "data" / STAMP_NAME, body)
    write_json(SITE / "data" / "cko" / STAMP_NAME, body)
    return body


if __name__ == "__main__":
    out = generate()
    print("kanban", out["id"], out["materialization"]["sha256"])
