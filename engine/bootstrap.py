"""Day-zero governed registries. Business keys only; UUIDv7 generator is HOLD."""

from __future__ import annotations

import json
from pathlib import Path

from .paths import ROOT
from .agents import agent_records

CORE_DIR = ROOT / "cko_core"
MD_DIR = ROOT / "cko_md"
REG_DIR = ROOT / "cko_reg"
ASSURANCE_DIR = ROOT / "cko_assurance"

LAYERS: list[dict] = [
    {"code": "L10", "n": 10, "name": "CKO-MD", "class": "backbone", "md": "entidades, IDs, conceitos, fields, unidades, reference data", "reg": "normas de dados/metadata aplicáveis"},
    {"code": "L20", "n": 20, "name": "CKO-REG", "class": "backbone", "md": "instrumentos, emissores, jurisdictions como entidades MD", "reg": "autoridade, requirements, applicability"},
    {"code": "L30", "n": 30, "name": "Clinical Calculators", "class": "domain", "md": "calculator, formula, variable, input, result", "reg": "fórmula, população, units, thresholds, source"},
    {"code": "L40", "n": 40, "name": "Scales & Scores", "class": "domain", "md": "scale, dimension, item, option, scoring model", "reg": "instrumento original, versão, rights, validação"},
    {"code": "L50", "n": 50, "name": "Clinical Rules", "class": "domain", "md": "rule, condition, trigger, outcome", "reg": "guideline, evidence, applicability"},
    {"code": "L60", "n": 60, "name": "Library Objects", "class": "domain", "md": "device, material, product class, characteristic", "reg": "ANVISA/authority conforme objeto"},
    {"code": "L70", "n": 70, "name": "Medications & Solutions", "class": "domain", "md": "substance, presentation, concentration, route", "reg": "ANVISA, medicamento, dose, safety"},
    {"code": "L80", "n": 80, "name": "Laboratory Exams", "class": "domain", "md": "analyte, specimen, method, range, unit", "reg": "authority/evidence por exame"},
    {"code": "L90", "n": 90, "name": "Anatomy", "class": "domain", "md": "structure, part, region, relationship", "reg": "terminologias/fontes científicas aplicáveis"},
    {"code": "L100", "n": 100, "name": "Diseases / Conditions", "class": "domain", "md": "condition, symptom, risk factor", "reg": "classifications, evidence, authorities"},
    {"code": "L110", "n": 110, "name": "Procedures / Protocols", "class": "domain", "md": "procedure, step, material, prerequisite", "reg": "COFEN/MS/ANVISA/guideline aplicável"},
    {"code": "L120", "n": 120, "name": "Terminologies", "class": "domain", "md": "concept system, term, code, mappings", "reg": "release, license, jurisdiction, rights"},
    {"code": "L130", "n": 130, "name": "Educational / Contest", "class": "domain", "md": "exam, subject, topic, competency", "reg": "edital, legislação, authority/source"},
    {"code": "L140", "n": 140, "name": "References / Bibliography / Glossary", "class": "domain", "md": "work, citation, author, publisher, term", "reg": "rights, citation rules, provenance"},
    {"code": "L150", "n": 150, "name": "Articles / Guides / Summaries", "class": "domain", "md": "editorial/content identities", "reg": "source/evidence/citation/applicability"},
    {"code": "L160", "n": 160, "name": "Flashcards / Questions / Quizzes", "class": "domain", "md": "question, answer, distractor, objective", "reg": "source/evidence/rights"},
    {"code": "L170", "n": 170, "name": "Page Templates", "class": "experience", "md": "template, slot, region, variation", "reg": "standards/requirements aplicáveis"},
    {"code": "L180", "n": 180, "name": "Document Templates", "class": "experience", "md": "document profile, section, field", "reg": "document/rights/accessibility requirements"},
    {"code": "L190", "n": 190, "name": "Images / Media / Icons", "class": "experience", "md": "asset, rendition, metadata", "reg": "rights/license/provenance/a11y"},
    {"code": "L200", "n": 200, "name": "Asset Derivation", "class": "experience", "md": "derivative, transformation, variant", "reg": "rights, provenance, allowed transformation"},
    {"code": "L210", "n": 210, "name": "HCD / Usability", "class": "governance", "md": "user group, context, task, requirement", "reg": "ISO 9241 applicability"},
    {"code": "L220", "n": 220, "name": "Accessibility", "class": "governance", "md": "criterion, semantic object, test", "reg": "LBI/WCAG/ARIA/eMAG"},
    {"code": "L230", "n": 230, "name": "Design System", "class": "governance", "md": "token, component, variant, state", "reg": "a11y/HCD/technical standards"},
    {"code": "L240", "n": 240, "name": "UI Components & Interaction", "class": "governance", "md": "form, field, toaster, control, interaction", "reg": "accessibility/privacy/security requirements"},
    {"code": "L250", "n": 250, "name": "Privacy / LGPD", "class": "governance", "md": "data class, purpose, processing activity", "reg": "LGPD/ANPD/ISO 27701"},
    {"code": "L260", "n": 260, "name": "Security / Cybersecurity", "class": "governance", "md": "asset, threat, control, secret, dependency", "reg": "ISO 27001/OWASP — cláusula licenciada EVIDENCE_PENDING"},
    {"code": "L270", "n": 270, "name": "Routes / URLs", "class": "distribution", "md": "route, canonical URL, redirect", "reg": "web/SEO/privacy rules"},
    {"code": "L280", "n": 280, "name": "SEO", "class": "distribution", "md": "metadata profile, sitemap entry", "reg": "RFC 9309/Sitemaps/guidance"},
    {"code": "L290", "n": 290, "name": "Open Graph / Social", "class": "distribution", "md": "social profile, card, OG asset", "reg": "OGP/rights/media rules"},
    {"code": "L300", "n": 300, "name": "Structured Data", "class": "distribution", "md": "schema projection, property mappings", "reg": "JSON-LD/Schema.org"},
    {"code": "L310", "n": 310, "name": "i18n / l10n", "class": "distribution", "md": "language, locale, translation object", "reg": "BCP47/CLDR/jurisdiction"},
    {"code": "L320", "n": 320, "name": "Internal Search", "class": "distribution", "md": "index object, synonym, search field", "reg": "privacy/rights/discovery controls"},
    {"code": "L330", "n": 330, "name": "Recommendations", "class": "distribution", "md": "relation/profile/ranking candidate", "reg": "safety/privacy/explainability"},
    {"code": "L340", "n": 340, "name": "User State / Favorites / Collections", "class": "distribution", "md": "local state object, preference reference", "reg": "privacy/security/retention"},
    {"code": "L350", "n": 350, "name": "Analytics / Telemetry", "class": "operations", "md": "event, property, target, metric", "reg": "privacy/LGPD/security"},
    {"code": "L360", "n": 360, "name": "Performance", "class": "operations", "md": "metric, budget, threshold", "reg": "quality standards/SLAs"},
    {"code": "L370", "n": 370, "name": "Reliability / Resilience", "class": "operations", "md": "SLI/SLO, failure mode, recovery", "reg": "quality/security/continuity requirements"},
    {"code": "L380", "n": 380, "name": "Observability", "class": "operations", "md": "trace, metric, log schema", "reg": "OpenTelemetry/privacy/security"},
    {"code": "L390", "n": 390, "name": "Sustainability", "class": "operations", "md": "energy/carbon/software metric", "reg": "sustainability framework; ISO/IEC 21031 candidate"},
    {"code": "L400", "n": 400, "name": "Renderer", "class": "delivery", "md": "renderer, recipe, projection contract", "reg": "a11y/rights/privacy/web requirements"},
    {"code": "L410", "n": 410, "name": "Runtime / E2E", "class": "delivery", "md": "runtime profile, environment, E2E case", "reg": "security/privacy/quality"},
    {"code": "L420", "n": 420, "name": "PDF / Export Profiles", "class": "delivery", "md": "export profile, document rendition", "reg": "PDF 2.0/PDF-UA/rights — cláusula EVIDENCE_PENDING"},
    {"code": "L430", "n": 430, "name": "Publication / Release", "class": "delivery", "md": "release, publication, channel, manifest", "reg": "release/rights/regulatory gates"},
    {"code": "L440", "n": 440, "name": "Monitoring", "class": "delivery", "md": "monitor, target, threshold, incident", "reg": "freshness/regulatory/security/privacy"},
]


def layer_records() -> list[dict]:
    records = []
    for item in LAYERS:
        bk = f"LAYER-{item['n']:03d}"
        records.append({
            "business_key": bk,
            "canonical_id": None,
            "uuid": None,
            "identity_scheme": "CKO-BK-1",
            "entity_type": "LAYER",
            "layer_code": item["code"],
            "layer_number": item["n"],
            "canonical_name": item["name"],
            "layer_class": item["class"],
            "md_profile_ref": f"{bk}-MD",
            "reg_profile_ref": f"{bk}-REG",
            "domain_schema_ref": f"{bk}-DOMAIN",
            "md_registers": item["md"],
            "reg_governs": item["reg"],
            "mandatory": True,
            "active": True,
            "maturity": "M0_REGISTERED",
            "populated": False,
            "implemented": False,
            "assured": False,
            "uuid_status": "HOLD",
            "uuid_reason": "UUIDv7 generator not implemented; business_key is operational identity.",
            "status": "REGISTERED",
            "version": "0.1.0",
            "epistemic_status": "PROPOSED",
        })
    return records


def dump(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def write_registries() -> list[Path]:
    layers = layer_records()
    written = []
    written.append(dump(CORE_DIR / "identity_policy.json", {
        "business_key": "IDPOL-CKO-CORE-001",
        "identity_scheme": "CKO-BK-1",
        "uuid_algorithm": "UUIDv7",
        "uuid_generator_status": "HOLD",
        "rule": "Governed objects use business_key as operational identity until a tested UUIDv7 generator exists. uuid MUST be null. Do not invent UUIDv4 to proceed.",
        "reuse_existing": True,
        "silent_id_invention": "FORBIDDEN",
        "version": "1.0.0",
        "status": "DOCUMENTADO",
        "implemented": False,
    }))
    written.append(dump(CORE_DIR / "layer_registry.json", {
        "business_key": "REG-LAYER-CATALOG-001",
        "schemaVersion": "1.0.0",
        "population": len(layers),
        "maturity": "M0_REGISTERED",
        "note": "Layer EXISTS at bootstrap. EXISTS ≠ POPULATED ≠ IMPLEMENTED ≠ ASSURED.",
        "layers": layers,
    }))
    written.append(dump(CORE_DIR / "epistemic_states.json", {
        "business_key": "REF-EPISTEMIC-001",
        "states": [
            "OBSERVED", "VERIFIED", "SOURCE_DERIVED", "INFERRED", "PROPOSED",
            "IMPLEMENTED", "ASSURED", "UNKNOWN", "EVIDENCE_PENDING", "CONFLICT",
            "HOLD", "NOT_APPLICABLE", "SUPERSEDED", "DEPRECATED", "REJECTED",
        ],
        "forbidden_alone": ["OK", "PRONTO", "100%", "FINALIZADO", "PASS"],
        "pass_requires": ["population", "tested", "failed", "test_run", "evidence_bundle", "hash"],
    }))
    written.append(dump(CORE_DIR / "maturity_model.json", {
        "business_key": "REF-MATURITY-001",
        "levels": [
            {"code": "M0_REGISTERED", "meaning": "camada/objeto existe no registry"},
            {"code": "M1_SCHEMA_DEFINED", "meaning": "contrato/schema escrito"},
            {"code": "M2_CONFIGURED", "meaning": "perfis MD/REG preenchidos"},
            {"code": "M3_IMPLEMENTED", "meaning": "runtime observado"},
            {"code": "M4_VALIDATED", "meaning": "teste executado com evidência"},
            {"code": "M5_ASSURED", "meaning": "reperformance + IPE"},
            {"code": "M6_AUTONOMOUS", "meaning": "DoD agêntico completo"},
            {"code": "M7_CONTINUOUSLY_MONITORED", "meaning": "monitoramento contínuo evidenciado"},
        ],
    }))
    written.append(dump(CORE_DIR / "framework_registry.json", {
        "business_key": "REG-FRAMEWORK-001",
        "note": "Frameworks de controle, não autoridade clínica. Texto de cláusula licenciada NÃO está neste repositório.",
        "frameworks": [
            {
                "business_key": "FWK-COSO-001",
                "name": "COSO Internal Control",
                "role": "control environment / risk / activities / information / monitoring",
                "clause_text": "CLAUSE_TEXT_UNAVAILABLE",
                "status": "EVIDENCE_PENDING",
                "epistemic_status": "PROPOSED",
            },
            {
                "business_key": "FWK-COBIT-001",
                "name": "COBIT",
                "role": "technology governance (EDM/APO/BAI/DSS/MEA) as mapping target",
                "clause_text": "CLAUSE_TEXT_UNAVAILABLE",
                "status": "EVIDENCE_PENDING",
                "epistemic_status": "PROPOSED",
                "note": "Não inventar IDs/texto de objetivos COBIT além dos nomes de família.",
            },
        ],
    }))
    written.append(dump(MD_DIR / "entity_type_registry.json", {
        "business_key": "MD-ENTITY-TYPE-REG-001",
        "uuid": None,
        "status": "REGISTERED",
        "maturity": "M0_REGISTERED",
        "types": [
            {"business_key": "ETYPE-LAYER", "name": "Layer"},
            {"business_key": "ETYPE-ENTITY", "name": "Entity"},
            {"business_key": "ETYPE-CONCEPT", "name": "Concept"},
            {"business_key": "ETYPE-FIELD", "name": "Field"},
            {"business_key": "ETYPE-UNIT", "name": "Unit"},
            {"business_key": "ETYPE-RELATIONSHIP", "name": "Relationship"},
            {"business_key": "ETYPE-SOURCE", "name": "Source"},
            {"business_key": "ETYPE-CALCULATOR", "name": "Calculator"},
            {"business_key": "ETYPE-FORMULA", "name": "Formula"},
            {"business_key": "ETYPE-SCALE", "name": "Scale"},
            {"business_key": "ETYPE-CONTENT_OBJECT", "name": "Content Object"},
            {"business_key": "ETYPE-AGENT", "name": "Agent"},
            {"business_key": "ETYPE-LOCALE", "name": "Locale"},
            {"business_key": "ETYPE-ENGINE", "name": "Engine"},
            {"business_key": "ETYPE-VALIDATOR", "name": "Validator"},
            {"business_key": "ETYPE-CAAT", "name": "CAAT"},
            {"business_key": "ETYPE-IPE", "name": "IPE"},
            {"business_key": "ETYPE-TWIN", "name": "Digital Twin"},
            {"business_key": "ETYPE-API", "name": "API"},
            {"business_key": "ETYPE-ROUTE", "name": "Route"},
            {"business_key": "ETYPE-ADMIN_SURFACE", "name": "Admin Surface"},
        ],
        "note": "Tipos mínimos do bootstrap. Locale Drive (MD-LOCALE-REG-001) é RELATED_TAXONOMY a MD-LANG-LOC-001, não substitui pt-BR runtime.",
    }))
    written.append(dump(REG_DIR / "authority_classes.json", {
        "business_key": "REG-AUTH-CLASS-001",
        "status": "REGISTERED",
        "classes": [
            {"business_key": "AUTH-OFFICIAL-BR", "name": "Autoridade oficial brasileira", "examples_candidate": ["Planalto", "MS", "ANVISA", "COFEN", "DOU"]},
            {"business_key": "AUTH-PROFESSIONAL", "name": "Fonte profissional oficial"},
            {"business_key": "AUTH-SCIENTIFIC-PRIMARY", "name": "Fonte científica primária"},
            {"business_key": "AUTH-SECONDARY", "name": "Fonte secundária"},
            {"business_key": "AUTH-AGGREGATOR", "name": "Agregador — nunca substitui oficial"},
        ],
        "epistemic_status": "PROPOSED",
        "note": "Classes nominais. Nenhum instrument/provision populado neste bootstrap.",
    }))
    written.append(dump(ASSURANCE_DIR / "caat_registry.json", {
        "business_key": "REG-CAAT-001",
        "status": "REGISTERED",
        "implemented": False,
        "caats": [
            "CAAT-ID-UNIQUENESS", "CAAT-UUID-VALIDITY", "CAAT-BUSINESS-KEY-COLLISION",
            "CAAT-FIELD-DICTIONARY-COVERAGE", "CAAT-VALUE-DOMAIN-COVERAGE",
            "CAAT-RELATIONSHIP-INTEGRITY", "CAAT-ORPHAN-EDGE",
            "CAAT-VERSION-CHAIN", "CAAT-HASH-CHAIN", "CAAT-PROVENANCE-COVERAGE", "CAAT-LINEAGE-INTEGRITY",
            "CAAT-SOURCE-AUTHORITY", "CAAT-REG-BINDING-COVERAGE", "CAAT-APPLICABILITY-COVERAGE",
            "CAAT-ALCOA", "CAAT-STEWARDSHIP", "CAAT-QUALITY",
            "CAAT-API-CONTRACT", "CAAT-API-FRESHNESS",
            "CAAT-A11Y", "CAAT-SEO", "CAAT-STRUCTURED-DATA", "CAAT-PRIVACY", "CAAT-SECURITY",
            "CAAT-RENDER-PARITY", "CAAT-PUBLICATION-PARITY",
            "CAAT-LAYER-COUNT-44",
        ],
    }))
    written.append(dump(ASSURANCE_DIR / "ipe_registry.json", {
        "business_key": "REG-IPE-001",
        "status": "REGISTERED",
        "implemented": False,
        "carr": ["COMPLETE", "ACCURATE", "RELEVANT", "RELIABLE", "REPRODUCIBLE"],
        "ipes": [
            "IPE-MASTER-DATA-REGISTER", "IPE-REGULATORY-REGISTER", "IPE-SOURCE-REGISTER",
            "IPE-FIELD-DICTIONARY", "IPE-RELATIONSHIP-REGISTER",
            "IPE-VALIDATION-REPORT", "IPE-CAAT-REPORT", "IPE-FINDING-REPORT",
            "IPE-RISK-REGISTER", "IPE-CHANGE-REGISTER",
            "IPE-AGENT-RUN-REGISTER", "IPE-API-RUN-REGISTER",
            "IPE-RELEASE-MANIFEST", "IPE-PUBLICATION-INVENTORY", "IPE-QUALITY-DASHBOARD",
        ],
        "rule": "Relatório interno não é evidência sem avaliação IPE.",
    }))
    written.append(dump(ASSURANCE_DIR / "alcoa_profile.json", {
        "business_key": "PROF-ALCOA-PLUSPLUS-001",
        "status": "REGISTERED",
        "alcoa": ["Attributable", "Legible", "Contemporaneous", "Original", "Accurate"],
        "alcoa_plus": ["Complete", "Consistent", "Enduring", "Available"],
        "cko_integrity_extensions": ["Traceable", "Versioned", "Reproducible", "Tamper-evident"],
        "note": "Extensões CKO não são o acrônimo formal ALCOA++. Profile DOCUMENTADO, testes não executados.",
        "implemented": False,
    }))
    written.append(dump(ROOT / "admin" / "contract.json", {
        "business_key": "CONTRACT-ADMIN-FRONTEND-001",
        "version": "1.0.0",
        "status": "DOCUMENTADO",
        "implemented_runtime": "PARTIAL",
        "store": "GitHub (Day Zero). Nenhuma API admin autenticada observada neste repositório.",
        "principle": "Studio/Admin projeta objetos governados. Não reescreve verdade clínica.",
        "communication": {
            "mode": "SHARED_GITHUB_CONTRACTS",
            "description": "Admin e frontend leem os mesmos JSON versionados. O renderer gera ambas as superfícies. Não há CMS paralelo nem escrita canônica no browser.",
            "admin_surface": "admin.html",
            "frontend_surface": "index.html + tools/*.html",
            "runtime_json_projection": ["admin/contract.json", "admin/layer_registry.json"],
        },
        "frontend": {
            "role": "PRESENTATION_ONLY",
            "reads": ["render projections", "status badges", "HOLD banners"],
            "writes_canonical": False,
        },
        "admin": {
            "role": "orchestration / preview / status / exceptions / publication control",
            "reads": ["cko_core", "cko_md", "cko_reg", "cko_assurance", "data/tools"],
            "allowed_write_when_implemented": ["changeset", "new version", "finding", "exception"],
            "forbidden_write": ["silent UPDATE of formula", "dose", "threshold", "canonical identity"],
        },
        "events": {
            "allowed": [
                "ADMIN_READ_LAYERS",
                "ADMIN_READ_CATALOG",
                "ADMIN_READ_FINDINGS",
                "ADMIN_REQUEST_PREVIEW",
                "FRONTEND_RENDER_PROJECTION",
            ],
            "forbidden": [
                "ADMIN_WRITE_FORMULA",
                "FRONTEND_WRITE_CANONICAL",
                "LLM_PROMOTE_IDENTITY",
            ],
        },
        "privacy": "PRIV-NO-SENSITIVE-CAPTURE",
        "segregation": "MAKER ≠ CHECKER ≠ AUDITOR",
    }))
    md_profiles = []
    reg_profiles = []
    for layer in layers:
        md_profiles.append({
            "business_key": layer["md_profile_ref"],
            "uuid": None,
            "layer_ref": layer["business_key"],
            "registers": layer["md_registers"],
            "required_entity_types": ["ETYPE-LAYER"],
            "status": "REGISTERED",
            "maturity": "M0_REGISTERED",
            "populated": False,
        })
        reg_profiles.append({
            "business_key": layer["reg_profile_ref"],
            "uuid": None,
            "layer_ref": layer["business_key"],
            "governs": layer["reg_governs"],
            "field_binding_required": True,
            "clause_text": "CLAUSE_TEXT_UNAVAILABLE",
            "status": "REGISTERED",
            "maturity": "M0_REGISTERED",
            "populated": False,
            "applicability": "APPLICABILITY_UNVERIFIED",
        })
    written.append(dump(CORE_DIR / "layer_md_profiles.json", {
        "business_key": "REG-LAYER-MD-PROFILES-001",
        "population": len(md_profiles),
        "profiles": md_profiles,
    }))
    written.append(dump(CORE_DIR / "layer_reg_profiles.json", {
        "business_key": "REG-LAYER-REG-PROFILES-001",
        "population": len(reg_profiles),
        "profiles": reg_profiles,
        "note": "REG qualifica identidades MD. Nenhum instrument/provision populado.",
    }))
    written.append(dump(CORE_DIR / "taxonomy_relation.json", {
        "business_key": "REL-TAXONOMY-21-TO-44-001",
        "relation_type": "RELATED_TAXONOMY",
        "from_ref": "data/layers-21.json",
        "to_ref": "cko_core/layer_registry.json",
        "not": "1:1 SUPERSEDE",
        "note": "O corte de 21 camadas do v0.1 descreve o produto piloto. O registry de 44 camadas é a governança Day Zero. Não mesclar nem apagar silenciosamente.",
        "status": "REGISTERED",
    }))
    written.append(dump(MD_DIR / "language_locale_registry.json", {
        "business_key": "MD-LANG-LOC-001",
        "uuid": None,
        "status": "REGISTERED",
        "languages": [
            {
                "business_key": "LANG-PT",
                "bcp47": "pt",
                "epistemic_status": "OBSERVED",
                "source": "html lang=pt-BR neste repositório",
            }
        ],
        "locales": [
            {
                "business_key": "LOC-PT-BR",
                "bcp47": "pt-BR",
                "epistemic_status": "OBSERVED",
                "source": "UI e conteúdo piloto em português brasileiro",
            }
        ],
        "territories": [
            {
                "business_key": "TERR-BR",
                "iso3166": "BR",
                "epistemic_status": "PROPOSED",
                "note": "Jurisdição-alvo do produto; não é binding regulatório.",
            }
        ],
        "jurisdictions": [
            {
                "business_key": "JUR-BR",
                "name": "Brasil",
                "epistemic_status": "PROPOSED",
                "status": "APPLICABILITY_UNVERIFIED",
            }
        ],
        "related_drive_catalog": "MD-LOCALE-REG-001",
        "relation_type": "RELATED_TAXONOMY",
        "note": "pt-BR é o locale de runtime observado. Os 19 códigos de locales.zip não substituem este registry.",
    }))
    written.append(dump(MD_DIR / "field_dictionary.json", {
        "business_key": "MD-FIELD-DICT-001",
        "uuid": None,
        "status": "REGISTERED",
        "maturity": "M0_REGISTERED",
        "population": 0,
        "fields": [],
        "note": "Dicionário existe. Campos de domínio ainda não populados.",
    }))
    agents = agent_records()
    written.append(dump(ASSURANCE_DIR / "agent_registry.json", {
        "business_key": "REG-AGENT-001",
        "status": "IMPLEMENTED_INBOX_ONLY",
        "implemented": True,
        "publication_implemented": False,
        "rule": "Agente executa processo. Agente não cria autoridade. MAKER ≠ CHECKER ≠ AUDITOR.",
        "classes": [
            "ORCHESTRATOR", "DISCOVERY", "ACQUISITION", "EXTRACTION", "NORMALIZATION",
            "ENTITY_RESOLUTION", "MD", "REGULATORY", "KNOWLEDGE", "EVIDENCE",
            "CONTENT", "SEO", "A11Y", "PRIVACY", "SECURITY", "SUSTAINABILITY",
            "RENDERER", "PUBLICATION", "VALIDATION", "CAAT", "IPE", "RISK",
            "AUDIT", "SEARCH", "SAE", "MONITORING",
        ],
        "agents": agents,
        "population": len(agents),
    }))
    written.append(dump(ASSURANCE_DIR / "api_registry.json", {
        "business_key": "REG-API-001",
        "status": "REGISTERED",
        "implemented": False,
        "note": "API REST base_url permanece null. Páginas HTML oficiais observadas em cko_inbox/extracted/regulated_pages.json.",
        "apis": [
            {"business_key": "API-CAND-COFEN", "name": "COFEN", "base_url": None, "html_page": "https://www.cofen.gov.br/", "kind": "REGULATED_HTML_PAGE", "status": "SOURCE_DERIVED"},
            {"business_key": "API-CAND-ANVISA", "name": "ANVISA", "base_url": None, "html_page": "https://www.gov.br/anvisa/pt-br", "kind": "REGULATED_HTML_PAGE", "status": "SOURCE_DERIVED"},
            {"business_key": "API-CAND-MS", "name": "Ministério da Saúde", "base_url": None, "html_page": "https://www.gov.br/saude/pt-br", "kind": "REGULATED_HTML_PAGE", "status": "SOURCE_DERIVED"},
            {"business_key": "API-CAND-INTERNAL", "name": "CKO extract runner", "base_url": None, "cli": "python3 -m engine.cli extract", "status": "IMPLEMENTED_INBOX_ONLY"},
        ],
    }))
    written.append(dump(ASSURANCE_DIR / "twin_registry.json", {
        "business_key": "REG-TWIN-001",
        "status": "REGISTERED",
        "implemented": False,
        "twins": [],
        "population": 0,
        "note": "Digital Twin registry existe. Nenhum twin de objeto de domínio sincronizado.",
    }))
    written.append(dump(ASSURANCE_DIR / "search_registry.json", {
        "business_key": "REG-SEARCH-001",
        "status": "REGISTERED",
        "implemented": False,
        "policy": "INTERNAL CANONICAL SEARCH FIRST",
        "indexes": [],
        "population": 0,
    }))
    written.append(dump(ASSURANCE_DIR / "privacy_profile.json", {
        "business_key": "PRIV-NO-SENSITIVE-CAPTURE",
        "status": "REGISTERED",
        "implemented": False,
        "rules": [
            "no patient name",
            "no CPF",
            "no prontuário",
            "no address",
            "no email",
            "no phone",
            "no persistent patient ID",
            "no health profile persistence",
            "no device identifier for advertising",
            "clinical inputs ephemeral and not sent to product analytics",
        ],
    }))
    written.append(dump(ASSURANCE_DIR / "wave_registry.json", {
        "business_key": "REG-WAVE-001",
        "note": "Waves materializam maturidade. Camadas já existem em M0.",
        "waves": [
            {"code": "W0", "name": "FOUNDATION", "target": "M0-M1"},
            {"code": "W1", "name": "ASSURANCE", "target": "M1"},
            {"code": "W2", "name": "INTEGRATION", "target": "M1"},
            {"code": "W3", "name": "AGENTIC CORE", "target": "M1"},
            {"code": "W4", "name": "DIGITAL TWIN", "target": "M1"},
            {"code": "W5", "name": "SAE", "target": "M1"},
            {"code": "W6", "name": "GOVERNANCE FRAMEWORKS", "target": "M1"},
            {"code": "W7", "name": "TRANSVERSAL PLATFORM", "target": "M1"},
            {"code": "W8", "name": "DOMAIN POPULATION", "target": "M2+"},
            {"code": "W9", "name": "RUNTIME / RELEASE", "target": "M3"},
            {"code": "W10", "name": "GLOBAL ASSURANCE", "target": "M4-M5"},
        ],
        "this_changeset": "W0 registration + admin read-only surface",
    }))
    written.append(dump(ASSURANCE_DIR / "risk_registry.json", {
        "business_key": "REG-RISK-001",
        "status": "REGISTERED",
        "population": 1,
        "risks": [
            {
                "business_key": "RISK-DUP-CANONICAL-ID",
                "risk_statement": "Identidade canônica duplicada por canal/idioma/template",
                "control_refs": ["CTRL-MD-ID-001"],
                "status": "OPEN",
                "epistemic_status": "PROPOSED",
            }
        ],
    }))
    written.append(dump(ASSURANCE_DIR / "control_registry.json", {
        "business_key": "REG-CONTROL-001",
        "status": "REGISTERED",
        "framework_refs": ["FWK-COSO-001", "FWK-COBIT-001"],
        "note": "Mapeamento de família apenas. Sem texto de cláusula COSO/COBIT.",
        "controls": [
            {
                "business_key": "CTRL-MD-ID-001",
                "objective": "Unicidade de business_key no Layer Registry",
                "risk_refs": ["RISK-DUP-CANONICAL-ID"],
                "caat_refs": ["CAAT-LAYER-COUNT-44", "CAAT-BUSINESS-KEY-COLLISION"],
                "control_type": "PREVENTIVE",
                "automation_level": "AUTOMATED",
                "status": "REGISTERED",
            }
        ],
    }))
    return written


def evaluate_layer_registry(path: Path | None = None) -> dict:
    """CAAT-LAYER-COUNT-44: full population of registered layers."""
    target = path or (CORE_DIR / "layer_registry.json")
    if not target.exists():
        return {
            "id": "CAAT-LAYER-COUNT-44",
            "status": "HOLD",
            "population": None,
            "tested": 0,
            "failed": None,
            "reason": "layer_registry.json not written",
            "epistemic_status": "EVIDENCE_PENDING",
        }
    payload = json.loads(target.read_text(encoding="utf-8"))
    layers = payload.get("layers") or []
    findings = []
    keys = [item.get("business_key") for item in layers]
    if len(layers) != 44:
        findings.append({"id": "LAYER_COUNT", "observed": len(layers), "expected": 44})
    if len(set(keys)) != len(keys):
        findings.append({"id": "BUSINESS_KEY_COLLISION"})
    for item in layers:
        if item.get("uuid") is not None:
            findings.append({"id": "UUID_INVENTED", "business_key": item.get("business_key")})
        if not item.get("md_profile_ref") or not item.get("reg_profile_ref"):
            findings.append({"id": "MD_OR_REG_PROFILE_MISSING", "business_key": item.get("business_key")})
        if not str(item.get("md_profile_ref", "")).endswith("-MD"):
            findings.append({"id": "MD_PROFILE_ORDER", "business_key": item.get("business_key")})
        if not str(item.get("reg_profile_ref", "")).endswith("-REG"):
            findings.append({"id": "REG_PROFILE_ORDER", "business_key": item.get("business_key")})
    failed = len(findings)
    return {
        "id": "CAAT-LAYER-COUNT-44",
        "status": "PASS" if failed == 0 else "FAIL",
        "population": len(layers),
        "tested": len(layers),
        "failed": failed,
        "findings": findings,
        "epistemic_status": "VERIFIED" if failed == 0 else "CONFLICT",
        "note": "PASS aplica-se somente à população do Layer Registry, não ao projeto inteiro.",
    }
