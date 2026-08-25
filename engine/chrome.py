"""Public Design System chrome matching production placeholders.

SOURCE_DERIVED from origin snapshots + Drive locales + pages_full inventory.
Renderer remains PRESENTATION_ONLY. No ads. No email capture. No CDN. No cookie wall.
"""

from __future__ import annotations

import json
import re

from .html import attr, esc
from .paths import ASSETS_DIR, ROOT

SITE_NAME = "Calculadoras de Enfermagem"
SITE_NS = "CKO"
DISCLAIMER = (
    "Apoio à decisão clínica e ao estudo. Não substitui julgamento profissional, "
    "protocolo institucional nem prescrição."
)


def asset_prefix(home_href: str) -> str:
    return "../" if str(home_href).startswith("../") else ""


def _icon(name: str) -> str:
    paths = {
        "type": '<polyline points="4 7 4 4 20 4 20 7"/><line x1="9" x2="15" y1="20" y2="20"/><line x1="12" x2="12" y1="4" y2="20"/>',
        "line": '<line x1="3" x2="21" y1="6" y2="6"/><line x1="3" x2="21" y1="12" y2="12"/><line x1="3" x2="21" y1="18" y2="18"/>',
        "letter": '<path d="M10 12H3"/><path d="M21 12h-7"/><path d="M12 20V4"/>',
        "contrast": '<circle cx="12" cy="12" r="10"/><path d="M12 2a10 10 0 0 1 0 20z"/>',
        "moon": '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>',
        "font": '<path d="M4 20V4h7"/><path d="M4 12h5"/><path d="M15 20V9h5"/><path d="M15 14h3"/>',
        "reset": '<path d="M3 12a9 9 0 1 0 3-6.7"/><polyline points="3 4 3 9 8 9"/>',
        "access": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="7" r="1"/><path d="M9 21v-6h6v6"/><path d="M8 11h8l-1 4H9z"/>',
        "gauge": '<path d="M12 14v4"/><path d="M12 2a10 10 0 0 0-9.8 12.3 4 4 0 0 0 5.7 5.7A10 10 0 0 0 22 12Z"/>',
        "play": '<polygon points="5 3 19 12 5 21 5 3"/>',
        "restart": '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.76 2.75L3 8"/><path d="M3 3v5h5"/>',
        "volume": '<path d="M11 5L6 9H2v6h4l5 4V5z"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M22.42 1.42a15 15 0 0 1 0 21.16"/>',
        "keyboard": '<rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 10h.01M10 10h.01M14 10h.01M18 10h.01M8 14h8"/>',
    }
    return (
        f'<svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        f'fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" '
        f'stroke-linejoin="round">{paths[name]}</svg>'
    )


def _footer_strings() -> dict:
    for path in (
        ROOT / "cko_inbox" / "drive" / "site_shell" / "site-shell" / "footer.json",
        ROOT / "cko_inbox" / "drive" / "locales" / "pt" / "footer.json",
    ):
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            return payload.get("footer") or {}
    return {}


def _shell_languages() -> list[tuple[str, str]]:
    """Language names from Drive site-shell. Flag images are not in the zip."""
    path = ROOT / "cko_inbox" / "drive" / "site_shell" / "site-shell" / "_language_selector.html"
    if not path.exists():
        return [("pt", "Português")]
    text = path.read_text(encoding="utf-8")
    pairs = re.findall(r'data-value="([^"]+)"[\s\S]*?<span>([^<]+)</span>', text)
    return [(code, name.strip()) for code, name in pairs] or [("pt", "Português")]


def _locale_codes() -> list[str]:
    path = ROOT / "cko_md" / "locale_registry.json"
    if not path.exists():
        return ["pt-BR"]
    codes = json.loads(path.read_text(encoding="utf-8")).get("zip_codes_observed") or []
    return list(codes)


def _a11y_btn(btn_id: str, label: str, icon: str, *, span_id: str = "", span_text: str = "", sr_only: bool = False) -> str:
    text = span_text or label
    if sr_only:
        inner = f'<span class="sr-only">{esc(label)}</span>'
    elif span_id:
        inner = f'<span id="{attr(span_id)}">{esc(text)}</span>'
    else:
        inner = f"<span>{esc(text)}</span>"
    return (
        f'<button type="button" id="{attr(btn_id)}" aria-label="{attr(label)}">'
        f"{_icon(icon)}{inner}</button>"
    )


def ds_a11y_bar() -> str:
    """GAP ONLY from Drive global-body-elements.html. No cookie wall, SW, or Font Awesome CDN."""
    colors = """
          <button type="button" class="color-option" data-color="yellow" style="background-color: yellow" aria-label="Cor de foco amarela"></button>
          <button type="button" class="color-option" data-color="lime" style="background-color: lime" aria-label="Cor de foco verde-limão"></button>
          <button type="button" class="color-option" data-color="cyan" style="background-color: cyan" aria-label="Cor de foco ciano"></button>
          <button type="button" class="color-option" data-color="magenta" style="background-color: magenta" aria-label="Cor de foco magenta"></button>"""
    return f"""<div id="statusMessage" class="sr-only" aria-live="polite" aria-atomic="true"></div>
<button type="button" id="accessibilityToggleButton" aria-label="Abrir menu de acessibilidade" aria-controls="pwaAcessibilidadeBar" aria-expanded="false">{_icon("access")}</button>
<div id="pwaAcessibilidadeBar" role="dialog" aria-label="Acessibilidade">
    <div class="pwa-acessibilidade-header">
      <h3>Acessibilidade</h3>
      <button type="button" id="pwaAcessibilidadeCloseBtn" class="pwa-acessibilidade-close-btn" aria-label="Fechar menu de acessibilidade">&times;</button>
    </div>
    {_a11y_btn("btnAlternarTamanhoFontePWA", "Alterar tamanho da fonte", "type", span_id="fontSizeTextPWA", span_text="Tamanho da Fonte")}
    {_a11y_btn("btnAlternarEspacamentoLinhaPWA", "Alterar espaçamento de linha", "line", span_id="lineHeightTextPWA", span_text="Espaçamento Linha")}
    {_a11y_btn("btnAlternarEspacamentoLetraPWA", "Alterar espaçamento de letra", "letter", span_id="letterSpacingTextPWA", span_text="Espaçamento Letra")}
    {_a11y_btn("btnAlternarContrastePWA", "Alternar alto contraste", "contrast", span_text="Alto Contraste")}
    {_a11y_btn("btnAlternarModoEscuroPWA", "Alternar modo escuro", "moon", span_text="Modo Escuro")}
    {_a11y_btn("btnAlternarFonteDislexiaPWA", "Alternar fonte para dislexia", "font", span_text="Fonte Dislexia")}
    <div class="color-options-pwa" role="radiogroup" aria-label="Cor de foco de acessibilidade">{colors}
    </div>
    {_a11y_btn("btnKeyboardShortcutsPWA", "Atalhos de Teclado", "keyboard", span_text="Atalhos")}
    {_a11y_btn("btnResetarAcessibilidadePWA", "Redefinir configurações", "reset", span_text="Redefinir Tudo")}
  </div>
<div id="menuOverlay" class="menu-overlay"></div>
<div id="barraAcessibilidade" role="region" aria-label="Barra de acessibilidade" accesskey="A">
    {_a11y_btn("btnAlternarTamanhoFonte", "Alterar tamanho da fonte", "type", span_id="fontSizeText", span_text="Normal")}
    {_a11y_btn("btnAlternarEspacamentoLinha", "Alterar espaçamento de linha", "line", span_id="lineHeightText", span_text="Médio")}
    {_a11y_btn("btnAlternarEspacamentoLetra", "Alterar espaçamento de letra", "letter", span_id="letterSpacingText", span_text="Normal")}
    {_a11y_btn("btnAlternarVelocidadeLeitura", "Alterar velocidade de leitura", "gauge", span_id="readingSpeedText", span_text="Normal")}
    {_a11y_btn("btnToggleLeitura", "Reproduzir/Pausar leitura do conteúdo principal", "play", sr_only=True)}
    {_a11y_btn("btnReiniciarLeitura", "Reiniciar leitura do conteúdo principal", "restart", sr_only=True)}
    {_a11y_btn("btnReadFocused", "Ler elemento focado", "volume", sr_only=True)}
    {_a11y_btn("btnAlternarContraste", "Alternar alto contraste", "contrast", sr_only=True)}
    {_a11y_btn("btnAlternarModoEscuro", "Alternar modo escuro", "moon", sr_only=True)}
    {_a11y_btn("btnAlternarFonteDislexia", "Alternar fonte para dislexia", "font", sr_only=True)}
    <div class="color-options" role="radiogroup" aria-label="Cor de foco de acessibilidade">{colors}
    </div>
    {_a11y_btn("btnKeyboardShortcuts", "Atalhos de Teclado", "keyboard", sr_only=True)}
    {_a11y_btn("btnResetarAcessibilidade", "Redefinir configurações de acessibilidade", "reset", sr_only=True)}
  </div>
<div id="keyboardShortcutsModal" role="dialog" aria-modal="true" aria-labelledby="keyboardModalTitle">
    <div class="keyboard-modal-content">
      <button type="button" id="keyboardModalCloseButton" class="modal-close-btn" aria-label="Fechar atalhos de teclado">&times;</button>
      <h3 id="keyboardModalTitle">Atalhos de Teclado e Navegação</h3>
      <ul>
        <li><strong>Alt + Shift + I:</strong> Ir para o Início</li>
        <li><strong>Alt + Shift + C:</strong> Ir para o Conteúdo Principal</li>
        <li><strong>Alt + Shift + A:</strong> Ir para a Barra de Acessibilidade</li>
        <li><strong>Alt + Shift + T:</strong> Voltar ao Topo da Página</li>
      </ul>
    </div>
  </div>
<button type="button" id="backToTopBtn" aria-label="Voltar ao topo da página" accesskey="T">Voltar ao Topo</button>"""


def ds_header(home_href: str, prefix: str) -> str:
    logo = f"{prefix}assets/img/icontopbar1-calculadoras-de-enfermagem.webp"
    inspector = home_href.replace("index.html", "inspector.html") if home_href.endswith("index.html") else "inspector.html"
    admin = home_href.replace("index.html", "admin.html") if home_href.endswith("index.html") else "admin.html"
    biblioteca = home_href.replace("index.html", "biblioteca.html") if home_href.endswith("index.html") else "biblioteca.html"
    calc_href = "gotejamento.html" if home_href.startswith("../") else "tools/gotejamento.html"
    return f"""<div id="global-header-container">
    <header class="site-header" role="banner">
    <div class="wrap header-row">
      <button type="button" id="hamburgerButton" class="hamburger-button" aria-label="Abrir menu de navegação" aria-expanded="false" aria-controls="primary-nav">
        <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" /></svg>
      </button>
      <a class="brand" href="{attr(home_href)}">
        <img class="brand-mark" src="{attr(logo)}" width="48" height="32" alt="{esc(SITE_NAME)}" decoding="async">
        <span class="brand-text">
          <span class="brand-name">{esc(SITE_NAME)}</span>
          <span class="brand-sub">{esc(SITE_NS)} · lote piloto</span>
        </span>
      </a>
      <nav id="primary-nav" class="nav desktop-nav" aria-label="Navegação Principal">
        <a href="{attr(home_href)}" accesskey="I">Início</a>
        <a href="{attr(biblioteca)}">Biblioteca</a>
        <a href="{attr(inspector)}">Sobre Nós</a>
        <a href="{attr(calc_href)}">Calculadoras</a>
        <a href="{attr(biblioteca)}#curriculo">Conteúdos</a>
        <a href="{attr(admin)}">Admin</a>
      </nav>
    </div>
  </header>
  </div>"""


def ds_language_bar(home_href: str) -> str:
    from .who_i18n import RUNTIME_LOCAL_BCP47, runtime_who_local_key

    locales = home_href.replace("index.html", "admin/locales.html") if home_href.endswith("index.html") else "admin/locales.html"
    items = []
    for code, name in _shell_languages():
        items.append(
            f'<button type="button" class="lang-option" data-value="{attr(code)}" lang="{attr(code)}">'
            f'<span>{esc(name)}</span> <code>{esc(code)}</code></button>'
        )
    menu = "\n        ".join(items)
    key = runtime_who_local_key()
    return f"""<div id="language-selector-placeholder" data-i18n-gate="HOLD" data-owner-i18n="APPROVED" data-who-official="en,ar,zh,fr,ru,es" data-who-local-key="{attr(key)}" data-local-bcp47="{attr(RUNTIME_LOCAL_BCP47)}" data-pt-variants="HOLD">
    <div class="wrap lang-bar">
      <p class="lang-runtime">{esc(key)} · i18n HOLD. Variantes lusófonas catalogadas, não ligadas. Candidatos WHO HQ (en ar zh fr ru es) não ligam o seletor. PAHO pt-br observado. Bandeiras EVIDENCE_PENDING. Tradução não redireciona.</p>
      <div id="language-dropdown-wrapper">
        <button type="button" id="langButton" aria-haspopup="listbox" aria-expanded="false" aria-controls="langMenu">
          <span id="langText">Português</span>
          <svg class="lang-caret" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
        </button>
        <div id="langMenu" class="hidden" role="listbox" aria-label="Idiomas observados no site-shell">
        {menu}
        </div>
      </div>
      <a class="lang-chip" href="{attr(locales)}">Locales / Drive</a>
    </div>
  </div>"""


def ds_footer(home_href: str, prefix: str) -> str:
    t = _footer_strings()
    logo = f"{prefix}assets/img/iconrodape1-80-calculadoras-de-enfermagem.webp"
    inspector = home_href.replace("index.html", "inspector.html") if home_href.endswith("index.html") else "inspector.html"
    admin = home_href.replace("index.html", "admin.html") if home_href.endswith("index.html") else "admin.html"
    maturity = home_href.replace("index.html", "admin/maturity.html") if home_href.endswith("index.html") else "admin/maturity.html"
    copyright_text = str(t.get("copyright") or "© {{year}} Calculadoras de Enfermagem. Todos os direitos reservados.").replace("{{year}}", "2026")
    heading = t.get("footerHeading") or "Rodapé do site"
    return f"""<div id="footer-placeholder">
  <footer class="site-footer" id="institucional" role="contentinfo" aria-labelledby="footer-heading">
    <h2 id="footer-heading" class="sr-only">{esc(heading)}</h2>
    <div class="wrap footer-logo-row">
      <a href="{attr(home_href)}" aria-label="{esc(t.get("homeAria") or "Ir para a página inicial")}">
        <img class="footer-mark-80" src="{attr(logo)}" width="80" height="80" alt="{esc(t.get("logoAlt") or SITE_NAME)}" decoding="async">
      </a>
    </div>
    <div class="wrap footer-grid">
      <nav class="footer-col" aria-label="{esc(t.get("institutional") or "Institucional")}">
        <h2>{esc(t.get("institutional") or "Institucional")}</h2>
        <ul>
          <li><a href="{attr(home_href)}">{esc(t.get("home") or "Início")}</a></li>
          <li><a href="{attr(inspector)}">{esc(t.get("about") or "Sobre Nós")}</a></li>
          <li><a href="{attr(inspector)}">{esc(t.get("siteMap") or "Mapa do Site")}</a></li>
          <li><span class="footer-hold">{esc(t.get("privacyCenter") or "Central de Privacidade")} · HOLD</span></li>
          <li><span class="footer-hold">{esc(t.get("terms") or "Termos e Condições de Uso")} · HOLD</span></li>
          <li><span class="footer-hold">{esc(t.get("accessibilityPolicy") or "Política de Acessibilidade")} · HOLD</span></li>
        </ul>
      </nav>
      <nav class="footer-col" aria-label="{esc(t.get("digitalSustainability") or "Sustentabilidade Digital")}">
        <h2>{esc(t.get("digitalSustainability") or "Sustentabilidade Digital")}</h2>
        <ul>
          <li><a href="{attr(maturity)}">{esc(t.get("ourCommitment") or "Nosso Compromisso")}</a></li>
          <li><span class="footer-hold">{esc(t.get("impact") or "Relatório de Impacto")} · HOLD</span></li>
          <li><span class="footer-hold">{esc(t.get("greenTech") or "Tecnologia Verde")} · HOLD</span></li>
        </ul>
      </nav>
      <div class="footer-col">
        <h2>{esc(t.get("ourCommitment") or "Nosso Compromisso")}</h2>
        <p>{esc(t.get("commitmentText") or "Padrões de acessibilidade, sustentabilidade digital, segurança da informação e proteção de dados.")}</p>
        <p class="footer-commitment">WCAG nomeada; equivalente BR eMAG/LBI. Texto de cláusula W3C não ingerido. Sem captura de e-mail e sem mural de cookies neste lote (NO_SENSITIVE_CAPTURE).</p>
      </div>
      <div class="footer-col">
        <h2>{esc(t.get("followUs") or "Siga-nos")}</h2>
        <ul>
          <li><a href="https://linkedin.com/company/calculadoras-de-enfermagem" rel="noopener noreferrer me">LinkedIn</a></li>
          <li><a href="https://www.instagram.com/calculadorasdeenfermagem/" rel="noopener noreferrer me">Instagram</a></li>
          <li><a href="https://www.youtube.com/channel/UC_6runTDHz8u5S1Yab842pg" rel="noopener noreferrer me">YouTube</a></li>
          <li><a href="{attr(admin)}">Admin Studio</a></li>
        </ul>
      </div>
    </div>
    <div class="wrap footer-bottom">
      <p>{esc(DISCLAIMER)}</p>
      <p>{esc(copyright_text)} Audit Educa · {esc(SITE_NS)}. Newsletter/e-mail não implantados.</p>
    </div>
  </footer>
  </div>"""


def ds_header_footer(home_href: str) -> tuple[str, str]:
    prefix = asset_prefix(home_href)
    header = ds_a11y_bar() + ds_header(home_href, prefix) + ds_language_bar(home_href)
    return header, ds_footer(home_href, prefix)


def ds_a11y_script(*, inline: bool, prefix: str) -> str:
    href = f"{prefix}assets/a11y.js"
    if inline:
        js = (ASSETS_DIR / "js" / "a11y.js").read_text(encoding="utf-8")
        return f"<script>\n{js}\n</script>"
    return f'<script src="{attr(href)}"></script>'
