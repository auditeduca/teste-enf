#!/usr/bin/env python3
"""Bind the shared-conversation assurance + acquisition APIs as POLICY_MASTER HOLD.

Source is the conversation that maps:
  TLA+ / SHACL / OPA-Rego / PROV / GSN / OpenTelemetry / Event Sourcing / Agent Evaluation
  plus frontend acquisition APIs connecting API × extraction × content.

This is DOCUMENTADO, not implantado, not ACTIVE, not RELEASE.
MD/REG completeness remains the next task.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cko_policy_contract import CASCADE, FAIL_CLOSED_ID, POLICY_MASTER_ID, specialize

GATE = Path(__file__).resolve().parents[1]
SITE = GATE.parent / "reference-website"

OUT_POLICY = GATE / "public" / "policies" / "governed-fabric.json"
OUT_SITE = SITE / "data" / "cko" / "governed-fabric.json"
OUT_CASCADE = SITE / "data" / "cko" / "cascade" / "governed-fabric.json"

ASSURE = [
    {"id": "OPA", "name": "OPA / Rego", "question": "É permitido?", "order": 1, "preexisting": False},
    {"id": "SHACL", "name": "SHACL / RDF", "question": "O grafo é semanticamente válido?", "order": 2, "preexisting": True, "binding": "cko-controlled/public/graph/shacl.json"},
    {"id": "EVENT", "name": "Event Sourcing", "question": "O que aconteceu?", "order": 3, "preexisting": False},
    {"id": "OTEL", "name": "OpenTelemetry", "question": "Como foi executado?", "order": 4, "preexisting": False},
    {"id": "PROV", "name": "W3C PROV", "question": "De onde veio / como foi produzido?", "order": 5, "preexisting": False},
    {"id": "EVAL", "name": "Agent Evaluation", "question": "Funcionou adequadamente?", "order": 6, "preexisting": False},
    {"id": "GSN", "name": "GSN / SACM", "question": "Por que podemos confiar na afirmação?", "order": 7, "preexisting": False},
    {"id": "TLA", "name": "TLA+", "question": "O sistema pode chegar a um estado proibido?", "order": 8, "preexisting": False},
]

ACQ_METHODS = [
    {"id": "api", "name": "API", "rank": "preferred"},
    {"id": "structured_data", "name": "JSON-LD / Schema.org / Microdata / RDFa", "rank": "preferred"},
    {"id": "rendered_dom", "name": "DOM renderizado", "rank": "preferred"},
    {"id": "static_html", "name": "HTML estático / HTTP fetch", "rank": "preferred"},
    {"id": "browser", "name": "Browser automation (Playwright)", "rank": "fallback"},
]

EXTRACTORS = [
    "HTMLExtractor",
    "PDFExtractor",
    "TableExtractor",
    "JSONExtractor",
    "JSONLDExtractor",
    "MicrodataExtractor",
    "RDFExtractor",
    "OCRExtractor",
    "ImageExtractor",
    "TranscriptExtractor",
]

AGENT_TOOLS = [
    {"id": "fetch_url", "role": "http_get"},
    {"id": "open_browser", "role": "browser"},
    {"id": "inspect_dom", "role": "dom"},
    {"id": "inspect_a11y", "role": "accessibility_tree"},
    {"id": "inspect_network", "role": "network_intercept"},
    {"id": "extract_jsonld", "role": "structured_data"},
    {"id": "extract_table", "role": "table"},
    {"id": "extract_content", "role": "readability"},
    {"id": "call_api", "role": "api_registry"},
    {"id": "save_artifact", "role": "raw_artifact"},
    {"id": "create_content", "role": "content_object"},
    {"id": "validate_object", "role": "contract"},
    {"id": "request_approval", "role": "human_boundary"},
]

REGISTRIES = [
    {"id": "API_REGISTRY", "governs": "call_api"},
    {"id": "SOURCE_REGISTRY", "governs": "acquisition_planner"},
    {"id": "EXTRACTOR_REGISTRY", "governs": "extractors"},
    {"id": "AGENT_TOOL_REGISTRY", "governs": "agent_tools"},
    {"id": "ACQUISITION_PLANNER", "governs": "method_selection"},
]

CONTENT_STAGES = [
    "ACQUISITION",
    "EXTRACTION",
    "INTERPRETATION",
    "CANONICALIZATION",
    "GOVERNANCE",
]


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
        "status": "CONTROLLED_FABRIC_HOLD",
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
            policy_type="FABRIC",
            objective=objective,
            deny_if=deny_if,
            layers=layers,
            authority=authority,
            extra_identity={"family_id": family_id},
        ),
    }
    body.update(extra)
    return body


def item(kind: str, ident: str, **extra) -> dict:
    row = {
        "kind": kind,
        "id": ident,
        "operational": "NOT_ASSERTED",
        "implantado": False,
        "assured": False,
        "release": "HOLD / NOT_RELEASED",
    }
    row.update(extra)
    return row


def build() -> dict:
    assure_items = [
        item(
            "assurance_technology",
            t["id"],
            name=t["name"],
            question=t["question"],
            study_order=t["order"],
            preexisting_binding=t["preexisting"],
            binding=t.get("binding"),
        )
        for t in ASSURE
    ]
    method_items = [item("acquisition_method", m["id"], name=m["name"], rank=m["rank"]) for m in ACQ_METHODS]
    extractor_items = [item("extractor", name, name=name) for name in EXTRACTORS]
    tool_items = [item("agent_api", t["id"], name=f"{t['id']}()", role=t["role"]) for t in AGENT_TOOLS]
    registry_items = [item("registry", r["id"], name=r["id"], governs=r["governs"]) for r in REGISTRIES]
    content_items = [item("pipeline_stage", s, name=s) for s in CONTENT_STAGES]
    front_items = [
        item(
            "frontend",
            "ACQUISITION_BROWSER",
            name="Acquisition Browser / Inspector",
            note="Seleção DOM/A11y/JSON-LD/API no front. Fetch cross-origin permanece no worker — CORS/CSP.",
        )
    ]
    md_items = [
        item(
            "next_task",
            "MD_REG_COMPLETE",
            name="MD/REG via aquisição governada",
            classified_md_fields=2496,
            classified_reg_bindings=10913,
            materialized_field_bindings=False,
            corpus_denominator=0,
            md_reg_complete=False,
        )
    ]
    families = [
        family(
            "FAB-ASSURE",
            "Stack de garantia da conversa compartilhada",
            "ASSURANCE",
            "bind_eight_assurance_questions_without_claiming_operational",
            "assure.implantado == true or TLA claimed without model",
            ["CKO-REG", "LYR-SEC-001"],
            ["shared conversation assurance stack"],
            {"items": assure_items, "item_count": len(assure_items)},
        ),
        family(
            "FAB-ACQ-METHOD",
            "Estratégia de aquisição (API primeiro)",
            "ACQUISITION",
            "prefer_api_then_structured_then_dom_then_html_browser_fallback",
            "browser_used_when_api_available == true",
            ["LYR-SEC-001", "LYR-RUN-001"],
            ["Acquisition Strategy"],
            {
                "items": method_items,
                "item_count": len(method_items),
                "precedence": ["api", "structured_data", "rendered_dom", "static_html", "browser"],
            },
        ),
        family(
            "FAB-ACQ-EXTRACTOR",
            "Extractors especializados — não um AIExtractor único",
            "EXTRACTION",
            "keep_deterministic_extractors_separate_from_semantic_llm",
            "single_llm_extractor == canonical",
            ["CKO-REG", "LYR-TERM-001"],
            ["Extraction Fabric"],
            {"items": extractor_items, "item_count": len(extractor_items)},
        ),
        family(
            "FAB-AGENT-TOOL",
            "APIs do agente de extração via front",
            "AGENT_API",
            "bind_specialized_agent_tools_not_one_giant_browser_tool",
            "agent.browser == unconstrained",
            ["LYR-SEC-001", "LYR-RUN-001"],
            ["Agent Tool Registry"],
            {"items": tool_items, "item_count": len(tool_items)},
        ),
        family(
            "FAB-REGISTRY",
            "API × extração × conteúdo — registries",
            "REGISTRY",
            "route_api_extraction_content_through_registries_and_opa",
            "call_api without API_REGISTRY",
            ["LYR-SEC-001", "CKO-REG"],
            ["API Registry", "Source Registry", "Content Integration Fabric"],
            {"items": registry_items, "item_count": len(registry_items)},
        ),
        family(
            "FAB-CONTENT",
            "Pipeline conteúdo canónico",
            "CONTENT",
            "separate_acquisition_extraction_interpretation_canonicalization_governance",
            "website_to_llm_to_database == true",
            ["CKO-MD", "CKO-REG"],
            ["Canonical Object Model"],
            {"items": content_items, "item_count": len(content_items)},
        ),
        family(
            "FAB-FRONT",
            "Acquisition Browser no front-end",
            "FRONTEND",
            "allow_user_assisted_front_extraction_without_unrestricted_cors_scrape",
            "frontend.fetch_any_origin == true",
            ["LYR-UI-001", "LYR-SEC-001"],
            ["Acquisition Browser / Inspector"],
            {"items": front_items, "item_count": len(front_items)},
        ),
        family(
            "FAB-MD-REG-NEXT",
            "MD/REG via fabric — próxima tarefa",
            "NEXT_TASK",
            "forbid_claiming_md_reg_complete_in_this_catalog",
            "md_reg_complete == true",
            ["CKO-MD", "CKO-REG"],
            ["CKO-MD", "CKO-REG"],
            {
                "items": md_items,
                "item_count": len(md_items),
                "md_reg_complete": False,
                "note": "Classificado ≠ extraído clause-level ≠ implantado. Completar MD/REG é a próxima tarefa.",
            },
        ),
    ]
    item_total = sum(f["item_count"] for f in families)
    return {
        "id": "POL-CKO-GOVERNED-FABRIC-1.0.0",
        "kind": "policy-as-code",
        "mode": "fail-closed",
        "root": False,
        "starts_at": "policy-as-code",
        "parent": POLICY_MASTER_ID,
        "specializes": POLICY_MASTER_ID,
        "inherits": [FAIL_CLOSED_ID, POLICY_MASTER_ID],
        "document_id": "CKO-POL-FABRIC-001",
        "document_version": "1.0.0",
        "status": "CONTROLLED_FABRIC_HOLD",
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
        "item_total": item_total,
        "md_reg_complete": False,
        "md_reg_next_task": True,
        "source": {
            "kind": "shared_conversation",
            "not": "cko-deepseek-blackboard",
            "topics": [
                "TLA+",
                "SHACL",
                "OPA/Rego",
                "PROV",
                "GSN",
                "OpenTelemetry",
                "Event Sourcing",
                "Agent Evaluation",
                "frontend acquisition",
                "API x extraction x content",
            ],
        },
        "pipeline": CONTENT_STAGES,
        "families": families,
        "rule": "A conversa compartilhada liga o stack de garantia e as APIs de aquisição front/API/conteúdo a policy-as-code. Nenhuma tecnologia está operacional. MD/REG completa na próxima tarefa.",
        "evaluation": {
            "verdict": "FABRIC_HOLD_BOUND_NOT_OPERATIONAL",
            "documentado": True,
            "implantado": False,
            "assured": False,
            "active": False,
            "md_reg_complete": False,
            "findings": [
                {
                    "id": "FAB-F-ASSURE-EIGHT",
                    "severity": "HOLD",
                    "text": "OPA, SHACL, Event Sourcing, OpenTelemetry, PROV, Agent Evaluation, GSN/SACM e TLA+ ligados como perguntas, não como runtime.",
                },
                {
                    "id": "FAB-F-AGENT-APIS",
                    "severity": "HOLD",
                    "text": "13 APIs de agente especializadas. Sem ferramenta browser gigante. Sem scraper LLM-only.",
                },
                {
                    "id": "FAB-F-MD-REG-NEXT",
                    "severity": "HOLD",
                    "text": "MD 2496 e REG 10913 permanecem classificados. Completar extração/amarração MD/REG é a próxima tarefa.",
                },
            ],
        },
    }


def generate() -> dict:
    policy = build()
    if policy["family_count"] != 8:
        raise SystemExit(f"expected 8 fabric families, got {policy['family_count']}")
    if policy["item_total"] != 48:
        raise SystemExit(f"expected 48 fabric items, got {policy['item_total']}")
    if policy["md_reg_complete"] is not False:
        raise SystemExit("md_reg_complete must stay false")
    for dest in (OUT_POLICY, OUT_SITE, OUT_CASCADE):
        write_json(dest, policy)
    return policy


if __name__ == "__main__":
    doc = generate()
    print(
        f"wrote {OUT_POLICY} families={doc['family_count']} items={doc['item_total']} status={doc['status']}"
    )
