#!/usr/bin/env python3
"""Print ordered next steps to remediate platform pendencies (fail-closed)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "public" / "data"


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def main() -> None:
    pend = load("pendencies.json")
    items = pend["items"]
    by_id = {i["id"]: i for i in items}

    step1_ids = [
        "PEND-DIR-ASA-TOOL-CONFIG",
        "PEND-DIR-SLUG-braden",
        "PEND-DIR-SLUG-glasgow",
        "PEND-DIR-SLUG-morse",
        "PEND-DIR-I18N-da",
        "PEND-DIR-I18N-uk",
        "PEND-DIR-I18N-zh",
    ]
    step1_done = all(
        by_id.get(pid, {}).get("status") == "CREATED_IN_RUNTIME_HOLD" for pid in step1_ids
    )

    steps = [
        {
            "step": 1,
            "id": "STEP-PLATFORM-RUNTIME",
            "title": "Sanar runtime da plataforma (diretório)",
            "can_execute_now": not step1_done,
            "executed": step1_done,
            "closes_b9": False,
            "items": step1_ids,
            "item_status": {pid: by_id.get(pid, {}).get("status") for pid in step1_ids},
            "evidence_required": "HTML/JSON no reference-website; tool-config parseável; seletor i18n continua desligado",
        },
        {
            "step": 2,
            "id": "STEP-WAVE2-ROUTE-PRIVACY",
            "title": "Rotas institucionais, privacidade e formulários",
            "can_execute_now": False,
            "closes_b9": False,
            "blocked_by": ["PEND-W2-FORUM-CRITICAL", "PEND-W2-H09", "PEND-W2-H06"],
            "evidence_required": "runtime observado de form/privacy + remediação de fórum sem expor admin/RLS",
        },
        {
            "step": 3,
            "id": "STEP-A11Y-EMPIRICAL",
            "title": "Acessibilidade empírica (AT/humano)",
            "can_execute_now": False,
            "closes_b9": False,
            "blocked_by": ["PEND-W2-A11Y-EMPIRICAL", "UNK-A11Y-EMPIRICAL"],
            "evidence_required": "ensaio com leitor de tela + humano; estático já PASS",
        },
        {
            "step": 4,
            "id": "STEP-I18N-HUMAN",
            "title": "Rebase + revisão humana dos 30 locales",
            "can_execute_now": False,
            "closes_b9": False,
            "count": sum(1 for i in items if i["kind"] == "locale-cell" and i.get("status") != "PASS_STATIC_HOLD_RELEASE"),
            "evidence_required": "review_status=reviewed; não ativar seletor antes de 100% das chaves",
        },
        {
            "step": 5,
            "id": "STEP-P0-SEC",
            "title": "P0 — hardening SECURITY DEFINER + recertificação",
            "can_execute_now": False,
            "closes_b9": False,
            "blocked_by": ["PEND-P0-SEC", "PEND-UNK-SECURITY-RECERT"],
            "evidence_required": "patch + reperformance + recert PASS (hoje 1 FAIL)",
        },
        {
            "step": 6,
            "id": "STEP-RIGHTS",
            "title": "P1 — fechar cadeia de direitos (13 holds)",
            "can_execute_now": False,
            "closes_b9": False,
            "blocked_by": ["PEND-P1-RIGHTS", "PEND-PDF-RIGHTS-BUCKET"],
            "evidence_required": "RIGHTS_PROVENANCE por mídia/marca; sem isso não publicar",
        },
        {
            "step": 7,
            "id": "STEP-LEARN-OUTBOX",
            "title": "P1 — 201 reperformance + 296 outbox PENDING≠ACK",
            "can_execute_now": False,
            "closes_b9": False,
            "blocked_by": ["PEND-PDF-REPERF-BUCKET", "PEND-PDF-OUTBOX-BUCKET"],
            "evidence_required": "ownership + regression + ACK real; PENDING não é ACK",
        },
        {
            "step": 8,
            "id": "STEP-OBSERVED-RUNTIME",
            "title": "P0 — runtime observado (deploy/browser/mobile/perf)",
            "can_execute_now": False,
            "closes_b9": False,
            "blocked_by": ["PEND-P0-REL", "PEND-UNK-OBSERVED-RUNTIME", "PEND-UNK-NURSEPALM-OPS"],
            "evidence_required": "deployment + readback observados; Nurse-PaLM permanece NOT_ASSERTED até isso",
        },
        {
            "step": 9,
            "id": "STEP-B9-FANIN",
            "title": "Só então considerar B9 — ainda HOLD / NOT_RELEASED",
            "can_execute_now": False,
            "closes_b9": False,
            "blocked_by": ["PEND-BLOCK-B9", "PEND-PDF-HOLDS-BUCKET"],
            "evidence_required": "recert PASS + rights=0 + runtime observado; classificação técnica não vira homologação clínica",
        },
    ]

    created = sum(1 for i in items if i["status"] == "CREATED_IN_RUNTIME_HOLD")
    holdish = sum(1 for i in items if "HOLD" in str(i["status"]) or i["status"] in {"OPEN", "PENDING_REPERFORMANCE", "PENDING_NOT_ACK", "EXPLICIT_UNKNOWN", "NOT_ASSERTED", "NOT_RELEASED", "P0", "P1", "P2"})
    plan = {
        "id": "CKO-REMEDIATION-PLAN-1.0.0",
        "root": "policy-as-code",
        "release": "HOLD / NOT_RELEASED",
        "mutate_drive": False,
        "closes_b9": False,
        "progress": {
            "ledger_items": len(items),
            "created_in_runtime_hold": created,
            "still_open_or_hold": holdish,
            "kpis": pend["kpis"],
            "step1_executable": not step1_done,
            "step1_executed": step1_done,
            "b9": by_id.get("PEND-BLOCK-B9", {}).get("status"),
        },
        "steps": steps,
    }
    out = DATA / "remediation-plan.json"
    out.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("PROGRESSO DAS PENDÊNCIAS DA PLATAFORMA")
    print(f"ledger={len(items)}  criadas_no_runtime={created}  ainda_abertas_ou_hold={holdish}")
    print(f"B9={by_id.get('PEND-BLOCK-B9', {}).get('status')}  mutate_drive=false")
    print(f"holds={pend['kpis']['holds']} findings={pend['kpis']['findings_open']} reperf={pend['kpis']['pending_reperformance']} outbox={pend['kpis']['outbox_pending']} rights={pend['kpis']['rights_holds']}")
    print()
    for s in steps:
        if s.get("executed"):
            flag = "EXECUTADO (HOLD)"
        elif s["can_execute_now"]:
            flag = "EXECUTAR AGORA"
        else:
            flag = "BLOQUEADO"
        print(f"  {s['step']}. [{flag}] {s['title']}")
        if s.get("count"):
            print(f"     n={s['count']}")
        if s.get("item_status"):
            for pid, status in s["item_status"].items():
                print(f"     {pid}: {status}")
        print(f"     evidencia: {s['evidence_required']}")
    print()
    print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
