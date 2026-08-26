"""Evidence-based MD+REG envelopes for all 44 layers. Phased. Not a completeness claim.

EXISTS ≠ POPULATED ≠ IMPLEMENTADO ≠ ASSURED ≠ PUBLICADO.
Envelope COMPLETE means every layer has MD+REG fields filled from observed evidence.
It does not mean the domain is implemented or assured.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .bootstrap import LAYERS, layer_records
from .paths import ROOT, TOOLS_DIR

CATALOG_PATH = ROOT / "cko_md" / "layer_md_reg_phase.json"
MD_PROFILES_PATH = ROOT / "cko_core" / "layer_md_profiles.json"
REG_PROFILES_PATH = ROOT / "cko_core" / "layer_reg_profiles.json"

PHASES = (
    {
        "id": "P0",
        "name": "Espinha MD+REG",
        "layers": ["L10", "L20"],
        "depends_on": [],
        "owner_secret": False,
        "goal": "Identidade e qualificação normativa do lote piloto. Sem certificação ISO.",
    },
    {
        "id": "P1",
        "name": "Domínio dos cinco pilotos",
        "layers": ["L30", "L40", "L50", "L70", "L110", "L130"],
        "depends_on": ["P0"],
        "owner_secret": False,
        "goal": "Pilotos em data/tools. Dimensionamento e insulina HOLD. Sem Braden.",
    },
    {
        "id": "P2",
        "name": "Bibliotecas e APIs observadas",
        "layers": ["L60", "L80", "L90", "L100", "L140", "L150", "L160"],
        "depends_on": ["P0"],
        "owner_secret": False,
        "goal": "API só HTTP 200. 32 bibliotecas EVIDENCE_PENDING. Sem dump CID/LOINC/UMLS.",
    },
    {
        "id": "P3",
        "name": "Rights, privacidade, segurança",
        "layers": ["L120", "L250", "L260"],
        "depends_on": ["P0"],
        "owner_secret": True,
        "goal": "NNN HOLD até A/B/C. Cookie banner NÃO implantado. ISO 27001 cláusula indisponível.",
    },
    {
        "id": "P4",
        "name": "Experiência, chrome, i18n",
        "layers": [
            "L170", "L180", "L190", "L200", "L210", "L220", "L230", "L240",
            "L270", "L280", "L290", "L300", "L310",
        ],
        "depends_on": ["P0", "P1"],
        "owner_secret": False,
        "goal": "Chrome a11y/OG first-party. i18n who.en+local.pt-BR HOLD. Design zip SKIP_BINARY.",
    },
    {
        "id": "P5",
        "name": "Operação e publicação",
        "layers": [
            "L320", "L330", "L340", "L350", "L360", "L370", "L380", "L390",
            "L400", "L410", "L420", "L430", "L440",
        ],
        "depends_on": ["P0", "P1", "P4"],
        "owner_secret": False,
        "goal": "Renderer PRESENTATION_ONLY. Release HOLD. PDF-UA EVIDENCE_PENDING. Sem ads.",
    },
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _dump(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _exists(*parts: str) -> bool:
    return (ROOT.joinpath(*parts)).exists()


def _pilot_slugs() -> list[str]:
    return sorted(path.stem for path in TOOLS_DIR.glob("*.json"))


def _layer_spec() -> dict[str, dict]:
    """Static evidence plan per layer. Runtime overlay adds file existence."""
    return {
        "L10": {
            "phase": "P0",
            "md_population": "PARTIAL",
            "md_implemented": True,
            "reg_population": "PARTIAL",
            "evidence": [
                "cko_md/field_dictionary.json",
                "cko_core/identity_policy.json",
                "cko_md/iso8000_profile.json",
            ],
            "identities": ["MD-FRONTS-PLAN-001", "MD-CLIN-DICT-001", "MD-WHO-I18N-001"],
            "reg_instruments": ["PGD-INSTR-POLITICA", "PGD-INSTR-ESTRATEGIA"],
            "gap": "UUIDv7 HOLD. Envelope completo ≠ dicionário populado. Sem certificação.",
            "do_not": "Inventar UUID. Marcar certified=true.",
            "unblock": None,
        },
        "L20": {
            "phase": "P0",
            "md_population": "PARTIAL",
            "md_implemented": True,
            "reg_population": "PARTIAL",
            "evidence": [
                "cko_md/pgdados_program.json",
                "cko_inbox/official/lei-9610.html",
                "cko_md/iso8000_pgdados_binding.json",
            ],
            "identities": ["MD-PGDADOS-001", "INS-LEI-9610-1998"],
            "reg_instruments": ["INS-LEI-9610-1998", "PGD-INSTR-PLANO"],
            "gap": (
                "Reprobe HTML ao vivo: hub+guia HTTP 200; Parte 3 ainda só rótulo (sem href PDF); "
                "cartilhas vol. 4 e 5 mencionadas no hub sem href volume-4/volume-5. "
                "Cláusula ISO CLAUSE_TEXT_UNAVAILABLE. mwpt/ABNT não copiados."
            ),
            "do_not": "Substituir cláusula ISO licenciada por PGDADOS.",
            "unblock": None,
        },
        "L30": {
            "phase": "P1",
            "md_population": "PARTIAL",
            "md_implemented": True,
            "reg_population": "PARTIAL",
            "evidence": ["data/tools/gotejamento.json", "data/tools/dimensionamento.json"],
            "identities": ["gotejamento", "CALC-GOTEJAMENTO-001", "CALC-DIMENSIONAMENTO-001"],
            "reg_instruments": ["INS-LEI-9610-1998"],
            "gap": "Dimensionamento HOLD. ABNT NBR 5891 arredondamento cláusula não ingerida.",
            "do_not": "Unzip HTML pages_full em data/tools.",
            "unblock": None,
        },
        "L40": {
            "phase": "P1",
            "md_population": "PARTIAL",
            "md_implemented": True,
            "reg_population": "HOLD",
            "evidence": ["data/tools/meows.json"],
            "identities": ["meows", "SCALE-MEOWS-001"],
            "reg_instruments": ["INS-LEI-9610-1998"],
            "gap": "Braden/Norton/Glasgow QUARANTINE. Rights de escala de terceiro HOLD.",
            "do_not": "Copiar braden.html / escala-de-braden.json para data/tools.",
            "unblock": None,
        },
        "L50": {
            "phase": "P1",
            "md_population": "PARTIAL",
            "md_implemented": True,
            "reg_population": "PARTIAL",
            "evidence": ["data/tools/cinco-ts-pcr.json"],
            "identities": ["cinco-ts-pcr", "GUIDE-5TS-PCR-001"],
            "reg_instruments": ["INS-LEI-9610-1998"],
            "gap": "COMPARE_NOT_1TO1 com Simulado PCR no Drive.",
            "do_not": "LLM autor de regra clínica.",
            "unblock": None,
        },
        "L60": {
            "phase": "P2",
            "md_population": "COMPARE_ONLY",
            "md_implemented": False,
            "reg_population": "EVIDENCE_PENDING",
            "evidence": [
                "cko_inbox/extracted/vaccines_zip_inventory.json",
                "cko_inbox/extracted/templates_bibliotecas_compare.json",
                "cko_md/library_api_map.json",
                "cko_md/library_32_compare.json",
            ],
            "identities": ["SET-VAC-15", "SET-DEVICE-11", "SET-CLINICAL-24"],
            "reg_instruments": [],
            "gap": (
                "Owner COMPARE_ACCEPTED para UNBLOCK-32-LIST: evidência observada persistida "
                "(11 PAHO/device + 24 objetos clínicos + 15 CAL-VAC). "
                "Claimed 32 permanece EVIDENCE_PENDING. "
                "Não inventar 32 adapters; não promover CAL-VAC/Braden/NNN."
            ),
            "do_not": "Inventar 32 adapters. Promover CAL-VAC. Somar conjuntos heterogéneos até dar 32.",
            "unblock": "UNBLOCK-32-LIST",
        },
        "L70": {
            "phase": "P1",
            "md_population": "HOLD",
            "md_implemented": False,
            "reg_population": "HOLD",
            "evidence": ["cko_md/clinical_dictionary_catalog.json"],
            "identities": ["PILOT-CKO-INSULINA"],
            "reg_instruments": [],
            "gap": "PNGs insulina SKIP_BINARY. Sem data/tools/insulina.json.",
            "do_not": "Ligar PNG de insulina no chrome. Inventar dose.",
            "unblock": None,
        },
        "L80": {
            "phase": "P2",
            "md_population": "EVIDENCE_PENDING",
            "md_implemented": False,
            "reg_population": "EVIDENCE_PENDING",
            "evidence": ["cko_md/api_adapter_registry.json"],
            "identities": ["API-NLM-CLINICALTABLES-ICD10CM"],
            "reg_instruments": [],
            "gap": "NLM ICD-10-CM = busca US. Sem dump LOINC.",
            "do_not": "Despejar pasta LOINC do Drive.",
            "unblock": None,
        },
        "L90": {
            "phase": "P2",
            "md_population": "EVIDENCE_PENDING",
            "md_implemented": False,
            "reg_population": "EVIDENCE_PENDING",
            "evidence": [],
            "identities": [],
            "reg_instruments": [],
            "gap": "Pasta Anatomia Drive. Sem API REST oficial observada.",
            "do_not": "Despejar UMLS.",
            "unblock": None,
        },
        "L100": {
            "phase": "P2",
            "md_population": "EVIDENCE_PENDING",
            "md_implemented": False,
            "reg_population": "EVIDENCE_PENDING",
            "evidence": ["cko_md/api_adapter_registry.json"],
            "identities": ["API-NLM-CLINICALTABLES-ICD10CM"],
            "reg_instruments": [],
            "gap": "Busca NLM ≠ CID-10/11 DATASUS. ICD-11 texto FORBIDDEN.",
            "do_not": "Unzip classificacoes_medicas.zip (99 MB).",
            "unblock": None,
        },
        "L110": {
            "phase": "P1",
            "md_population": "PARTIAL",
            "md_implemented": True,
            "reg_population": "PARTIAL",
            "evidence": ["data/tools/cinco-ts-pcr.json"],
            "identities": ["cinco-ts-pcr"],
            "reg_instruments": ["INS-LEI-9610-1998"],
            "gap": "Protocolo PCR piloto. Atos de órgão (F5) HOLD.",
            "do_not": "Misturar portaria MS neste tubo.",
            "unblock": "HOLD-ORGAN-ACTS",
        },
        "L120": {
            "phase": "P3",
            "md_population": "PARTIAL",
            "md_implemented": True,
            "reg_population": "HOLD",
            "evidence": ["cko_md/nnn_rights_architecture.json", "cko_md/nnn_identity_catalog.json"],
            "identities": ["MD-NNN-RIGHTS-001", "MD-NNN-IDENTITY-001", "CKO-NNN-DIAG-00046"],
            "reg_instruments": [],
            "gap": "UNBLOCK-NNN-LICENSE OPT-B: identity catalog codes+deep-link. Labels withheld. nanda-00046.json QUARANTINE.",
            "do_not": "Copiar banco NANDA/NIC/NOC.",
            "unblock": "UNBLOCK-NNN-LICENSE",
        },
        "L130": {
            "phase": "P1",
            "md_population": "PARTIAL",
            "md_implemented": True,
            "reg_population": "PARTIAL",
            "evidence": ["data/tools/simulado-tecnico.json"],
            "identities": ["simulado-tecnico", "EXAM-SIMULADO-TEC-001"],
            "reg_instruments": ["INS-LEI-9610-1998"],
            "gap": "COMPARE_NOT_1TO1 Simulado Técnicos 1/2. Sem banco de provas de terceiro.",
            "do_not": "Gerar questões com LLM.",
            "unblock": None,
        },
        "L140": {
            "phase": "P2",
            "md_population": "PARTIAL",
            "md_implemented": False,
            "reg_population": "HOLD",
            "evidence": ["cko_md/api_adapter_registry.json"],
            "identities": ["API-CROSSREF-WORKS"],
            "reg_instruments": ["FLD-REF-ACCESSED"],
            "gap": "ABNT NBR 6023:2025 nomeada; cláusula não ingerida. SciELO 403.",
            "do_not": "Republicar abstract como canônico.",
            "unblock": None,
        },
        "L150": {
            "phase": "P2",
            "md_population": "PARTIAL",
            "md_implemented": True,
            "reg_population": "PARTIAL",
            "evidence": ["cko_md/content_curriculum.json", "cko_md/api_adapter_registry.json"],
            "identities": ["MD-CONTENT-CURR-001", "API-NCBI-EUTILS-ESEARCH"],
            "reg_instruments": ["INS-LEI-9610-1998"],
            "gap": "Renderer PRESENTATION_ONLY. LLM FORBIDDEN no canônico.",
            "do_not": "LLM autor de guia canônico.",
            "unblock": None,
        },
        "L160": {
            "phase": "P2",
            "md_population": "PARTIAL",
            "md_implemented": True,
            "reg_population": "PARTIAL",
            "evidence": ["data/tools/simulado-tecnico.json"],
            "identities": ["simulado-tecnico"],
            "reg_instruments": ["INS-LEI-9610-1998"],
            "gap": "Edge extrair-questoes-enfermagem = slug only, não invocar.",
            "do_not": "Copiar provas de terceiros sem rights.",
            "unblock": None,
        },
        "L170": {
            "phase": "P4",
            "md_population": "COMPARE_ONLY",
            "md_implemented": False,
            "reg_population": "COMPARE_ONLY",
            "evidence": ["cko_inbox/drive/site_shell/INVENTORY.json"],
            "identities": ["SRC-SITE-SHELL"],
            "reg_instruments": [],
            "gap": "Templates Drive COMPARE. Sem promover HTML a golden MD.",
            "do_not": "Copiar ads/cookie wall do shell.",
            "unblock": None,
        },
        "L180": {
            "phase": "P4",
            "md_population": "EVIDENCE_PENDING",
            "md_implemented": False,
            "reg_population": "EVIDENCE_PENDING",
            "evidence": [],
            "identities": [],
            "reg_instruments": [],
            "gap": "PDF/export de documento clínico não observado neste lote.",
            "do_not": "Inventar template SAE canônico.",
            "unblock": None,
        },
        "L190": {
            "phase": "P4",
            "md_population": "PARTIAL",
            "md_implemented": True,
            "reg_population": "HOLD",
            "evidence": ["assets/img/icontopbar1-calculadoras-de-enfermagem.webp"],
            "identities": ["TOK-SHELL-HEADER-BG"],
            "reg_instruments": ["INS-LEI-9610-1998"],
            "gap": "Bandeiras seletor EVIDENCE_PENDING. Design zip SKIP_BINARY.",
            "do_not": "Unzip Design e arquivos das imagens (7).zip.",
            "unblock": None,
        },
        "L200": {
            "phase": "P4",
            "md_population": "PARTIAL",
            "md_implemented": True,
            "reg_population": "PARTIAL",
            "evidence": ["assets/img/og-default.png"],
            "identities": ["OG-DEFAULT-FIRST-PARTY"],
            "reg_instruments": ["INS-LEI-9610-1998"],
            "gap": "151 cards Drive não copiados.",
            "do_not": "Usar card Drive de terceiro como OG.",
            "unblock": None,
        },
        "L210": {
            "phase": "P4",
            "md_population": "EVIDENCE_PENDING",
            "md_implemented": False,
            "reg_population": "EVIDENCE_PENDING",
            "evidence": [],
            "identities": [],
            "reg_instruments": [],
            "gap": "ISO 9241 nomeada; cláusula CLAUSE_TEXT_UNAVAILABLE.",
            "do_not": "Ingerir texto ISO 9241.",
            "unblock": None,
        },
        "L220": {
            "phase": "P4",
            "md_population": "PARTIAL",
            "md_implemented": True,
            "reg_population": "PARTIAL",
            "evidence": ["assets/js/a11y.js", "cko_md/field_dictionary.json"],
            "identities": ["FLD-A11Y-WCAG-EMAG"],
            "reg_instruments": ["PGD-INSTR-ESTRATEGIA"],
            "gap": "WCAG/eMAG/LBI nomeados. Texto W3C não ingerido.",
            "do_not": "Fonte OpenDyslexic CDN. Cookie wall.",
            "unblock": None,
        },
        "L230": {
            "phase": "P4",
            "md_population": "PARTIAL",
            "md_implemented": True,
            "reg_population": "PARTIAL",
            "evidence": ["cko_core/design_token_registry.json"],
            "identities": ["TOK-SHELL-HEADER-BG", "TOK-FONT-SANS"],
            "reg_instruments": [],
            "gap": "Tokens first-party. Mockups LAYOUT_LANGUAGE_ONLY.",
            "do_not": "Copiar 98% de mockup Studio como produto.",
            "unblock": None,
        },
        "L240": {
            "phase": "P4",
            "md_population": "PARTIAL",
            "md_implemented": True,
            "reg_population": "PARTIAL",
            "evidence": ["assets/js/a11y.js"],
            "identities": ["language-selector-placeholder"],
            "reg_instruments": [],
            "gap": "Seletor i18n HOLD. Sem write de fórmula no admin.",
            "do_not": "ADMIN_WRITE_FORMULA.",
            "unblock": None,
        },
        "L250": {
            "phase": "P3",
            "md_population": "HOLD",
            "md_implemented": False,
            "reg_population": "HOLD",
            "evidence": [],
            "identities": [],
            "reg_instruments": [],
            "gap": "Banner cookies do zip NÃO implantado (NO_SENSITIVE_CAPTURE).",
            "do_not": "Captura granular de cookies. type=email no chrome piloto.",
            "unblock": None,
        },
        "L260": {
            "phase": "P3",
            "md_population": "EVIDENCE_PENDING",
            "md_implemented": False,
            "reg_population": "EVIDENCE_PENDING",
            "evidence": ["cko_core/identity_policy.json"],
            "identities": ["IDPOL-CKO-CORE-001"],
            "reg_instruments": [],
            "gap": "ISO 27001/OWASP nomeados; cláusula EVIDENCE_PENDING.",
            "do_not": "Commitar service_role. Inventar senha Supabase.",
            "unblock": "UNBLOCK-SUPABASE-SQL",
        },
        "L270": {
            "phase": "P4",
            "md_population": "PARTIAL",
            "md_implemented": True,
            "reg_population": "PARTIAL",
            "evidence": ["cko_md/page_inventory.json"],
            "identities": ["gotejamento", "meows"],
            "reg_instruments": [],
            "gap": "Cinco rotas piloto. 1516 pages_full não publicadas.",
            "do_not": "Publicar stems Drive como URL canônica.",
            "unblock": None,
        },
        "L280": {
            "phase": "P4",
            "md_population": "PARTIAL",
            "md_implemented": True,
            "reg_population": "COMPARE_ONLY",
            "evidence": ["cko_md/page_inventory.json"],
            "identities": ["FLD-SEO-OG-IMAGE"],
            "reg_instruments": [],
            "gap": "W3C/RFC 9309 não ingeridos. OG first-party no piloto.",
            "do_not": "hreflang fantasma para 29 idiomas sem página.",
            "unblock": None,
        },
        "L290": {
            "phase": "P4",
            "md_population": "PARTIAL",
            "md_implemented": True,
            "reg_population": "PARTIAL",
            "evidence": ["assets/img/og-default.png"],
            "identities": ["OG-DEFAULT-FIRST-PARTY"],
            "reg_instruments": ["INS-LEI-9610-1998"],
            "gap": "151 cards Drive COMPARE.",
            "do_not": "MedicalOrganization no JSON-LD.",
            "unblock": None,
        },
        "L300": {
            "phase": "P4",
            "md_population": "PARTIAL",
            "md_implemented": True,
            "reg_population": "PARTIAL",
            "evidence": ["render/fetch/index.html"],
            "identities": ["WebSite", "Organization"],
            "reg_instruments": [],
            "gap": "JSON-LD WebSite/Organization. Nunca MedicalOrganization.",
            "do_not": "Schema clínico sem identidade MD.",
            "unblock": None,
        },
        "L310": {
            "phase": "P4",
            "md_population": "PARTIAL",
            "md_implemented": False,
            "reg_population": "HOLD",
            "evidence": ["cko_md/who_i18n_modulation.json", "cko_reg/i18n_profile.json", "cko_md/translation_envelopes.json"],
            "identities": ["who.en+local.pt-BR", "MD-WHO-I18N-001", "MD-TR-ENV-001"],
            "reg_instruments": ["FLD-I18N-WHO-LOCAL-KEY"],
            "gap": "Owner APPROVED who.en+local.pt-BR. translation_gate HOLD. Seletor não ligado. Sem strings EN inventadas.",
            "do_not": "Inferir pt→pt-BR. Dump ICD/ICNP/GHO. Ligar o seletor.",
            "unblock": "UNBLOCK-I18N-TRANSLATION",
        },
        "L320": {
            "phase": "P5",
            "md_population": "EMPTY",
            "md_implemented": False,
            "reg_population": "EMPTY",
            "evidence": [],
            "identities": [],
            "reg_instruments": [],
            "gap": "Busca interna não observada no piloto.",
            "do_not": "Indexar pages_full em produção.",
            "unblock": None,
        },
        "L330": {
            "phase": "P5",
            "md_population": "EMPTY",
            "md_implemented": False,
            "reg_population": "EMPTY",
            "evidence": [],
            "identities": [],
            "reg_instruments": [],
            "gap": "Recomendação não observada. Cinco cards estáticos.",
            "do_not": "Ranking LLM de calculadora clínica.",
            "unblock": None,
        },
        "L340": {
            "phase": "P5",
            "md_population": "HOLD",
            "md_implemented": False,
            "reg_population": "HOLD",
            "evidence": [],
            "identities": [],
            "reg_instruments": [],
            "gap": "Favoritos/coleções exigiriam estado de usuário. LGPD HOLD.",
            "do_not": "localStorage.clear indiscriminado. Conta de usuário neste lote.",
            "unblock": None,
        },
        "L350": {
            "phase": "P5",
            "md_population": "HOLD",
            "md_implemented": False,
            "reg_population": "HOLD",
            "evidence": [],
            "identities": [],
            "reg_instruments": [],
            "gap": "Sem ads/telemetry de terceiro. adsbygoogle FORBIDDEN.",
            "do_not": "Google Analytics / adsbygoogle.",
            "unblock": None,
        },
        "L360": {
            "phase": "P5",
            "md_population": "EMPTY",
            "md_implemented": False,
            "reg_population": "EMPTY",
            "evidence": [],
            "identities": [],
            "reg_instruments": [],
            "gap": "Budget de performance não medido neste ciclo.",
            "do_not": "Inventar SLA.",
            "unblock": None,
        },
        "L370": {
            "phase": "P5",
            "md_population": "EMPTY",
            "md_implemented": False,
            "reg_population": "EMPTY",
            "evidence": [],
            "identities": [],
            "reg_instruments": [],
            "gap": "SLO/falha não populados. Release HOLD.",
            "do_not": "PASS de resiliência sem teste.",
            "unblock": None,
        },
        "L380": {
            "phase": "P5",
            "md_population": "PARTIAL",
            "md_implemented": True,
            "reg_population": "PARTIAL",
            "evidence": ["cko_assurance/monitoring_events.json"],
            "identities": ["IPE-AGENT-RUN-001"],
            "reg_instruments": [],
            "gap": "Eventos inbox. Sem OpenTelemetry cláusula.",
            "do_not": "Telemetry PII.",
            "unblock": None,
        },
        "L390": {
            "phase": "P5",
            "md_population": "EVIDENCE_PENDING",
            "md_implemented": False,
            "reg_population": "EVIDENCE_PENDING",
            "evidence": [],
            "identities": [],
            "reg_instruments": [],
            "gap": "ISO/IEC 21031 candidate. Sem métrica observada.",
            "do_not": "Claim green hosting.",
            "unblock": None,
        },
        "L400": {
            "phase": "P5",
            "md_population": "PARTIAL",
            "md_implemented": True,
            "reg_population": "PARTIAL",
            "evidence": ["cko_md/concept_renderer.json"],
            "identities": ["MD-CONCEPT-RENDER-001"],
            "reg_instruments": [],
            "gap": "Renderer PRESENTATION_ONLY. LLM canônico FORBIDDEN.",
            "do_not": "LLM como fonte de fórmula.",
            "unblock": None,
        },
        "L410": {
            "phase": "P5",
            "md_population": "PARTIAL",
            "md_implemented": True,
            "reg_population": "PARTIAL",
            "evidence": ["tests/test_who_i18n.py"],
            "identities": ["pytest"],
            "reg_instruments": [],
            "gap": "pytest local + CI. E2E clínico HOLD (release).",
            "do_not": "Publicar por CI verde.",
            "unblock": None,
        },
        "L420": {
            "phase": "P5",
            "md_population": "EVIDENCE_PENDING",
            "md_implemented": False,
            "reg_population": "EVIDENCE_PENDING",
            "evidence": [],
            "identities": [],
            "reg_instruments": [],
            "gap": "PDF 2.0/PDF-UA cláusula EVIDENCE_PENDING.",
            "do_not": "Export clínico sem perfil MD.",
            "unblock": None,
        },
        "L430": {
            "phase": "P5",
            "md_population": "HOLD",
            "md_implemented": False,
            "reg_population": "HOLD",
            "evidence": ["validators/release_gate.py"],
            "identities": ["REG-RELEASE-GATE"],
            "reg_instruments": [],
            "gap": "Publication HOLD. Cinco pilotos. Dimensionamento HOLD.",
            "do_not": "Auto-PASS de release.",
            "unblock": None,
        },
        "L440": {
            "phase": "P5",
            "md_population": "PARTIAL",
            "md_implemented": True,
            "reg_population": "PARTIAL",
            "evidence": ["cko_assurance/monitoring_events.json", "cko_inbox/vault/pointers.json"],
            "identities": ["SRC-LEI-9610-1998"],
            "reg_instruments": ["INS-LEI-9610-1998"],
            "gap": "WORM/freshness inbox. Não é monitoramento contínuo M7.",
            "do_not": "Apagar vault para limpar drift.",
            "unblock": None,
        },
    }


def _phase_for(code: str) -> str:
    spec = _layer_spec()
    return spec[code]["phase"]


def compose_layer_md_reg_phase() -> dict:
    spec = _layer_spec()
    slugs = _pilot_slugs()
    braden = (TOOLS_DIR / "braden.json").exists()
    rows = []
    for layer in LAYERS:
        code = layer["code"]
        item = spec[code]
        evidence_ok = []
        evidence_missing = []
        for rel in item["evidence"]:
            if _exists(*rel.split("/")):
                evidence_ok.append(rel)
            else:
                evidence_missing.append(rel)
        md_populated = item["md_population"] in {"PARTIAL", "COMPARE_ONLY"} and bool(
            item["identities"] or evidence_ok
        )
        row = {
            "business_key": f"LAYER-{layer['n']:03d}",
            "uuid": None,
            "layer_code": code,
            "layer_number": layer["n"],
            "canonical_name": layer["name"],
            "layer_class": layer["class"],
            "phase": item["phase"],
            "envelope_complete": True,
            "md": {
                "profile_ref": f"LAYER-{layer['n']:03d}-MD",
                "registers": layer["md"],
                "population": item["md_population"],
                "populated": md_populated,
                "implemented": item["md_implemented"] and not braden,
                "assured": False,
                "identities": item["identities"],
                "evidence_ok": evidence_ok,
                "evidence_missing": evidence_missing,
            },
            "reg": {
                "profile_ref": f"LAYER-{layer['n']:03d}-REG",
                "governs": layer["reg"],
                "population": item["reg_population"],
                "populated": item["reg_population"] == "PARTIAL" and bool(item["reg_instruments"] or evidence_ok),
                "implemented": False,
                "assured": False,
                "clause_text": "CLAUSE_TEXT_UNAVAILABLE",
                "applicability": "APPLICABILITY_UNVERIFIED",
                "instruments": item["reg_instruments"],
            },
            "gap": item["gap"],
            "do_not": item["do_not"],
            "owner_unblock": item["unblock"],
            "publication": "HOLD",
        }
        rows.append(row)
    counts = {
        "envelope_complete": sum(1 for row in rows if row["envelope_complete"]),
        "md_populated": sum(1 for row in rows if row["md"]["populated"]),
        "md_implemented": sum(1 for row in rows if row["md"]["implemented"]),
        "reg_populated": sum(1 for row in rows if row["reg"]["populated"]),
        "assured": sum(1 for row in rows if row["md"]["assured"] or row["reg"]["assured"]),
    }
    by_phase = []
    for phase in PHASES:
        codes = set(phase["layers"])
        by_phase.append({
            **phase,
            "md_populated": sum(1 for row in rows if row["layer_code"] in codes and row["md"]["populated"]),
            "layer_count": len(phase["layers"]),
        })
    return {
        "business_key": "MD-LAYER-PHASE-001",
        "uuid": None,
        "status": "DOCUMENTADO",
        "implemented": True,
        "publication": "HOLD",
        "assured": False,
        "rule": (
            "Envelope MD+REG completo nas 44 camadas ≠ população completa ≠ implementação ≠ assurance. "
            "SEM EVIDÊNCIA → EVIDENCE_PENDING/HOLD. certified=false."
        ),
        "population": len(rows),
        "pilot_slugs": slugs,
        "braden_in_data_tools": braden,
        "counts": counts,
        "phases": by_phase,
        "layers": rows,
        "layer_records_remain_m0": True,
        "note": (
            "cko_core/layer_registry.json permanece M0_REGISTERED (EXISTS). "
            "Este catálogo qualifica evidência por camada sem promover maturidade M5."
        ),
        "evaluated_at": _now(),
    }


def _enrich_profiles(catalog: dict) -> None:
    by_code = {row["layer_code"]: row for row in catalog["layers"]}
    md_doc = _load(MD_PROFILES_PATH)
    reg_doc = _load(REG_PROFILES_PATH)
    md_profiles = md_doc.get("profiles") or []
    reg_profiles = reg_doc.get("profiles") or []
    for profile in md_profiles:
        code = next(
            (row["layer_code"] for row in catalog["layers"] if row["md"]["profile_ref"] == profile.get("business_key")),
            None,
        )
        row = by_code.get(code) if code else None
        if not row:
            continue
        profile["populated"] = row["md"]["populated"]
        profile["implemented"] = row["md"]["implemented"]
        profile["assured"] = False
        profile["envelope_complete"] = True
        profile["phase"] = row["phase"]
        profile["population_status"] = row["md"]["population"]
        profile["evidence_ok"] = row["md"]["evidence_ok"]
        profile["gap"] = row["gap"]
        profile["do_not"] = row["do_not"]
        profile["publication"] = "HOLD"
    for profile in reg_profiles:
        code = next(
            (row["layer_code"] for row in catalog["layers"] if row["reg"]["profile_ref"] == profile.get("business_key")),
            None,
        )
        row = by_code.get(code) if code else None
        if not row:
            continue
        profile["populated"] = row["reg"]["populated"]
        profile["implemented"] = False
        profile["assured"] = False
        profile["envelope_complete"] = True
        profile["phase"] = row["phase"]
        profile["population_status"] = row["reg"]["population"]
        profile["clause_text"] = "CLAUSE_TEXT_UNAVAILABLE"
        profile["applicability"] = "APPLICABILITY_UNVERIFIED"
        profile["instruments"] = row["reg"]["instruments"]
        profile["gap"] = row["gap"]
        profile["do_not"] = row["do_not"]
        profile["publication"] = "HOLD"
    if md_doc:
        md_doc["phase_ref"] = "MD-LAYER-PHASE-001"
        md_doc["note"] = "Envelope completo ≠ populated. publication HOLD."
        md_doc["profiles"] = md_profiles
        _dump(MD_PROFILES_PATH, md_doc)
    if reg_doc:
        reg_doc["phase_ref"] = "MD-LAYER-PHASE-001"
        reg_doc["note"] = (
            "REG qualifica identidades MD. clause_text CLAUSE_TEXT_UNAVAILABLE. "
            "Nenhum instrument copiado como regra de produto."
        )
        reg_doc["profiles"] = reg_profiles
        _dump(REG_PROFILES_PATH, reg_doc)


def evaluate_layer_md_reg() -> dict:
    from .govlib import compare_claimed_32

    compare_claimed_32()
    catalog = compose_layer_md_reg_phase()
    _dump(CATALOG_PATH, catalog)
    _enrich_profiles(catalog)
    assert catalog["counts"]["envelope_complete"] == 44
    assert catalog["counts"]["assured"] == 0
    assert catalog["braden_in_data_tools"] is False
    assert len(layer_records()) == 44
    return {
        "agent_id": "AG-LAYER-PHASE",
        "class": "MD",
        "role": "CHECKER",
        "status": "DOCUMENTADO",
        "envelope_complete": 44,
        "md_populated": catalog["counts"]["md_populated"],
        "md_implemented": catalog["counts"]["md_implemented"],
        "assured": False,
        "publication": "HOLD",
        "llm_used": False,
        "promotes_to_md": False,
        "writes_to": "cko_md/layer_md_reg_phase.json",
    }
