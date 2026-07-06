"""Chrome components — cookies, FABs, locale mega-menu data, preferences modal."""

from __future__ import annotations



import json

from collections import defaultdict

from pathlib import Path



from icons_lib import lucide_icon

from chrome_content_lib import get_shell
from website_lib import esc, rel_prefix, route_href



ROOT = Path(__file__).resolve().parents[1]

DATASETS = ROOT / "datasets"

LOCALE_JSON = ROOT / "website" / "assets" / "data" / "locale-options.json"

LOCALE_COUNT = 195





def build_locale_options() -> dict:

    countries = json.loads((DATASETS / "global" / "countries.json").read_text(encoding="utf-8"))

    locales = json.loads((DATASETS / "global" / "locales.json").read_text(encoding="utf-8"))

    by_country: dict[str, list] = defaultdict(list)

    for loc in locales.get("records", []):

        code = loc.get("locale_code", "")

        if "-" in code:

            by_country[code.split("-", 1)[1]].append(loc)



    options = []

    for country in sorted(countries.get("records", []), key=lambda c: c.get("name", "")):

        cc = country.get("country_code", "")

        locs = by_country.get(cc, [])

        primary = next((l for l in locs if l.get("is_primary")), locs[0] if locs else None)

        if primary:

            lang = primary.get("language_name_pt") or primary.get("language_name") or primary.get("locale_code", "")

            locale_code = primary.get("locale_code", f"en-{cc}")

        else:

            lang = "English"

            locale_code = f"en-{cc}"

        from flags_lib import flag_asset_path

        options.append({

            "country_code": cc,

            "country_name": country.get("name", cc),

            "name_local": country.get("name_local", ""),

            "locale_code": locale_code,

            "language_label": lang,

            "who_region": country.get("who_region", ""),

            "flag_file": flag_asset_path(cc),

        })



    global LOCALE_COUNT

    LOCALE_COUNT = len(options)

    data = {

        "schema_version": "2026.1.0",

        "count": LOCALE_COUNT,

        "records": options,

    }

    LOCALE_JSON.parent.mkdir(parents=True, exist_ok=True)

    LOCALE_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return data





def _icon(name: str) -> str:

    return lucide_icon(name)





def _ui_switch(pref: str, label: str) -> str:

    return f"""

<button type="button" class="ui-switch" data-cookie-pref="{esc(pref)}" role="switch" aria-checked="false" aria-label="{esc(label)}">

  <span class="ui-switch__track" aria-hidden="true"><span class="ui-switch__thumb"></span></span>

</button>"""





def render_accessibility_bar() -> str:
    bar = get_shell()["accessibility_bar"]
    return f"""

<div class="accessibility-bar" role="region" aria-label="{esc(bar["region_label"])}">

  <div class="section-container accessibility-bar__inner">

    <div class="a11y-toolbar" role="toolbar" aria-label="{esc(bar["toolbar_label"])}">

      <button type="button" class="a11y-btn a11y-btn--lg" data-a11y-font="inc" aria-label="{esc(bar["font_increase"]["aria_label"])}" title="{esc(bar["font_increase"]["title"])}">{esc(bar["font_increase"]["label"])}</button>

      <button type="button" class="a11y-btn a11y-btn--lg" data-a11y-font="dec" aria-label="{esc(bar["font_decrease"]["aria_label"])}" title="{esc(bar["font_decrease"]["title"])}">{esc(bar["font_decrease"]["label"])}</button>

      <button type="button" class="a11y-btn a11y-btn--theme" data-theme-toggle aria-label="{esc(bar["theme"]["aria_label"])}" aria-pressed="false" title="{esc(bar["theme"]["title"])}">

        <span class="a11y-btn__theme-icon" data-theme-icon="moon">{_icon("moon")}</span>

        <span class="a11y-btn__theme-icon is-hidden" data-theme-icon="sun">{_icon("sun")}</span>

        <span>{esc(bar["theme"]["label"])}</span>

      </button>

      <button type="button" class="a11y-btn a11y-btn--prefs" data-prefs-toggle aria-expanded="false" aria-controls="prefs-modal" title="{esc(bar["preferences"]["title"])}">

        {_icon("settings")}<span>{esc(bar["preferences"]["label"])}</span>

      </button>

    </div>

  </div>

</div>"""


def render_chrome_stack(depth: int) -> str:
    """Header spacer + accessibility bar — single import point for page shells."""
    return f"""<div class="site-top-spacer">
    {render_accessibility_bar()}
  </div>"""





def render_locale_mega_shell(kind: str, depth: int, *, country_count: int = 195) -> str:

    panels = get_shell()["header"]["locale_panels"]

    if kind == "search":

        search = get_shell()["header"]["search"]

        hint = " · ".join(
            f'<a href="{esc(route_href(link["href"], depth))}">{esc(link["label"])}</a>'
            for link in search["hint_links"]
        )

        return f"""

<div class="header-mega header-mega--search" data-header-mega="search" hidden>

  <div class="header-mega__inner section-container">

    <form class="header-mega__search" role="search" data-site-search-form>

      <label class="visually-hidden" for="site-search-input">{esc(search["aria_label"])}</label>

      <div class="header-mega__search-row">

        {_icon("search")}

        <input id="site-search-input" type="search" name="q" placeholder="{esc(search["placeholder"])}" autocomplete="off" data-site-search-input>

        <button type="submit" class="btn-primary-sm">{esc(search["submit"])}</button>

      </div>

    </form>

    <div class="header-mega__results" data-site-search-results aria-live="polite"></div>

    <p class="header-mega__hint">{hint}</p>

  </div>

</div>"""

    title = panels["lang_title"] if kind == "header-lang" else panels["country_title"]

    input_id = f"locale-filter-{kind}"

    aside = panels["aside"]

    aside_links = "".join(
        f'<a href="{esc(route_href(link["href"], depth))}">{esc(link["label"])}</a>'
        for link in aside["links"]
    )

    return f"""

<div class="header-mega header-mega--locale" data-header-mega="{esc(kind)}" hidden>

  <div class="header-mega__inner section-container">

    <div class="header-mega__head">

      <h2>{_icon("globe")} {esc(title)}</h2>

      <p>{country_count} {esc(panels["countries_hint"])}</p>

    </div>

    <label class="visually-hidden" for="{esc(input_id)}">{esc(panels["filter_label"])}</label>

    <div class="header-mega__filter-wrap">

      {_icon("search")}

      <input id="{esc(input_id)}" type="search" class="header-mega__filter" placeholder="{esc(panels["filter_placeholder"])}" data-locale-filter="{esc(kind)}" autocomplete="off">

    </div>

    <div class="header-mega__locale-layout" data-locale-panel="{esc(kind)}">

      <div class="header-mega__locale-col">

        <h3 class="header-mega__locale-heading">{esc(panels["popular_heading"])}</h3>

        <div class="header-mega__locale-list" data-locale-popular="{esc(kind)}" role="listbox" aria-label="{esc(panels["popular_aria"])}"></div>

      </div>

      <div class="header-mega__locale-col header-mega__locale-col--regions">

        <h3 class="header-mega__locale-heading">{esc(panels["regions_heading"])}</h3>

        <div class="header-mega__locale-regions" data-locale-regions="{esc(kind)}"></div>

      </div>

      <aside class="header-mega__locale-aside">

        <img class="header-mega__locale-aside-img" src="{esc(rel_prefix(depth))}assets/images/{esc(aside["image"])}" alt="{esc(aside["image_alt"])}" width="280" height="160" loading="lazy">

        <p class="header-mega__locale-aside-text">{esc(aside["text"])}</p>

        <div class="header-mega__locale-quick">

          {aside_links}

        </div>

      </aside>

    </div>

  </div>

</div>"""





def render_header_mega_panels(depth: int, *, country_count: int = 195) -> str:

    return f"""

<div class="header-mega-layer" data-header-mega-layer>

  {render_locale_mega_shell("search", depth, country_count=country_count)}

  {render_locale_mega_shell("header-lang", depth, country_count=country_count)}

  {render_locale_mega_shell("header-country", depth, country_count=country_count)}

</div>"""





def render_header_actions(depth: int, *, country_count: int = 195) -> str:

    prefix = rel_prefix(depth)
    actions = get_shell()["header"]["actions"]
    auth = get_shell()["header"]["auth"]

    locale_data = {"records": []}

    if LOCALE_JSON.exists():

        try:

            locale_data = json.loads(LOCALE_JSON.read_text(encoding="utf-8"))

        except json.JSONDecodeError:

            pass

    return f"""

<div class="header-actions">

  <div class="header-actions__item" data-mega-trigger="search">

    <button type="button" class="icon-btn" data-mega-open="search" aria-expanded="false" aria-haspopup="true" aria-label="{esc(actions["search_aria"])}">{_icon("search")}</button>

  </div>

  <div class="header-actions__item" data-mega-trigger="header-lang">

    <button type="button" class="icon-btn header-lang-btn" data-mega-open="header-lang" aria-expanded="false" aria-haspopup="true">

      {_icon("globe")}<span class="visually-hidden">{esc(actions["locale_hidden"])}</span><span data-current-locale-label>{esc(actions["locale_default"])}</span>

    </button>

  </div>

  <div class="header-actions__item" data-mega-trigger="header-country">

    <button type="button" class="icon-btn header-country-btn" data-mega-open="header-country" aria-expanded="false" aria-haspopup="true">

      <img class="header-country-flag" data-current-country-flag src="{esc(prefix)}assets/images/{esc(actions["country_flag"])}" alt="" width="20" height="15" loading="eager" decoding="async"><span class="visually-hidden">{esc(actions["country_hidden"])}</span><span data-current-country-label>{esc(actions["country_default"])}</span>

    </button>

  </div>

  <div class="header-auth">

    <a class="btn-outline" href="{esc(route_href(auth["login"]["href"], depth))}">{esc(auth["login"]["label"])}</a>

    <a class="btn-primary-sm" href="{esc(route_href(auth["signup"]["href"], depth))}">{esc(auth["signup"]["label"])}</a>

  </div>

  <button type="button" class="icon-btn mobile-menu-btn" data-mobile-menu-toggle aria-label="{esc(actions["menu_aria"])}" aria-expanded="false">{_icon("menu")}</button>

</div>

<script type="application/json" id="locale-options-data">{json.dumps(locale_data, ensure_ascii=False)}</script>

<script type="application/json" id="locale-options-path">{json.dumps(prefix + "assets/data/locale-options.json")}</script>"""





def render_cookie_banner(depth: int) -> str:

    banner = get_shell()["cookies"]["banner"]
    priv = route_href(banner["learn_more_href"], depth)

    return f"""

<div class="cookie-banner" id="cookie-banner" role="dialog" aria-modal="true" aria-labelledby="cookie-banner-title" hidden>

  <div class="section-container cookie-banner__inner">

    <div class="cookie-banner__icon" aria-hidden="true">{_icon("cookie")}</div>

    <div class="cookie-banner__text">

      <h2 id="cookie-banner-title">{esc(banner["title"])}</h2>

      <p>{esc(banner["body"])}

        <a href="{esc(priv)}">{esc(banner["learn_more"])}</a></p>

    </div>

    <div class="cookie-banner__actions">

      <button type="button" class="btn-outline" data-cookie-customize>{_icon("settings")} {esc(banner["customize"])}</button>

      <button type="button" class="btn-outline" data-cookie-reject>{esc(banner["reject"])}</button>

      <button type="button" class="btn" data-cookie-accept>{_icon("check")} {esc(banner["accept"])}</button>

    </div>

  </div>

</div>"""





def render_cookie_modal() -> str:

    modal = get_shell()["cookies"]["modal"]
    cats = modal["categories"]
    necessary = cats[0]
    analytics = cats[1]
    marketing = cats[2]

    return f"""

<div class="site-modal" id="cookie-modal" role="dialog" aria-modal="true" aria-labelledby="cookie-modal-title" hidden>

  <div class="site-modal__backdrop" data-modal-close="cookie"></div>

  <div class="site-modal__panel cookie-modal__panel">

    <header class="site-modal__header">

      <h2 id="cookie-modal-title">{_icon("shield")} {esc(modal["title"])}</h2>

      <button type="button" class="site-modal__close" data-modal-close="cookie" aria-label="{esc(modal["close_aria"])}">{_icon("x")}</button>

    </header>

    <div class="site-modal__body">

      <div class="cookie-pref">

        <div><strong>{esc(necessary["title"])}</strong><span>{esc(necessary["description"])}</span></div>

        <span class="cookie-pref__badge">{esc(necessary["badge"])}</span>

      </div>

      <div class="cookie-pref cookie-pref--toggle">

        <div><strong>{esc(analytics["title"])}</strong><span>{esc(analytics["description"])}</span></div>

        {_ui_switch("analytics", analytics["toggle_aria"])}

      </div>

      <div class="cookie-pref cookie-pref--toggle">

        <div><strong>{esc(marketing["title"])}</strong><span>{esc(marketing["description"])}</span></div>

        {_ui_switch("marketing", marketing["toggle_aria"])}

      </div>

      <button type="button" class="cookie-revoke" data-cookie-revoke>{esc(modal["revoke"])}</button>

    </div>

    <footer class="site-modal__footer">

      <button type="button" class="btn-outline" data-modal-close="cookie">{esc(modal["cancel"])}</button>

      <button type="button" class="btn" data-cookie-save>{esc(modal["save"])}</button>

    </footer>

  </div>

</div>"""





def render_preferences_modal(depth: int) -> str:

    prefs = get_shell()["preferences_modal"]
    a11y_href = route_href(prefs["inclusive"]["note_href"], depth)

    font_values = ["normal", "large", "extra-large"]
    font_buttons = "".join(
        f'<button type="button" data-prefs-font="{val}" aria-pressed="{"true" if i == 0 else "false"}">{esc(label)}</button>'
        for i, (val, label) in enumerate(zip(font_values, prefs["font_size"]["options"]))
    )

    scheme_values = ["default", "dark", "sepia"]
    scheme_buttons = "".join(
        f'<button type="button" data-prefs-scheme="{val}" aria-pressed="{"true" if i == 0 else "false"}">{esc(label)}</button>'
        for i, (val, label) in enumerate(zip(scheme_values, prefs["color_scheme"]["options"]))
    )

    profile_opts = "".join(
        f'<label class="prefs-profile__option"><input type="radio" name="prefs-profile" value="{esc(opt["value"])}" data-prefs-profile-select><span>{_icon(opt["icon"])} {esc(opt["label"])}</span></label>'
        for opt in prefs["profile"]["options"]
    )

    inclusive_items = "".join(
        f'<li><strong>{esc(item["title"])}</strong> — {esc(item["description"])}</li>'
        for item in prefs["inclusive"]["items"]
    )

    hc = prefs["high_contrast"]
    rm = prefs["reduce_motion"]

    return f"""

<div class="site-modal" id="prefs-modal" role="dialog" aria-modal="true" aria-labelledby="prefs-modal-title" hidden>

  <div class="site-modal__backdrop" data-modal-close="prefs"></div>

  <div class="site-modal__panel prefs-modal__panel">

    <header class="site-modal__header">

      <h2 id="prefs-modal-title">{_icon("palette")} {esc(prefs["title"])}</h2>

      <button type="button" class="site-modal__close" data-modal-close="prefs" aria-label="{esc(prefs["close_aria"])}">{_icon("x")}</button>

    </header>

    <div class="site-modal__body">

      <fieldset class="prefs-field">

        <legend>{_icon("type")} {esc(prefs["font_size"]["legend"])}</legend>

        <div class="prefs-segment">

          {font_buttons}

        </div>

      </fieldset>

      <div class="prefs-toggle-row">

        <span><strong>{_icon("contrast")} {esc(hc["title"])}</strong><small>{esc(hc["description"])}</small></span>

        <button type="button" class="ui-switch" data-prefs-contrast role="switch" aria-checked="false" aria-label="{esc(hc["aria"])}"><span class="ui-switch__track"><span class="ui-switch__thumb"></span></span></button>

      </div>

      <div class="prefs-toggle-row">

        <span><strong>{_icon("monitor")} {esc(rm["title"])}</strong><small>{esc(rm["description"])}</small></span>

        <button type="button" class="ui-switch" data-prefs-motion role="switch" aria-checked="false" aria-label="{esc(rm["aria"])}"><span class="ui-switch__track"><span class="ui-switch__thumb"></span></span></button>

      </div>

      <fieldset class="prefs-field">

        <legend>{esc(prefs["color_scheme"]["legend"])}</legend>

        <div class="prefs-segment">

          {scheme_buttons}

        </div>

      </fieldset>

      <section class="prefs-profile" aria-labelledby="prefs-profile-title">

        <h3 id="prefs-profile-title">{esc(prefs["profile"]["title"])}</h3>

        <p class="prefs-profile__current" data-prefs-profile-current>{esc(prefs["profile"]["current_hint"])}</p>

        <div class="prefs-profile__grid" role="radiogroup" aria-label="{esc(prefs["profile"]["radiogroup_aria"])}">
          {profile_opts}
        </div>

        <button type="button" class="btn-outline" data-profile-change>{esc(prefs["profile"]["change_button"])}</button>

      </section>

      <section class="prefs-downloads" aria-labelledby="prefs-downloads-title">

        <h3 id="prefs-downloads-title">{esc(prefs["downloads"]["title"])}</h3>

        <p class="prefs-downloads__hint">{esc(prefs["downloads"]["hint"])}</p>

        <ul class="prefs-downloads__list" data-prefs-downloads-list></ul>

        <p class="prefs-downloads__empty" data-prefs-downloads-empty hidden>{esc(prefs["downloads"]["empty"])}</p>

      </section>

      <section class="prefs-offline" aria-labelledby="prefs-offline-title">

        <h3 id="prefs-offline-title">{esc(prefs["offline"]["title"])}</h3>

        <p class="prefs-offline__hint">{esc(prefs["offline"]["hint"])}</p>

        <ul class="prefs-offline__list" data-prefs-offline-list></ul>

        <p class="prefs-offline__empty" data-prefs-offline-empty hidden>{esc(prefs["offline"]["empty"])}</p>

        <button type="button" class="btn-outline" data-prefs-offline-sync>{esc(prefs["offline"]["sync_button"])}</button>

      </section>

      <section class="prefs-handtalk" aria-labelledby="prefs-handtalk-title">

        <h3 id="prefs-handtalk-title">{esc(prefs["inclusive"]["title"])}</h3>

        <ul class="prefs-handtalk__list">

          {inclusive_items}

        </ul>

        <div class="prefs-handtalk__actions">

          <button type="button" class="btn-outline" data-prefs-share>{_icon("share-2")} {esc(prefs["inclusive"]["share"])}</button>

          <button type="button" class="btn-outline" data-prefs-save-fav>{_icon("bookmark")} {esc(prefs["inclusive"]["favorites"])}</button>

          <button type="button" class="btn-outline" data-prefs-print>{_icon("printer")} {esc(prefs["inclusive"]["print"])}</button>

        </div>

        <p class="prefs-handtalk__note"><a href="{esc(a11y_href)}">{esc(prefs["inclusive"]["note_link"])}</a>{esc(prefs["inclusive"]["note_after"])}</p>

      </section>

    </div>

    <footer class="site-modal__footer">

      <button type="button" class="btn" data-modal-close="prefs">{esc(prefs["close_button"])}</button>

    </footer>

  </div>

</div>"""





def render_profile_onboarding_modal() -> str:
    ob = get_shell()["profile_onboarding"]
    cards = ""
    for opt in ob["options"]:
        cards += f"""
<button type="button" class="profile-option" data-profile-select="{esc(opt["key"])}">
  <span class="profile-option__icon" aria-hidden="true">{lucide_icon(opt["icon"], size="20")}</span>
  <span class="profile-option__text">
    <strong>{esc(opt["title"])}</strong>
    <small>{esc(opt["description"])}</small>
  </span>
</button>"""
    return f"""
<div class="site-modal" id="profile-onboarding-modal" role="dialog" aria-modal="true" aria-labelledby="profile-welcome-title" hidden>

  <div class="site-modal__backdrop" aria-hidden="true"></div>

  <div class="site-modal__panel profile-onboarding__panel">

    <div class="site-modal__body" data-profile-step="welcome">
      <h2 id="profile-welcome-title">{esc(ob["welcome_title"])}</h2>
      <p>{esc(ob["welcome_body"])}</p>
      <button type="button" class="btn btn-primary-lg" data-profile-next>{esc(ob["continue"])}</button>
    </div>

    <div class="site-modal__body" data-profile-step="choose" hidden>
      <h2 id="profile-choose-title">{esc(ob["choose_title"])}</h2>
      <p class="profile-onboarding__hint">{esc(ob["choose_hint"])}</p>
      <div class="profile-options">{cards}</div>
    </div>

  </div>

</div>

<script type="application/json" id="user-profile-config-path">"assets/data/user-profile-config.json"</script>"""





def render_fabs() -> str:

    fabs = get_shell()["fabs"]
    cookie = get_shell()["cookies"]["fab"]

    return f"""

<div class="site-fabs" aria-label="{esc(fabs["region_aria"])}">

  <button type="button" class="site-fab site-fab--cookie" data-cookie-fab aria-label="{esc(cookie["aria_label"])}" title="{esc(cookie["title"])}">{_icon("cookie")}</button>

  <button type="button" class="site-fab site-fab--top" data-scroll-top aria-label="{esc(fabs["scroll_top_aria"])}" title="{esc(fabs["scroll_top_title"])}" hidden>{_icon("arrow-up")}</button>

</div>"""





def render_shell_extras(depth: int) -> str:

    return (

        render_cookie_banner(depth)

        +         render_cookie_modal()

        + render_preferences_modal(depth)

        + render_profile_onboarding_modal()

        + render_fabs()

    )





def render_footer_lang_select() -> str:

    loc = get_shell()["footer"]["locale_select"]

    return f"""

<div class="footer-lang">

  <label for="footer-locale-select">{esc(loc["label"])}</label>

  <select id="footer-locale-select" data-footer-locale aria-label="{esc(loc["aria"])}">

    <option value="{esc(loc["default_value"])}" data-country="{esc(loc["default_country"])}" selected>{esc(loc["default_option"])}</option>

  </select>

</div>"""


