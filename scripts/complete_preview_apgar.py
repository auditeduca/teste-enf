#!/usr/bin/env python3
"""Completa preview_apgar.html: cognitivo, CIP, cards e ferramentas relacionadas."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "preview_apgar.html",
    ROOT / "NIFS" / "DELIVERY" / "preview_apgar.html",
    ROOT / "NIFS" / "DELIVERY" / "apgar.html",
    ROOT / "NIFS" / "DELIVERY" / "html" / "apgar.html",
]

COGNITIVE_STRIP = """
    <div id="cognitiveProfileStrip" class="cognitive-profile-strip" aria-live="polite">
      <span class="cog-kicker">Raciocínio clínico integrado (Nurse-PaLM)</span>
      <strong>NANDA:</strong> <span id="cogStripNanda">—</span> ·
      <strong>NIC:</strong> <span id="cogStripNic">—</span> ·
      <strong>NOC:</strong> <span id="cogStripNoc">—</span>
    </div>
"""

RECURSOS_ADICIONAIS = """
        <div class="flow-divider"><span>Recursos Adicionais</span></div>

        <div class="learning-track-wrap">
          <div class="learning-track-grid">
            <a class="learn-card" href="#"><div class="icon-wrap"><svg class="icon"><use href="#i-book"/></svg></div><h3>Artigos</h3><p>Evidência científica e literatura de referência sobre o tema.</p><span class="learn-cta">Ler artigos <svg class="icon icon-sm"><use href="#i-arrow"/></svg></span></a>
            <a class="learn-card" href="protocolos.html"><div class="icon-wrap"><svg class="icon"><use href="#i-clipboard"/></svg></div><h3>Protocolos</h3><p>Protocolos institucionais e fluxos operacionais de enfermagem.</p><span class="learn-cta">Ver protocolos <svg class="icon icon-sm"><use href="#i-arrow"/></svg></span></a>
            <a class="learn-card" href="#"><div class="icon-wrap"><svg class="icon"><use href="#i-file"/></svg></div><h3>Casos Clínicos</h3><p>Situações reais com tomada de decisão e raciocínio clínico.</p><span class="learn-cta">Ver casos <svg class="icon icon-sm"><use href="#i-arrow"/></svg></span></a>
            <a class="learn-card" href="#"><div class="icon-wrap"><svg class="icon"><use href="#i-clipcheck"/></svg></div><h3>Check-lists</h3><p>Listas de verificação para prática segura e auditoria.</p><span class="learn-cta">Baixar check-lists <svg class="icon icon-sm"><use href="#i-download"/></svg></span></a>
            <a class="learn-card" href="#"><div class="icon-wrap"><svg class="icon"><use href="#i-pulse"/></svg></div><h3>Simulados</h3><p>Cenários práticos com decisões clínicas em tempo real.</p><span class="learn-cta">Simular agora <svg class="icon icon-sm"><use href="#i-arrow"/></svg></span></a>
            <a class="learn-card" href="#"><div class="icon-wrap"><svg class="icon"><use href="#i-bulb"/></svg></div><h3>Flashcards</h3><p>Fichas de revisão rápida para fixação de conceitos-chave.</p><span class="learn-cta">Estudar flashcards <svg class="icon icon-sm"><use href="#i-arrow"/></svg></span></a>
            <a class="learn-card" href="#"><div class="icon-wrap"><svg class="icon"><use href="#i-network"/></svg></div><h3>Infográficos</h3><p>Visualizações gráficas para ensino e treinamento em serviço.</p><span class="learn-cta">Ver infográficos <svg class="icon icon-sm"><use href="#i-arrow"/></svg></span></a>
            <a class="learn-card" href="#"><div class="icon-wrap"><svg class="icon"><use href="#i-flask"/></svg></div><h3>Guia de Bolso</h3><p>Resumo rápido para consulta à beira do leito.</p><span class="learn-cta">Consultar guia <svg class="icon icon-sm"><use href="#i-arrow"/></svg></span></a>
            <a class="learn-card" href="#"><div class="icon-wrap"><svg class="icon"><use href="#i-monitor"/></svg></div><h3>Slides</h3><p>Material de apresentação para aulas e treinamentos.</p><span class="learn-cta">Baixar slides <svg class="icon icon-sm"><use href="#i-download"/></svg></span></a>
            <a class="learn-card" href="#"><div class="icon-wrap"><svg class="icon"><use href="#i-play"/></svg></div><h3>Vídeos</h3><p>Tutoriais e demonstrações práticas em vídeo.</p><span class="learn-cta">Assistir vídeos <svg class="icon icon-sm"><use href="#i-arrow"/></svg></span></a>
          </div>
        </div>"""

FOOTER_BLOCKS = """
    <section class="tool-footer-zone">
      <h2 class="related-tools-title">Ferramentas relacionadas</h2>
      <div class="related-tools-grid">
        <a class="related-tool-card" href="ballard.html"><div class="icon-wrap"><svg class="icon"><use href="#i-baby"/></svg></div><div><h3>New Ballard Score</h3><p>Estimativa da idade gestacional</p></div></a>
        <a class="related-tool-card" href="capurro.html"><div class="icon-wrap"><svg class="icon"><use href="#i-users"/></svg></div><div><h3>Capurro</h3><p>Maturidade somática do recém-nascido</p></div></a>
        <a class="related-tool-card" href="bps.html"><div class="icon-wrap"><svg class="icon"><use href="#i-pulse"/></svg></div><div><h3>Perfil Biofísico</h3><p>Avaliação do bem-estar fetal</p></div></a>
        <a class="related-tool-card" href="silverman-andersen.html"><div class="icon-wrap"><svg class="icon"><use href="#i-pulse"/></svg></div><div><h3>Silverman-Andersen</h3><p>Desconforto respiratório neonatal</p></div></a>
        <a class="related-tool-card" href="downes.html"><div class="icon-wrap"><svg class="icon"><use href="#i-pulse"/></svg></div><div><h3>Downes</h3><p>Escore de desconforto respiratório infantil</p></div></a>
        <a class="related-tool-card" href="bishop.html"><div class="icon-wrap"><svg class="icon"><use href="#i-gauge"/></svg></div><div><h3>Bishop</h3><p>Avaliação do colo uterino</p></div></a>
        <a class="related-tool-card" href="medicamentos.html"><div class="icon-wrap"><svg class="icon"><use href="#i-pills"/></svg></div><div><h3>Calculadora de Medicamentos</h3><p>Regra de três e dose por volume</p></div></a>
      </div>
    </section>

    <section class="cip-section cip-hidden">
      <h2 class="cip-section-title">Clinical Intelligence Package</h2>
      <p class="cip-section-intro">6 dimensões de inteligência clínica integradas ao resultado da calculadora</p>
      <div id="cipContainer" class="cip-hidden"></div>
    </section>

    <section class="cog-section-wrapper cip-hidden">
      <div id="cognitivePanel" class="cognitive-panel cip-hidden">
        <div class="cognitive-panel-header">
          <h3><i class="fa-solid fa-brain"></i> Análise Cognitiva</h3>
          <span class="cognitive-badge">Motor Clínico</span>
        </div>
        <div id="cognitivePanelContent"></div>
      </div>
    </section>

    <section class="cip-kg-links cip-hidden">
      <h3><i class="fa-solid fa-link"></i> Recursos Conectados</h3>
      <div class="cip-kg-links-list">
        <a href="biblioteca.html" class="cip-kg-link"><i class="fa-solid fa-book"></i> Biblioteca de Recursos</a>
        <a href="nurse-palm.html" class="cip-kg-link"><i class="fa-solid fa-brain"></i> Dashboard Nurse-PaLM</a>
        <a href="diagnosticosnanda.html" class="cip-kg-link"><i class="fa-solid fa-clipboard-list"></i> NANDA-I</a>
        <a href="sae.html" class="cip-kg-link"><i class="fa-solid fa-file-medical"></i> SAE</a>
        <a href="sbar.html" class="cip-kg-link"><i class="fa-solid fa-comments"></i> SBAR</a>
        <a href="medicamentos.html" class="cip-kg-link"><i class="fa-solid fa-pills"></i> Medicamentos</a>
        <a href="protocolos.html" class="cip-kg-link"><i class="fa-solid fa-shield-halved"></i> Protocolos</a>
      </div>
    </section>"""

SAFETY_OLD = """            <div class="safety-grid">
              <div class="safety-col">
                <span class="nnn-label">9 Certos da Medicação</span>
                <ul class="tips-list">
                  <li><svg class="icon"><use href="#i-check"/></svg> Paciente certo</li>
                  <li><svg class="icon"><use href="#i-check"/></svg> Medicamento certo</li>
                  <li><svg class="icon"><use href="#i-check"/></svg> Via certa</li>
                  <li><svg class="icon"><use href="#i-check"/></svg> Dose certa</li>
                  <li><svg class="icon"><use href="#i-check"/></svg> Hora certa</li>
                </ul>
              </div>
              <div class="safety-col">
                <span class="nnn-label">Metas Internacionais (IPSG)</span>
                <ul class="tips-list">
                  <li><svg class="icon"><use href="#i-check"/></svg> Identificação correta do recém-nascido</li>
                  <li><svg class="icon"><use href="#i-check"/></svg> Segurança na reanimação neonatal</li>
                  <li><svg class="icon"><use href="#i-check"/></svg> Redução do risco de infecção</li>
                </ul>
              </div>
            </div>"""

SAFETY_NEW = """            <div class="safety-grid">
              <div class="safety-col" id="calcSafetyMeds">
                <span class="nnn-label">9 Certos da Medicação</span>
                <ul class="tips-list" id="calcSafetyMedsList"></ul>
              </div>
              <div class="safety-col" id="calcSafetyIpsg">
                <span class="nnn-label">Metas Internacionais (IPSG)</span>
                <ul class="tips-list" id="calcSafetyIpsgList"></ul>
              </div>
            </div>"""

I_BABY = '  <symbol id="i-baby" viewBox="0 0 24 24"><circle cx="12" cy="7" r="3.5"/><path d="M6 20c0-3.5 2.5-5.5 6-5.5s6 2 6 5.5"/><circle cx="9" cy="6.5" r="0.6" fill="currentColor" stroke="none"/><circle cx="15" cy="6.5" r="0.6" fill="currentColor" stroke="none"/></symbol>\n'


def patch(content: str) -> str:
    if 'id="cognitiveProfileStrip"' not in content:
        content = content.replace(
            '    <div data-tab-panels="perfil">',
            COGNITIVE_STRIP + "\n    <div data-tab-panels=\"perfil\">",
            1,
        )

    if SAFETY_OLD in content:
        content = content.replace(SAFETY_OLD, SAFETY_NEW, 1)

    if 'data-tab-panel="estudante">' in content and "estCognitiveHint" not in content:
        content = content.replace(
            '<div class="tab-panel" data-tab-panel="estudante">',
            '<div class="tab-panel" data-tab-panel="estudante">\n        <p id="estCognitiveHint" class="cognitive-profile-strip" style="display:none;margin-bottom:12px;"></p>',
            1,
        )

    if 'id="urgResultNum"' in content and "urgCognitiveHint" not in content:
        content = content.replace(
            '<div class="urg-result">',
            '<p id="urgCognitiveHint" class="cognitive-profile-strip" style="display:none;margin-bottom:12px;"></p>\n            <div class="urg-result">',
            1,
        )

    if 'data-tab-panel="sae"' in content and "cognitive-locked" not in content:
        content = content.replace(
            '<div class="tab-panel" data-tab-panel="sae">',
            '<div class="tab-panel cognitive-locked" data-tab-panel="sae">',
            1,
        )

    if "Recursos Adicionais" not in content:
        marker = "        </div>\n</div>\n\n<div class=\"tab-panel\" data-tab-panel=\"estudante\">"
        if marker in content:
            content = content.replace(
                marker,
                "        </div>" + RECURSOS_ADICIONAIS + "\n</div>\n\n<div class=\"tab-panel\" data-tab-panel=\"estudante\">",
                1,
            )

    if "tool-footer-zone" not in content:
        content = content.replace(
            "  </div>\n</main>",
            "  </div>\n" + FOOTER_BLOCKS + "\n</main>",
            1,
        )

    if 'id="i-baby"' not in content and "i-pills" in content:
        content = content.replace(
            '  <symbol id="i-pills"',
            I_BABY + '  <symbol id="i-pills"',
            1,
        )

    # Remover script inline duplicado (calc-engine-v2 cuida do fluxo)
    import re

    content = re.sub(
        r"<script>\s*\(function\(\)\s*\{\s*var form = document\.getElementById\(\"calcForm\"\).*?calcClinicalFlow\.scrollIntoView.*?\}\)\(\);\s*</script>\s*",
        "",
        content,
        flags=re.DOTALL,
    )

    return content


def main() -> None:
    for path in TARGETS:
        if not path.is_file():
            continue
        updated = patch(path.read_text(encoding="utf-8"))
        path.write_text(updated, encoding="utf-8")
        print("Atualizado:", path)


if __name__ == "__main__":
    main()
