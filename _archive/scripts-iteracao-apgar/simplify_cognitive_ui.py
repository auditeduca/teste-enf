#!/usr/bin/env python3
"""Alinha calculadoras ao preview_v2: lógica Nurse-PaLM silenciosa + fluxo clínico pós-cálculo."""
from __future__ import annotations

import argparse
import glob
import os
import re
import shutil

HTML_DIR = os.path.join(os.path.dirname(__file__), "..", "NIFS", "DELIVERY", "html")
DELIVERY_DIR = os.path.join(os.path.dirname(__file__), "..", "NIFS", "DELIVERY")

CIP_BLOCK_RE = re.compile(
    r"\s*<!-- ═══ Clinical Intelligence Package.*?<!-- ═══ Knowledge Graph Links.*?<section class=\"cip-kg-links\">.*?</section>\s*",
    re.DOTALL,
)

INLINE_REVEAL_RE = re.compile(
    r"\s*<script>\s*// Revelar Raciocinio Clinico.*?</script>\s*",
    re.DOTALL,
)

CLINICAL_FLOW_BLOCK = """
        <!-- Raciocínio Clínico Integrado — revelado após calcular (preview_v2) -->
        <div class="flow-divider" id="calcFlowDivider" style="display:none;">
          <span>Raciocínio Clínico Integrado</span>
        </div>

        <div id="calcClinicalFlow" class="clinical-flow-wrap">

          <section class="calc-card flow-card" aria-labelledby="calcNandaTitle">
            <div class="calc-card-header">
              <span class="bar" aria-hidden="true"></span>
              <h2 id="calcNandaTitle"><svg class="icon icon-sm"><use href="#i-brain"/></svg> Raciocínio NANDA · NIC · NOC</h2>
            </div>
            <div class="nnn-grid">
              <div>
                <span class="nnn-label">Diagnóstico (NANDA-I)</span>
                <p class="nnn-value" id="calcNandaText">—</p>
              </div>
              <div>
                <span class="nnn-label">Intervenção (NIC)</span>
                <p class="nnn-value" id="calcNicText">—</p>
              </div>
              <div>
                <span class="nnn-label">Resultado esperado (NOC)</span>
                <p class="nnn-value" id="calcNocText">—</p>
              </div>
            </div>
          </section>

          <section class="calc-card flow-card" aria-labelledby="calcPlanTitle">
            <div class="calc-card-header">
              <span class="bar" aria-hidden="true"></span>
              <h2 id="calcPlanTitle"><svg class="icon icon-sm"><use href="#i-clipcheck"/></svg> Plano de Ação</h2>
            </div>
            <ul class="tips-list">
              <li><svg class="icon"><use href="#i-clipcheck"/></svg> Confirmar dados do paciente e contexto clínico.</li>
              <li><svg class="icon"><use href="#i-clipcheck"/></svg> Aplicar o resultado conforme protocolo institucional.</li>
              <li><svg class="icon"><use href="#i-clipcheck"/></svg> Registrar escore, horário e conduta no prontuário.</li>
              <li><svg class="icon"><use href="#i-clipcheck"/></svg> Reavaliar conforme a gravidade e evolução clínica.</li>
            </ul>
          </section>

          <section class="calc-card flow-card" aria-labelledby="calcEvalTitle">
            <div class="calc-card-header">
              <span class="bar" aria-hidden="true"></span>
              <h2 id="calcEvalTitle"><svg class="icon icon-sm"><use href="#i-trend"/></svg> Avaliação &amp; Monitoramento (NOC)</h2>
            </div>
            <p class="flow-text">Monitorar sinais vitais, evolução do escore e resposta às intervenções. Reavaliar nos intervalos definidos pelo protocolo e comunicar alterações à equipe.</p>
          </section>

          <section class="calc-card flow-card" aria-labelledby="calcSafetyTitle">
            <div class="calc-card-header">
              <span class="bar" aria-hidden="true"></span>
              <h2 id="calcSafetyTitle"><svg class="icon icon-sm"><use href="#i-shield"/></svg> Segurança do Paciente</h2>
            </div>
            <div class="safety-grid">
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
                  <li><svg class="icon"><use href="#i-check"/></svg> Identificação correta do paciente</li>
                  <li><svg class="icon"><use href="#i-check"/></svg> Comunicação efetiva na transferência de cuidado</li>
                  <li><svg class="icon"><use href="#i-check"/></svg> Segurança em procedimentos de alta vigilância</li>
                </ul>
              </div>
            </div>
          </section>
        </div>
"""

INJECT_AFTER_FORM_RE = re.compile(
    r"(</form>\s*\n)(\s*</div>\s*\n\s*<!-- ================= PERFIL: ESTUDANTE)",
    re.MULTILINE,
)


def sync_assets() -> None:
    pairs = [
        ("js/calc-engine-v2.js", "html/js/calc-engine-v2.js"),
        ("js/cognitive-ui.js", "html/js/cognitive-ui.js"),
        ("js/partials-loader.js", "html/js/partials-loader.js"),
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

    if CIP_BLOCK_RE.search(content):
        content = CIP_BLOCK_RE.sub("\n", content)
        changes.append("remove_cip")

    if INLINE_REVEAL_RE.search(content):
        content = INLINE_REVEAL_RE.sub("\n", content)
        changes.append("remove_inline_reveal")

    if 'id="calcClinicalFlow"' not in content and INJECT_AFTER_FORM_RE.search(content):
        content = INJECT_AFTER_FORM_RE.sub(
            r"\1" + CLINICAL_FLOW_BLOCK + r"\n\2",
            content,
            count=1,
        )
        changes.append("inject_clinical_flow")

    if content != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    return changes


def main() -> None:
    parser = argparse.ArgumentParser(description="Simplificar UI cognitiva (modelo preview_v2)")
    parser.add_argument("--dir", default=HTML_DIR)
    parser.add_argument("--no-sync", action="store_true")
    args = parser.parse_args()

    if not args.no_sync:
        sync_assets()

    files = sorted(glob.glob(os.path.join(args.dir, "*.html")))
    stats = {"remove_cip": 0, "inject_clinical_flow": 0, "remove_inline_reveal": 0}
    for path in files:
        changes = process_file(path)
        if changes:
            print(f"{os.path.basename(path)}: {', '.join(changes)}")
            for c in changes:
                stats[c] = stats.get(c, 0) + 1

    print(
        f"\nProcessados {len(files)} arquivos — "
        f"remove_cip={stats['remove_cip']} "
        f"inject_clinical_flow={stats['inject_clinical_flow']} "
        f"remove_inline_reveal={stats['remove_inline_reveal']}"
    )


if __name__ == "__main__":
    main()
