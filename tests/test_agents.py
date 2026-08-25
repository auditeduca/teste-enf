"""Extraction agents write inbox inventories. They do not promote HTML to data/tools."""

import json

from engine.agents import run_extraction
from engine.generate import build
from engine.paths import ROOT, TOOLS_DIR
from validators.clinical_completeness import evaluate_catalog
from validators.dual_render import check_parity
from validators.release_gate import evaluate_release


def test_extract_offline_inventories_pages_full_without_promoting_braden():
    run = run_extraction(network=False)
    assert run["publication"] == "HOLD"
    assert run["ipe_reliance"] is False
    assert run["status"] in {"HOLD", "PASS_WITH_FINDINGS"}
    assert [step["agent_id"] for step in run["steps"]] == [
        "AG-FETCH-ORIGIN",
        "AG-FETCH-REGULATED",
        "AG-PARSE-PAGES-FULL",
        "AG-PARSE-SITEMAP",
        "AG-PARSE-CHROME",
        "AG-INTEGRITY",
        "AG-CAAT-EXTRACT",
        "AG-IPE-EXTRACT",
        "AG-LINK-MD",
    ]
    inventory = json.loads((ROOT / "cko_inbox" / "drive" / "pages_full" / "INVENTORY.json").read_text(encoding="utf-8"))
    assert inventory["business_key"] == "MD-PAGE-INV-001"
    assert inventory["quarantine"] is True
    assert inventory["promoted_to_data_tools"] is False
    assert inventory["html_count"] >= 1500
    stems = {item["stem"] for item in inventory["pages"]}
    assert "braden" in stems
    assert not (TOOLS_DIR / "braden.json").exists()
    slugs = {path.stem for path in TOOLS_DIR.glob("*.json")}
    assert slugs == {"gotejamento", "meows", "cinco-ts-pcr", "simulado-tecnico", "dimensionamento"}
    agents = json.loads((ROOT / "cko_assurance" / "agent_registry.json").read_text(encoding="utf-8"))
    assert agents["population"] == 10
    assert agents["implemented"] is True
    assert agents["publication_implemented"] is False
    ipe = json.loads((ROOT / "cko_inbox" / "extracted" / "ipe_extract.json").read_text(encoding="utf-8"))
    assert ipe["reliance"] is False
    assert ipe["carr"]["RELIABLE"] == "FAIL"
    regulated = json.loads((ROOT / "cko_inbox" / "extracted" / "regulated_pages.json").read_text(encoding="utf-8"))
    assert all(page.get("api_base_url") is None for page in regulated["pages"])
    assert all("adsbygoogle" not in json.dumps(step) for step in run["steps"])


def test_public_chrome_matches_production_contract_without_ads():
    build()
    html = (ROOT / "render" / "fetch" / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "assets" / "css" / "app.css").read_text(encoding="utf-8")
    for token in (
        'id="global-header-container"',
        'id="language-selector-placeholder"',
        'id="footer-placeholder"',
        'id="barraAcessibilidade"',
        "icontopbar1-calculadoras-de-enfermagem.webp",
        "iconrodape1-80-calculadoras-de-enfermagem.webp",
        "Navegação Principal",
        "pt-BR · i18n HOLD",
    ):
        assert token in html
    assert "--header-height: 96px" in css
    assert "--lang-height: 46px" in css
    assert "cdn.jsdelivr" not in html.lower()
    assert "googleapis" not in html.lower()
    assert "adsbygoogle" not in html
    assert 'type="email"' not in html
    assert "opendyslexic" not in html.lower()
    assert (ROOT / "assets" / "fonts" / "inter" / "inter-regular.woff2").exists()
    assert (ROOT / "assets" / "fonts" / "nunito" / "nunito-700.woff2").exists()
    parity = check_parity()
    assert parity["status"] == "PASS"
    release = evaluate_release(evaluate_catalog(), parity)
    assert release["status"] == "HOLD"
