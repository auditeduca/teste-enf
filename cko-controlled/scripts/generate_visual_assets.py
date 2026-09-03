#!/usr/bin/env python3
"""Emit Visual Asset System as DesignOS policy-as-code HOLD.

Not a 45th sequential layer. Binds MEDIA / DERIVE / DS / OG / EXPORT / DOC-TPL.
One canonical object → many visual projections. Generator NOT_ASSERTED.
Word/PPT binaries are not claimed created.
"""
from __future__ import annotations

import json
from pathlib import Path

GATE = Path(__file__).resolve().parents[1]
SITE = GATE.parent / "reference-website"
OUT_POLICY = GATE / "public" / "policies" / "visual-assets.json"
OUT_SITE = SITE / "data" / "cko" / "visual-assets.json"

CASCADE = [
    "policy-as-code",
    "schemas",
    "graph-constraints",
    "CI-gates",
    "runtime-assertions",
    "automatic-evidence",
]

BIND_LAYERS = [
    "LYR-DS-001",
    "LYR-MEDIA-001",
    "LYR-DERIVE-001",
    "LYR-OG-001",
    "LYR-EXPORT-001",
    "LYR-DOC-TPL-001",
]

OBJECT_LANGUAGES = [
    ("CAL", "calculator", "fórmula + instrumento + número"),
    ("SCL", "scale", "score + gráfico"),
    ("SCR", "screener", "perguntas + checklist"),
    ("ART", "article", "editorial"),
    ("CAS", "clinical_case", "contexto clínico abstrato; sem paciente real"),
    ("QIZ", "quiz", "questão/interação"),
    ("QST", "question", "questão"),
    ("FLH", "flashcard", "pergunta/resposta"),
    ("SIM", "exam_sim", "prova/documento"),
    ("INF", "infographic", "dados/visualização"),
    ("PBG", "pocket_guide", "referência rápida"),
    ("SLD", "slide", "apresentação"),
    ("EBK", "ebook", "capa editorial"),
    ("PDF", "pdf", "documento"),
    ("DOC", "docx", "documento"),
    ("XLS", "xlsx", "tabela/dados"),
]

FAMILIES = [
    {
        "id": "discovery",
        "name": "Discovery Images",
        "purpose": "encontrar o conteúdo",
        "surfaces": ["homepage_card", "library_card", "search_result", "related", "recommendation", "category", "thumbnail"],
    },
    {
        "id": "share",
        "name": "Share Images",
        "purpose": "sair do ecossistema",
        "surfaces": ["og", "linkedin", "facebook", "x", "whatsapp", "telegram", "instagram", "pinterest", "story"],
    },
    {
        "id": "content",
        "name": "Content Images",
        "purpose": "dentro do conteúdo",
        "surfaces": ["article_hero", "illustration", "diagram", "table", "infographic", "clinical_image", "pdf_cover", "slide_cover"],
    },
]

VIS_POLICIES = [
    ("POL-VIS-001", "Identidade visual canônica"),
    ("POL-VIS-002", "Assets: nomenclatura, formato, ciclo de vida"),
    ("POL-VIS-003", "Templates versionados"),
    ("POL-VIS-004", "Evidências visuais"),
    ("POL-VIS-005", "Proveniência Object→Content→Template→Generator→Asset→Publication"),
    ("POL-VIS-006", "Acessibilidade visual"),
    ("POL-VIS-007", "Direitos autorais e licenciamento"),
    ("POL-VIS-008", "SEO/GEO/AEO visual"),
    ("POL-VIS-009", "Social media assets"),
    ("POL-VIS-010", "Document assets PDF/DOCX/XLSX/PPTX/ebook"),
    ("POL-VIS-011", "Versionamento independente template/asset/objeto"),
    ("POL-VIS-012", "Alteração: sem overwrite silencioso"),
    ("POL-VIS-013", "Depreciação ACTIVE→SUPERSEDED→DEPRECATED→ARCHIVED"),
    ("POL-VIS-014", "Quality gates"),
    ("POL-VIS-015", "Segurança e integridade"),
]

EVIDENCE_TEMPLATES = [
    "EVD-001 Source Evidence",
    "EVD-002 Claim Evidence",
    "EVD-003 Clinical Evidence",
    "EVD-004 Regulatory Evidence",
    "EVD-005 Visual Evidence",
    "EVD-006 Accessibility Evidence",
    "EVD-007 Copyright Evidence",
    "EVD-008 Calculation Evidence",
    "EVD-009 AI Generation Evidence",
    "EVD-010 Human Review Evidence",
    "EVD-011 Publication Evidence",
    "EVD-012 Change Evidence",
    "EVD-013 Provenance Evidence",
    "EVD-014 Validation Evidence",
    "EVD-015 Audit Evidence",
]

REGISTRY_FIELDS = [
    "asset_id",
    "object_id",
    "asset_type",
    "variant",
    "dimensions",
    "format",
    "template_id",
    "template_version",
    "generated_at",
    "content_hash",
    "alt_text",
    "caption",
    "copyright",
    "license",
    "creator",
    "source",
    "provenance",
    "status",
]


def build() -> dict:
    assert len(VIS_POLICIES) == 15
    assert len(OBJECT_LANGUAGES) == 16
    assert len(FAMILIES) == 3
    return {
        "id": "POL-CKO-VISUAL-ASSET-1.0.0",
        "kind": "policy-as-code",
        "mode": "fail-closed",
        "root": False,
        "starts_at": "policy-as-code",
        "parent": "POL-CKO-POLICY-MASTER-CONTRACT-1.0.0",
        "inherits": ["POL-CKO-FAIL-CLOSED-1.0.0", "POL-CKO-UNIVERSAL-TOOL-1.3.0"],
        "document_id": "CKO-VAS-001",
        "document_version": "1.0.0",
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
        "layer_count_must_remain": 44,
        "primary_layers": BIND_LAYERS,
        "library_label": "09. VISUAL ASSET LIBRARY",
        "library_is_layer": False,
        "one_image_per_page": False,
        "principle": "Canonical object → Visual Identity → Web/Social/File projections → Image Registry. Screenshot of the page is not an OG image.",
        "families": FAMILIES,
        "object_languages": [
            {"code": code, "object_type": typ, "language": lang, "status": "DOCUMENTADO_HOLD"}
            for code, typ, lang in OBJECT_LANGUAGES
        ],
        "dimensions": {
            "og": {"width": 1200, "height": 630, "ratio": "1.91:1"},
            "linkedin": {"width": 1200, "height": 627, "ratio": "1.91:1", "master": "og"},
            "social": ["LANDSCAPE", "SQUARE", "PORTRAIT", "STORY"],
        },
        "text_budget": {
            "thumbnail": "3-7",
            "og": "5-12",
            "social": "3-10",
            "hero": "full_headline_allowed",
            "infographic": "information_allowed",
        },
        "hierarchy": [
            "CANONICAL_OBJECT",
            "CONTENT_MODEL",
            "DESIGN_SYSTEM",
            "VISUAL_CONTRACT",
            "ASSET_GENERATOR",
            "IMAGE_REGISTRY",
            "PROVENANCE",
            "EVIDENCE",
        ],
        "visual_contract": {
            "identity_required": True,
            "discovery_required": ["homepage_card", "library_card", "search_thumbnail"],
            "social_required": ["og", "linkedin"],
            "accessibility": {"alt_text": "required", "decorative_flag": "required"},
            "provenance": {"generated_from": "canonical_object_id", "template_version": "required", "asset_version": "required"},
            "status": "DOCUMENTADO_HOLD",
        },
        "image_registry": {
            "replaces": "ad_hoc_/images_folder_as_truth",
            "fields": REGISTRY_FIELDS,
            "status": "DOCUMENTADO_HOLD",
            "materialized": False,
        },
        "generator": {
            "id": "visual_asset_generator",
            "operational": "NOT_ASSERTED",
            "may_publish": False,
            "human_review_required": True,
        },
        "document_projections": {
            "pdf_cover": "HOLD",
            "docx": {"cover": "HOLD", "toc": "HOLD", "identification": "HOLD", "files_generated": False},
            "pptx": {"title_slide": "HOLD", "files_generated": False},
            "xlsx": {"banner_not_large_image": True, "governance_sheet": "HOLD"},
            "ebook_cover": "HOLD",
            "note": "Word/PPT completos não foram gerados. São projeções do mesmo objeto, não conteúdos paralelos.",
        },
        "internal_policies": [
            {
                "id": pid,
                "name": name,
                "status": "DOCUMENTADO_HOLD",
                "active": False,
                "implemented": False,
                "inherits_master": True,
            }
            for pid, name in VIS_POLICIES
        ],
        "evidence_templates": [{"id": row.split()[0], "name": row, "status": "DOCUMENTADO_HOLD"} for row in EVIDENCE_TEMPLATES],
        "utc_bindings": ["UTC-045", "UTC-047", "UTC-053", "UTC-056", "UTC-071"],
        "publication_gate": [
            "GENERATED",
            "VALIDATED",
            "EVIDENCED",
            "REVIEWED",
            "APPROVED",
            "PUBLISHED",
        ],
        "evaluation": {
            "verdict": "DOCUMENTADO_HOLD_NOT_IMPLEMENTED",
            "clinical_promotion": "DENIED",
            "word_pptx_created": False,
        },
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
    print(f"wrote {OUT_POLICY} families={len(doc['families'])} vis_pol={len(doc['internal_policies'])}")
