#!/usr/bin/env python3
"""Alinha calculadoras ao preview_v2 + relatório PDF: perfis, recursos, impressão, gestor."""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil

HTML_DIR = os.path.join(os.path.dirname(__file__), "..", "NIFS", "DELIVERY", "html")
DELIVERY_DIR = os.path.join(os.path.dirname(__file__), "..", "NIFS", "DELIVERY")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "reference-website", "data", "tools")

COGNITIVE_STRIP = """
    <div id="cognitiveProfileStrip" class="cognitive-profile-strip" aria-live="polite">
      <span class="cog-kicker">Raciocínio clínico integrado (Nurse-PaLM)</span>
      <strong>NANDA:</strong> <span id="cogStripNanda">—</span> ·
      <strong>NIC:</strong> <span id="cogStripNic">—</span> ·
      <strong>NOC:</strong> <span id="cogStripNoc">—</span>
    </div>
"""

GESTOR_TAB = (
    '<button class="tab" data-tab="gestor" type="button" role="tab" aria-selected="false">'
    '<svg class="icon icon-sm"><use href="#i-trend"/></svg> Gestor</button>'
)

GESTOR_PANEL = """
      <div class="tab-panel" data-tab-panel="gestor">
        <div class="gestor-notice"><svg class="icon"><use href="#i-warning"/></svg> Painel demonstrativo — dados fictícios (mock). Conecte a um backend institucional para uso em produção.</div>
        <div class="kpi-grid">
          <div class="kpi-card"><div class="kpi-label">Cálculos (7 dias)</div><div class="kpi-value">—</div><div class="kpi-sub">Aguardando integração</div></div>
          <div class="kpi-card"><div class="kpi-label">Dentro da faixa</div><div class="kpi-value">—</div><div class="kpi-sub">Aguardando integração</div></div>
          <div class="kpi-card"><div class="kpi-label">Alarmes</div><div class="kpi-value">—</div><div class="kpi-sub">Aguardando integração</div></div>
          <div class="kpi-card"><div class="kpi-label">Unidades</div><div class="kpi-value">—</div><div class="kpi-sub">Aguardando integração</div></div>
        </div>
      </div>
"""

LEARNING_TRACK = """
        <div class="flow-divider"><span>Recursos Adicionais</span></div>
        <div class="learning-track-wrap">
          <div class="learning-track-grid">
            <a class="learn-card" href="biblioteca.html"><div class="icon-wrap"><svg class="icon"><use href="#i-book"/></svg></div><h3>Artigos</h3><p>Evidência científica e literatura de referência.</p><span class="learn-cta">Ler artigos <svg class="icon icon-sm"><use href="#i-arrow"/></svg></span></a>
            <a class="learn-card" href="protocolos.html"><div class="icon-wrap"><svg class="icon"><use href="#i-clipcheck"/></svg></div><h3>Protocolos</h3><p>Fluxos operacionais de enfermagem.</p><span class="learn-cta">Ver protocolos <svg class="icon icon-sm"><use href="#i-arrow"/></svg></span></a>
            <a class="learn-card" href="caso-clinico.html"><div class="icon-wrap"><svg class="icon"><use href="#i-file"/></svg></div><h3>Casos Clínicos</h3><p>Tomada de decisão em cenários reais.</p><span class="learn-cta">Ver casos <svg class="icon icon-sm"><use href="#i-arrow"/></svg></span></a>
            <a class="learn-card" href="checklist.html"><div class="icon-wrap"><svg class="icon"><use href="#i-clipcheck"/></svg></div><h3>Check-lists</h3><p>Prática segura e auditoria.</p><span class="learn-cta">Baixar <svg class="icon icon-sm"><use href="#i-download"/></svg></span></a>
            <a class="learn-card" href="simulados.html"><div class="icon-wrap"><svg class="icon"><use href="#i-pulse"/></svg></div><h3>Simulados</h3><p>Cenários práticos em tempo real.</p><span class="learn-cta">Simular <svg class="icon icon-sm"><use href="#i-arrow"/></svg></span></a>
            <a class="learn-card" href="flashcards.html"><div class="icon-wrap"><svg class="icon"><use href="#i-bulb"/></svg></div><h3>Flashcards</h3><p>Revisão rápida de conceitos.</p><span class="learn-cta">Estudar <svg class="icon icon-sm"><use href="#i-arrow"/></svg></span></a>
          </div>
        </div>
"""

PRINT_TEMPLATE = """
<div class="print-area no-print-screen" style="display:none;" id="printTemplate">
  <div class="print-header">
    <div class="print-header-left">
      <h1 id="printToolName">Calculadora</h1>
      <p class="subtitle" id="printToolCategory">Escala clínica</p>
      <span class="badge-validated">✓ Validada clinicamente</span>
    </div>
    <div class="print-header-right">
      <div class="report-date" id="printDate"></div>
      <div>calculadorasdeenfermagem.com.br</div>
    </div>
  </div>
  <div class="print-section">
    <div class="print-section-title"><span class="section-number">2</span> Dados do Paciente</div>
    <div class="print-patient-grid">
      <div><div class="label">Nome</div><div class="value" id="printPatientName">—</div></div>
      <div><div class="label">Registro</div><div class="value" id="printPatientReg">—</div></div>
      <div><div class="label">Idade</div><div class="value" id="printPatientAge">—</div></div>
      <div><div class="label">Leito / Setor</div><div class="value" id="printPatientBed">—</div></div>
    </div>
  </div>
  <div class="print-section">
    <div class="print-section-title"><span class="section-number">3</span> Parâmetros Inseridos</div>
    <ul class="print-params-list" id="printParamsList"></ul>
  </div>
  <div class="print-section">
    <div class="print-section-title"><span class="section-number">4</span> Classificação e Interpretação</div>
    <div class="print-classification">
      <div class="score" id="printScore">—</div>
      <div class="label" id="printClassification">—</div>
    </div>
    <div class="print-interpretation" id="printInterpretation"></div>
  </div>
  <div class="print-section">
    <div class="print-section-title"><span class="section-number">5</span> Raciocínio Clínico (NANDA · NIC · NOC)</div>
    <p><strong>NANDA:</strong> <span id="printNandaText">—</span></p>
    <p><strong>NIC:</strong> <span id="printNicText">—</span></p>
    <p><strong>NOC:</strong> <span id="printNocText">—</span></p>
  </div>
  <div class="print-section">
    <div class="print-section-title"><span class="section-number">6</span> Metas Internacionais de Segurança</div>
    <div class="print-safety-grid">
      <div class="print-safety-col" id="printSafetyMedsCol">
        <h4>9 Certos da Medicação</h4>
        <ul id="printSafetyMeds"></ul>
      </div>
      <div class="print-safety-col">
        <h4>Metas Internacionais (IPSG)</h4>
        <ul id="printSafetyIpsg"></ul>
      </div>
    </div>
  </div>
  <div class="print-section">
    <div class="print-section-title"><span class="section-number">7</span> Referência</div>
    <div class="print-reference" id="printReference">Documento gerado automaticamente.</div>
  </div>
  <div class="print-signature">
    <div class="print-signature-left">
      <div>Enf. Responsável: _________________</div>
      <div class="coren">COREN: _______</div>
    </div>
    <div class="print-signature-right">
      <div class="url">calculadorasdeenfermagem.com.br</div>
      <div class="disclaimer">Documento gerado automaticamente — não substitui avaliação profissional</div>
    </div>
  </div>
</div>
"""

# Atualiza bloco de segurança no fluxo clínico (IDs para lógica condicional)
SAFETY_OLD = re.compile(
    r'<div class="safety-grid">.*?</section>\s*</div>\s*\n\s*</div>',
    re.DOTALL,
)
SAFETY_NEW = """<div class="safety-grid">
              <div class="safety-col" id="calcSafetyMeds">
                <span class="nnn-label">9 Certos da Medicação</span>
                <ul class="tips-list" id="calcSafetyMedsList"></ul>
              </div>
              <div class="safety-col" id="calcSafetyIpsg">
                <span class="nnn-label">Metas Internacionais (IPSG)</span>
                <ul class="tips-list" id="calcSafetyIpsgList"></ul>
              </div>
            </div>
          </section>
        </div>
"""


def load_tool_config(path: str) -> dict | None:
    m = re.search(r'<script type="application/json" id="tool-config">(.*?)</script>', path, re.DOTALL)
    if not m:
        return None
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
        m2 = re.search(r'<script type="application/json" id="tool-config">(.*?)</script>', content, re.DOTALL)
        return json.loads(m2.group(1)) if m2 else None
    except (json.JSONDecodeError, OSError):
        return None


def related_tools_html(cfg: dict, slug: str) -> str:
    specialty = (cfg.get("overview") or {}).get("specialty") or []
    cat = (cfg.get("breadcrumb") or {}).get("category") or ""
    links = []
    if os.path.isdir(DATA_DIR):
        for jf in sorted(glob.glob(os.path.join(DATA_DIR, "*.json"))):
            base = os.path.splitext(os.path.basename(jf))[0]
            if base == slug:
                continue
            try:
                with open(jf, encoding="utf-8") as f:
                    other = json.load(f)
            except (json.JSONDecodeError, OSError):
                continue
            ov = other.get("overview") or {}
            other_cat = (other.get("breadcrumb") or {}).get("category") or ""
            other_spec = ov.get("specialty") or []
            if cat and other_cat == cat:
                links.append((base, ov.get("name", base), ov.get("icon", "i-calculator")))
            elif specialty and any(s in other_spec for s in specialty):
                links.append((base, ov.get("name", base), ov.get("icon", "i-calculator")))
            if len(links) >= 6:
                break
    if not links:
        links = [
            ("glasgow", "Escala de Glasgow", "i-brain"),
            ("morse", "Escala de Morse", "i-person"),
            ("braden", "Escala de Braden", "i-shield"),
            ("news2", "NEWS 2", "i-pulse"),
        ]
    cards = []
    for href, title, icon in links[:6]:
        cards.append(
            f'<a class="related-tool-card" href="{href}.html">'
            f'<div class="icon-wrap"><svg class="icon"><use href="#{icon}"/></svg></div>'
            f"<div><h3>{title}</h3><p>Ferramenta relacionada</p></div></a>"
        )
    return (
        '<section class="tool-footer-zone">\n'
        '  <h2 class="related-tools-title">Ferramentas relacionadas</h2>\n'
        '  <div class="related-tools-grid">\n    '
        + "\n    ".join(cards)
        + "\n  </div>\n</section>"
    )


def sync_assets() -> None:
    pairs = [
        ("css/site-styles.css", "html/css/site-styles.css"),
        ("css/print-template.css", "html/css/print-template.css"),
        ("js/calc-engine-v2.js", "html/js/calc-engine-v2.js"),
    ]
    for src_rel, dst_rel in pairs:
        src = os.path.join(DELIVERY_DIR, src_rel)
        dst = os.path.join(DELIVERY_DIR, dst_rel)
        if os.path.isfile(src) and os.path.realpath(src) != os.path.realpath(dst):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)


def process_file(path: str) -> list[str]:
    with open(path, encoding="utf-8") as f:
        content = f.read()
    if 'id="tool-config"' not in content:
        return []

    original = content
    changes: list[str] = []

    if 'id="cognitiveProfileStrip"' not in content and "profile-tabs-bar" in content:
        content = content.replace(
            '<div data-tab-panels="perfil">',
            COGNITIVE_STRIP + "\n    <div data-tab-panels=\"perfil\">",
            1,
        )
        changes.append("cognitive_strip")

    if 'data-tab="gestor"' not in content and 'data-tab="academico"' in content:
        content = content.replace(
            '<button class="tab" data-tab="academico"',
            GESTOR_TAB + '\n        <button class="tab" data-tab="academico"',
            1,
        )
        if 'data-tab-panel="gestor"' not in content:
            content = content.replace(
                "\n    </div>\n\n    <section class=\"about-section\">",
                GESTOR_PANEL + "\n    </div>\n\n    <section class=\"about-section\">",
                1,
            )
        changes.append("gestor")

    if "learning-track-wrap" not in content and "calcClinicalFlow" in content:
        content = content.replace(
            "        </div>\n\n      <!-- ================= PERFIL: ESTUDANTE",
            "        </div>\n" + LEARNING_TRACK + "\n      <!-- ================= PERFIL: ESTUDANTE",
            1,
        )
        if "learning-track-wrap" not in content:
            content = content.replace(
                "        </div>\n\n      <!-- ================= PERFIL: MODO URGÊNCIA",
                "        </div>\n" + LEARNING_TRACK + "\n      <!-- ================= PERFIL: MODO URGÊNCIA",
                1,
            )
        changes.append("learning_track")

    if SAFETY_OLD.search(content) and "calcSafetyMedsList" not in content:
        content = SAFETY_OLD.sub(SAFETY_NEW, content, count=1)
        changes.append("safety_ids")

    if 'id="urgCognitiveHint"' not in content and 'id="urgResultNum"' in content:
        content = content.replace(
            '<div class="urg-result">',
            '<p id="urgCognitiveHint" class="cognitive-profile-strip" style="display:none;margin-bottom:12px;"></p>\n            <div class="urg-result">',
            1,
        )
        changes.append("urg_hint")

    if 'id="estCognitiveHint"' not in content and 'data-tab-panel="estudante"' in content:
        content = content.replace(
            '<div class="tab-panel" data-tab-panel="estudante">\n        <div class="est-grid">',
            '<div class="tab-panel" data-tab-panel="estudante">\n        <p id="estCognitiveHint" class="cognitive-profile-strip" style="display:none;margin-bottom:12px;"></p>\n        <div class="est-grid">',
            1,
        )
        changes.append("est_hint")

    if 'id="printTemplate"' not in content:
        content = content.replace(
            '<div id="site-footer"></div>',
            PRINT_TEMPLATE + "\n<div id=\"site-footer\"></div>",
            1,
        )
        changes.append("print_template")

    if 'print-template.css' not in content and 'site-styles.css' in content:
        content = content.replace(
            '<link rel="stylesheet" href="css/site-styles.css">',
            '<link rel="stylesheet" href="css/site-styles.css">\n<link rel="stylesheet" href="css/print-template.css">',
            1,
        )
        changes.append("print_css")

    if "related-tools-grid" not in content:
        cfg = None
        try:
            m = re.search(r'<script type="application/json" id="tool-config">(.*?)</script>', content, re.DOTALL)
            if m:
                cfg = json.loads(m.group(1))
        except json.JSONDecodeError:
            cfg = None
        slug = os.path.splitext(os.path.basename(path))[0]
        rt = related_tools_html(cfg or {}, slug)
        if '<section class="tool-footer-zone">' in content:
            content = re.sub(
                r'<section class="tool-footer-zone">.*?</section>',
                rt,
                content,
                count=1,
                flags=re.DOTALL,
            )
        else:
            content = content.replace(
                "</main>",
                "\n    " + rt + "\n\n</main>",
                1,
            )
        changes.append("related_tools")

    if content != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    return changes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default=HTML_DIR)
    parser.add_argument("--no-sync", action="store_true")
    args = parser.parse_args()
    if not args.no_sync:
        sync_assets()
    total = 0
    for path in sorted(glob.glob(os.path.join(args.dir, "*.html"))):
        ch = process_file(path)
        if ch:
            total += 1
            print(f"{os.path.basename(path)}: {', '.join(ch)}")
    print(f"\nAlinhados {total} arquivos")


if __name__ == "__main__":
    main()
