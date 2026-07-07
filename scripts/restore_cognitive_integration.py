#!/usr/bin/env python3
"""Reinsere seções CIP / Nurse-PaLM / KG links nas páginas de calculadoras."""
from __future__ import annotations

import argparse
import glob
import os
import shutil

HTML_DIR = os.path.join(os.path.dirname(__file__), "..", "NIFS", "DELIVERY", "html")
DELIVERY_DIR = os.path.join(os.path.dirname(__file__), "..", "NIFS", "DELIVERY")

INTELLIGENCE_BLOCK = """
    <!-- ═══ Clinical Intelligence Package — 6 Dimensões Inline ═══ -->
    <section class="cip-section">
      <h2 class="cip-section-title">📦 Clinical Intelligence Package</h2>
      <p class="cip-section-intro">6 dimensões de inteligência clínica integradas ao resultado da calculadora</p>
      <div id="cipContainer" class="cip-hidden"></div>
    </section>

    <!-- ═══ Nurse-PaLM Cognitive Analysis ═══ -->
    <section class="cog-section-wrapper">
      <div id="cognitivePanel" class="cognitive-panel cip-hidden">
        <div class="cognitive-panel-header">
          <h3><i class="fa-solid fa-brain"></i> Análise Cognitiva</h3>
          <span class="cognitive-badge">Motor Clínico</span>
        </div>
        <div id="cognitivePanelContent"></div>
      </div>
    </section>
    <!-- ═══ Knowledge Graph Links ═══ -->
    <section class="cip-kg-links">
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


def sync_assets() -> None:
    """Copia JS/CSS atualizados para html/ (espelho de publicação)."""
    pairs = [
        ("js/calc-engine-v2.js", "html/js/calc-engine-v2.js"),
        ("js/cognitive-ui.js", "html/js/cognitive-ui.js"),
        ("js/partials-loader.js", "html/js/partials-loader.js"),
        ("css/site-styles.css", "html/css/site-styles.css"),
    ]
    for src_rel, dst_rel in pairs:
        src = os.path.join(DELIVERY_DIR, src_rel)
        dst = os.path.join(DELIVERY_DIR, dst_rel)
        if os.path.isfile(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if os.path.realpath(src) != os.path.realpath(dst):
                shutil.copy2(src, dst)


def inject_file(path: str) -> bool:
    with open(path, encoding="utf-8") as f:
        content = f.read()
    if 'id="tool-config"' not in content:
        return False
    if 'id="cipContainer"' in content:
        return False
    marker = "</main>"
    idx = content.rfind(marker)
    if idx == -1:
        return False
    content = content[:idx] + INTELLIGENCE_BLOCK + "\n" + content[idx:]
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Restaurar integração cognitiva nas calculadoras")
    parser.add_argument("--dir", default=HTML_DIR)
    parser.add_argument("--no-sync", action="store_true")
    args = parser.parse_args()

    if not args.no_sync:
        sync_assets()

    files = sorted(glob.glob(os.path.join(args.dir, "*.html")))
    updated = 0
    for path in files:
        if inject_file(path):
            updated += 1
            print(os.path.basename(path))
    print(f"\nInjetadas seções cognitivas em {updated} arquivos em {args.dir}")


if __name__ == "__main__":
    main()
