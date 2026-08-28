#!/usr/bin/env python3
"""Unifica motor clínico: um fluxo compartilhado, sem CIP duplicado, visual integrado."""
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

ACA_BODY = """            <div class="tab-panel active" data-tab-panel="calculo">
              <h4>Dados informados</h4>
              <p>Frequência Cardíaca: <strong data-aca-value="fc">2</strong> · Esforço Respiratório: <strong data-aca-value="respiracao">2</strong> · Tônus Muscular: <strong data-aca-value="tono">2</strong> · Irritabilidade Reflexa: <strong data-aca-value="irritabilidade">2</strong> · Cor da Pele: <strong data-aca-value="cor">2</strong></p>
              <h4>Resultado</h4>
              <p>Índice de Apgar: <strong data-aca-value="__result__">10 pontos</strong> — <span data-aca-value="__range__">Normal / Boa Vitalidade</span></p>
              <button type="button" class="btn btn-outline-navy aca-print-btn" onclick="window.print()"><svg class="icon icon-sm"><use href="#i-printer"/></svg> Exportar / Imprimir</button>
            </div>
            <div class="tab-panel" data-tab-panel="fundamentacao"><h4>Fundamentação</h4><p>O Índice de Apgar foi desenvolvido pela anestesiologista Virginia Apgar em 1952 como um método rápido e padronizado para avaliar a condição clínica do recém-nascido logo após o parto, permitindo identificar precocemente a necessidade de reanimação.</p><h4>Histórico</h4><p>Adotado mundialmente como padrão de avaliação neonatal imediata, sendo recomendado pela Academia Americana de Pediatria (AAP) e pelo Colégio Americano de Obstetras e Ginecologistas (ACOG) como parte da rotina de nascimento.</p></div>
            <div class="tab-panel cognitive-locked" data-tab-panel="sae"><h4>NANDA — Padrão respiratório ineficaz</h4><p>Inspiração e/ou expiração que não proporciona ventilação adequada.</p><h4>NANDA — Risco de nível de glicemia instável</h4><p>Vulnerabilidade a variação nos níveis de glicose/açúcar no sangue, o que pode comprometer a saúde do recém-nascido.</p><h4>NOC — Status respiratório do recém-nascido</h4><ul class="tips-list"><li>Frequência respiratória adequada</li><li>Ausência de cianose</li><li>Choro vigoroso</li></ul><h4>NOC — Adaptação do recém-nascido à vida extrauterina</h4><ul class="tips-list"><li>Estabilidade térmica</li><li>Estabilidade cardiorrespiratória</li><li>Reflexos presentes</li></ul><h4>NIC — Cuidados ao recém-nascido: imediatos</h4><ul class="tips-list"><li>Secar e aquecer o recém-nascido</li><li>Avaliar Apgar no 1º e 5º minuto</li><li>Aspirar vias aéreas se necessário</li><li>Realizar contato pele a pele</li></ul></div>
            <div class="tab-panel" data-tab-panel="evidencias"><h4>Validação científica</h4><p>Amplamente validado na literatura como indicador de vitalidade neonatal, embora não deva ser usado isoladamente para prever prognóstico neurológico a longo prazo.</p><h4>Limitações</h4><p>O escore de Apgar isolado não deve ser utilizado para diagnosticar asfixia perinatal nem para prever desfechos neurológicos a longo prazo — deve ser interpretado em conjunto com gasometria de cordão e exame clínico completo.</p></div>
            <div class="tab-panel" data-tab-panel="referencias"><ol class="ref-list"><li><span class="ref-num">1</span>APGAR, V. A proposal for a new method of evaluation of the newborn infant. Current Researches in Anesthesia and Analgesia, v. 32, n. 4, p. 260-267, 1953.</li><li><span class="ref-num">2</span>AMERICAN ACADEMY OF PEDIATRICS; AMERICAN COLLEGE OF OBSTETRICIANS AND GYNECOLOGISTS. The Apgar Score. Committee Opinion, 2015 (reafirmado).</li><li><span class="ref-num">3</span>BRASIL. Ministério da Saúde. Atenção à Saúde do Recém-Nascido: Guia para os Profissionais de Saúde. Brasília: MS, 2014.</li><li><span class="ref-num">4</span>BRUNNER, L. S.; SUDDARTH, D. S. Tratado de enfermagem médico-cirúrgica. 14ª ed. Rio de Janeiro: Guanabara Koogan, 2020.</li><li><span class="ref-num">5</span>COFEN. Resolução COFEN nº 564/2017 — Código de Ética dos Profissionais de Enfermagem. Brasília: COFEN, 2017.</li></ol></div>
          </div>
        </div>
        <div data-profile-shared="academico"></div>
      </div>"""

SHARED_CLINICAL_FLOW = """
    <div class="flow-divider" id="calcFlowDivider" style="display:none;">
      <span>Raciocínio Clínico Integrado</span>
    </div>

    <div id="calcClinicalFlow" class="clinical-flow-wrap" data-profile-clinical-flow>
      <section class="calc-card flow-card" aria-labelledby="calcNandaTitle">
        <div class="calc-card-header">
          <span class="bar" aria-hidden="true"></span>
          <h2 id="calcNandaTitle"><svg class="icon icon-sm"><use href="#i-brain"/></svg> Raciocínio NANDA · NIC · NOC</h2>
        </div>
        <div class="nnn-grid">
          <div><span class="nnn-label">Diagnóstico (NANDA-I)</span><p class="nnn-value" id="calcNandaText">—</p></div>
          <div><span class="nnn-label">Intervenção (NIC)</span><p class="nnn-value" id="calcNicText">—</p></div>
          <div><span class="nnn-label">Resultado esperado (NOC)</span><p class="nnn-value" id="calcNocText">—</p></div>
        </div>
      </section>

      <section class="calc-card flow-card flow-card--cognitive cip-hidden" data-cog-section aria-labelledby="calcCogTitle">
        <div class="calc-card-header">
          <span class="bar" aria-hidden="true"></span>
          <h2 id="calcCogTitle"><svg class="icon icon-sm"><use href="#i-brain"/></svg> Análise Cognitiva — Nurse-PaLM</h2>
          <span class="cognitive-badge">Motor Clínico</span>
        </div>
        <div id="cognitivePanel" class="cognitive-panel cognitive-panel--embedded cip-hidden" data-cognitive-mount>
          <div id="cognitivePanelContent" data-cognitive-panel-content></div>
        </div>
      </section>

      <section class="calc-card flow-card" aria-labelledby="calcPlanTitle">
        <div class="calc-card-header">
          <span class="bar" aria-hidden="true"></span>
          <h2 id="calcPlanTitle"><svg class="icon icon-sm"><use href="#i-clipcheck"/></svg> Plano de Ação</h2>
        </div>
        <ul class="tips-list">
          <li><svg class="icon"><use href="#i-clipcheck"/></svg> Avaliar FC, respiração, tônus, irritabilidade e cor.</li>
          <li><svg class="icon"><use href="#i-clipcheck"/></svg> Registrar escore do 1º e 5º minuto separadamente.</li>
          <li><svg class="icon"><use href="#i-clipcheck"/></svg> Iniciar reanimação se Apgar &lt; 7 — não aguardar o cálculo.</li>
          <li><svg class="icon"><use href="#i-clipcheck"/></svg> Repetir a cada 5 minutos se escore permanecer &lt; 7.</li>
        </ul>
      </section>

      <section class="calc-card flow-card" aria-labelledby="calcEvalTitle">
        <div class="calc-card-header">
          <span class="bar" aria-hidden="true"></span>
          <h2 id="calcEvalTitle"><svg class="icon icon-sm"><use href="#i-trend"/></svg> Avaliação &amp; Monitoramento (NOC)</h2>
        </div>
        <p class="flow-text">Monitorar vitalidade do recém-nascido: frequência cardíaca, esforço respiratório, tônus muscular, irritabilidade reflexa e coloração da pele. Reavaliar conforme protocolo institucional.</p>
      </section>

      <section class="calc-card flow-card" aria-labelledby="calcSafetyTitle">
        <div class="calc-card-header">
          <span class="bar" aria-hidden="true"></span>
          <h2 id="calcSafetyTitle"><svg class="icon icon-sm"><use href="#i-shield"/></svg> Segurança do Paciente</h2>
        </div>
        <div class="safety-grid">
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

      <section class="calc-card flow-card" id="calcMedicationSection" aria-labelledby="calcMedTitle" hidden>
        <div class="calc-card-header">
          <span class="bar" aria-hidden="true"></span>
          <h2 id="calcMedTitle"><svg class="icon icon-sm"><use href="#i-pills"/></svg> Medicamentos — Base de Dados</h2>
        </div>
        <p class="med-link-band" id="calcMedBandLabel"></p>
        <p class="flow-text" id="calcMedSummary"></p>
        <div id="calcMedicationLinks" class="med-links-grid"></div>
        <p class="med-link-disclaimer">Referência da base NKOS. Prescrição e administração dependem de avaliação médica e protocolo institucional.</p>
      </section>

      <section class="calc-card flow-card flow-card--cip cip-hidden" data-cip-section aria-labelledby="calcCipTitle">
        <div class="calc-card-header">
          <span class="bar" aria-hidden="true"></span>
          <h2 id="calcCipTitle"><svg class="icon icon-sm"><use href="#i-book"/></svg> Evidência &amp; Pérolas Clínicas</h2>
        </div>
        <div id="cipContainer" class="cip-flow-inner cip-hidden" data-cip-mount></div>
      </section>

      <section class="calc-card flow-card flow-card--kg cip-hidden" data-kg-section aria-labelledby="calcKgTitle">
        <div class="calc-card-header">
          <span class="bar" aria-hidden="true"></span>
          <h2 id="calcKgTitle"><svg class="icon icon-sm"><use href="#i-link"/></svg> Recursos Conectados</h2>
        </div>
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
    </div>
"""

FLOW_BLOCK_RE = re.compile(
    r"<!-- Raciocinio Clinico Integrado.*?<div id=\"calcClinicalFlow\".*?</div>\s*"
    r"(?=<div class=\"flow-divider\"><span>Trilha de Aprendizagem</span></div>)",
    re.DOTALL,
)


def restore_academico(content: str) -> str:
    broken = '<div class="aca-body" data-tab-panels="academico-conteudo">\n\n    </div>'
    if broken in content:
        content = content.replace(broken, '<div class="aca-body" data-tab-panels="academico-conteudo">\n' + ACA_BODY)
    return content


def patch(content: str) -> str:
    content = restore_academico(content)
    content = FLOW_BLOCK_RE.sub("", content)
    anchor = "\n    </div>\n\n    <section class=\"about-section\">"
    if SHARED_CLINICAL_FLOW.strip() not in content:
        content = content.replace(
            anchor,
            "\n    </div>\n" + SHARED_CLINICAL_FLOW + anchor,
            1,
        )
    return content


def main() -> None:
    for path in TARGETS:
        if not path.is_file():
            continue
        path.write_text(patch(path.read_text(encoding="utf-8")), encoding="utf-8")
        print("Unificado:", path)


if __name__ == "__main__":
    main()
