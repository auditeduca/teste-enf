"""Marketing / analytics head snippets — GA4 first-party + AdSense (consent-gated via marketing.js)."""

from __future__ import annotations

import json
from pathlib import Path

from website_lib import esc, rel_prefix

from content_paths import ROOT, content_path

MARKETING_JSON = content_path("marketing_config")
ASSETS_DATA = ROOT / "website" / "assets" / "data" / "marketing-config.json"


def load_marketing_config() -> dict:
    if not MARKETING_JSON.exists():
        return {"enabled": False}
    try:
        return json.loads(MARKETING_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"enabled": False}


def export_marketing_config() -> Path:
    cfg = load_marketing_config()
    ASSETS_DATA.parent.mkdir(parents=True, exist_ok=True)
    ASSETS_DATA.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ASSETS_DATA


def render_marketing_preconnect(cfg: dict) -> str:
    if not cfg.get("enabled"):
        return ""
    links = []
    for url in cfg.get("preconnect") or []:
        links.append(f'<link rel="preconnect" href="{esc(url)}" crossorigin>')
        host = url.replace("https://", "").replace("http://", "").split("/")[0]
        links.append(f'<link rel="dns-prefetch" href="//{esc(host)}">')
    return "\n  ".join(links)


def render_marketing_consent_stub() -> str:
    """Consent Mode v2 defaults — no personal data until cookie banner grants consent."""
    return """<script>
window.dataLayer=window.dataLayer||[];
function gtag(){dataLayer.push(arguments);}
gtag('consent','default',{
  ad_storage:'denied',
  ad_user_data:'denied',
  ad_personalization:'denied',
  analytics_storage:'denied',
  functionality_storage:'granted',
  security_storage:'granted',
  wait_for_update:500
});
gtag('set','ads_data_redaction',true);
gtag('set','url_passthrough',true);
</script>"""


def render_marketing_head(cfg: dict | None = None) -> str:
    cfg = cfg or load_marketing_config()
    if not cfg.get("enabled"):
        return ""
    preconnect = render_marketing_preconnect(cfg)
    parts = [render_marketing_consent_stub()]
    if preconnect:
        parts.append(preconnect)
    return "\n  ".join(parts)


def render_marketing_ad_rail(cfg: dict | None = None) -> str:
    cfg = cfg or load_marketing_config()
    if not cfg.get("enabled"):
        return ""
    ads = cfg.get("adsense") or {}
    if not ads.get("client") and not ads.get("auto_ads"):
        return ""
    return """
<div class="site-ad-rail" data-ad-rail hidden aria-label="Espaço publicitário">
  <div class="section-container">
    <p class="site-ad-rail__label" data-ad-label>Publicidade</p>
    <div class="site-ad-rail__slot" data-ad-slot="content"></div>
  </div>
</div>"""


def render_marketing_body(depth: int, cfg: dict | None = None) -> str:
    """Config path + deferred loader."""
    cfg = cfg or load_marketing_config()
    if not cfg.get("enabled"):
        return ""
    prefix = rel_prefix(depth)
    config_path = f"{prefix}assets/data/marketing-config.json"
    return f"""
<script type="application/json" id="marketing-config-path">{json.dumps(config_path)}</script>
<script src="{esc(prefix)}assets/js/marketing.js" defer></script>"""
