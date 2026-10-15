#!/usr/bin/env python3
"""Emit the directory-local Historical Policy & Decision Register.

Scope: this repository only. IndiciumFIN is out of scope.
This register does not approve policies, assign vigência, or replace CKO-MD/CKO-REG.
Documentado ≠ implantado ≠ ACTIVE ≠ RELEASE.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

GATE = Path(__file__).resolve().parents[1]
SITE = GATE.parent / "reference-website"
STAMP_NAME = "CKO-DIRECTORY-GOVERNANCE-HOLD.json"

# Instant this directory was read for the register. Not a vigência date.
RECORDED_AT = "2026-10-14T23:10:00Z"


def decision(
    hid: str,
    *,
    text: str,
    disposition: str,
    domain: str,
    observed_in: list[str],
    status: str,
    note: str,
) -> dict:
    return {
        "id": hid,
        "text": text,
        "disposition": disposition,
        "domain": domain,
        "observed_in": observed_in,
        "documentary_status": status,
        "assigns_vigencia": False,
        "note": note,
    }


def payload() -> dict:
    return {
        "id": "CKO-DIRECTORY-GOVERNANCE-HOLD",
        "title": "Registo histórico de decisões — diretório actual",
        "kind": "historical_decision_register",
        "version": "0.1.0",
        "recorded_at": RECORDED_AT,
        "scope": "this_directory_only",
        "excludes": [
            "IndiciumFIN/calculadorasdeenfermagem",
            "IndiciumFIN CI || echo",
            "IndiciumFIN process Vigente automático",
            "kauesp0007/calculadoras-de-enfermagem orquestrador.js",
        ],
        "new_architectural_root": False,
        "replaces_cko_md": False,
        "replaces_cko_reg": False,
        "replaces_fail_closed": False,
        "replaces_universal_tool": False,
        "replaces_human_decisions": False,
        "replaces_source_registry": False,
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
        "authority": {
            "note": "Identidade canónica continua em CKO-MD e CKO-REG. Este registo só mapeia decisões e contratos já presentes neste diretório.",
            "canonical_ids": ["CKO-MD", "CKO-REG"],
        },
        "executable_here": [
            {
                "id": "POL-CKO-FAIL-CLOSED-1.0.0",
                "path": "cko-controlled/public/policies/fail-closed.json",
                "kind": "policy-as-code",
                "class": "implemented_control",
                "note": "31 deny_if. Raiz da cascata. Não é a biblioteca de 19 políticas.",
            },
            {
                "id": "POL-CKO-UNIVERSAL-TOOL-1.3.0",
                "document_id": "CKO-POL-UT-001",
                "path": "cko-controlled/public/policies/universal-tool.json",
                "kind": "policy-as-code",
                "class": "documented_control",
                "document_version": "1.3.0",
                "export_lineage": "1.5.0",
                "snapshot_delta": "1.6.0",
                "implemented_n": 0,
                "implantado": False,
                "version_lineage": "VERSION_DRIFT_HOLD",
                "note": "Não unificar 1.3.0 / 1.5.0 / 1.6.0.",
            },
            {
                "id": "POL-CKO-MD-REG-FRONTEND-1.0.0",
                "path": "cko-controlled/public/policies/md-reg-frontend.json",
                "kind": "policy-as-code",
                "class": "implemented_control",
                "fields_classified": 2496,
                "bindings_classified": 10913,
                "materialized_field_bindings": False,
            },
            {
                "id": "CKO-HOLD-HUMAN-1.0.0",
                "path": "cko-controlled/public/data/human-decisions.json",
                "kind": "hold-human-non-blocking",
                "class": "implemented_control",
                "blocking_inspect": False,
                "blocking_ci": False,
                "blocking_release": True,
                "items_n": 9,
            },
            {
                "id": "CKO-CALENF-GOVERNANCE-1.0.0",
                "path": "reference-website/data/cko/governance.json",
                "kind": "calenf-runtime-governance",
                "class": "implemented_control",
                "nursePalm": "NOT_ASSERTED",
                "agentic": "NOT_ASSERTED",
                "digitalTwin_observed": False,
            },
            {
                "id": "CKO-CONTROLLED-GATE",
                "path": ".github/workflows/cko-controlled-gate.yml",
                "kind": "ci_gate",
                "class": "implemented_control",
                "masks_errors": False,
                "note": "Corre generate → sync → testes → asserts. Sem || echo. Não homologa produção.",
            },
        ],
        "families_absent_from_this_directory": [
            {
                "id": "CKO-POL-REGISTRY-2026-08-24",
                "kind": "19_policies",
                "disposition": "HOLD",
                "present": False,
                "note": "Inventário histórico. Só UT está projectada aqui.",
            },
            {
                "id": "CKO-POL-MAN-001",
                "kind": "11_versioned_policies",
                "disposition": "HOLD",
                "present": False,
                "note": "Família de 28/08. Não somar com as 19.",
            },
            {
                "id": "CKO-NOR-WORKBOOK-0.1.0",
                "kind": "10_nor_policies_proposed",
                "disposition": "HOLD",
                "present": False,
                "note": "PROPOSTO / FOR REVIEW. Não operacional.",
            },
        ],
        "incident_packages": {
            "v0_1_incident_impact": {
                "present_in_this_directory": False,
                "disposition": "REFERENCE_ONLY",
                "promotes_policy": False,
            },
            "v0_2_incident_continuity": {
                "present_in_this_directory": False,
                "disposition": "REFERENCE_ONLY",
                "promotes_policy": False,
            },
            "note": "Escrever o contrato não aprova a política. Pacotes candidatos ficam fora do working set até objecto MD e aprovação.",
        },
        "decisions": [
            decision(
                "HIST-001",
                text="Master Data / Canonical Control Plane detém o estado canónico. Kernel e agentes não são autoridade semântica.",
                disposition="KEEP",
                domain="GOV",
                observed_in=[
                    "cko-controlled/public/policies/md-reg-frontend.json",
                    "cko-controlled/public/policies/fail-closed.json",
                ],
                status="registered_and_projected",
                note="Alinhado com POL-CKO-MD-REG-FRONTEND-1.0.0.",
            ),
            decision(
                "HIST-002",
                text="Regulatory Core controla aplicabilidade normativa. Downstream não contorna o vínculo exigido.",
                disposition="KEEP",
                domain="REG",
                observed_in=["cko-controlled/public/policies/md-reg-frontend.json"],
                status="registered_and_projected",
                note="10913 bindings classificados; não materializados.",
            ),
            decision(
                "HIST-003",
                text="Policy-as-code é independente de prompts. Instrução de agente não substitui PEP.",
                disposition="KEEP",
                domain="AI",
                observed_in=["cko-controlled/public/policies/fail-closed.json"],
                status="registered_and_projected",
                note="Cascata começa em policy-as-code. PEP/Work Order runtime NOT_VERIFIED neste disco.",
            ),
            decision(
                "HIST-004",
                text="Kernel executa contratos e validadores previamente aprovados. Não inventa políticas, estados ou regras.",
                disposition="KEEP",
                domain="TEC",
                observed_in=["cko-controlled/public/engine/core.js"],
                status="registered_and_projected",
                note="core.js avalia deny_if. Não cria política nova.",
            ),
            decision(
                "HIST-006",
                text="Agent ≠ Authority. Selecção ou atribuição de tarefa não é permissão.",
                disposition="KEEP",
                domain="AI",
                observed_in=["reference-website/data/cko/governance.json"],
                status="registered_and_projected",
                note="AGT-ORCH-001 operacional NOT_ASSERTED. Maker ≠ Checker ≠ Auditor declarado.",
            ),
            decision(
                "HIST-007",
                text="Maker ≠ Checker ≠ Auditor. Autoaprovação e autopromoção são proibidas.",
                disposition="KEEP",
                domain="GOV",
                observed_in=[
                    "cko-controlled/public/policies/universal-tool.json",
                    "reference-website/data/cko/governance.json",
                ],
                status="registered_and_projected",
                note="Independência declarada. Recertificação B7 continua HOLD humano.",
            ),
            decision(
                "HIST-010",
                text="Runtime log ≠ Evidence ≠ Assurance. Telemetria não prova conformidade.",
                disposition="KEEP",
                domain="AUD",
                observed_in=["cko-controlled/public/policies/fail-closed.json"],
                status="registered_and_projected",
                note="DISCOVERY_IS_NOT_EVIDENCE e RUNTIME_OBSERVED_NOT_INFERRED.",
            ),
            decision(
                "HIST-011",
                text="Falha, HOLD ou evidência incompleta não viram PASS. Fail-closed.",
                disposition="KEEP",
                domain="GOV",
                observed_in=[
                    "cko-controlled/public/policies/fail-closed.json",
                    "cko-controlled/public/data/human-decisions.json",
                ],
                status="registered_and_projected",
                note="HOLD humano não bloqueia CI e continua a negar release.",
            ),
            decision(
                "HIST-012",
                text="Factory gera candidatos. Não aprova, promove ou publica unilateralmente.",
                disposition="KEEP",
                domain="EDI",
                observed_in=["cko-controlled/public/policies/fail-closed.json"],
                status="registered_and_projected",
                note="RIGHTS_CHAIN_REQUIRED_TO_PUBLISH e RELEASE_FAIL_CLOSED.",
            ),
            decision(
                "HIST-013",
                text="Universal Tool Policy define requisitos. Standard Guard só fiscaliza.",
                disposition="KEEP",
                domain="CLI",
                observed_in=["cko-controlled/public/policies/universal-tool.json"],
                status="registered_and_projected",
                note="UT_POLICY_HOLD. implemented_n=0. Calculadoras e escalas PAUSED.",
            ),
            decision(
                "HIST-015",
                text="Fonte da verdade lógica pode ter múltiplos armazenamentos. Um repositório físico não é dono de todos os domínios.",
                disposition="KEEP",
                domain="GOV",
                observed_in=["cko-controlled/public/data/CKO-DRIVE-SUPABASE-TRUTH-INDEX-HOLD.json"],
                status="registered_and_projected",
                note="Índice observado Drive × Supabase. Sem IndiciumFIN.",
            ),
            decision(
                "HIST-016",
                text="Versões aprovadas não são sobrescritas. Changeset, impacto, migração, regressão e lineage.",
                disposition="KEEP",
                domain="TEC",
                observed_in=["cko-controlled/public/policies/universal-tool.json"],
                status="registered_and_projected",
                note="VERSION_DRIFT_HOLD em UT 1.3 / 1.5 / 1.6.",
            ),
            decision(
                "HIST-017",
                text="Nenhum claim fictício de conformidade. Distinguir desenho, implementação e operação comprovada.",
                disposition="KEEP",
                domain="AUD",
                observed_in=["cko-controlled/public/policies/universal-tool.json"],
                status="registered_and_projected",
                note="documentado=true, implantado=false, assured=false na UT.",
            ),
            decision(
                "HIST-018",
                text="CONTROL_PLANE_PASS ≠ RUNTIME_PASS ≠ RELEASED.",
                disposition="KEEP",
                domain="REL",
                observed_in=["cko-controlled/public/data/human-decisions.json"],
                status="registered_and_projected",
                note="CI PASS deste gate não é homologação clínica nem release.",
            ),
            decision(
                "HIST-019",
                text="Extração prioriza fontes públicas, gratuitas e sem cadastro. Incompatíveis = REFERENCE_ONLY / LICENSE_BLOCKED / NOT_ELIGIBLE_FOR_EXTRACTION.",
                disposition="KEEP",
                domain="MIN",
                observed_in=[],
                status="recovered_not_objected",
                note="Decisão 04/10. Sem objecto canónico próprio neste disco.",
            ),
            decision(
                "HIST-020",
                text="ISO sem acesso integral autorizado: metadado VERIFY_PENDING; sem cláusula inventada.",
                disposition="KEEP",
                domain="REG",
                observed_in=[],
                status="recovered_not_objected",
                note="Não promove afirmação normativa sem suporte.",
            ),
            decision(
                "HIST-021",
                text="Design System oficial único. Hero é MEDIA, não autoridade de DS. Leitura obrigatória da baseline.",
                disposition="KEEP",
                domain="BRA",
                observed_in=["cko-controlled/public/data/design-system.json"],
                status="registered_and_projected",
                note="CE-DS-POL-001 v1.0.0 recuperada; implementação em agentes/CI NOT_VERIFIED.",
            ),
            decision(
                "HIST-022",
                text="Disclaimer não elimina responsabilidade da plataforma pelo conteúdo, evidências, regras, funcionamento, monitorização e comunicação.",
                disposition="KEEP",
                domain="COM",
                observed_in=["cko-controlled/public/policies/universal-tool.json"],
                status="registered_and_projected",
                note="DISCLAIMER-CLINICAL-EDU-001 ainda present_as_governed_object=false.",
            ),
            decision(
                "HIST-023",
                text="Cadeia FINDING → ROOT CAUSE → LEARNING → CORRECTION → REGRESSION → REPERFORMANCE → RECERTIFICATION.",
                disposition="KEEP",
                domain="AUD",
                observed_in=[
                    "cko-controlled/scripts/generate_universe.py",
                    "cko-controlled/scripts/generate_pendencies.py",
                ],
                status="registered_and_projected",
                note="PEND-PDF-FINDINGS-BUCKET usa CYCLE_FINDING_ROOTCAUSE_LEARNING_REPERF_RECERT. Contrato de incidente ausente.",
            ),
            decision(
                "HIST-024",
                text="Princípio de consequências reais e confiança institucional: erro não se encerra com documentação, correção pontual ou ticket. Avaliar causa, exposição, efeito, pessoas, imagem, propagação e eficácia. Comunicação e publicação ficam fora do próprio registo de incidente.",
                disposition="KEEP",
                domain="GOV",
                observed_in=[],
                status="recovered_not_objected",
                note="Princípio recuperado (ago–out/2026). Redacção consolidada NÃO é política aprovada. Reputação é consequência transversal, não domínio novo. Pacotes v0.1/v0.2 = REFERENCE_ONLY.",
            ),
            decision(
                "HIST-025",
                text="Diagnóstico de erro também pode estar errado. Finding e retratação fundamentada ficam no histórico.",
                disposition="KEEP",
                domain="AUD",
                observed_in=[],
                status="recovered_not_objected",
                note="Braden / Gotejamento 22/08. Sem apagar o finding original.",
            ),
            decision(
                "HIST-026",
                text="PASS técnico não determina sozinho o fecho de auditoria. Avaliar findings, suficiência da evidência e risco residual.",
                disposition="KEEP",
                domain="AUD",
                observed_in=["cko-controlled/public/data/unknown-universe.json"],
                status="registered_and_projected",
                note="1 recertificação FAIL permanece UNK-SECURITY-RECERT.",
            ),
            decision(
                "HIST-027",
                text="Aparência de credibilidade sem factos verificáveis é risco reputacional. Números públicos exigem fonte, métrica, data e consistência.",
                disposition="KEEP",
                domain="EDI",
                observed_in=[],
                status="recovered_not_objected",
                note="Achado P0 histórico 04/09 (alcance/estatísticas). Não recontado neste registo.",
            ),
            decision(
                "HIST-029",
                text="Normas, ferramentas (calculadoras, escalas) e bibliotecas são objectos canónicos. O HTML é projecção de um template por kind. Canonical não é published, não é Vigente e não é release.",
                disposition="KEEP",
                domain="MD",
                observed_in=[
                    "cko-controlled/scripts/generate_canonical_catalog.py",
                    "cko-controlled/scripts/generate_norm_instrument.py",
                    "reference-website/data/tools",
                    "reference-website/biblioteca",
                ],
                status="registered_and_projected",
                note="Famílias etc. (protocolo, checklist, simulado, diretriz, template) são o mesmo contrato. UT implemented_n=0. Sem promoção.",
            ),
            decision(
                "HIST-028",
                text="Publicação não encerra responsabilidade. Monitorização posterior e reavaliação continuam.",
                disposition="KEEP",
                domain="EDI",
                observed_in=["cko-controlled/public/data/human-decisions.json"],
                status="registered_and_projected",
                note="HOLD-HUMAN-OBSERVED-RUNTIME e B7 recert.",
            ),
            decision(
                "HIST-005",
                text="AGT-ORCH-001 solicita Work Orders. Serviço governado formaliza. Estado permanece no plano canónico.",
                disposition="HOLD",
                domain="AI",
                observed_in=["reference-website/data/cko/governance.json"],
                status="declared_not_verified",
                note="Agentes listados. Work Order / PEP runtime NOT_VERIFIED. Sem IndiciumFIN.",
            ),
            decision(
                "HIST-009",
                text="Sigstore exigido para evidência governada quando o contrato o pedir.",
                disposition="HOLD",
                domain="AUD",
                observed_in=[],
                status="requirement_not_verified",
                note="Requisito histórico. Operação real NOT_VERIFIED neste disco.",
            ),
            decision(
                "HIST-CONST",
                text="Constituição CKO e Charter de Governança (sete domínios) como autoridade máxima.",
                disposition="HOLD",
                domain="GOV",
                observed_in=[],
                status="proposed_not_ratified",
                note="Ratificação formal não demonstrada neste diretório. Não promover.",
            ),
        ],
        "directory_working_set": {
            "identity": ["CKO-MD", "CKO-REG"],
            "policy_as_code": [
                "POL-CKO-FAIL-CLOSED-1.0.0",
                "POL-CKO-UNIVERSAL-TOOL-1.3.0",
                "POL-CKO-MD-REG-FRONTEND-1.0.0",
            ],
            "human": "CKO-HOLD-HUMAN-1.0.0",
            "observed_catalog": "CKO-DRIVE-SUPABASE-TRUTH-INDEX-HOLD",
            "this_register": "CKO-DIRECTORY-GOVERNANCE-HOLD",
            "canonical_catalog": "CKO-CANONICAL-OBJECTS-HOLD",
            "runtime_pages_n": 12,
            "institutional_page_count_locked": True,
            "this_page_is_not_a_13th_runtime_page": True,
        },
        "unknowns": [
            {
                "id": "UNK-POLICY-REGISTRY-FILE",
                "statement": "policy-registry.json das 19 políticas não está neste diretório.",
            },
            {
                "id": "UNK-INCIDENT-OBJECT",
                "statement": "Não existe objecto MD de incidente/consequência/reputação neste disco.",
            },
            {
                "id": "UNK-PEP-RUNTIME",
                "statement": "Work Order + PEP declarados na história; sem execução verificável aqui.",
            },
            {
                "id": "UNK-SIGSTORE",
                "statement": "Assinatura governada exigida em conversas; operação NOT_VERIFIED.",
            },
        ],
        "findings": [
            {
                "id": "FND-GOV-DOCUMENTED-NOT-IMPLANTED",
                "severity": "high",
                "statement": "UT documentada com 98 controlos e implemented_n=0. Aparência de política ≠ política operacional.",
            },
            {
                "id": "FND-GOV-NO-INCIDENT-CONTRACT",
                "severity": "high",
                "statement": "O ciclo de finding existe como pendência; falta o contrato que liga consequência, imagem, learning e recertificação sem autorizar publicação.",
            },
        ],
        "single_base": {
            "what_this_is": "Um único registo HOLD das decisões e contratos deste diretório, com disposição KEEP/HOLD/REFERENCE_ONLY e sem vigência automática.",
            "what_this_is_not": [
                "Política nova aprovada",
                "Saneamento do IndiciumFIN",
                "Substituição de CKO-MD / CKO-REG / fail-closed",
                "Release, ACTIVE operacional ou fecho de B9",
                "Promoção dos pacotes Incident Impact v0.1 / Continuity v0.2",
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
        "generated_by": "cko-controlled/scripts/generate_directory_governance.py",
    }
    write_json(GATE / "public" / "data" / STAMP_NAME, body)
    write_json(SITE / "data" / "cko" / STAMP_NAME, body)
    return body


if __name__ == "__main__":
    out = generate()
    print("directory_governance", out["id"], out["materialization"]["sha256"])
