"""Public Design System chrome matching production placeholders.

SOURCE_DERIVED from origin snapshots + Drive locales + pages_full inventory.
Renderer remains PRESENTATION_ONLY. No ads. No email capture. No CDN. No cookie wall.
"""

from __future__ import annotations

import json

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
    }
    return (
        f'<svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        f'fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" '
        f'stroke-linejoin="round">{paths[name]}</svg>'
    )


def _footer_strings() -> dict:
    path = ROOT / "cko_inbox" / "drive" / "locales" / "pt" / "footer.json"
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("footer") or {}


def _locale_codes() -> list[str]:
    path = ROOT / "cko_md" / "locale_registry.json"
    if not path.exists():
        return ["pt-BR"]
    codes = json.loads(path.read_text(encoding="utf-8")).get("zip_codes_observed") or []
    return list(codes)


def ds_a11y_bar() -> str:
    return f"""<div id="statusMessage" class="sr-only" aria-live="polite" aria-atomic="true"></div>
<div id="barraAcessibilidade" role="region" aria-label="Barra de acessibilidade">
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
  <button type="button" id="accessibilityToggleButton" aria-label="Abrir menu de acessibilidade" aria-controls="barraAcessibilidade" aria-expanded="false">{_icon("access")}</button>"""


def ds_header(home_href: str, prefix: str) -> str:
    logo = f"{prefix}assets/img/icontopbar1-calculadoras-de-enfermagem.webp"
    inspector = home_href.replace("index.html", "inspector.html") if home_href.endswith("index.html") else "inspector.html"
    admin = home_href.replace("index.html", "admin.html") if home_href.endswith("index.html") else "admin.html"
    locales = home_href.replace("index.html", "admin/locales.html") if home_href.endswith("index.html") else "admin/locales.html"
    calc_href = "gotejamento.html" if home_href.startswith("../") else "tools/gotejamento.html"
    return f"""<div id="global-header-container">
    <header class="site-header" role="banner">
    <div class="wrap header-row">
      <a class="brand" href="{attr(home_href)}">
        <img class="brand-mark" src="{attr(logo)}" width="48" height="32" alt="{esc(SITE_NAME)}" decoding="async">
        <span class="brand-text">
          <span class="brand-name">{esc(SITE_NAME)}</span>
          <span class="brand-sub">{esc(SITE_NS)} · lote piloto</span>
        </span>
      </a>
      <nav class="nav desktop-nav" aria-label="Navegação Principal">
        <a href="{attr(home_href)}" accesskey="I">Início</a>
        <a href="{attr(inspector)}">Sobre Nós</a>
        <a href="{attr(calc_href)}">Calculadoras</a>
        <a href="{attr(inspector)}">Conteúdos</a>
        <a href="{attr(admin)}">Admin</a>
        <a class="lang-chip" href="{attr(locales)}" title="19 códigos observados no Drive; tradução HOLD">pt-BR · i18n HOLD</a>
      </nav>
    </div>
  </header>
  </div>"""


def ds_language_bar(home_href: str) -> str:
    locales = home_href.replace("index.html", "admin/locales.html") if home_href.endswith("index.html") else "admin/locales.html"
    chips = " ".join(
        f'<span class="lang-code" lang="{esc(code)}">{esc(code)}</span>'
        for code in _locale_codes()
    )
    return f"""<div id="language-selector-placeholder" data-i18n-gate="HOLD">
    <div class="wrap lang-bar">
      <p class="lang-runtime">Idioma de runtime: <strong>pt-BR</strong>. Seletor observado (Drive/origin) · tradução HOLD.</p>
      <p class="lang-codes" aria-label="Códigos de locale observados">{chips}</p>
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
        <p class="footer-commitment">Sem captura de e-mail e sem mural de cookies neste lote (NO_SENSITIVE_CAPTURE).</p>
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
