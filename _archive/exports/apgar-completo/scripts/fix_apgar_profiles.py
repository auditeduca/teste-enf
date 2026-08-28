#!/usr/bin/env python3
"""Corrige ferramentas relacionadas (perfil Padrão) e CSS dos perfis no Apgar."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "preview_apgar.html",
    ROOT / "NIFS" / "DELIVERY" / "preview_apgar.html",
    ROOT / "NIFS" / "DELIVERY" / "apgar.html",
    ROOT / "NIFS" / "DELIVERY" / "html" / "apgar.html",
]

CSS_TARGETS = [
    ROOT / "NIFS" / "DELIVERY" / "css" / "site-styles.css",
    ROOT / "NIFS" / "DELIVERY" / "html" / "css" / "site-styles.css",
]

PADRAO_FOOTER = """
        <section class="tool-footer-zone">
          <div class="tool-tags">
            <a href="index.html#calculadoras" class="tool-tag">#Neonatologia</a>
            <a href="index.html#calculadoras" class="tool-tag">#Apgar</a>
            <a href="index.html#calculadoras" class="tool-tag">#AvaliaçãoNeonatal</a>
            <a href="index.html#calculadoras" class="tool-tag">#ReanimaçãoNeonatal</a>
            <a href="index.html#calculadoras" class="tool-tag">#RecémNascido</a>
            <a href="diagnosticosnanda.html" class="tool-tag">#NANDA-I</a>
            <a href="sae.html" class="tool-tag">#SAE</a>
            <a href="protocolos.html" class="tool-tag">#Protocolos</a>
            <a href="medicamentos.html" class="tool-tag">#Medicação</a>
          </div>
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

GLOBAL_FOOTER_RE = re.compile(
    r"\n\s*<section class=\"tool-footer-zone\">.*?</section>\s*"
    r"<section class=\"cip-kg-links cip-hidden\">.*?</section>\s*(?=</main>)",
    re.DOTALL,
)

MARKER_BEFORE_ESTUDANTE = (
    '            <a class="learn-card" href="#"><div class="icon-wrap"><svg class="icon"><use href="#i-play"/></svg></div>'
    '<h3>Vídeos</h3><p>Tutoriais e demonstrações práticas em vídeo.</p>'
    '<span class="learn-cta">Assistir vídeos <svg class="icon icon-sm"><use href="#i-arrow"/></svg></span></a>\n'
    "          </div>\n"
    "        </div>\n"
    "</div>\n\n"
    '<div class="tab-panel" data-tab-panel="estudante">'
)


def patch_html(content: str) -> str:
    content = content.replace(
        'id="calcMedicationLinks" class="related-tools-grid"',
        'id="calcMedicationLinks" class="med-links-grid"',
    )
    content = content.replace(' style="background:rgba(255,255,255,.07);border-"', "")
    content = content.replace(
        'class="field-select-wrap" style="flex:1;min-width:220px"',
        'class="field-select-wrap field-select-wrap--step"',
    )
    content = content.replace(
        'class="cognitive-profile-strip" style="display:none;margin-bottom:12px;"',
        'class="cognitive-profile-strip cognitive-profile-strip--hint"',
    )

    content = GLOBAL_FOOTER_RE.sub("\n", content)

    if "tool-tags" not in content and MARKER_BEFORE_ESTUDANTE in content:
        content = content.replace(
            MARKER_BEFORE_ESTUDANTE,
            MARKER_BEFORE_ESTUDANTE.replace(
                "</div>\n\n<div class=\"tab-panel\" data-tab-panel=\"estudante\">",
                PADRAO_FOOTER + "\n</div>\n\n<div class=\"tab-panel\" data-tab-panel=\"estudante\">",
                1,
            ),
            1,
        )

    return content


CSS_SNIPPET = """
/* Hashtags da ferramenta */
.tool-tags{display:flex; flex-wrap:wrap; gap:8px; margin-bottom:28px;}
.tool-tag{padding:5px 14px; border-radius:99px; font-size:12px; font-weight:600; color:var(--blue-600); background:var(--blue-100); text-decoration:none; transition:all .15s;}
.tool-tag:hover{background:var(--blue-200); transform:translateY(-1px);}

/* Estudante — selects nos passos */
.step-content .field-select-wrap,
.field-select-wrap--step{flex:1; min-width:220px;}

/* Hint cognitivo em perfis secundários */
.cognitive-profile-strip--hint{display:none; margin-bottom:12px;}
.cognitive-profile-strip--hint.is-visible{display:block;}

/* Medicamentos no fluxo clínico */
.med-links-grid{
  display:grid;
  grid-template-columns:repeat(auto-fill, minmax(240px, 1fr));
  gap:12px;
  margin-top:4px;
}
"""


def patch_css(content: str) -> str:
    if ".tool-tags{" in content:
        return content
    anchor = ".med-link-card{align-items:stretch;}"
    if anchor not in content:
        return content + CSS_SNIPPET
    return content.replace(anchor, anchor + CSS_SNIPPET, 1)


def main() -> None:
    for path in TARGETS:
        if not path.is_file():
            continue
        updated = patch_html(path.read_text(encoding="utf-8"))
        path.write_text(updated, encoding="utf-8")
        print("HTML:", path)

    for path in CSS_TARGETS:
        if not path.is_file():
            continue
        updated = patch_css(path.read_text(encoding="utf-8"))
        path.write_text(updated, encoding="utf-8")
        print("CSS:", path)


if __name__ == "__main__":
    main()
