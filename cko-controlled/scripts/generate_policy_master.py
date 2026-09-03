#!/usr/bin/env python3
"""Emit POLICY_MASTER_CONTRACT v1.0.0 as fail-closed policy-as-code.

Frozen template. Specializations inherit this structure; they do not invent a new one.
DOCUMENTADO ≠ IMPLANTADO ≠ ASSURED. Not ACTIVE.
"""
from __future__ import annotations

import json
from pathlib import Path

GATE = Path(__file__).resolve().parents[1]
SITE = GATE.parent / "reference-website"
OUT_POLICY = GATE / "public" / "policies" / "policy-master.json"
OUT_SITE = SITE / "data" / "cko" / "policy-master.json"

CASCADE = [
    "policy-as-code",
    "schemas",
    "graph-constraints",
    "CI-gates",
    "runtime-assertions",
    "automatic-evidence",
]

CHAIN = [
    "AUTHORITY",
    "NORMATIVE_ATOM",
    "APPLICABILITY",
    "CONTROL",
    "POLICY_SPECIFICATION",
    "POLICY_CONTRACT",
    "POLICY_AS_CODE",
    "TEST",
    "CI_GATE",
    "RUNTIME_ENFORCEMENT",
    "OBSERVABILITY",
    "EVIDENCE",
    "ASSURANCE",
    "HUMAN_GOVERNANCE",
]

FIELDS = [
    ("01", "IDENTITY", "Qual política?", "architectural", "ISO 27001/9001, NIST CSF, W3C PROV, configuration management"),
    ("02", "AUTHORITY", "Por que existe?", "normative", "lei, regulamento, standard, WCAG, LGPD, ISO, NIST, OWASP, política interna"),
    ("03", "INTENT", "O que pretende assegurar?", "normative", "control objectives, WCAG outcomes, NIST, COBIT, requisitos"),
    ("04", "APPLICABILITY", "Quando se aplica?", "normative", "ISO 27001 scope, NIST context, LGPD, WCAG conteúdo aplicável"),
    ("05", "SCOPE", "Onde se aplica?", "architectural", "ISO/NIST scope, 44 camadas × verticais × application × object × field"),
    ("06", "SUBJECT", "Quem/o que está sujeito?", "normative", "IAM, RBAC/ABAC, ISO 27001, least privilege, human governance"),
    ("07", "MODALITY", "Qual a força da obrigação?", "normative", "RFC 2119, RFC 8174"),
    ("08", "CONDITIONS", "Sob quais condições?", "technical", "OPA/Rego, SHACL, regra condicional"),
    ("09", "CONSTRAINTS", "Quais propriedades são obrigatórias?", "technical", "JSON Schema, SHACL, OWL"),
    ("10", "DECISION", "Qual decisão determinística?", "technical", "OPA/Rego, policy engines, ABAC"),
    ("11", "OUTCOME", "Qual resultado/estado?", "technical", "state machine, workflow, CI/CD gates"),
    ("12", "ENFORCEMENT", "Como será imposto?", "technical", "OPA, DevSecOps, NIST, ISO 27001, secure SDLC"),
    ("13", "CONTRACT", "Qual contrato formal?", "technical", "Design by Contract, JSON Schema, OpenAPI, SHACL"),
    ("14", "IMPLEMENTATION", "Como foi implementado?", "technical", "policy-as-code, OPA, CI/CD"),
    ("15", "TESTS", "Como provamos que funciona?", "technical", "OPA tests, ISO 9001/27001, CI"),
    ("16", "CI_GATES", "Pode ser promovido?", "technical", "NIST SSDF, SLSA, DevSecOps"),
    ("17", "RUNTIME_ASSERTIONS", "Continua válido em produção?", "technical", "runtime policy, OpenTelemetry, SRE"),
    ("18", "OBSERVABILITY", "Como observamos?", "technical", "OpenTelemetry, SRE, ISO 27001 auditoria operacional"),
    ("19", "EVIDENCE", "Qual prova existe?", "normative", "ISO 27001/9001, auditoria, W3C PROV, ALCOA+"),
    ("20", "PROVENANCE", "De onde veio?", "normative", "W3C PROV, ALCOA+, ISO 27001, lineage"),
    ("21", "GOVERNANCE", "Quem decide?", "normative", "ISO 27001/38500, NIST, AI governance, Maker≠Checker≠Auditor"),
    ("22", "EXCEPTIONS", "Quando pode haver exceção?", "normative", "gestão de risco, controles compensatórios, ISO 27001"),
    ("23", "DEPENDENCIES", "Do que depende?", "architectural", "configuration management, lineage, impact analysis"),
    ("24", "VERSIONING", "Qual versão governa?", "architectural", "ISO 9001/27001, semantic versioning, imutabilidade de release"),
    ("25", "LIFECYCLE", "Em que estado está?", "architectural", "lifecycle/change management ISO 9001/27001"),
    ("26", "CHANGE_IMPACT", "O que será afetado?", "architectural", "change/impact analysis, dependency graph"),
    ("27", "READINESS", "Está pronta?", "architectural", "assurance, release governance, DevSecOps"),
    ("28", "ASSURANCE", "Como provamos continuamente?", "normative", "ISO/NIST, auditoria, continuous assurance"),
]


def build() -> dict:
    fields = [
        {
            "seq": seq,
            "id": name,
            "question": question,
            "base_kind": kind,
            "bases": bases,
            "status": "DOCUMENTADO_HOLD",
            "implemented": False,
        }
        for seq, name, question, kind, bases in FIELDS
    ]
    assert len(fields) == 28, len(fields)
    return {
        "id": "POL-CKO-POLICY-MASTER-CONTRACT-1.0.0",
        "kind": "policy-as-code",
        "mode": "fail-closed",
        "root": False,
        "starts_at": "policy-as-code",
        "parent": "POL-CKO-FAIL-CLOSED-1.0.0",
        "document_id": "POLICY_MASTER_CONTRACT",
        "document_version": "1.0.0",
        "status": "CONTROLLED_TEMPLATE_HOLD",
        "frozen": True,
        "active": False,
        "cascade": CASCADE,
        "chain": CHAIN,
        "release": "HOLD / NOT_RELEASED",
        "release_allowed": False,
        "published": False,
        "operational": "NOT_ASSERTED",
        "canonical_promotion": False,
        "documentado": True,
        "implantado": False,
        "assured": False,
        "new_architectural_root": False,
        "specialization_rule": "Policies specialize this contract by layer + vertical + application + object + field + context. They do not invent a parallel structure.",
        "golden_rule": "Uma Policy não é completa quando foi escrita. Ela é completa quando autoridade, aplicabilidade, decisão, enforcement, teste, evidência e governança humana são reconstruíveis.",
        "field_count": 28,
        "fields": fields,
        "maturity_target": "P6_CONTINUOUSLY_ASSURED",
        "maturity_current": "P2_GOVERNED_HOLD",
        "rule": "AUTHORITY → NORMATIVE ATOM → APPLICABILITY → CONTROL → POLICY SPECIFICATION → CONTRACT → POLICY-AS-CODE → TEST → CI GATE → RUNTIME → EVIDENCE → ASSURANCE",
    }


def generate() -> dict:
    payload = build()
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    OUT_POLICY.parent.mkdir(parents=True, exist_ok=True)
    OUT_SITE.parent.mkdir(parents=True, exist_ok=True)
    OUT_POLICY.write_text(text, encoding="utf-8")
    OUT_SITE.write_text(text, encoding="utf-8")
    return payload


if __name__ == "__main__":
    doc = generate()
    print(f"wrote {OUT_POLICY} fields={doc['field_count']} status={doc['status']}")
