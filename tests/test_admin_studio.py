"""Admin Studio modules, Studio CMS quarantine, and control plane."""

import json

from engine.admin_site import inventory_tables, studio_map
from engine.control_plane import git_status, is_loopback, prepare_deploy
from engine.generate import build
from engine.paths import ROOT
from validators.dual_render import check_parity
from validators.release_gate import evaluate_release
from validators.clinical_completeness import evaluate_catalog


def test_studio_map_is_quarantined_not_published():
    studio = studio_map()
    assert studio["quarantine"] is True
    assert studio["epistemic_status"] == "SOURCE_DERIVED"
    assert studio["images_in_conversation"]["status"] == "NOT_FOUND"
    braden = next(item for item in studio["tabela_itens_logicos"] if item["id_logico"] == "BRADEN")
    assert braden["cko_status"] == "QUARANTINED"
    assert braden["in_data_tools"] is False
    assert braden["uuid"] is None
    slugs = {path.stem for path in (ROOT / "data" / "tools").glob("*.json")}
    assert "braden" not in slugs
    assert studio["visao_geral_item"]["qualidade_conteudo"]["epistemic_status"] == "DOCUMENT_CLAIM"


def test_build_emits_admin_modules_and_keeps_release_hold():
    written = build()
    names = {path.name for path in written}
    for name in (
        "admin.html",
        "database.html",
        "catalog.html",
        "pipeline.html",
        "layers.html",
        "validations.html",
        "agents.html",
        "monitoring.html",
        "library.html",
        "apis.html",
        "backlog.html",
        "design-system.html",
        "locales.html",
        "mdm.html",
        "frameworks.html",
        "maturity.html",
        "renderer.html",
        "deploy.html",
        "studio_cms_map.v1.json",
        "mockup_reference_map.v1.json",
        "locale_registry.json",
        "design_token_registry.json",
        "admin-control.js",
        "a11y.js",
        "logotipo-calculadoras-de-enfermagem.webp",
        "icontopbar1-calculadoras-de-enfermagem.webp",
        "iconrodape1-80-calculadoras-de-enfermagem.webp",
    ):
        assert name in names
    fetch_admin = (ROOT / "render" / "fetch" / "admin.html").read_text(encoding="utf-8")
    catalog = (ROOT / "render" / "fetch" / "admin" / "catalog.html").read_text(encoding="utf-8")
    design = (ROOT / "render" / "fetch" / "admin" / "design-system.html").read_text(encoding="utf-8")
    deploy = (ROOT / "render" / "fetch" / "admin" / "deploy.html").read_text(encoding="utf-8")
    database = (ROOT / "render" / "fetch" / "admin" / "database.html").read_text(encoding="utf-8")
    locales = (ROOT / "render" / "fetch" / "admin" / "locales.html").read_text(encoding="utf-8")
    maturity = (ROOT / "render" / "fetch" / "admin" / "maturity.html").read_text(encoding="utf-8")
    frameworks = (ROOT / "render" / "fetch" / "admin" / "frameworks.html").read_text(encoding="utf-8")
    fetch_index = (ROOT / "render" / "fetch" / "index.html").read_text(encoding="utf-8")
    assert "CKO Studio" in fetch_admin
    assert 'id="barraAcessibilidade"' in fetch_admin
    assert 'id="barraAcessibilidade"' in fetch_index
    assert 'id="global-header-container"' in fetch_index
    assert 'id="language-selector-placeholder"' in fetch_index
    assert 'id="footer-placeholder"' in fetch_index
    assert "adsbygoogle" not in fetch_index
    assert "googleads" not in fetch_index.lower()
    assert 'type="email"' not in fetch_index
    assert "--header-bg: #ffffff" in (ROOT / "assets" / "css" / "app.css").read_text(encoding="utf-8")
    assert "cdn.jsdelivr" not in fetch_index.lower()
    assert "googleapis" not in fetch_index.lower()
    assert "Layer Registry (44)" in fetch_admin
    assert "QUARANTINED" in catalog
    assert "STUDIO-CAND-BRADEN" in catalog
    assert "SOURCE_DERIVED" in design
    assert "RESTORED" in design
    assert "EVIDENCE_PENDING" in design
    assert "git push é FORBIDDEN" in deploy
    assert "Nenhuma alteração de RLS" in database
    assert "MD-LOCALE-REG-001" in locales or "19" in locales
    assert "SOURCE_DERIVED" in locales
    assert "HOLD" in maturity
    assert "CLAUSE_TEXT_UNAVAILABLE" in frameworks
    assert "cdn.jsdelivr" not in fetch_admin.lower()
    parity = check_parity()
    assert parity["status"] == "PASS"
    release = evaluate_release(evaluate_catalog(), parity)
    assert release["status"] == "HOLD"


def test_drive_locales_are_source_derived_not_wired():
    locales = json.loads((ROOT / "cko_md" / "locale_registry.json").read_text(encoding="utf-8"))
    assert locales["business_key"] == "MD-LOCALE-REG-001"
    assert locales["population"] == 19
    assert locales["stems_only"] == ["cookies", "footer"]
    assert locales["related_to"] == "MD-LANG-LOC-001"
    assert all(item["wired_to_frontend"] is False for item in locales["locales"])
    assert (ROOT / "cko_inbox" / "drive" / "locales" / "pt" / "footer.json").exists()
    assert not (ROOT / "data" / "tools" / "braden.json").exists()


def test_maturity_panorama_is_hold_without_fake_pass():
    from engine.bootstrap import write_registries
    from engine.maturity import evaluate_maturity

    write_registries()
    panorama = evaluate_maturity()
    assert panorama["release"] == "HOLD"
    assert panorama["layers"]["population"] == 44
    assert panorama["agents"]["population"] == 27
    assert panorama["agents"]["implemented"] is True
    assert panorama["agents"]["publication_implemented"] is False
    assert panorama["ipe"]["registry_implemented"] is False
    assert panorama["domain_candidates"]["braden_in_data_tools"] is False
    assert "APO12.01" not in json.dumps(panorama)


def test_mockups_are_layout_language_only():
    mockups = json.loads((ROOT / "admin" / "mockup_reference_map.v1.json").read_text(encoding="utf-8"))
    assert mockups["quarantine"] is True
    assert mockups["use"] == "LAYOUT_LANGUAGE_ONLY"
    assert "98%" in mockups["forbidden_to_copy"][0]


def test_control_plane_git_status_and_prepare_does_not_push():
    status = git_status()
    assert status["push"] == "FORBIDDEN"
    assert status["epistemic_status"] == "OBSERVED"
    prepared = prepare_deploy()
    assert prepared["push"] == "FORBIDDEN"
    assert prepared["uuid"] is None
    path = ROOT / prepared["path"]
    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["action"] == "DEPLOY_PREPARE"
    assert is_loopback("127.0.0.1")
    assert not is_loopback("8.8.8.8")


def test_github_json_inventory_is_non_empty():
    rows = inventory_tables()
    paths = {item["path"] for item in rows}
    assert "cko_core/layer_registry.json" in paths
    assert "cko_md/locale_registry.json" in paths
    assert "cko_md/entity_type_registry.json" in paths
    assert "cko_reg/authority_classes.json" in paths
    assert any(item["schema"] == "domain_candidate" for item in rows)
