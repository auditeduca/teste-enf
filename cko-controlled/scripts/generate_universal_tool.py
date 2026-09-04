#!/usr/bin/env python3
"""Emit CKO-POL-UT-001 v1.3.0 as fail-closed policy-as-code.

This is an evaluation object. DOCUMENTADO ≠ IMPLANTADO ≠ ASSURED.
Clinical Calculators / Scales remain PAUSED. No UTC is marked implemented.
"""
from __future__ import annotations

import json
from pathlib import Path

GATE = Path(__file__).resolve().parents[1]
SITE = GATE.parent / "reference-website"
OUT_POLICY = GATE / "public" / "policies" / "universal-tool.json"
OUT_SITE = SITE / "data" / "cko" / "universal-tool.json"

CASCADE = [
    "policy-as-code",
    "schemas",
    "graph-constraints",
    "CI-gates",
    "runtime-assertions",
    "automatic-evidence",
]

CONTROLS = [
    ("UTC-001", "Governance", "CKO-REG", "Norma/fonte autoritativa precede requisito, MD e ferramenta"),
    ("UTC-002", "Governance", "CKO-MD", "Binding governado em nível de campo"),
    ("UTC-003", "Governance", "CKO-MD", "Proibição de verdade clínica inline em HTML/JS/template"),
    ("UTC-004", "Identity", "CKO-MD", "canonical_id estável, UUIDv7, business key, version_ref"),
    ("UTC-005", "Versioning", "CKO-REG", "Version-on-change sem overwrite silencioso"),
    ("UTC-006", "Agents", "CKO-REG", "Maker ≠ Checker ≠ Auditor"),
    ("UTC-007", "Assurance", "CKO-REG", "CAAT, IPE e AUD-8L por camada"),
    ("UTC-008", "Source acquisition", "CKO-REG", "Official/API-first"),
    ("UTC-009", "Libraries", "LYR-LIB-001", "Bibliotecas como objetos canônicos"),
    ("UTC-010", "Medication master data", "LYR-MED-001", "Medicamento separado em objetos/relações"),
    ("UTC-011", "Device master data", "LYR-LIB-001", "Dispositivos com classificação e relações"),
    ("UTC-012", "Terminologies", "LYR-TERM-001", "Code systems com release, rights e mappings"),
    ("UTC-013", "Tool anatomy", "LYR-CLIN-CALC-001", "Universal Tool Contract"),
    ("UTC-014", "About tool", "LYR-CLIN-CALC-001", "Sobre a ferramenta declara escopo e limitações"),
    ("UTC-015", "Population", "CKO-MD", "Population/applicability é objeto do MD"),
    ("UTC-016", "Patient context", "LYR-CLIN-RULE-001", "Contexto mínimo; observations de runtime"),
    ("UTC-017", "Vital signs", "CKO-MD", "Sinais vitais canônicos no MD"),
    ("UTC-018", "Inputs", "LYR-CLIN-CALC-001", "Input Contract"),
    ("UTC-019", "Required fields", "LYR-CLIN-RULE-001", "Obrigatoriedade declarativa"),
    ("UTC-020", "Parsing", "LYR-I18N-001", "Parser numérico locale-aware"),
    ("UTC-021", "Measure conversion", "CKO-MD", "Conversão dimensional fail-closed"),
    ("UTC-022", "Anomalies", "LYR-CLIN-RULE-001", "Bloqueadores de anomalia"),
    ("UTC-023", "State machine", "LYR-CLIN-CALC-001", "Estados NOT_EVALUATED…ERROR"),
    ("UTC-024", "Formula engine", "LYR-CLIN-CALC-001", "Fórmula determinística versionada"),
    ("UTC-025", "Rule engine", "LYR-CLIN-RULE-001", "Regras declarativas source-backed"),
    ("UTC-026", "Inference", "LYR-CLIN-RULE-001", "Inferência classificada com allowed_use"),
    ("UTC-027", "AI", "LYR-CLIN-RULE-001", "IA não altera fórmula/threshold/dose/norma"),
    ("UTC-028", "Result", "LYR-CLIN-CALC-001", "Result Contract"),
    ("UTC-029", "Interpretation", "LYR-CLIN-RULE-001", "Interpretação separada do cálculo bruto"),
    ("UTC-030", "Calculation memory", "LYR-CLIN-CALC-001", "Memória de cálculo com replay hash"),
    ("UTC-031", "SAE", "LYR-CLIN-RULE-001", "SAE orquestra evidência; NANDA só homologado"),
    ("UTC-032", "Medication safety", "LYR-CLIN-RULE-001", "Certos de medicamentos versionados"),
    ("UTC-033", "Patient safety goals", "LYR-CLIN-RULE-001", "Metas de segurança como objetos"),
    ("UTC-034", "Tips", "LYR-CLIN-RULE-001", "Dicas governadas com source binding"),
    ("UTC-035", "Common errors", "LYR-CLIN-RULE-001", "Erros comuns com condition/recovery"),
    ("UTC-036", "Related tools", "LYR-REC-001", "Relações tipadas, nunca lista aleatória"),
    ("UTC-037", "Related libraries", "LYR-REC-001", "Bibliotecas resolvidas pelo grafo"),
    ("UTC-038", "Tool handoff", "LYR-REC-001", "ToolHandoffContract"),
    ("UTC-039", "Visibility", "LYR-UI-001", "Progressive disclosure"),
    ("UTC-040", "Feedback", "LYR-UI-001", "FeedbackEvent reutilizável"),
    ("UTC-041", "Tooltips", "LYR-UI-001", "Crítico não existe só no tooltip"),
    ("UTC-042", "Tour", "LYR-UI-001", "Tour versionado e acessível"),
    ("UTC-043", "Progress", "LYR-UI-001", "Progresso real; sem percentual fictício"),
    ("UTC-044", "Responsive", "LYR-DS-001", "Mobile-first; verdade clínica invariante"),
    ("UTC-045", "Design system", "LYR-DS-001", "DS oficial; sem CSS por página"),
    ("UTC-046", "Page template", "LYR-PAGE-TPL-001", "Anatomia declarativa"),
    ("UTC-047", "Document/PDF template", "LYR-DOC-TPL-001", "Export profile; não imprime o DOM"),
    ("UTC-048", "Bibliography", "LYR-REF-001", "Referências visíveis; audit bindings ocultos"),
    ("UTC-049", "Evidence level", "LYR-REF-001", "Framework declarado; sem badge A/B arbitrário"),
    ("UTC-050", "Regulatory change badge", "LYR-MON-001", "Badge humano de mudança normativa"),
    ("UTC-051", "Routes", "LYR-ROUTE-001", "Canonical do Route Registry"),
    ("UTC-052", "SEO", "LYR-SEO-001", "SEO derivado de objetos canônicos"),
    ("UTC-053", "Open Graph", "LYR-OG-001", "OG derivado de objeto + route + locale"),
    ("UTC-054", "Structured data", "LYR-SEM-001", "JSON-LD derivado do tipo canônico"),
    ("UTC-055", "i18n", "LYR-I18N-001", "IDs invariáveis; labels localizados"),
    ("UTC-056", "Media", "LYR-MEDIA-001", "Assets com ID, rights, alt e hash"),
    ("UTC-057", "Charts", "LYR-UI-001", "VisualizationContract"),
    ("UTC-058", "Favorites", "LYR-USERSTATE-001", "User State referencia canonical IDs"),
    ("UTC-059", "Persistence", "LYR-PRV-001", "Persistência por campo"),
    ("UTC-060", "Clinical data privacy", "LYR-PRV-001", "Observations fora de analytics/ads"),
    ("UTC-061", "Share", "LYR-UI-001", "Sharebar distingue ferramenta vs resultado"),
    ("UTC-062", "Security", "LYR-SEC-001", "Escaping, injection, source trust"),
    ("UTC-063", "Advertising", "LYR-ANL-001", "Advertising Intelligence governada"),
    ("UTC-064", "Advertising safety", "LYR-PRV-001", "Ads nunca usam valores clínicos"),
    ("UTC-065", "Analytics", "LYR-ANL-001", "Allowlist; sem valor clínico bruto"),
    ("UTC-066", "Funnels", "LYR-ANL-001", "Funis de jornada sem dado sensível"),
    ("UTC-067", "Observability", "LYR-OBS-001", "Trace técnico separado de product analytics"),
    ("UTC-068", "Performance", "LYR-PERF-001", "Budgets de runtime/PDF/ads"),
    ("UTC-069", "Reliability", "LYR-REL-001", "Retries/cancel/idempotency governados"),
    ("UTC-070", "Sustainability", "LYR-SUS-001", "Reuso de assets e lógica"),
    ("UTC-071", "Renderer", "LYR-RND-001", "Renderer não contém fórmula clínica"),
    ("UTC-072", "Runtime", "LYR-RUN-001", "E2E dos comportamentos essenciais"),
    ("UTC-073", "PDF export", "LYR-EXPORT-001", "PDF só com campos permitidos"),
    ("UTC-074", "Publication", "LYR-PUB-001", "Release gate bloqueia HOLD a montante"),
    ("UTC-075", "Monitoring", "LYR-MON-001", "Monitoramento normativo pós-release"),
    ("UTC-076", "Privacy", "LYR-PRV-001", "NO_SENSITIVE_CAPTURE"),
    ("UTC-077", "Privacy", "LYR-PRV-001", "Contexto clínico efêmero e não identificável"),
    ("UTC-078", "Analytics", "LYR-ANL-001", "Valores clínicos fora de analytics/ads/logs"),
    ("UTC-079", "References", "LYR-REF-001", "URL direta à fonte primária"),
    ("UTC-080", "References", "LYR-REF-001", "ABNT NBR 6023:2025 como baseline"),
    ("UTC-081", "Citations", "LYR-REF-001", "ABNT NBR 10520:2023"),
    ("UTC-082", "Citations", "CKO-REG", "Pinpoint locator legal/técnico"),
    ("UTC-083", "IP", "CKO-REG", "Antiplágio Lei 9.610/1998, CP art. 184, Lei 9.609/1998"),
    ("UTC-084", "IP", "LYR-CLIN-RULE-001", "Fórmulas não são exclusividade autoral; provenance obrigatória"),
    ("UTC-085", "IP", "CKO-REG", "Expressão protegida não pode ser copiada sem base"),
    ("UTC-086", "Software IP", "LYR-SEC-001", "Código/deps com origem, versão e licença"),
    ("UTC-087", "Official Sources", "CKO-REG", "Atos oficiais com fonte, vigência e snapshot"),
    ("UTC-088", "Rounding", "LYR-CLIN-RULE-001", "ABNT NBR 5891:2014 baseline"),
    ("UTC-089", "Rounding", "LYR-CLIN-RULE-001", "calculation_precision ≠ display_precision"),
    ("UTC-090", "Rounding", "LYR-CLIN-RULE-001", "Regra da fonte prevalece sobre baseline"),
    ("UTC-091", "i18n/Citation", "LYR-I18N-001", "Citação traduzida preserva fonte e idioma"),
    ("UTC-092", "AI/References", "LYR-CONTENT-001", "IA não substitui referência primária"),
    ("UTC-093", "Disclaimer", "CKO-REG", "Aviso educacional/apoio profissional"),
    ("UTC-094", "Disclaimer", "CKO-REG", "Uso educacional não autoriza ato privativo"),
    ("UTC-095", "Disclaimer", "CKO-REG", "Disclaimer não é waiver genérico"),
    ("UTC-096", "Disclaimer visibility", "LYR-UI-001", "Versão curta sempre visível"),
    ("UTC-097", "Disclaimer emergency", "LYR-CLIN-RULE-001", "Aviso de urgência condicional"),
    ("UTC-098", "Disclaimer versioning/export", "LYR-EXPORT-001", "Perfil de disclaimer versionado no PDF"),
]


def build() -> dict:
    controls = [
        {
            "id": cid,
            "domain": domain,
            "primary_layer": layer,
            "requirement": req,
            "status": "DOCUMENTADO_HOLD",
            "implemented": False,
            "assured": False,
            "canonical_promotion": False,
        }
        for cid, domain, layer, req in CONTROLS
    ]
    assert len(controls) == 98, len(controls)
    assert [c["id"] for c in controls] == [f"UTC-{i:03d}" for i in range(1, 99)]
    return {
        "id": "POL-CKO-UNIVERSAL-TOOL-1.3.0",
        "kind": "policy-as-code",
        "mode": "fail-closed",
        "root": False,
        "starts_at": "policy-as-code",
        "parent": "POL-CKO-FAIL-CLOSED-1.0.0",
        "document_id": "CKO-POL-UT-001",
        "document_version": "1.3.0",
        "document_date": "2026-08-22",
        "document_status": "POLITICA_CONTROLADA",
        "cascade": CASCADE,
        "release": "HOLD / NOT_RELEASED",
        "release_allowed": False,
        "published": False,
        "operational": "NOT_ASSERTED",
        "canonical_promotion": False,
        "control_count": 98,
        "implemented_n": 0,
        "assured_n": 0,
        "documentado": True,
        "implantado": False,
        "assured": False,
        "md_gate": "REMEDIATION_REQUIRED_NORMATIVE_GATE",
        "clinical_calculators": "PAUSED",
        "scales_scores": "PAUSED",
        "field_authority": {
            "policy_bound": 44,
            "policy_hold": 8,
            "classified_md_holds_n": 11,
            "classified_fields": 2496,
            "materialized_field_bindings": False,
            "same_set_as_classified": False,
            "note": "44 BOUND / 8 HOLD é o claim da política v1.3.0; CKO-MD classificado tem holds_n=11 e bindings não materializados. Não unificar.",
        },
        "abnt": {
            "nbr_6023": {"edition": "2025", "supersedes": "2018", "clause_level": "HOLD"},
            "nbr_10520": {"edition": "2023", "clause_level": "HOLD"},
            "nbr_5891": {"edition": "2014", "clause_level": "HOLD", "role": "rounding_baseline"},
        },
        "inventory_agent": {
            "id": "AGENT-INVENTORY-001",
            "authorized": True,
            "present": False,
            "operational": "NOT_ASSERTED",
            "canonical_promotion": False,
        },
        "disclaimer_profile": {
            "id": "DISCLAIMER-CLINICAL-EDU-001",
            "present_as_governed_object": False,
            "compact_required": (
                "Esta ferramenta tem finalidade educacional e de apoio à prática. "
                "Não substitui avaliação clínica, julgamento profissional, protocolos "
                "institucionais nem atos privativos de profissional legalmente habilitado."
            ),
        },
        "privacy": {
            "principle": "NO_SENSITIVE_CAPTURE",
            "present_as_governed_object": False,
        },
        "version_lineage": {
            "status": "VERSION_DRIFT_HOLD",
            "evaluated": "1.3.0",
            "export_lineage": "OV-CKO-POL-UT-001-1.5.0",
            "snapshot_delta": "CKO-POL-UT-001-v1.6.0-Tool-Resource-Profile-delta.json",
            "note": "Não unificar 1.3.0 / 1.5.0 / 1.6.0. Drift permanece HOLD.",
        },
        "evaluation": {
            "date": "2026-09-03",
            "verdict": "DOCUMENTADO_HOLD_NOT_IMPLEMENTED",
            "documentado": True,
            "implantado": False,
            "assured": False,
            "clinical_promotion": "DENIED",
            "findings": [
                {
                    "id": "UT-F-VERSION-DRIFT",
                    "severity": "HOLD",
                    "text": "Texto avaliado é v1.3.0; snapshot mapeia delta v1.6.0 em LYR-CLIN-CALC-001; lineage de export cita 1.5.0.",
                },
                {
                    "id": "UT-F-NO-UTC-CATALOG",
                    "severity": "HOLD",
                    "text": "UTC-001…UTC-098 não existiam como policy-as-code executável antes desta materialização HOLD.",
                },
                {
                    "id": "UT-F-INLINE-CLINICAL",
                    "severity": "HOLD",
                    "text": "UTC-003 violado no overlay CALENF: fórmulas, escores, interpretações e canonical SEO estão em HTML/tool-config; status published contradiz PAUSED.",
                },
                {
                    "id": "UT-F-MD-GATE",
                    "severity": "HOLD",
                    "text": "CKO-MD permanece REMEDIATION_REQUIRED_NORMATIVE_GATE. Field bindings não materializados. Calculators/Scales herdam o bloqueio.",
                },
                {
                    "id": "UT-F-FIELD-COUNT-MISMATCH",
                    "severity": "HOLD",
                    "text": "Política declara 44 BOUND / 8 HOLD; snapshot classificado declara 2496 campos e 11 holds em CKO-MD. Conjuntos distintos.",
                },
                {
                    "id": "UT-F-INVENTORY-AGENT-ABSENT",
                    "severity": "HOLD",
                    "text": "AGENT-INVENTORY-001 autorizado pela política mas ausente no runtime/governança operacional.",
                },
                {
                    "id": "UT-F-DISCLAIMER-DRIFT",
                    "severity": "HOLD",
                    "text": "Ferramentas têm disclaimer semelhante, não o perfil DISCLAIMER-CLINICAL-EDU-001 nem o texto compacto obrigatório.",
                },
                {
                    "id": "UT-F-ABNT-CLAUSE-HOLD",
                    "severity": "HOLD",
                    "text": "Cutover 6023:2025 registado; extração clause-level de 6023/10520/5891 permanece HOLD até exemplar autorizado.",
                },
                {
                    "id": "UT-F-DS-PARTIAL",
                    "severity": "NOTE",
                    "text": "UTC-045 tem correspondência parcial: catálogo DS vivo via render, HOLD / NOT_RELEASED, raiz em policy-as-code. Não fecha o contrato universal da ferramenta.",
                },
                {
                    "id": "UT-F-AGENTS-DECLARED",
                    "severity": "NOTE",
                    "text": "UTC-006 está declarado (maker!=checker!=auditor) com operational NOT_ASSERTED. Não é evidência de segregação em runtime.",
                },
            ],
        },
        "controls": controls,
        "rule": "Fonte/Norma → Requisito → CKO-REG → CKO-MD → Tool Contract → Engines → Safety/SAE → Renderer → Assurance → Release. Nenhum UTC PASS enquanto md_gate for REMEDIATION_REQUIRED_NORMATIVE_GATE.",
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
    print(f"wrote {OUT_POLICY} controls={doc['control_count']} verdict={doc['evaluation']['verdict']}")
