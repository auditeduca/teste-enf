#!/usr/bin/env python3
"""Emit platform-closure policy-as-code and bind the 9 human holds.

Each hold specializes POLICY_MASTER_CONTRACT. None are ACTIVE.
DOCUMENTADO ≠ IMPLANTADO ≠ ASSURED. Release remains HOLD / NOT_RELEASED.
"""
from __future__ import annotations

import json
from pathlib import Path

GATE = Path(__file__).resolve().parents[1]
SITE = GATE.parent / "reference-website"

OUT_POLICY = GATE / "public" / "policies" / "platform-closure.json"
OUT_SITE = SITE / "data" / "cko" / "platform-closure.json"
OUT_CASCADE = SITE / "data" / "cko" / "cascade" / "platform-closure.json"
OUT_LEDGER = GATE / "public" / "data" / "human-decisions.json"
OUT_LEDGER_SITE = SITE / "data" / "cko" / "human-decisions.json"
OUT_LEDGER_CASCADE = SITE / "data" / "cko" / "cascade" / "human-decisions.json"
OUT_RIGHTS_FORM = GATE / "public" / "data" / "CKO-RIGHTS-DECISION-FORM-HOLD.json"
OUT_RIGHTS_FORM_SITE = SITE / "data" / "cko" / "CKO-RIGHTS-DECISION-FORM-HOLD.json"

POLICY_MASTER_ID = "POL-CKO-POLICY-MASTER-CONTRACT-1.0.0"
FAIL_CLOSED_ID = "POL-CKO-FAIL-CLOSED-1.0.0"
CASCADE = [
    "policy-as-code",
    "schemas",
    "graph-constraints",
    "CI-gates",
    "runtime-assertions",
    "automatic-evidence",
]
MASTER_FIELDS = [
    "IDENTITY",
    "AUTHORITY",
    "INTENT",
    "APPLICABILITY",
    "SCOPE",
    "SUBJECT",
    "MODALITY",
    "CONDITIONS",
    "CONSTRAINTS",
    "DECISION",
    "OUTCOME",
    "ENFORCEMENT",
    "CONTRACT",
    "IMPLEMENTATION",
    "TESTS",
    "CI_GATES",
    "RUNTIME_ASSERTIONS",
    "OBSERVABILITY",
    "EVIDENCE",
    "PROVENANCE",
    "GOVERNANCE",
    "EXCEPTIONS",
    "DEPENDENCIES",
    "VERSIONING",
    "LIFECYCLE",
    "CHANGE_IMPACT",
    "READINESS",
    "ASSURANCE",
]

EXISTING = [
    {"id": "POL-CKO-FAIL-CLOSED-1.0.0", "role": "root", "document_id": "FAIL_CLOSED"},
    {"id": POLICY_MASTER_ID, "role": "contract", "document_id": "POLICY_MASTER_CONTRACT"},
    {"id": "POL-CKO-MD-REG-FRONTEND-1.0.0", "role": "frontend", "document_id": "CKO-MD-REG"},
    {"id": "POL-CKO-UNIVERSAL-TOOL-1.3.0", "role": "application", "document_id": "CKO-POL-UT-001"},
    {"id": "POL-CKO-VISUAL-ASSET-1.0.0", "role": "designos", "document_id": "CKO-VAS-001"},
    {"id": "POL-CKO-LAYER-CATALOG-1.0.0", "role": "layers", "document_id": "CKO-POL-LYR-001"},
    {"id": "POL-CKO-EXTRACTION-1.0.0", "role": "extraction", "document_id": "CKO-POL-EXTRACT-001"},
    {"id": "POL-CKO-API-CATALOG-1.0.0", "role": "apis", "document_id": "CKO-POL-API-001"},
    {"id": "POL-CKO-GOVERNED-FABRIC-1.0.0", "role": "fabric", "document_id": "CKO-POL-FABRIC-001"},
]

HOLDS = [
    {
        "hold_id": "HOLD-HUMAN-CLINICAL-HOMOLOG",
        "policy_id": "POL-CKO-HOLD-CLINICAL-HOMOLOG-1.0.0",
        "policy_type": "RELEASE",
        "name": "Homologação clínica operacional",
        "decision": "Homologação clínica operacional",
        "next_human": "Homologação clínica operacional permanece DENIED (2026-09-05); nova assinatura só se reabrir",
        "code_progress": "Humano 2026-09-05: DENIED. CKO-POL-UT-001 especializa o molde; templates BOUND_HOLD; calculadoras PAUSED; promoção DENIED",
        "modality": "MUST_NOT",
        "objective": "block_clinical_promotion_until_human_homologation",
        "deny_if": "clinical_promotion != DENIED or calculators != PAUSED",
        "layers": ["LYR-CLIN-CALC-001", "CKO-MD", "CKO-REG"],
        "authority": ["CKO-REG", "CKO-MD", "CKO-POL-UT-001"],
        "count": None,
        "recorded_human": {
            "verdict": "DENIED",
            "recorded_at": "2026-09-05T20:21:00Z",
            "source": "user_message",
            "unpauses_calc_scales": False,
            "closes_b9": False,
        },
    },
    {
        "hold_id": "HOLD-HUMAN-RIGHTS-CHAIN",
        "policy_id": "POL-CKO-HOLD-RIGHTS-1.0.0",
        "policy_type": "GOVERNANCE",
        "name": "Cadeia de direitos de publicação",
        "decision": "Cadeia de direitos de publicação (13 holds)",
        "next_human": "Humano 2026-09-05: aprovado (bucket). Contagem 13 e títulos ausentes permanecem; proveniência por mídia/marca não fechada",
        "code_progress": "Humano 2026-09-05: aprovado. 13 rights holds explícitos; títulos NÃO extraídos; rights_holds continua 13; sem assets novos",
        "modality": "MUST_NOT",
        "objective": "block_publication_while_rights_holds_open",
        "deny_if": "rights_holds > 0 and action == publish",
        "layers": ["CKO-REG", "LYR-MEDIA-001"],
        "authority": ["Lei 9.610/1998", "CKO-REG"],
        "count": 13,
        "recorded_human": {
            "verdict": "APPROVED",
            "mapped_choice": "CLEAR",
            "recorded_at": "2026-09-05T20:58:00Z",
            "source": "user_message",
            "text": "aprovado",
            "scope": "bucket_and_named_adjacent",
            "closes_rights_count_13": False,
            "provenance_per_media": False,
            "closes_b9": False,
        },
    },
    {
        "hold_id": "HOLD-HUMAN-A11Y-EMPIRICAL",
        "policy_id": "POL-CKO-HOLD-A11Y-1.0.0",
        "policy_type": "ACCESSIBILITY",
        "name": "Acessibilidade empírica B6.3",
        "decision": "Acessibilidade empírica B6.3",
        "next_human": "Auditoria B6.3 em browsers e dispositivos reais",
        "code_progress": "Skip links e :focus-visible; identidade v10 no cluster; escalas sem hero navy local",
        "modality": "MUST_NOT",
        "objective": "forbid_claiming_B6.3_pass_without_empirical_audit",
        "deny_if": "a11y.empirical == PASS without human audit",
        "layers": ["LYR-UI-001", "LYR-DS-001"],
        "authority": ["WCAG-2.2", "B6.3"],
        "count": None,
    },
    {
        "hold_id": "HOLD-HUMAN-NURSEPALM-OPS",
        "policy_id": "POL-CKO-HOLD-NURSEPALM-1.0.0",
        "policy_type": "AI",
        "name": "Nurse-PaLM operacional",
        "decision": "Nurse-PaLM operacional",
        "next_human": "Certificar Nurse-PaLM operacional",
        "code_progress": "NOT_ASSERTED mantido; gate recusa claim operacional",
        "modality": "MUST_NOT",
        "objective": "forbid_nurse_palm_operational_assertion",
        "deny_if": "nursePalm == ASSERTED or operational == true",
        "layers": ["B10"],
        "authority": ["CKO-REG", "B10"],
        "count": None,
    },
    {
        "hold_id": "HOLD-HUMAN-LOCALE-ACTIVATE",
        "policy_id": "POL-CKO-HOLD-LOCALE-1.0.0",
        "policy_type": "CONTENT",
        "name": "Ativação de locale Wave2",
        "decision": "Ativar células de locale Wave2 no seletor",
        "next_human": "Revisão linguística antes de activate_in_selector",
        "code_progress": "360 células HOLD; seletor continua desativado",
        "modality": "MUST_NOT",
        "objective": "keep_360_locale_cells_off_selector",
        "deny_if": "activate_in_selector == true",
        "layers": ["LYR-I18N-001"],
        "authority": ["CKO-REG", "Wave2"],
        "count": 360,
    },
    {
        "hold_id": "HOLD-HUMAN-HERO-MEDIA-RIGHTS",
        "policy_id": "POL-CKO-HOLD-HERO-MEDIA-1.0.0",
        "policy_type": "CONTENT",
        "name": "Mídia de hero e direitos de imagem",
        "decision": "Mídia de hero (camada 7) e direitos de imagem",
        "next_human": "Humano 2026-09-05: aprovado no pacote de direitos. Camada 7 de mídia continua sem publicar",
        "code_progress": "Humano 2026-09-05: aprovado. Heroes de template e DS são texto-only; sem camada 7 de mídia publicada",
        "modality": "MUST_NOT",
        "objective": "forbid_hero_media_without_rights",
        "deny_if": "hero.media.published == true",
        "layers": ["LYR-MEDIA-001", "LYR-DS-001"],
        "authority": ["CKO-VAS-001", "Lei 9.610/1998"],
        "count": None,
        "recorded_human": {
            "verdict": "APPROVED",
            "mapped_choice": "CLEAR",
            "recorded_at": "2026-09-05T20:58:00Z",
            "source": "user_message",
            "text": "aprovado",
            "publishes_hero_layer_7": False,
            "closes_b9": False,
        },
    },
    {
        "hold_id": "HOLD-HUMAN-OBSERVED-RUNTIME",
        "policy_id": "POL-CKO-HOLD-RUNTIME-1.0.0",
        "policy_type": "RUNTIME",
        "name": "Runtime observado",
        "decision": "Runtime observado em browser/mobile/produção",
        "next_human": "Assinar runtime observado em produção/mobile",
        "code_progress": "Preview local e staging; observed:false no twin",
        "modality": "MUST_NOT",
        "objective": "forbid_inferred_observed_runtime",
        "deny_if": "runtime_claim == observed and runtime_source != observed",
        "layers": ["B5", "LYR-RUN-001"],
        "authority": ["NIFS-600-15", "B5"],
        "count": None,
    },
    {
        "hold_id": "HOLD-HUMAN-RECERT-B7",
        "policy_id": "POL-CKO-HOLD-RECERT-1.0.0",
        "policy_type": "ASSURANCE",
        "name": "Reperformance e recertificação B7",
        "decision": "Reperformance e recertificação B7",
        "next_human": "Aprovar reperformance e recertificação B7",
        "code_progress": "201 pending_reperformance explícitos; recert B7 FAIL",
        "modality": "MUST_NOT",
        "objective": "block_release_while_b7_recert_fail",
        "deny_if": "recert == FAIL and action == release",
        "layers": ["B7", "B9"],
        "authority": ["CKO-REG", "B7"],
        "count": 201,
    },
    {
        "hold_id": "HOLD-HUMAN-COPY-RATINGS",
        "policy_id": "POL-CKO-HOLD-RATINGS-1.0.0",
        "policy_type": "CONTENT",
        "name": "Texto de avaliações nas fichas",
        "decision": "Texto de avaliações/estrelas nas fichas de ferramenta",
        "next_human": "Autorizar texto de avaliações, se algum",
        "code_progress": "js/cko-ratings-hold.js substitui .stars/.tool-rating; gerador deixa de emitir estrelas",
        "modality": "MUST_NOT",
        "objective": "forbid_star_ratings_without_human_copy",
        "deny_if": "ratings.copy == published without HOLD-HUMAN-COPY-RATINGS authorization",
        "layers": ["LYR-UI-001", "LYR-CLIN-CALC-001"],
        "authority": ["CKO-REG", "HOLD-HUMAN-COPY-RATINGS"],
        "count": None,
    },
]


def specialize(hold: dict) -> dict:
    fields = {fid: {"status": "SPECIALIZED_HOLD", "implemented": False, "assured": False} for fid in MASTER_FIELDS}
    fields["IDENTITY"].update(
        {
            "policy_id": hold["policy_id"],
            "hold_id": hold["hold_id"],
            "policy_name": hold["name"],
            "policy_type": hold["policy_type"],
            "policy_status": "HOLD_HUMAN_NON_BLOCKING",
        }
    )
    fields["AUTHORITY"].update({"sources": hold["authority"]})
    fields["INTENT"].update(
        {
            "objective": hold["objective"],
            "desired_state": "human_signed_or_explicit_hold",
            "prohibited_state": "silent_bypass_or_release",
        }
    )
    fields["APPLICABILITY"].update({"mode": "REQUIRED", "hold_id": hold["hold_id"]})
    fields["SCOPE"].update({"layers": hold["layers"]})
    fields["SUBJECT"].update({"actors": ["HUMAN", "AGENT"], "objects": ["PLATFORM", "RELEASE"]})
    fields["MODALITY"].update({"type": hold["modality"]})
    fields["DECISION"].update({"deny_if": [hold["deny_if"]], "allow_if": ["human.signed == true"]})
    fields["OUTCOME"].update({"on_deny": "HOLD", "on_allow": "HUMAN_REVIEW", "severity": "BLOCKER"})
    fields["ENFORCEMENT"].update({"preventive": ["INSPECT", "CI_GATE"], "detective": ["LEDGER"]})
    fields["GOVERNANCE"].update(
        {
            "owner": "HUMAN",
            "approval_required": True,
            "human_boundary": "FINAL_APPROVAL",
            "blocking_inspect": False,
            "blocking_release": True,
        }
    )
    fields["READINESS"].update({"score": "NOT_READY", "active": False})
    fields["ASSURANCE"].update({"verdict": "HOLD_HUMAN_NON_BLOCKING", "release_allowed": False})
    assert list(fields) == MASTER_FIELDS
    return {
        "contract_id": POLICY_MASTER_ID,
        "status": "SPECIALIZED_HOLD",
        "implemented": False,
        "assured": False,
        "field_count": 28,
        "fields": fields,
    }


def hold_policy(hold: dict) -> dict:
    policy = {
        "id": hold["policy_id"],
        "kind": "policy-as-code",
        "hold_id": hold["hold_id"],
        "document_id": hold["hold_id"],
        "document_version": "1.0.0",
        "policy_type": hold["policy_type"],
        "name": hold["name"],
        "parent": POLICY_MASTER_ID,
        "specializes": POLICY_MASTER_ID,
        "inherits": [FAIL_CLOSED_ID, POLICY_MASTER_ID],
        "starts_at": "policy-as-code",
        "status": "HOLD_HUMAN_NON_BLOCKING",
        "active": False,
        "implantado": False,
        "assured": False,
        "release": "HOLD / NOT_RELEASED",
        "release_allowed": False,
        "blocking_inspect": False,
        "blocking_ci": False,
        "blocking_release": True,
        "modality": hold["modality"],
        "decision": hold["decision"],
        "next_human": hold["next_human"],
        "code_progress": hold["code_progress"],
        "count": hold["count"],
        "contract": specialize(hold),
    }
    if hold.get("recorded_human"):
        policy["recorded_human"] = hold["recorded_human"]
    return policy


def ledger() -> dict:
    items = []
    for hold in HOLDS:
        item = {
            "id": hold["hold_id"],
            "decision": hold["decision"],
            "owner": "human",
            "status": "HOLD_HUMAN_NON_BLOCKING",
            "blocking_inspect": False,
            "blocking_release": True,
            "code_progress": hold["code_progress"],
            "next_human": hold["next_human"],
            "policy_id": hold["policy_id"],
            "specializes": POLICY_MASTER_ID,
            "policy_type": hold["policy_type"],
            "modality": hold["modality"],
        }
        if hold["count"] is not None:
            item["count"] = hold["count"]
        if hold.get("recorded_human"):
            item["recorded_human"] = hold["recorded_human"]
        items.append(item)
    return {
        "id": "CKO-HOLD-HUMAN-1.0.0",
        "kind": "hold-human-non-blocking",
        "root": "policy-as-code",
        "policy": "POL-CKO-PLATFORM-CLOSURE-1.0.0",
        "specializes": POLICY_MASTER_ID,
        "status": "HOLD_HUMAN_NON_BLOCKING",
        "blocking_inspect": False,
        "blocking_ci": False,
        "blocking_release": True,
        "release": "HOLD / NOT_RELEASED",
        "release_allowed": False,
        "rule": "decisão humana = HOLD_HUMAN_NON_BLOCKING; cada hold especializa POLICY_MASTER_CONTRACT; não bloqueia inspect/CI",
        "hold_count": 9,
        "items": items,
    }


def build() -> dict:
    holds = [hold_policy(h) for h in HOLDS]
    assert len(holds) == 9
    assert [h["hold_id"] for h in holds] == [row["hold_id"] for row in HOLDS]
    return {
        "id": "POL-CKO-PLATFORM-CLOSURE-1.0.0",
        "kind": "policy-as-code",
        "mode": "fail-closed",
        "root": False,
        "starts_at": "policy-as-code",
        "parent": POLICY_MASTER_ID,
        "specializes": POLICY_MASTER_ID,
        "inherits": [FAIL_CLOSED_ID, POLICY_MASTER_ID],
        "document_id": "CKO-POL-CLOSURE-001",
        "document_version": "1.0.0",
        "status": "CONTROLLED_CLOSURE_HOLD",
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
        "hold_count": 9,
        "existing_policy_count": len(EXISTING),
        "existing_policies": EXISTING,
        "holds": holds,
        "human_ledger": "CKO-HOLD-HUMAN-1.0.0",
        "rule": "Fecho da plataforma = fail-closed + contrato-mestre + especializações + holds humanos ligados a policy-as-code. Nenhum hold ACTIVE. Release permanece HOLD.",
        "evaluation": {
            "verdict": "CLOSURE_HOLD_NOT_RELEASED",
            "documentado": True,
            "implantado": False,
            "assured": False,
            "active": False,
            "clinical_promotion": "DENIED",
            "findings": [
                {
                    "id": "CLO-F-HOLDS-NOW-POLICIES",
                    "severity": "HOLD",
                    "text": "Os 9 holds humanos especializam POLICY_MASTER_CONTRACT. Binding ≠ assinatura humana ≠ RELEASE.",
                },
                {
                    "id": "CLO-F-STILL-DENIES-RELEASE",
                    "severity": "HOLD",
                    "text": "B9 NOT_RELEASED. Nurse-PaLM NOT_ASSERTED. Calculadoras PAUSED. Rights holds = 13.",
                },
            ],
        },
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def unnamed_slot(n: int) -> dict:
    return {
        "slot": n,
        "id": f"RIGHTS-PROVENANCE-SLOT-{n:02d}",
        "title": None,
        "title_in_ledger": False,
        "awaiting": "CLEAR | HOLD | DENY",
        "initials": None,
        "date": None,
        "notes": None,
    }


def rights_decision_form() -> dict:
    """13 untitled slots. Do not invent PDF titles. Clinical DENIED is recorded."""
    return {
        "id": "CKO-RIGHTS-DECISION-FORM-HOLD-1.0.0",
        "title": "Formulário de decisão — 13 RIGHTS_PROVENANCE sem títulos no ledger",
        "kind": "rights-decision-form-hold",
        "root": "policy-as-code",
        "status": "HOLD_HUMAN_NON_BLOCKING",
        "active": False,
        "implantado": False,
        "assured": False,
        "release": "HOLD / NOT_RELEASED",
        "release_allowed": False,
        "published": False,
        "operational": "NOT_ASSERTED",
        "md_reg_complete": False,
        "clinical_promotion": "DENIED",
        "calculators_scales": "PAUSED",
        "closes_b9": False,
        "mutate_drive": False,
        "do_not_alter_drive_file": True,
        "titles_invented": False,
        "canonical_navy": "#1A3E74",
        "canonical_navy_token": "--cko-navy-900",
        "readback": "2026-09-05T20:58:00Z",
        "rule": "O Relatório Técnico OV-CKO-GLOBAL-FINAL-AUD8L-1.0.0 deixa a contagem rights_holds=13. O ledger não extrai 13 títulos. SLOT-01..13 não são nomes do PDF. Aprovação humana do bucket não zera a contagem, não é proveniência por mídia/marca e não fecha B9.",
        "recorded_human": {
            "HOLD-HUMAN-CLINICAL-HOMOLOG": {
                "verdict": "DENIED",
                "recorded_at": "2026-09-05T20:21:00Z",
                "source": "user_message",
                "text": "1 - continua denied",
                "unpauses_calc_scales": False,
                "clinical_promotion": "DENIED",
                "closes_b9": False,
            },
            "HOLD-HUMAN-RIGHTS-CHAIN": {
                "verdict": "APPROVED",
                "mapped_choice": "CLEAR",
                "recorded_at": "2026-09-05T20:58:00Z",
                "source": "user_message",
                "text": "aprovado",
                "scope": "bucket_and_named_adjacent",
                "closes_rights_count_13": False,
                "provenance_per_media": False,
                "closes_b9": False,
            },
        },
        "closes_rights_count_13": False,
        "provenance_per_media": False,
        "bucket": {
            "id": "HOLD-HUMAN-RIGHTS-CHAIN",
            "also": [
                "PEND-PDF-RIGHTS-BUCKET",
                "PEND-P1-RIGHTS",
                "UNK-RIGHTS-CHAIN",
                "P1-RIGHTS",
            ],
            "count": 13,
            "kind": "RIGHTS_PROVENANCE",
            "source_document": "OV-CKO-GLOBAL-FINAL-AUD8L-1.0.0",
            "titles_in_ledger": False,
            "next_action": "KEEP_RIGHTS_COUNT_13_UNTIL_PER_MEDIA_PROVENANCE",
            "awaiting": None,
            "verdict": "APPROVED",
            "mapped_choice": "CLEAR",
            "initials": None,
            "date": "2026-09-05",
            "notes": "user_message: aprovado. Bucket only. Slots remain untitled.",
        },
        "unnamed_slots": [unnamed_slot(n) for n in range(1, 14)],
        "named_rights_adjacent_not_the_13_titles": [
            {
                "id": "HOLD-HUMAN-HERO-MEDIA-RIGHTS",
                "what": "Mídia de hero (camada 7) e direitos de imagem",
                "status": "HOLD_HUMAN_NON_BLOCKING",
                "verdict": "APPROVED",
                "mapped_choice": "CLEAR",
                "publishes_hero_layer_7": False,
                "initials": None,
                "date": "2026-09-05",
            },
            {
                "id": "PEND-HOLD-B6.1-rights",
                "what": "Rights no bloco B6.1 Clinical Vertical",
                "status": "HOLD",
                "verdict": "APPROVED",
                "mapped_choice": "CLEAR",
                "initials": None,
                "date": "2026-09-05",
            },
            {
                "id": "PEND-HOLD-B6.2-rights",
                "what": "Rights no bloco B6.2 Knowledge/Libraries",
                "status": "HOLD",
                "verdict": "APPROVED",
                "mapped_choice": "CLEAR",
                "initials": None,
                "date": "2026-09-05",
            },
            {
                "id": "PEND-HOLD-B6.3-rights",
                "what": "Rights no bloco B6.3 Experience/Publication",
                "status": "HOLD",
                "verdict": "APPROVED",
                "mapped_choice": "CLEAR",
                "initials": None,
                "date": "2026-09-05",
            },
            {
                "id": "PEND-W2-H10",
                "what": "H10 Rights / Licensing / Copyright (Wave2)",
                "status": "HOLD_SCOPED",
                "verdict": "APPROVED",
                "mapped_choice": "CLEAR",
                "initials": None,
                "date": "2026-09-05",
            },
            {
                "id": "SRC-REF-0001",
                "what": "Visual Reference Asset Registry — rights_status mixed_unknown; ai_processing_permission DENY. Histórico 2026-08-05. Não fecha o bucket de 13.",
                "status": "HOLD",
                "verdict": "APPROVED",
                "mapped_choice": "CLEAR",
                "closes_rights_count_13": False,
                "initials": None,
                "date": "2026-09-05",
            },
        ],
        "how_to_reply": {
            "choices": ["CLEAR", "HOLD", "DENY"],
            "received": "aprovado",
            "mapped_choice": "CLEAR",
            "bucket_decision_is_enough": True,
            "slots_remain_untitled": True,
            "does_not_close_b9": True,
            "does_not_publish": True,
            "does_not_zero_rights_holds": True,
        },
    }


def generate() -> dict:
    closure = build()
    human = ledger()
    rights = rights_decision_form()
    for dest in (OUT_POLICY, OUT_SITE, OUT_CASCADE):
        write_json(dest, closure)
    for dest in (OUT_LEDGER, OUT_LEDGER_SITE, OUT_LEDGER_CASCADE):
        write_json(dest, human)
    for dest in (OUT_RIGHTS_FORM, OUT_RIGHTS_FORM_SITE):
        write_json(dest, rights)
    return closure


if __name__ == "__main__":
    doc = generate()
    print(f"wrote {OUT_POLICY} holds={doc['hold_count']} status={doc['status']}")
