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
OUT_CASCADE = SITE / "data" / "cko" / "cascade" / "policy-master.json"

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

# seq, id, question, base_kind, bases, meaning
FIELDS = [
    (
        "01",
        "IDENTITY",
        "Qual política?",
        "architectural",
        "ISO 27001/9001, NIST CSF, W3C PROV, configuration management",
        "Identifica inequivocamente a política (policy_id, version, name, type, status). IDs no formato POL-{DOMAIN}-{CATEGORY}-{SEQUENCE} nunca se reutilizam.",
    ),
    (
        "02",
        "AUTHORITY",
        "Por que existe?",
        "normative",
        "lei, regulamento, standard, WCAG, LGPD, ISO, NIST, OWASP, política interna",
        "Origem legítima da obrigação: fonte autoritativa → átomo normativo → requisito → controlo. A política não inventa a norma.",
    ),
    (
        "03",
        "INTENT",
        "O que pretende assegurar?",
        "normative",
        "control objectives, WCAG outcomes, NIST, COBIT, requisitos",
        "Intenção normativa (objective, problem, desired_state, prohibited_state). INTENT ≠ IMPLEMENTATION.",
    ),
    (
        "04",
        "APPLICABILITY",
        "Quando se aplica?",
        "normative",
        "ISO 27001 scope, NIST context, LGPD, WCAG conteúdo aplicável",
        "Determina quando a política realmente se aplica (REQUIRED | CONDITIONAL | NOT_APPLICABLE). Requisitos existentes ≠ requisitos aplicáveis.",
    ),
    (
        "05",
        "SCOPE",
        "Onde se aplica?",
        "architectural",
        "ISO/NIST scope, 44 camadas × verticais × application × object × field",
        "Onde a política atua: layer → vertical → application → module → object → field → environment.",
    ),
    (
        "06",
        "SUBJECT",
        "Quem/o que está sujeito?",
        "normative",
        "IAM, RBAC/ABAC, ISO 27001, least privilege, human governance",
        "Actores, papéis e objectos submetidos. Liga o Human Governance Boundary (agente detecta; humano aprova).",
    ),
    (
        "07",
        "MODALITY",
        "Qual a força da obrigação?",
        "normative",
        "RFC 2119, RFC 8174",
        "Força normativa: MUST, MUST_NOT, SHOULD, SHOULD_NOT, MAY.",
    ),
    (
        "08",
        "CONDITIONS",
        "Sob quais condições?",
        "technical",
        "OPA/Rego, SHACL, regra condicional",
        "Condições determinísticas (all / any / none) que disparam a política.",
    ),
    (
        "09",
        "CONSTRAINTS",
        "Quais propriedades são obrigatórias?",
        "technical",
        "JSON Schema, SHACL, OWL",
        "Restrições estruturais: required, datatype, cardinality, nullability, pattern, allowed/forbidden values.",
    ),
    (
        "10",
        "DECISION",
        "Qual decisão determinística?",
        "technical",
        "OPA/Rego, policy engines, ABAC",
        "Decisão allow_if / deny_if / require_if / escalate_if. Coração do policy-as-code.",
    ),
    (
        "11",
        "OUTCOME",
        "Qual resultado/estado?",
        "technical",
        "state machine, workflow, CI/CD gates",
        "Resultado canónico (ALLOW, DENY, BLOCK, REQUIRE, WARN, ESCALATE, REVIEW, DEFER) e transição de estado.",
    ),
    (
        "12",
        "ENFORCEMENT",
        "Como será imposto?",
        "technical",
        "OPA, DevSecOps, NIST, ISO 27001, secure SDLC",
        "Como a decisão é imposta (PREVENTIVE / DETECTIVE / CORRECTIVE / COMPENSATING) e em que modo (pre_commit, ci, pre_publish, runtime).",
    ),
    (
        "13",
        "CONTRACT",
        "Qual contrato formal?",
        "technical",
        "Design by Contract, JSON Schema, OpenAPI, SHACL",
        "Contrato de input/output/decision/error/evidence. Implementação que o viola é inválida.",
    ),
    (
        "14",
        "IMPLEMENTATION",
        "Como foi implementado?",
        "technical",
        "policy-as-code, OPA, CI/CD",
        "Onde e como a especificação vira código (engine, language, artifact). Código não precede a política.",
    ),
    (
        "15",
        "TESTS",
        "Como provamos que funciona?",
        "technical",
        "OPA tests, ISO 9001/27001, CI",
        "Provas positivas, negativas, de fronteira, de excepção, de conflito, adversariais e de regressão.",
    ),
    (
        "16",
        "CI_GATES",
        "Pode ser promovido?",
        "technical",
        "NIST SSDF, SLSA, DevSecOps",
        "Gates obrigatórios (syntax, schema, semantic, policy, security, regression, coverage, evidence, approval) antes de ACTIVE.",
    ),
    (
        "17",
        "RUNTIME_ASSERTIONS",
        "Continua válido em produção?",
        "technical",
        "runtime policy, OpenTelemetry, SRE",
        "Asserções contínuas após publicação. Um PASS de CI ontem não autoriza drift hoje.",
    ),
    (
        "18",
        "OBSERVABILITY",
        "Como observamos?",
        "technical",
        "OpenTelemetry, SRE, ISO 27001 auditoria operacional",
        "Métricas, logs, traces e alertas das avaliações e violações.",
    ),
    (
        "19",
        "EVIDENCE",
        "Qual prova existe?",
        "normative",
        "ISO 27001/9001, auditoria, W3C PROV, ALCOA+",
        "Prova automática, com integridade (hash) e proveniência, de decisão, teste, asserção e telemetria.",
    ),
    (
        "20",
        "PROVENANCE",
        "De onde veio?",
        "normative",
        "W3C PROV, ALCOA+, ISO 27001, lineage",
        "WHO / WHAT / WHEN / WHERE / WHY / HOW / WITH_WHICH_VERSION / USING_WHICH_INPUT / POLICY / ENGINE.",
    ),
    (
        "21",
        "GOVERNANCE",
        "Quem decide?",
        "normative",
        "ISO 27001/38500, NIST, AI governance, Maker≠Checker≠Auditor",
        "Owner, steward, approver e fronteira humana. Agente pode descobrir/propor; não aprova nem publica.",
    ),
    (
        "22",
        "EXCEPTIONS",
        "Quando pode haver exceção?",
        "normative",
        "gestão de risco, controles compensatórios, ISO 27001",
        "Desvio governado (prazo, justificação, compensação, aprovação humana). Nunca bypass informal.",
    ),
    (
        "23",
        "DEPENDENCIES",
        "Do que depende?",
        "architectural",
        "configuration management, lineage, impact analysis",
        "Políticas, controlos, schemas, vocabulários, standards, serviços e tecnologias de que depende.",
    ),
    (
        "24",
        "VERSIONING",
        "Qual versão governa?",
        "architectural",
        "ISO 9001/27001, semantic versioning, imutabilidade de release",
        "MAJOR.MINOR.PATCH. Versão publicada não se muta retroactivamente (P12).",
    ),
    (
        "25",
        "LIFECYCLE",
        "Em que estado está?",
        "architectural",
        "lifecycle/change management ISO 9001/27001",
        "DRAFT → IN_REVIEW → VALIDATED → APPROVED → ACTIVE → DEPRECATED → RETIRED (também SUSPENDED, SUPERSEDED). ACTIVE exige gates.",
    ),
    (
        "26",
        "CHANGE_IMPACT",
        "O que será afetado?",
        "architectural",
        "change/impact analysis, dependency graph",
        "Se a política mudar, o que quebra: control, schema, object, field, component, vertical, application.",
    ),
    (
        "27",
        "READINESS",
        "Está pronta?",
        "architectural",
        "assurance, release governance, DevSecOps",
        "NOT_READY | READY_FOR_REVIEW | READY_FOR_APPROVAL | RELEASE_READY | ACTIVE. Soma identidade…governação.",
    ),
    (
        "28",
        "ASSURANCE",
        "Como provamos continuamente?",
        "normative",
        "ISO/NIST, auditoria, continuous assurance",
        "Cadeia requirement → control → policy → implementation → test → gate → runtime → evidence → audit.",
    ),
]

FIELD_IDS = [row[1] for row in FIELDS]

PRINCIPLES = [
    ("P01", "Canonical Identity"),
    ("P02", "Explicit Authority"),
    ("P03", "Explicit Scope"),
    ("P04", "Explicit Applicability"),
    ("P05", "Deterministic Decision"),
    ("P06", "Explicit Constraints"),
    ("P07", "Explicit Enforcement"),
    ("P08", "Testability"),
    ("P09", "Evidence Generation"),
    ("P10", "Provenance"),
    ("P11", "Versionability"),
    ("P12", "Immutability of Released Versions"),
    ("P13", "Conflict Detection"),
    ("P14", "Exception Governance"),
    ("P15", "Human Governance"),
    ("P16", "Least Privilege"),
    ("P17", "Fail-Safe"),
    ("P18", "Traceability"),
    ("P19", "Observability"),
    ("P20", "Continuous Assurance"),
]

POLICY_TYPES = [
    "FOUNDATIONAL",
    "GOVERNANCE",
    "SECURITY",
    "PRIVACY",
    "DATA",
    "INTEGRITY",
    "IDENTITY",
    "ACCESS",
    "MASTER_DATA",
    "SOURCE",
    "NORMATIVE",
    "SEMANTIC",
    "CONTRACT",
    "API",
    "EVENT",
    "CONTENT",
    "ACCESSIBILITY",
    "SEO",
    "AGENT",
    "AI",
    "RUNTIME",
    "RELEASE",
    "ASSURANCE",
    "VERTICAL",
    "APPLICATION",
    "MODULE",
    "OBJECT",
    "FIELD",
]

POLICY_STATUSES = [
    "DRAFT",
    "IN_REVIEW",
    "VALIDATED",
    "APPROVED",
    "ACTIVE",
    "SUSPENDED",
    "DEPRECATED",
    "RETIRED",
    "SUPERSEDED",
]

MODALITIES = ["MUST", "MUST_NOT", "SHOULD", "SHOULD_NOT", "MAY"]
OUTCOMES = ["ALLOW", "DENY", "BLOCK", "REQUIRE", "WARN", "ESCALATE", "REVIEW", "DEFER"]
SEVERITIES = ["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL", "BLOCKER"]
CONFLICT_PRECEDENCE = [
    "CONSTITUTIONAL_FOUNDATION",
    "SECURITY_SAFETY",
    "LEGAL_REGULATORY",
    "NORMATIVE",
    "HORIZONTAL",
    "VERTICAL",
    "APPLICATION",
    "MODULE",
    "OBJECT",
    "FIELD",
]


def build() -> dict:
    fields = [
        {
            "seq": seq,
            "id": name,
            "question": question,
            "meaning": meaning,
            "base_kind": kind,
            "bases": bases,
            "status": "DOCUMENTADO_HOLD",
            "implemented": False,
        }
        for seq, name, question, kind, bases, meaning in FIELDS
    ]
    assert len(fields) == 28, len(fields)
    assert [f["id"] for f in fields] == FIELD_IDS
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
        "formula": "POLICY = AUTHORITY + APPLICABILITY + INTENT + SCOPE + SUBJECT + MODALITY + CONDITIONS + CONSTRAINTS + DECISION + OUTCOME + ENFORCEMENT + CONTRACT + IMPLEMENTATION + TESTS + CI + RUNTIME + OBSERVABILITY + EVIDENCE + PROVENANCE + GOVERNANCE + EXCEPTIONS + DEPENDENCIES + VERSIONING + LIFECYCLE + CHANGE IMPACT + READINESS + ASSURANCE",
        "architectural_principle": "POLICY IS NOT DOCUMENTATION. POLICY IS A GOVERNED EXECUTABLE CONTRACT.",
        "field_count": 28,
        "fields": fields,
        "principles": [{"id": pid, "name": name, "status": "DOCUMENTADO_HOLD"} for pid, name in PRINCIPLES],
        "policy_types": POLICY_TYPES,
        "policy_statuses": POLICY_STATUSES,
        "modalities": MODALITIES,
        "outcomes": OUTCOMES,
        "severities": SEVERITIES,
        "conflict_precedence": CONFLICT_PRECEDENCE,
        "conflict_rule": "Uma Policy de menor precedência não pode silenciosamente neutralizar uma Policy de maior precedência. Conflitos produzem POLICY_CONFLICT.",
        "readiness_gates": [
            "IDENTITY",
            "AUTHORITY",
            "NORMATIVE_MAPPING",
            "APPLICABILITY",
            "CONTROL",
            "SCOPE",
            "CONTRACT",
            "SCHEMA",
            "DECISION_LOGIC",
            "ENFORCEMENT",
            "TESTS",
            "CI_GATES",
            "EVIDENCE",
            "PROVENANCE",
            "GOVERNANCE",
            "VERSIONING",
        ],
        "maturity_target": "P6_CONTINUOUSLY_ASSURED",
        "maturity_current": "P2_GOVERNED_HOLD",
        "maturity_model": [
            "P0_INFORMAL",
            "P1_DOCUMENTED",
            "P2_GOVERNED",
            "P3_TESTABLE",
            "P4_EXECUTABLE",
            "P5_EVIDENCED",
            "P6_CONTINUOUSLY_ASSURED",
        ],
        "template_governance_rule": "Nenhum template HTML (tool, scale, calculator, page) pode existir fora deste contrato. CKO-POL-UT-001 especializa o molde e liga UTC-013/UTC-046 aos templates. Binding ≠ implantado ≠ ACTIVE.",
        "evaluation": {
            "verdict": "ACCEPTED_FROZEN_HOLD",
            "documentado": True,
            "implantado": False,
            "assured": False,
            "active": False,
            "findings": [
                {
                    "id": "PMC-F-COMPOSITE-AUTHORITY",
                    "severity": "NOTE",
                    "text": "Os 28 campos são estrutura composta (ISO/NIST/W3C/RFC/OPA/SHACL). A autoridade de cada especialização vem de fora — lei, norma, standard — não destes campos.",
                },
                {
                    "id": "PMC-F-TEMPLATE-MUST-SPECIALIZE",
                    "severity": "HOLD",
                    "text": "Templates tool/scale/calculator devem especializar este contrato via CKO-POL-UT-001. Sem binding o HTML é chrome não governado.",
                },
            ],
        },
        "rule": "AUTHORITY → NORMATIVE ATOM → APPLICABILITY → CONTROL → POLICY SPECIFICATION → CONTRACT → POLICY-AS-CODE → TEST → CI GATE → RUNTIME → EVIDENCE → ASSURANCE",
    }


def generate() -> dict:
    payload = build()
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    for dest in (OUT_POLICY, OUT_SITE, OUT_CASCADE):
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
    return payload


if __name__ == "__main__":
    doc = generate()
    print(f"wrote {OUT_POLICY} fields={doc['field_count']} status={doc['status']}")
