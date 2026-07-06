#!/usr/bin/env python3
"""Build home_page schema 2026.3.0 (pt-BR) from 2026.1 canonical + section templates."""
from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "datasets" / "content" / "site" / "home_page.json"
OUT_SCHEMA = ROOT / "datasets" / "content" / "schemas" / "home_page.2026.3.pt-BR.json"
OUT_SITE = ROOT / "datasets" / "content" / "site" / "home_page.json"

PAGE_SECTIONS_ORDER = [
    "hero",
    "search",
    "profile_selector",
    "featured",
    "nursing_os_map",
    "knowledge_hub",
    "clinical_cases",
    "competency_track",
    "ai_assistant",
    "management_block",
    "patient_safety_center",
    "occupational_health",
    "impact_dashboard",
    "global_platform",
    "sustainability_block",
    "governance_center",
    "cta_final",
]


def _pt_br_sections(base: dict) -> dict:
    edu = base.get("education_block") or {}
    mgmt = base.get("management_block") or {}
    eco = base.get("tool_ecosystem") or {}
    daily = base.get("daily_tip") or {}

    return {
        "page_sections_order": PAGE_SECTIONS_ORDER,
        "profile_selector": {
            "title": "Personalize sua experiência",
            "subtitle": "Conteúdos, ferramentas e indicadores adaptados ao seu perfil profissional.",
            "default_profile": "profissional",
            "items": [
                {
                    "code": "estudante",
                    "label": "Sou estudante",
                    "description": "Trilhas, flashcards e simulados para sua formação.",
                    "href": "/educacao",
                    "icon": "graduation-cap",
                },
                {
                    "code": "profissional",
                    "label": "Sou enfermeiro(a) assistencial",
                    "description": "Calculadoras, escalas e protocolos para o plantão.",
                    "href": "/calculadoras",
                    "icon": "user-check",
                },
                {
                    "code": "profissional",
                    "label": "Sou enfermeiro(a) de urgência",
                    "description": "Ferramentas rápidas para situações de alta complexidade.",
                    "href": "/ferramentas",
                    "icon": "siren",
                },
                {
                    "code": "gestor",
                    "label": "Sou gestor(a)",
                    "description": "Indicadores, qualidade e gestão de equipes.",
                    "href": "/gestao",
                    "icon": "chart",
                },
                {
                    "code": "academico",
                    "label": "Sou docente",
                    "description": "Recursos didáticos e bancos de questões para ensino.",
                    "href": "/biblioteca",
                    "icon": "book",
                },
                {
                    "code": "gestor",
                    "label": "Sou instituição",
                    "description": "Soluções corporativas, compliance e capacitação em escala.",
                    "href": "/sobre",
                    "icon": "building",
                },
            ],
        },
        "clinical_feed": {
            "title": "Atualizações clínicas",
            "subtitle": "Acompanhe novidades da plataforma em tempo real.",
            "view_all_label": "Ver todas as atualizações",
            "view_all_href": "/dicas",
            "categories": [
                {"label": "Novo guia", "icon": "file-text"},
                {"label": "Novo protocolo", "icon": "clipboard"},
                {"label": "Novo artigo", "icon": "document"},
                {"label": "Novo caso clínico", "icon": "stethoscope"},
                {"label": "Nova ferramenta", "icon": "calculator"},
            ],
            "feed_source": "CMS.DYNAMIC",
            "max_items_displayed": 6,
            "badge": daily.get("badge", "Dica do dia"),
            "more_label": daily.get("more_label", "Ver mais dicas"),
            "more_href": daily.get("more_href", "/dicas"),
        },
        "nursing_os_map": {
            "title": "Ecossistema Calculadoras de Enfermagem",
            "subtitle": "Como assistência, gestão, educação e sustentabilidade se conectam em uma única plataforma.",
            "layout": "orbital",
            "center_node": {"label": "Nursing OS", "icon": "network"},
            "orbit_nodes": [
                {
                    "label": "Assistência",
                    "description": "Calculadoras, escalas e protocolos clínicos.",
                    "href": "/calculadoras",
                    "icon": "calculator",
                    "position": "right",
                },
                {
                    "label": "Educação",
                    "description": "Artigos, cursos, flashcards e simulados.",
                    "href": "/educacao",
                    "icon": "book",
                    "position": "top",
                },
                {
                    "label": "Gestão",
                    "description": "Indicadores, qualidade e segurança do paciente.",
                    "href": "/gestao",
                    "icon": "chart",
                    "position": "left",
                },
                {
                    "label": "Sustentabilidade",
                    "description": "Tecnologia digital first com impacto mensurável.",
                    "href": "/sustentabilidade",
                    "icon": "leaf",
                    "position": "bottom",
                },
            ],
            "cta": {"label": "Explorar ecossistema", "href": "/ferramentas"},
        },
        "knowledge_hub": {
            "title": "Conhecimento aplicado",
            "subtitle": "Do artigo à certificação: trilha contínua de aprendizado clínico.",
            "flow": [
                {"step": 1, "label": "Artigo", "icon": "document"},
                {"step": 2, "label": "Flashcard", "icon": "lightbulb"},
                {"step": 3, "label": "Quiz", "icon": "check-circle"},
                {"step": 4, "label": "Caso clínico", "icon": "stethoscope"},
                {"step": 5, "label": "Certificado", "icon": "award"},
            ],
            "items": [
                {"title": "Artigos e protocolos", "href": "/artigos", "icon": "document"},
                {"title": "Casos clínicos", "href": "/simulados", "icon": "stethoscope"},
                {"title": "Flashcards", "href": "/flashcards", "icon": "lightbulb"},
                {"title": "Simulados", "href": "/simulados", "icon": "play"},
                {"title": "Guias", "href": "/biblioteca", "icon": "file-text"},
                {"title": "Biblioteca digital", "href": "/biblioteca", "icon": "book"},
            ],
            "cta": {"label": "Iniciar trilha", "href": "/educacao"},
            "image": edu.get("image", "homepage-section-001.webp"),
            "image_alt": edu.get("image_alt", "Profissionais de enfermagem em capacitação"),
            "badge": edu.get("badge"),
        },
        "clinical_cases": {
            "title": "Treinamento clínico",
            "subtitle": "Casos clínicos interativos por especialidade.",
            "view_all_label": "Ver todos os casos",
            "view_all_href": "/simulados",
            "items": [
                {"title": "Adulto", "href": "/simulados", "icon": "user"},
                {"title": "Pediatria", "href": "/simulados", "icon": "baby"},
                {"title": "UTI", "href": "/simulados", "icon": "activity"},
                {"title": "Urgência", "href": "/simulados", "icon": "siren"},
                {"title": "Centro cirúrgico", "href": "/simulados", "icon": "scissors"},
                {"title": "Saúde da família", "href": "/simulados", "icon": "home"},
            ],
        },
        "competency_track": {
            "title": "Meu desenvolvimento",
            "subtitle": "Avalie e evolua suas competências profissionais.",
            "tracks": [
                {"label": "Técnica", "icon": "tool"},
                {"label": "Científica", "icon": "flask"},
                {"label": "Gestão", "icon": "chart"},
                {"label": "Liderança", "icon": "users"},
                {"label": "Segurança do paciente", "icon": "shield"},
                {"label": "Sustentabilidade", "icon": "leaf"},
            ],
            "initial_assessment": {
                "label": "Fazer avaliação inicial",
                "href": "/trilhas",
            },
            "cta": {"label": "Ver minha trilha", "href": "/trilhas"},
        },
        "ai_assistant": {
            "title": "Assistente clínico",
            "subtitle": "Inteligência artificial com supervisão humana a serviço da prática de enfermagem.",
            "capabilities": [
                {"label": "Responde dúvidas clínicas", "icon": "message-circle"},
                {"label": "Sugere conteúdo personalizado", "icon": "sparkles"},
                {"label": "Monta plano de estudos", "icon": "calendar"},
                {"label": "Explica protocolos", "icon": "file-text"},
                {"label": "Gera simulados", "icon": "play"},
            ],
            "disclaimer": "Respostas geradas por IA não substituem decisão clínica profissional.",
            "cta": {"label": "Conversar com o assistente", "href": "/ferramentas"},
        },
        "patient_safety_center": {
            "title": "Centro de segurança do paciente",
            "subtitle": "Metas internacionais, eventos adversos e protocolos de segurança em um só lugar.",
            "items": [
                {
                    "title": "Metas Internacionais de Segurança do Paciente (IPSG)",
                    "href": "/gestao",
                    "icon": "target",
                },
                {"title": "Eventos adversos", "href": "/gestao", "icon": "alert-triangle"},
                {"title": "Quase incidente", "href": "/gestao", "icon": "eye"},
                {"title": "Notificações", "href": "/gestao", "icon": "bell"},
                {"title": "Protocolos de segurança", "href": "/protocolos", "icon": "clipboard"},
            ],
            "cta": {"label": "Acessar centro de segurança", "href": "/gestao"},
        },
        "occupational_health": {
            "title": "Saúde ocupacional em enfermagem",
            "subtitle": "Gestão de riscos e bem-estar do profissional de saúde.",
            "items": [
                {
                    "title": "PGR",
                    "description": "Programa de Gerenciamento de Riscos.",
                    "href": "/gestao",
                    "icon": "clipboard",
                },
                {
                    "title": "GRO",
                    "description": "Gerenciamento de Riscos Ocupacionais.",
                    "href": "/gestao",
                    "icon": "shield",
                },
                {
                    "title": "Riscos biológicos",
                    "description": "Prevenção e controle de exposição biológica.",
                    "href": "/gestao",
                    "icon": "biohazard",
                },
                {
                    "title": "NR-01",
                    "description": "Gerenciamento de SST e segurança.",
                    "href": "/gestao",
                    "icon": "hardhat",
                },
                {
                    "title": "NR-32",
                    "description": "Segurança no trabalho em serviços de saúde.",
                    "href": "/gestao",
                    "icon": "hardhat",
                },
                {
                    "title": "Saúde mental e burnout",
                    "description": "Recursos para prevenção e apoio emocional.",
                    "href": "/gestao",
                    "icon": "heart",
                },
                {
                    "title": "Ergonomia",
                    "description": "Orientações para prática segura e ergonômica.",
                    "href": "/gestao",
                    "icon": "activity",
                },
            ],
            "cta": {"label": "Acessar saúde ocupacional", "href": "/gestao"},
        },
        "impact_dashboard": {
            "title": "Impacto da plataforma",
            "subtitle": "Números que refletem o uso real por enfermeiros e enfermeiras.",
            "data_source": "ANALYTICS.AGGREGATED",
            "refresh_interval": "daily",
            "metrics": [
                {
                    "binding": "total_calculations",
                    "label": "Cálculos realizados",
                    "icon": "calculator",
                    "suffix": "+",
                    "value": "2,4M",
                },
                {
                    "binding": "protocols_accessed",
                    "label": "Protocolos acessados",
                    "icon": "clipboard",
                    "suffix": "+",
                    "value": "890K",
                },
                {
                    "binding": "decision_trees_used",
                    "label": "Árvores de decisão usadas",
                    "icon": "git-branch",
                    "suffix": "+",
                    "value": "156K",
                },
                {
                    "binding": "simulations_completed",
                    "label": "Simulados concluídos",
                    "icon": "play",
                    "suffix": "+",
                    "value": "420K",
                },
                {
                    "binding": "study_hours_logged",
                    "label": "Horas de estudo registradas",
                    "icon": "clock",
                    "suffix": "+",
                    "value": "1,1M",
                },
            ],
        },
        "sustainability_block": {
            "title": "Sustentabilidade digital",
            "subtitle": "Tecnologia digital first com impacto ambiental mensurável.",
            "data_source": "ANALYTICS.AGGREGATED",
            "metrics": [
                {
                    "binding": "paper_sheets_saved",
                    "label": "Folhas de papel economizadas",
                    "icon": "leaf",
                    "suffix": "+",
                    "value": "3,2M",
                },
                {
                    "binding": "co2_reduced_kg",
                    "label": "CO₂ reduzido (kg)",
                    "icon": "wind",
                    "suffix": "+",
                    "value": "48K",
                },
                {
                    "binding": "digital_protocols_pct",
                    "label": "Protocolos 100% digitais",
                    "icon": "document",
                    "suffix": "%",
                    "value": "94",
                },
            ],
            "cta": {"label": "Conhecer nossa sustentabilidade", "href": "/sustentabilidade"},
        },
        "governance_center": {
            "title": "Governança e transparência",
            "subtitle": "Confiança construída em privacidade, acessibilidade e responsabilidade digital.",
            "items": [
                {"title": "Privacidade e LGPD", "href": "/privacidade", "icon": "shield"},
                {"title": "Cookies", "href": "/privacidade", "icon": "cookie"},
                {"title": "IA responsável", "href": "/sustentabilidade", "icon": "brain"},
                {"title": "Sustentabilidade", "href": "/sustentabilidade", "icon": "leaf"},
                {"title": "Acessibilidade", "href": "/acessibilidade", "icon": "users"},
                {"title": "Metodologia científica", "href": "/sobre", "icon": "flask"},
            ],
            "scientific_credibility": {
                "title": "Credibilidade científica",
                "subtitle": "Conteúdo revisado por especialistas, com metodologia transparente.",
                "items": [
                    {"title": "Conselho editorial", "href": "/sobre", "icon": "users"},
                    {"title": "Especialistas colaboradores", "href": "/equipe", "icon": "award"},
                    {"title": "Processo de revisão", "href": "/sobre", "icon": "check-circle"},
                ],
                "partners": {
                    "title": "Parceiros e instituições",
                    "categories": ["Universidades", "Hospitais", "Sociedades científicas"],
                },
            },
            "cta": {"label": "Acessar centro de governança", "href": "/privacidade"},
        },
        "cta_final": {
            "title": "Pronto para elevar sua prática de enfermagem?",
            "subtitle": "Junte-se a profissionais em mais de 195 países que usam tecnologia para uma enfermagem mais segura e eficiente.",
            "cta_primary": {"label": "Criar conta gratuita", "href": "/login"},
            "cta_secondary": {"label": "Explorar ferramentas", "href": "/ferramentas"},
        },
        "management_block": deepcopy(mgmt),
        "global_platform": deepcopy(base.get("global_platform") or {}),
        "tool_ecosystem": deepcopy(eco),
        "schema_changelog": [
            {
                "version": "2026.3.0",
                "date": "2026-06-20",
                "summary": "Substituição de daily_tip/education_block por clinical_feed/knowledge_hub; 12 novas seções; page_sections_order.",
            }
        ],
    }


def build_2026_3(base: dict) -> dict:
    out = deepcopy(base)
    out["schema_version"] = "2026.3.0"
    out["generated_at"] = "2026-06-20T12:00:00Z"
    sections = _pt_br_sections(base)
    out.update(sections)
    out.pop("daily_tip", None)
    out.pop("education_block", None)
    return out


def main() -> int:
    promote = "--promote" in sys.argv
    base = json.loads(SRC.read_text(encoding="utf-8"))
    doc = build_2026_3(base)
    OUT_SCHEMA.parent.mkdir(parents=True, exist_ok=True)
    OUT_SCHEMA.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_SCHEMA.relative_to(ROOT)}")
    if promote:
        OUT_SITE.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Promoted -> {OUT_SITE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
