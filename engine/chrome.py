"""Public Design System chrome: a11y bar, white header, navy footer.

SOURCE_DERIVED from annex + reference-website + Drive logos/locales.
Renderer remains PRESENTATION_ONLY. No email capture. No CDN. No cookie wall.
"""

from __future__ import annotations

from .html import attr, esc
from .paths import ASSETS_DIR

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
    }
    return (
        f'<svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        f'fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" '
        f'stroke-linejoin="round">{paths[name]}</svg>'
    )


def ds_a11y_bar() -> str:
    return f"""<div id="barraAcessibilidade" role="region" aria-label="Barra de acessibilidade">
    <div class="a11y-bar-inner wrap">
      <p class="a11y-kicker">Acessibilidade</p>
      <div class="a11y-actions">
        <button type="button" id="btnAlternarTamanhoFonte" aria-label="Alterar tamanho da fonte">{_icon("type")}<span id="fontSizeText">Fonte</span></button>
        <button type="button" id="btnAlternarEspacamentoLinha" aria-label="Alterar espaçamento de linha">{_icon("line")}<span id="lineHeightText">Linha</span></button>
        <button type="button" id="btnAlternarEspacamentoLetra" aria-label="Alterar espaçamento de letra">{_icon("letter")}<span id="letterSpacingText">Letra</span></button>
        <button type="button" id="btnAlternarContraste" aria-label="Alternar alto contraste">{_icon("contrast")}<span>Contraste</span></button>
        <button type="button" id="btnAlternarModoEscuro" aria-label="Alternar modo escuro">{_icon("moon")}<span>Escuro</span></button>
        <button type="button" id="btnAlternarFonteDislexia" aria-label="Alternar fonte para dislexia">{_icon("font")}<span>Dislexia</span></button>
        <span class="a11y-sep" aria-hidden="true"></span>
        <span class="color-options" role="radiogroup" aria-label="Cor de foco">
          <button type="button" class="color-option" data-color="yellow" style="background:#ffd400" aria-label="Foco amarelo"></button>
          <button type="button" class="color-option" data-color="lime" style="background:#32cd32" aria-label="Foco verde-limão"></button>
          <button type="button" class="color-option" data-color="cyan" style="background:#00e5ff" aria-label="Foco ciano"></button>
          <button type="button" class="color-option" data-color="magenta" style="background:#ff00aa" aria-label="Foco magenta"></button>
        </span>
        <button type="button" id="btnResetAcessibilidade" aria-label="Redefinir acessibilidade">{_icon("reset")}<span>Reset</span></button>
      </div>
    </div>
  </div>
  <button type="button" id="accessibilityToggleButton" aria-label="Abrir menu de acessibilidade" aria-controls="pwaAcessibilidadeBar" aria-expanded="false">{_icon("access")}</button>"""


def ds_header(home_href: str, prefix: str) -> str:
    logo = f"{prefix}assets/img/logotipo-calculadoras-de-enfermagem.webp"
    inspector = home_href.replace("index.html", "inspector.html") if home_href.endswith("index.html") else "inspector.html"
    admin = home_href.replace("index.html", "admin.html") if home_href.endswith("index.html") else "admin.html"
    locales = home_href.replace("index.html", "admin/locales.html") if home_href.endswith("index.html") else "admin/locales.html"
    return f"""<header class="site-header" role="banner">
    <div class="wrap header-row">
      <a class="brand" href="{attr(home_href)}">
        <img class="brand-mark" src="{attr(logo)}" width="48" height="32" alt="{esc(SITE_NAME)}" decoding="async">
        <span class="brand-text">
          <span class="brand-name">{esc(SITE_NAME)}</span>
          <span class="brand-sub">{esc(SITE_NS)} · lote piloto</span>
        </span>
      </a>
      <nav class="nav" aria-label="Principal">
        <a href="{attr(home_href)}" accesskey="I">Início</a>
        <a href="{attr(inspector)}">Inspector</a>
        <a href="{attr(admin)}">Admin</a>
        <a class="lang-chip" href="{attr(locales)}" title="19 códigos observados no Drive; tradução HOLD">pt-BR · i18n HOLD</a>
      </nav>
    </div>
  </header>"""


def ds_footer(home_href: str, prefix: str) -> str:
    logo = f"{prefix}assets/img/logotipo-footer.png"
    inspector = home_href.replace("index.html", "inspector.html") if home_href.endswith("index.html") else "inspector.html"
    admin = home_href.replace("index.html", "admin.html") if home_href.endswith("index.html") else "admin.html"
    maturity = home_href.replace("index.html", "admin/maturity.html") if home_href.endswith("index.html") else "admin/maturity.html"
    return f"""<footer class="site-footer" id="institucional" role="contentinfo" aria-label="Rodapé do site">
    <div class="wrap footer-grid">
      <div class="footer-brand">
        <img class="footer-mark" src="{attr(logo)}" width="220" height="52" alt="{esc(SITE_NAME)}" decoding="async">
        <p>Tecnologia e conhecimento para uma enfermagem mais eficiente, com domínio e sustentável.</p>
        <p class="footer-commitment">Padrões de acessibilidade, sustentabilidade digital, segurança da informação e proteção de dados. Sem captura de e-mail neste lote (NO_SENSITIVE_CAPTURE).</p>
      </div>
      <div class="footer-col">
        <h2>Institucional</h2>
        <ul>
          <li><a href="{attr(home_href)}">Início</a></li>
          <li><a href="{attr(inspector)}">Inspector</a></li>
          <li><a href="{attr(admin)}">Admin Studio</a></li>
          <li><a href="{attr(maturity)}">Panorama de maturidade</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h2>Acessibilidade</h2>
        <ul>
          <li>Barra de acessibilidade (36px)</li>
          <li>Skip link · teclado</li>
          <li>Contraste, fonte, espaçamento</li>
          <li>Fonte dislexia: fallback Arial (woff2 GAP)</li>
        </ul>
      </div>
      <div class="footer-col">
        <h2>Governança</h2>
        <ul>
          <li>CKO-MD → CKO-REG → front-end</li>
          <li>Constituição CKO-INS-AI-PROJECT-001</li>
          <li>Renderer PRESENTATION_ONLY</li>
          <li>Release clínica HOLD</li>
        </ul>
      </div>
    </div>
    <div class="wrap footer-bottom">
      <p>{esc(DISCLAIMER)}</p>
      <p>© 2026 {esc(SITE_NAME)}. Audit Educa · {esc(SITE_NS)}. Newsletter/e-mail não implantados.</p>
    </div>
  </footer>"""


def ds_header_footer(home_href: str) -> tuple[str, str]:
    prefix = asset_prefix(home_href)
    header = ds_a11y_bar() + ds_header(home_href, prefix)
    return header, ds_footer(home_href, prefix)


def ds_a11y_script(*, inline: bool, prefix: str) -> str:
    href = f"{prefix}assets/a11y.js"
    if inline:
        js = (ASSETS_DIR / "js" / "a11y.js").read_text(encoding="utf-8")
        return f"<script>\n{js}\n</script>"
    return f'<script src="{attr(href)}"></script>'
