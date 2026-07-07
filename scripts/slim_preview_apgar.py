#!/usr/bin/env python3
"""Modulariza preview_apgar.html: CSS externo + header/footer/a11y + perfis completos."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "preview_apgar.html"
DELIVERY = ROOT / "NIFS" / "DELIVERY"

HEAD_ASSETS = """<style id="calc-critical-css">[data-tab-panels]>[data-tab-panel]:not(.active){display:none!important}</style>
<link rel="stylesheet" href="css/site-styles.css">
"""

FONT_AWESOME_MARKER = (
    'referrerpolicy="no-referrer" />\n'
)

PROFILE_TABS = """    <div class="profile-tabs-bar">
      <div class="tabs-inner" data-tab-group="perfil" role="tablist" aria-label="Perfil de visualização">
        <button class="tab active" data-tab="padrao" type="button" role="tab" aria-selected="true"><svg class="icon icon-sm"><use href="#i-person"/></svg> Padrão</button>
        <button class="tab" data-tab="estudante" type="button" role="tab" aria-selected="false"><svg class="icon icon-sm"><use href="#i-cap"/></svg> Estudante</button>
        <button class="tab" data-tab="urgencia" type="button" role="tab" aria-selected="false"><svg class="icon icon-sm"><use href="#i-bolt"/></svg> Modo Urgência</button>
        <button class="tab" data-tab="academico" type="button" role="tab" aria-selected="false"><svg class="icon icon-sm"><use href="#i-book"/></svg> Acadêmico</button>
        <button class="tab" data-tab="gestor" type="button" role="tab" aria-selected="false"><svg class="icon icon-sm"><use href="#i-trend"/></svg> Gestor</button>
      </div>
    </div>"""

LEARNING_TRACK_5 = """
        <div class="flow-divider"><span>Trilha de Aprendizagem</span></div>

        <div class="learning-track-wrap">
          <div class="learning-track-grid">
            <a class="learn-card" href="biblioteca-provas.html">
              <div class="icon-wrap"><svg class="icon"><use href="#i-clipboard"/></svg></div>
              <h3>Quiz</h3>
              <p>Teste seu conhecimento sobre o Índice de Apgar e vitalidade neonatal.</p>
              <span class="learn-cta">Responder agora <svg class="icon icon-sm"><use href="#i-arrow"/></svg></span>
            </a>
            <a class="learn-card" href="#">
              <div class="icon-wrap"><svg class="icon"><use href="#i-pulse"/></svg></div>
              <h3>Simulado</h3>
              <p>Cenário prático de avaliação neonatal com decisões em tempo real.</p>
              <span class="learn-cta">Simular caso <svg class="icon icon-sm"><use href="#i-arrow"/></svg></span>
            </a>
            <a class="learn-card" href="#">
              <div class="icon-wrap"><svg class="icon"><use href="#i-file"/></svg></div>
              <h3>Casos Clínicos</h3>
              <p>Situações reais de sala de parto e tomada de decisão clínica.</p>
              <span class="learn-cta">Ver casos <svg class="icon icon-sm"><use href="#i-arrow"/></svg></span>
            </a>
            <a class="learn-card" href="#">
              <div class="icon-wrap"><svg class="icon"><use href="#i-book"/></svg></div>
              <h3>Artigos &amp; Evidência</h3>
              <p>Literatura de referência e evidências sobre avaliação do recém-nascido.</p>
              <span class="learn-cta">Ler evidências <svg class="icon icon-sm"><use href="#i-arrow"/></svg></span>
            </a>
            <a class="learn-card" href="#">
              <div class="icon-wrap"><svg class="icon"><use href="#i-monitor"/></svg></div>
              <h3>Slides</h3>
              <p>Material de estudo para aula ou treinamento em serviço.</p>
              <span class="learn-cta">Baixar slides <svg class="icon icon-sm"><use href="#i-download"/></svg></span>
            </a>
          </div>
        </div>"""

CLINICAL_FLOW_SCRIPT = """
<script>
  (function() {
    var form = document.getElementById("calcForm");
    if (!form) return;
    var flowDivider = document.getElementById("calcFlowDivider");
    var clinicalFlow = document.getElementById("calcClinicalFlow");
    var nandaText = document.getElementById("calcNandaText");
    var nicText = document.getElementById("calcNicText");
    var nocText = document.getElementById("calcNocText");
    form.addEventListener("submit", function() {
      if (!clinicalFlow) return;
      var resultEl = document.getElementById("calcResultValue");
      var score = resultEl ? parseInt(resultEl.textContent, 10) : 10;
      if (nandaText) nandaText.textContent = score >= 7
        ? "Padrão respiratório ineficaz (00032) — risco baixo. Manter observação."
        : "Padrão respiratório ineficaz (00032) — risco de comprometimento da ventilação.";
      if (nicText) nicText.textContent = "Cuidados ao recém-nascido: imediatos (NIC 3250) e reanimação neonatal (NIC 3254).";
      if (nocText) nocText.textContent = "Status respiratório do recém-nascido (NOC 0413) e adaptação à vida extrauterina (NOC 0415).";
      if (flowDivider) flowDivider.style.display = "block";
      clinicalFlow.classList.add("is-visible");
      window.requestAnimationFrame(function() {
        clinicalFlow.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });
  })();
</script>"""


def remove_head_style_blocks(content: str) -> str:
    start = content.find(FONT_AWESOME_MARKER)
    if start == -1:
        raise ValueError("Marcador font-awesome não encontrado")
    start += len(FONT_AWESOME_MARKER)
    head_end = content.find("</head>", start)
    if head_end == -1:
        raise ValueError("</head> não encontrado")
    head_tail = content[start:head_end]
    head_tail = re.sub(r"<style[^>]*>.*?</style>\s*", "", head_tail, flags=re.DOTALL)
    return content[:start] + HEAD_ASSETS + "\n" + head_tail + content[head_end:]


def add_modular_shell(content: str) -> str:
    if 'id="site-header"' not in content:
        content = content.replace(
            '<main id="main-content">',
            '<!-- Módulos carregados via js/partials-loader.js -->\n'
            '<div id="site-header"></div>\n'
            '<div id="site-a11y"></div>\n\n'
            '<main id="main-content">',
        )
    if 'id="site-footer"' not in content:
        content = re.sub(
            r"</main>\s*",
            '</main>\n\n<div id="site-footer"></div>\n<div id="site-cookie"></div>\n\n',
            content,
            count=1,
        )
    if '<script src="js/partials-loader.js">' not in content:
        # Remover script inline duplicado de fluxo clínico (será reinserido limpo)
        content = re.sub(
            r'<script>\s*// Revelar Raciocinio Clinico.*?</script>\s*',
            "",
            content,
            flags=re.DOTALL,
        )
        content = content.replace(
            "</body>",
            f'{CLINICAL_FLOW_SCRIPT}\n<script src="js/partials-loader.js"></script>\n</body>',
        )
    return content


def remove_cip_blocks(content: str) -> str:
    content = re.sub(
        r"\s*<!-- ═══ Clinical Intelligence Package.*?<!-- ═══ Knowledge Graph Links ═══ -->.*?</section>\s*",
        "\n",
        content,
        flags=re.DOTALL,
    )
    content = re.sub(
        r'\s*<div id="cognitiveProfileStrip"[^>]*>.*?</div>\s*',
        "\n",
        content,
        flags=re.DOTALL,
    )
    content = re.sub(
        r'\s*<section class="tool-footer-zone">.*?</section>\s*',
        "\n",
        content,
        flags=re.DOTALL,
    )
    content = re.sub(
        r'\s*<div class="print-area[^"]*"[^>]*>.*?</div>\s*(?=<div id="site-footer">|</body>)',
        "\n",
        content,
        flags=re.DOTALL,
    )
    content = re.sub(r'<link rel="stylesheet" href="css/print-template\.css">\s*', "", content)
    content = re.sub(
        r"<style>\s*\.flow-divider\{.*?</style>\s*",
        "",
        content,
        flags=re.DOTALL,
    )
    return content


def fix_profile_tabs(content: str) -> str:
    return re.sub(
        r'<div class="profile-tabs-bar">.*?</div>\s*</div>',
        PROFILE_TABS,
        content,
        count=1,
        flags=re.DOTALL,
    )


def extract_panel(content: str, panel_id: str) -> str | None:
    """Extrai um painel de perfil completo (com divs aninhados)."""
    marker = f'data-tab-panel="{panel_id}"'
    idx = content.find(marker)
    if idx == -1:
        return None
    start = content.rfind("<div", 0, idx)
    if start == -1:
        return None

    # Avança contando divs abertos/fechados
    pos = start
    depth = 0
    while pos < len(content):
        open_div = content.find("<div", pos)
        close_div = content.find("</div>", pos)
        if close_div == -1:
            break
        if open_div != -1 and open_div < close_div:
            depth += 1
            pos = open_div + 4
        else:
            depth -= 1
            pos = close_div + len("</div>")
            if depth == 0:
                return content[start:pos]
    return None


def extract_div_by_id(content: str, element_id: str) -> str | None:
    marker = f'id="{element_id}"'
    idx = content.find(marker)
    if idx == -1:
        return None
    start = content.rfind("<div", 0, idx)
    if start == -1:
        return None
    pos = start
    depth = 0
    while pos < len(content):
        open_div = content.find("<div", pos)
        close_div = content.find("</div>", pos)
        if close_div == -1:
            break
        if open_div != -1 and open_div < close_div:
            depth += 1
            pos = open_div + 4
        else:
            depth -= 1
            pos = close_div + len("</div>")
            if depth == 0:
                return content[start:pos]
    return None


def extract_clinical_flow_block(content: str) -> str:
    divider_idx = content.find('id="calcFlowDivider"')
    if divider_idx == -1:
        return ""
    start = content.rfind("<!-- Raciocinio Clinico", 0, divider_idx)
    if start == -1:
        start = content.rfind('<div class="flow-divider"', 0, divider_idx)
    flow = extract_div_by_id(content, "calcClinicalFlow")
    if not flow:
        return ""
    divider = content[start:content.find("</div>", divider_idx) + len("</div>")]
    return divider + "\n\n" + flow


def replace_panel(content: str, panel_id: str, new_panel: str) -> str:
    old = extract_panel(content, panel_id)
    if not old:
        raise ValueError(f"Painel {panel_id} não encontrado para substituição")
    return content.replace(old, new_panel.strip(), 1)


def fix_padrao_panel(content: str) -> str:
    padrao = extract_panel(content, "padrao")
    if not padrao:
        raise ValueError("Painel padrao não encontrado")

    # Manter apenas formulário + abertura do painel
    form_match = re.search(
        r'(<div class="tab-panel active" data-tab-panel="padrao">\s*<form class="calc-grid" id="calcForm"[^>]*>.*?</form>)',
        padrao,
        flags=re.DOTALL,
    )
    if not form_match:
        raise ValueError("Formulário padrao não encontrado")
    form_block = form_match.group(1)

    flow_block = extract_clinical_flow_block(content)
    if flow_block:
        old_flow = extract_clinical_flow_block(content)
        if old_flow:
            content = content.replace(old_flow, "", 1)

    new_padrao = form_block + "\n" + flow_block + LEARNING_TRACK_5 + "\n</div>"
    return replace_panel(content, "padrao", new_padrao)


def reorder_panels(content: str) -> str:
    panels = {}
    for pid in ("padrao", "estudante", "urgencia", "academico", "gestor"):
        panel = extract_panel(content, pid)
        if panel:
            panels[pid] = panel.strip()

    if len(panels) < 5:
        raise ValueError(f"Painéis incompletos: {list(panels)}")

    ordered = "\n\n".join(panels[pid] for pid in ("padrao", "estudante", "urgencia", "academico", "gestor"))

    return re.sub(
        r'<div data-tab-panels="perfil">.*?</div>\s*<section class="about-section">',
        f'<div data-tab-panels="perfil">\n\n{ordered}\n\n    </div>\n\n    <section class="about-section">',
        content,
        count=1,
        flags=re.DOTALL,
    )


def fix_about_section(content: str) -> str:
    """Garante disclaimer-card com about-grid de duas colunas."""
    if "disclaimer-card" in content:
        content = content.replace('about-grid about-grid--single', "about-grid")
        return content

  # Inserir disclaimer se ausente
    disclaimer = """
        <div class="disclaimer-card">
          <h3><svg class="icon"><use href="#i-shieldcheck"/></svg> Aviso importante</h3>
          <p>Esta ferramenta tem finalidade educacional e de apoio à decisão clínica. Os resultados devem ser sempre conferidos e validados por um profissional de enfermagem qualificado, de acordo com a avaliação do paciente e os protocolos da instituição.</p>
        </div>"""
    return content.replace(
        "</details></div>\n        </div>\n      </div>\n    </section>",
        f"</details></div>\n        </div>\n{disclaimer}\n      </div>\n    </section>",
        1,
    )


def cleanup_orphan_blocks(content: str) -> str:
    """Remove blocos de fluxo/aprendizagem duplicados fora dos painéis."""
    content = re.sub(
        r'\s*<!-- Recursos Adicionais.*?<div class="learning-track-wrap">.*?</div>\s*</div>\s*',
        "\n",
        content,
        flags=re.DOTALL,
    )
    return content


def dedupe_clinical_script(content: str) -> str:
    scripts = list(
        re.finditer(
            r'<script>\s*(?:// Revelar Raciocinio|\(function\(\))\s*\{[^<]*calcClinicalFlow.*?</script>',
            content,
            flags=re.DOTALL,
        )
    )
    if len(scripts) <= 1:
        return content
    for m in reversed(scripts[1:]):
        content = content[: m.start()] + content[m.end() :]
    return content


def slim(content: str) -> str:
    if 'href="css/site-styles.css"' not in content or "<style>/* ======" in content:
        content = remove_head_style_blocks(content)

    content = remove_cip_blocks(content)
    content = fix_profile_tabs(content)
    content = fix_padrao_panel(content)
    content = cleanup_orphan_blocks(content)
    content = reorder_panels(content)
    content = fix_about_section(content)
    content = add_modular_shell(content)
    content = dedupe_clinical_script(content)
    return content


def write_outputs(slimmed: str) -> None:
    paths = [
        ROOT / "preview_apgar.html",
        DELIVERY / "preview_apgar.html",
        DELIVERY / "apgar.html",
        DELIVERY / "html" / "apgar.html",
    ]
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(slimmed, encoding="utf-8")


def main() -> None:
    if not SRC.is_file():
        raise SystemExit(f"Arquivo não encontrado: {SRC}")

    original = SRC.read_text(encoding="utf-8")
    slimmed = slim(original)
    write_outputs(slimmed)

    orig_lines = original.count("\n") + 1
    new_lines = slimmed.count("\n") + 1
    print(f"preview_apgar modularizado: {orig_lines} → {new_lines} linhas")
    print(f"  → {ROOT / 'preview_apgar.html'}")
    print(f"  → {DELIVERY / 'preview_apgar.html'}")
    print(f"  → {DELIVERY / 'apgar.html'}")
    print(f"  → {DELIVERY / 'html' / 'apgar.html'}")
    print("Preview: cd NIFS/DELIVERY && python3 -m http.server 8765")
    print("  http://localhost:8765/preview_apgar.html")


if __name__ == "__main__":
    main()
