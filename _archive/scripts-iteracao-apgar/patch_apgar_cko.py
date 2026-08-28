#!/usr/bin/env python3
"""Aplica CKO, reordena perfis e adiciona template de impressão ao Apgar."""
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

TABS_NEW = """        <div class="profile-tabs-bar">
      <div class="tabs-inner" data-tab-group="perfil" role="tablist" aria-label="Perfil de visualização">
        <button class="tab active" data-tab="padrao" type="button" role="tab" aria-selected="true"><svg class="icon icon-sm"><use href="#i-person"/></svg> Padrão</button>
        <button class="tab" data-tab="urgencia" type="button" role="tab" aria-selected="false"><svg class="icon icon-sm"><use href="#i-bolt"/></svg> Modo Urgência</button>
        <button class="tab" data-tab="gestor" type="button" role="tab" aria-selected="false"><svg class="icon icon-sm"><use href="#i-trend"/></svg> Gestor</button>
        <button class="tab" data-tab="estudante" type="button" role="tab" aria-selected="false"><svg class="icon icon-sm"><use href="#i-cap"/></svg> Estudante</button>
        <button class="tab" data-tab="academico" type="button" role="tab" aria-selected="false"><svg class="icon icon-sm"><use href="#i-book"/></svg> Acadêmico</button>
      </div>
    </div>"""

PRINT_TEMPLATE = """
<div class="print-area print-area--single-page no-print-screen" style="display:none;" id="printTemplate" aria-hidden="true">
  <div class="print-header">
    <div class="print-header-left">
      <h1 id="printToolName">Índice de Apgar</h1>
      <p class="subtitle" id="printToolCategory">Neonatologia</p>
      <span class="badge-validated">✓ Validada clinicamente</span>
    </div>
    <div class="print-header-right">
      <div class="report-date" id="printDate"></div>
      <div>calculadorasdeenfermagem.com.br</div>
    </div>
  </div>
  <div class="print-section">
    <div class="print-section-title"><span class="section-number">1</span> Dados do Paciente</div>
    <div class="print-patient-grid">
      <div><div class="label">Nome</div><div class="value" id="printPatientName">—</div></div>
      <div><div class="label">Registro</div><div class="value" id="printPatientReg">—</div></div>
      <div><div class="label">Idade</div><div class="value" id="printPatientAge">—</div></div>
      <div><div class="label">Leito / Setor</div><div class="value" id="printPatientBed">—</div></div>
    </div>
  </div>
  <div class="print-section">
    <div class="print-section-title"><span class="section-number">2</span> Parâmetros Inseridos</div>
    <ul class="print-params-list" id="printParamsList"></ul>
  </div>
  <div class="print-section">
    <div class="print-section-title"><span class="section-number">3</span> Classificação e Interpretação</div>
    <div class="print-classification">
      <div class="score" id="printScore">—</div>
      <div class="label" id="printClassification">—</div>
    </div>
    <div class="print-interpretation" id="printInterpretation"></div>
  </div>
  <div class="print-section">
    <div class="print-section-title"><span class="section-number">4</span> Raciocínio Clínico (NANDA · NIC · NOC)</div>
    <p style="font-size:11px;margin:4px 0"><strong>NANDA:</strong> <span id="printNandaText">—</span></p>
    <p style="font-size:11px;margin:4px 0"><strong>NIC:</strong> <span id="printNicText">—</span></p>
    <p style="font-size:11px;margin:4px 0"><strong>NOC:</strong> <span id="printNocText">—</span></p>
  </div>
  <div class="print-section">
    <div class="print-section-title"><span class="section-number">5</span> Segurança do Paciente</div>
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
    <div class="print-section-title"><span class="section-number">6</span> Referência</div>
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


def patch(content: str) -> str:
    content = content.replace(
        '<body data-page="apgar">',
        '<body data-page="apgar" data-tool-cko="apgar">',
        1,
    )

    if "print-template.css" not in content:
        content = content.replace(
            '<link rel="stylesheet" href="css/site-styles.css">',
            '<link rel="stylesheet" href="css/site-styles.css">\n<link rel="stylesheet" href="css/print-template.css">',
            1,
        )

    # Reordenar abas de perfil
    content = re.sub(
        r'<div class="profile-tabs-bar">.*?</div>\s*</div>',
        TABS_NEW,
        content,
        count=1,
        flags=re.DOTALL,
    )

    # Mount compartilhado — estudante
    if 'data-profile-shared="estudante"' not in content:
        content = content.replace(
            "        </div>\n      </div>\n\n<div class=\"tab-panel\" data-tab-panel=\"urgencia\">",
            "        </div>\n        <div data-profile-shared=\"estudante\"></div>\n      </div>\n\n<div class=\"tab-panel\" data-tab-panel=\"urgencia\">",
            1,
        )

    if 'data-profile-shared="urgencia"' not in content:
        content = content.replace(
            "        </div>\n      </div>\n\n<div class=\"tab-panel\" data-tab-panel=\"academico\">",
            "        </div>\n        <div data-profile-shared=\"urgencia\"></div>\n      </div>\n\n<div class=\"tab-panel\" data-tab-panel=\"academico\">",
            1,
        )

    if 'data-profile-shared="academico"' not in content:
        content = content.replace(
            "        </div>\n      </div>\n\n<div class=\"tab-panel\" data-tab-panel=\"gestor\">",
            "        </div>\n        <div data-profile-shared=\"academico\"></div>\n      </div>\n\n<div class=\"tab-panel\" data-tab-panel=\"gestor\">",
            1,
        )

    if 'data-profile-shared="gestor"' not in content:
        content = content.replace(
            "        </section>\n      </div>\n\n    </div>\n\n    <section class=\"about-section\">",
            "        </section>\n        <div data-profile-shared=\"gestor\"></div>\n      </div>\n\n    </div>\n\n    <section class=\"about-section\">",
            1,
        )

    if 'id="printTemplate"' not in content:
        content = content.replace(
            "<div id=\"site-footer\"></div>",
            PRINT_TEMPLATE + "\n<div id=\"site-footer\"></div>",
            1,
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
