#!/usr/bin/env python3
"""Integra CIP e motor cognitivo dentro do fluxo clínico no perfil Padrão."""
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

CIP_BLOCK = """
          <section class="cip-section cip-hidden" data-cip-section>
            <h2 class="cip-section-title">Clinical Intelligence Package</h2>
            <p class="cip-section-intro">6 dimensões de inteligência clínica integradas ao resultado da calculadora</p>
            <div id="cipContainer" class="cip-hidden" data-cip-mount></div>
          </section>

          <section class="cog-section-wrapper cip-hidden" data-cog-section>
            <div id="cognitivePanel" class="cognitive-panel cip-hidden" data-cognitive-mount>
              <div class="cognitive-panel-header">
                <h3><i class="fa-solid fa-brain"></i> Análise Cognitiva</h3>
                <span class="cognitive-badge">Motor Clínico</span>
              </div>
              <div id="cognitivePanelContent" data-cognitive-panel-content></div>
            </div>
          </section>

          <section class="cip-kg-links cip-hidden" data-kg-section>
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
          </section>
"""

OLD_TAIL = re.compile(
    r"\s*<section class=\"cip-section cip-hidden\">.*?</section>\s*"
    r"<section class=\"cog-section-wrapper cip-hidden\">.*?</section>\s*"
    r"<section class=\"cip-kg-links cip-hidden\">.*?</section>\s*</div>\s*\n<div class=\"tab-panel\"",
    re.DOTALL,
)


def patch(content: str) -> str:
    content = content.replace(
        '<div id="calcClinicalFlow" class="clinical-flow-wrap">',
        '<div id="calcClinicalFlow" class="clinical-flow-wrap" data-profile-clinical-flow>',
        1,
    )

    marker = '<p class="med-link-disclaimer">Referência da base NKOS. Prescrição e administração dependem de avaliação médica e protocolo institucional.</p>\n          </section>\n        </div>'
    if "data-cip-mount" not in content.split(marker)[0].split("calcClinicalFlow")[-1]:
        content = content.replace(
            marker,
            '<p class="med-link-disclaimer">Referência da base NKOS. Prescrição e administração dependem de avaliação médica e protocolo institucional.</p>\n          </section>' + CIP_BLOCK + "\n        </div>",
            1,
        )

    content = OLD_TAIL.sub("\n</div>\n\n<div class=\"tab-panel\"", content, count=1)
    return content


def main() -> None:
    for path in TARGETS:
        if not path.is_file():
            continue
        updated = patch(path.read_text(encoding="utf-8"))
        path.write_text(updated, encoding="utf-8")
        print("Integrado motor clínico:", path)


if __name__ == "__main__":
    main()
