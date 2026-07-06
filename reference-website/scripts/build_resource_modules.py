#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera páginas HTML modulares a partir dos TSX em Downloads."""
import json
import re
import shutil
import zipfile
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOWNLOADS = Path.home() / "Downloads"
OUT_DATA = ROOT / "js" / "modules" / "data"

HEAD_BASE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/main.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css" crossorigin="anonymous" referrerpolicy="no-referrer" />
<link rel="stylesheet" href="css/site-styles.css">
<style>
  #site-header:empty {{ display:block; min-height:118px; }}
  #site-a11y:empty {{ display:block; }}
  #site-footer:empty {{ display:block; min-height:320px; background:var(--navy-900,#1a3e74); }}
</style>
{extra_head}
</head>
<body data-page="{page_id}">
<a href="#main-content" class="skip-link">Pular para o conteúdo principal</a>
<div id="site-header"></div>
<div id="site-a11y"></div>
<main id="main-content">
"""

FOOT = """
<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">
<defs>
  <symbol id="i-clipboard" viewBox="0 0 24 24"><rect x="7" y="3" width="10" height="4" rx="1"/><rect x="5" y="7" width="14" height="14" rx="2"/></symbol>
  <symbol id="i-target" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/></symbol>
  <symbol id="i-layers" viewBox="0 0 24 24"><path d="M12 3 3 8l9 5 9-5-9-5z"/><path d="M3 12l9 5 9-5"/></symbol>
  <symbol id="i-chart" viewBox="0 0 24 24"><line x1="6" y1="20" x2="6" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="18" y1="20" x2="18" y2="14"/></symbol>
  <symbol id="i-check" viewBox="0 0 24 24"><path d="M5 12l4 4 10-10"/></symbol>
  <symbol id="i-arrow" viewBox="0 0 24 24"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></symbol>
  <symbol id="i-search" viewBox="0 0 24 24"><circle cx="11" cy="11" r="6"/><line x1="16" y1="16" x2="21" y2="21"/></symbol>
  <symbol id="i-shieldcheck" viewBox="0 0 24 24"><path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6z"/><path d="m9 12 2 2 4-4"/></symbol>
</defs></svg>
</main>
<div id="site-footer"></div>
<div id="site-cookie"></div>
<script src="js/partials-loader.js"></script>
<script src="js/resource-pages.js"></script>
{page_scripts}
</body>
</html>
"""


def strip_icons(block: str) -> str:
    block = re.sub(r"\bicon:\s*\w+,?\s*", "", block)
    block = re.sub(r"\bIcon:\s*\w+,?\s*", "", block)
    block = re.sub(r"color:\s*'[^']*',?\s*", "", block)
    block = re.sub(r"iconColor:\s*'[^']*',?\s*", "", block)
    block = re.sub(r"iconBg:\s*'[^']*',?\s*", "", block)
    block = re.sub(r"iconBorder:\s*'[^']*',?\s*", "", block)
    block = re.sub(r"bgColor:\s*'[^']*',?\s*", "", block)
    block = re.sub(r"textColor:\s*'[^']*',?\s*", "", block)
    block = re.sub(r"borderColor:\s*'[^']*',?\s*", "", block)
    block = re.sub(r"formatColor:\s*'[^']*',?\s*", "", block)
    block = re.sub(r"lightColor:\s*'[^']*',?\s*", "", block)
    block = re.sub(r"borderColor:\s*'[^']*',?\s*", "", block)
    return block


def extract_ts_array(content: str, varname: str):
    m = re.search(rf"const\s+{varname}\s*=\s*\[", content)
    if not m:
        return None
    start = m.end() - 1
    depth = 0
    for i in range(start, len(content)):
        if content[i] == "[":
            depth += 1
        elif content[i] == "]":
            depth -= 1
            if depth == 0:
                block = content[start : i + 1]
                block = strip_icons(block)
                block = re.sub(r"(\w+):", r'"\1":', block)
                block = block.replace("'", '"')
                block = re.sub(r",\s*}", "}", block)
                block = re.sub(r",\s*]", "]", block)
                try:
                    return json.loads(block)
                except json.JSONDecodeError:
                    return None
    return None


def read_tsx(name: str) -> str:
    p = DOWNLOADS / name
    if p.exists():
        return p.read_text(encoding="utf-8")
    return ""


def read_zip_tsx(zip_name: str, inner: str) -> str:
    zpath = DOWNLOADS / zip_name
    if not zpath.exists():
        return ""
    with zipfile.ZipFile(zpath) as zf:
        return zf.read(inner).decode("utf-8")


def shell(title, desc, page_id, body, page_scripts="", extra_head=""):
    return (
        HEAD_BASE.format(
            title=title, description=desc, page_id=page_id, extra_head=extra_head
        )
        + body
        + FOOT.format(page_scripts=page_scripts)
    )


def hero_block(title, accent, subtitle, cta_href, cta_label, steps_html=""):
    side = ""
    if steps_html:
        side = f'<div class="module-hero-card">{steps_html}</div>'
    return f"""
<section class="page-hero module-hero">
  <div class="page-hero-grid">
    <div>
      <p class="module-kicker"><svg class="icon icon-sm"><use href="#i-clipboard"/></svg> Calculadoras de Enfermagem</p>
      <h1>{title}<span class="accent">{accent}</span></h1>
      <p>{subtitle}</p>
      <div class="hero-actions">
        <a class="btn btn-green" href="{cta_href}">{cta_label}</a>
        <a class="btn btn-outline-white" href="index.html">Voltar ao início</a>
      </div>
    </div>
    {side}
  </div>
</section>
<div class="reading-progress" aria-hidden="true"></div>
"""


def steps_list(steps):
    items = []
    for s in steps:
        items.append(
            f'<div class="module-step"><span class="module-step-num">{s["n"]}</span>'
            f'<div><strong>{s["t"]}</strong><p>{s["d"]}</p></div></div>'
        )
    return '<div class="module-steps">' + "".join(items) + "</div>"


def feature_grid(features):
    cards = []
    for f in features:
        icon = f.get("icon", "i-check")
        cards.append(
            f'<article class="module-card"><div class="module-card-icon"><svg class="icon"><use href="#{icon}"/></svg></div>'
            f'<h3>{f["title"]}</h3><p>{f["desc"]}</p></article>'
        )
    return f'<section class="section module-section"><div class="container"><div class="section-head"><h2>Funcionalidades</h2></div><div class="module-grid-4">{"".join(cards)}</div></div></section>'


def faq_section(faqs):
    items = []
    for i, f in enumerate(faqs):
        items.append(
            f'<div class="faq-item"><button type="button" class="faq-q" aria-expanded="false">{f["q"]}'
            f'<svg class="icon icon-sm"><use href="#i-arrow"/></svg></button>'
            f'<div class="faq-a"><p>{f["a"]}</p></div></div>'
        )
    return f'<section class="section"><div class="container container-narrow"><div class="section-head"><h2>Perguntas frequentes</h2></div><div class="faq-list">{"".join(items)}</div></div></section>'


def catalog_shell(title, desc, page_id, data_file, categories_key, items_key, search_placeholder):
    body = hero_block(
        title.split(" — ")[0] if " — " in title else title[:20],
        title.split(" — ")[-1] if " — " in title else "Consulta clínica",
        desc,
        "#catalogo",
        "Explorar",
        "",
    )
    body += f"""
<section class="section catalog-section" id="catalogo">
  <div class="container">
    <div class="catalog-toolbar">
      <div class="catalog-search">
        <svg class="icon"><use href="#i-search"/></svg>
        <input type="search" id="catalog-search" placeholder="{search_placeholder}" aria-label="Buscar">
      </div>
      <div class="catalog-filters" id="catalog-filters" role="tablist"></div>
    </div>
    <div class="catalog-grid" id="catalog-grid"></div>
    <aside class="catalog-detail" id="catalog-detail" hidden></aside>
  </div>
</section>
<button type="button" class="back-top" id="back-top" aria-label="Voltar ao topo"><svg class="icon"><use href="#i-arrow"/></svg></button>
"""
    scripts = f"""
<script>
window.CATALOG_CONFIG = {{
  dataUrl: "js/modules/data/{data_file}",
  categoriesKey: "{categories_key}",
  itemsKey: "{items_key}"
}};
</script>
<script src="js/modules/catalog-page.js"></script>
"""
    return shell(title, desc, page_id, body, scripts)


def wizard_shell(title, desc, page_id, engine_js, mount_id="wizard-app"):
    body = f"""
<section class="section wizard-section">
  <div class="container">
    <div class="wizard-head">
      <a href="{page_id.replace('-wizard','')}.html" class="wizard-back"><svg class="icon icon-sm"><use href="#i-arrow"/></svg> Voltar</a>
      <h1>{title}</h1>
      <p>{desc}</p>
    </div>
    <div id="{mount_id}"></div>
  </div>
</section>
"""
    return shell(
        title + " | Calculadoras de Enfermagem",
        desc,
        page_id,
        body,
        f'<script src="js/modules/{engine_js}"></script>',
    )


def build_landing(page_id, title, accent, subtitle, cta_href, cta_label, steps, features, faqs):
    body = hero_block(title, accent, subtitle, cta_href, cta_label, steps_list(steps))
    body += feature_grid(features)
    body += faq_section(faqs)
    body += f'<section class="section module-cta"><div class="container module-cta-inner"><h2>Comece agora</h2><a class="btn btn-green" href="{cta_href}">{cta_label}</a></div></section>'
    return shell(f"{title} — {accent}", subtitle, page_id, body)


def build_sae_landing():
    steps = [
        {"n": 1, "t": "Coleta de dados", "d": "Histórico, queixas, avaliação física e dados relevantes."},
        {"n": 2, "t": "Diagnóstico de Enfermagem", "d": "Identifique diagnósticos com base na taxonomia NANDA-I."},
        {"n": 3, "t": "Planejamento", "d": "Defina resultados (NOC) e intervenções (NIC)."},
        {"n": 4, "t": "Implementação", "d": "Execute as intervenções planejadas."},
        {"n": 5, "t": "Avaliação", "d": "Analise os resultados e ajuste o plano de cuidado."},
    ]
    features = [
        {"icon": "i-clipboard", "title": "Avaliação Completa", "desc": "Formulários estruturados para coleta de dados do paciente."},
        {"icon": "i-target", "title": "Diagnósticos NANDA-I", "desc": "Taxonomia de diagnósticos com fatores relacionados."},
        {"icon": "i-layers", "title": "NOC & NIC Integrados", "desc": "Resultados e intervenções vinculados aos diagnósticos."},
        {"icon": "i-chart", "title": "Acompanhamento", "desc": "Monitore a evolução e ajuste o plano de cuidado."},
    ]
    faqs = [
        {"q": "O que é a SAE?", "a": "A Sistematização da Assistência de Enfermagem é método científico para planejar, executar e avaliar o cuidado. Obrigatória pela Resolução COFEN 358/2009."},
        {"q": "Integração NANDA, NOC e NIC?", "a": "Selecione diagnósticos NANDA-I e vincule resultados NOC e intervenções NIC em um plano coerente."},
        {"q": "Funciona no celular?", "a": "Sim, layout responsivo para documentação na beira do leito."},
    ]
    return build_landing("sae", "SAE", "Sistematização da Assistência de Enfermagem", "Organize o processo de enfermagem de forma estruturada, segura e baseada em evidências.", "sae-wizard.html", "Iniciar SAE", steps, features, faqs)


def build_sbar_landing():
    steps = [
        {"n": "S", "t": "Situação", "d": "Descreva o que está acontecendo agora com o paciente."},
        {"n": "B", "t": "Background", "d": "Contexto clínico e histórico relevante."},
        {"n": "A", "t": "Avaliação", "d": "Sua análise clínica do quadro."},
        {"n": "R", "t": "Recomendação", "d": "Ações sugeridas ou orientações solicitadas."},
    ]
    features = [
        {"icon": "i-shieldcheck", "title": "Comunicação Padronizada", "desc": "Reduza erros na passagem de plantão e emergências."},
        {"icon": "i-clipboard", "title": "Documentação SBAR", "desc": "Registre comunicações de forma rastreável."},
        {"icon": "i-target", "title": "Segurança do Paciente", "desc": "Alinhado às metas internacionais de segurança."},
        {"icon": "i-chart", "title": "Rápido e Objetivo", "desc": "Ideal para ligações médicas e transferências."},
    ]
    faqs = [
        {"q": "O que é SBAR?", "a": "Método de comunicação estruturada: Situation, Background, Assessment, Recommendation."},
        {"q": "Quando usar?", "a": "Passagem de plantão, deterioração clínica, transferências e comunicação com médicos."},
    ]
    return build_landing("sbar", "SBAR", "Passagem de plantão segura", "Comunicação estruturada para equipes de saúde.", "sbar-wizard.html", "Iniciar SBAR", steps, features, faqs)


def export_data():
    OUT_DATA.mkdir(parents=True, exist_ok=True)
    specs = [
        ("nanda.json", "DiagnosticoNANDA.tsx", ["nandaDomains", "nandaDiagnoses"]),
        ("doencas-compulsorias.json", "DoencasCompulsorias.tsx", ["diseaseCategories", "compulsoriaDiseases"]),
        ("calendario-vacinal.json", "CalendarioVacinal.tsx", ["calendarGroups", "vaccineSchedule"]),
        ("protocolos.json", "ProtocolosPage.tsx", ["categories", "protocols"]),
        ("biblioteca.json", "LibraryPage.tsx", ["categories", "libraryItems"]),
    ]
    for fname, tsx, keys in specs:
        content = read_tsx(tsx)
        if not content:
            continue
        obj = {}
        for k in keys:
            arr = extract_ts_array(content, k)
            if arr:
                obj[k] = arr
        if obj:
            (OUT_DATA / fname).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
            print("data:", fname, list(obj.keys()))


def main():
    # export_data()  # dados já em js/modules/data/*.json
    pages = {
        "sae.html": build_sae_landing(),
        "sae-wizard.html": wizard_shell("Assistente SAE", "Wizard em 5 etapas: coleta, diagnóstico, planejamento, implementação e avaliação.", "sae-wizard", "sae-engine.js"),
        "sbar.html": build_sbar_landing(),
        "sbar-wizard.html": wizard_shell("Passagem de plantão SBAR", "Comunicação estruturada S-B-A-R para passagem segura.", "sbar-wizard", "sbar-engine.js"),
        "protocolos.html": catalog_shell("Protocolos de Enfermagem", "Protocolos clínicos por categoria.", "protocolos", "protocolos.json", "categories", "protocols", "Buscar protocolos…"),
        "biblioteca-provas.html": catalog_shell("Biblioteca de Recursos", "Livros, protocolos, diretrizes e templates.", "biblioteca", "biblioteca.json", "categories", "libraryItems", "Buscar na biblioteca…"),
        "diagnosticosnanda.html": catalog_shell("Diagnósticos NANDA-I", "Consulta de diagnósticos de enfermagem.", "diagnosticosnanda", "nanda.json", "nandaDomains", "nandaDiagnoses", "Buscar diagnóstico NANDA…"),
        "notificacao-compulsoria.html": catalog_shell("Doenças de Notificação Compulsória", "Consulta de doenças de notificação compulsória.", "notificacao-compulsoria", "doencas-compulsorias.json", "diseaseCategories", "compulsoriaDiseases", "Buscar doença…"),
        "calculadoravacina.html": catalog_shell("Calendário Vacinal PNI", "Calendário vacinal por faixa etária.", "calculadoravacina", "calendario-vacinal.json", "calendarGroups", "vaccineSchedule", "Buscar vacina…"),
        "gerador-curriculo.html": wizard_shell("Gerador de Currículo", "Monte seu currículo profissional para enfermagem.", "gerador-curriculo", "cv-engine.js"),
        "testes-autoconhecimento.html": build_landing("testes-autoconhecimento", "Testes", "Autoconhecimento profissional", "Avalie inteligência emocional, liderança, comunicação e gestão do tempo.", "#testes", "Ver testes",
            [{"n": 1, "t": "Escolha o teste", "d": "Selecione entre categorias de autoconhecimento."}, {"n": 2, "t": "Responda", "d": "Questionários rápidos e orientados."}, {"n": 3, "t": "Resultado", "d": "Receba feedback para desenvolvimento profissional."}],
            [{"icon": "i-target", "title": "Liderança", "desc": "Descubra seu estilo de liderar equipes."}, {"icon": "i-chart", "title": "Gestão do tempo", "desc": "Avalie prioridades e produtividade."}, {"icon": "i-layers", "title": "Comunicação", "desc": "Assertividade e comunicação interpessoal."}, {"icon": "i-shieldcheck", "title": "Inteligência emocional", "desc": "Reconhecimento e regulação emocional."}],
            [{"q": "Para quem são os testes?", "a": "Profissionais e estudantes de enfermagem em desenvolvimento de carreira."}]),
        "trilha-conhecimento.html": build_landing("trilha-conhecimento", "Trilha", "de Conhecimento", "Percursos formativos em fundamentos, UTI, urgência e gestão em enfermagem.", "#trilhas", "Explorar trilhas",
            [{"n": "01", "t": "Fundamentos", "d": "Processo de enfermagem e cuidados básicos."}, {"n": "02", "t": "UTI", "d": "Monitorização e paciente crítico."}, {"n": "03", "t": "Urgência", "d": "Triagem e suporte avançado de vida."}, {"n": "04", "t": "Gestão", "d": "Liderança e qualidade assistencial."}],
            [{"icon": "i-clipboard", "title": "Aulas progressivas", "desc": "Conteúdo sequencial por módulo."}, {"icon": "i-chart", "title": "Acompanhe progresso", "desc": "Indicadores de conclusão por trilha."}, {"icon": "i-layers", "title": "Multidisciplinar", "desc": "Integração clínica, gestão e segurança."}, {"icon": "i-target", "title": "Prática clínica", "desc": "Foco em competências do cotidiano."}],
            [{"q": "Como funciona?", "a": "Escolha uma trilha, avance nas lições e acompanhe seu progresso salvo localmente."}]),
    }
    out_dir = Path(os.environ.get("TEMP", ".")) / "calc-pages-out"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, html in pages.items():
        dest = out_dir / name
        dest.write_text(html, encoding="utf-8")
        # tentativa no projeto
        try:
            (ROOT / name).write_text(html, encoding="utf-8")
            print("page:", name)
        except OSError:
            print("page (temp):", dest)
    src_dir = ROOT / "js" / "modules" / "src"
    src_dir.mkdir(parents=True, exist_ok=True)
    for f in DOWNLOADS.glob("*.tsx"):
        if f.name.startswith(("SAE", "CV", "Gerador", "Diagnostico", "Calendario", "Doencas", "Protocolos", "Library", "Article", "Testes", "Hero", "Sections")):
            shutil.copy2(f, src_dir / f.name)
    for zname, inner in [
        ("sbar-module-v1.0.0.zip", None),
        ("trilha-conhecimento.zip", None),
    ]:
        zpath = DOWNLOADS / zname
        if zpath.exists():
            with zipfile.ZipFile(zpath) as zf:
                for n in zf.namelist():
                    if n.endswith((".tsx", ".ts", ".html")):
                        dest = src_dir / Path(n).name
                        dest.write_bytes(zf.read(n))
    print("done")


if __name__ == "__main__":
    main()
