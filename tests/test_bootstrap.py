"""Day-zero Layer Registry and admin↔frontend contract tests."""

import json

from engine.bootstrap import evaluate_layer_registry, layer_records, write_registries
from engine.generate import build, generate_admin
from engine.paths import ADMIN_DIR, ROOT
from validators.clinical_completeness import evaluate_catalog
from validators.dual_render import check_parity
from validators.release_gate import evaluate_release


def test_layer_population_is_44_with_unique_business_keys():
    layers = layer_records()
    keys = [item["business_key"] for item in layers]
    assert len(layers) == 44
    assert len(set(keys)) == 44
    assert keys[0] == "LAYER-010"
    assert keys[-1] == "LAYER-440"


def test_uuid_is_null_and_md_precedes_reg_on_every_layer():
    for item in layer_records():
        assert item["uuid"] is None
        assert item["canonical_id"] is None
        assert item["md_profile_ref"] == f"{item['business_key']}-MD"
        assert item["reg_profile_ref"] == f"{item['business_key']}-REG"
        assert item["maturity"] == "M0_REGISTERED"
        assert item["populated"] is False
        assert item["implemented"] is False
        assert item["assured"] is False


def test_write_registries_and_layer_caat():
    written = write_registries()
    names = {path.name for path in written}
    assert "layer_registry.json" in names
    assert "contract.json" in names
    result = evaluate_layer_registry()
    assert result["population"] == 44
    assert result["tested"] == 44
    assert result["failed"] == 0
    assert result["status"] == "PASS"
    payload = json.loads((ROOT / "cko_core" / "layer_registry.json").read_text(encoding="utf-8"))
    assert payload["population"] == 44
    contract = json.loads((ADMIN_DIR / "contract.json").read_text(encoding="utf-8"))
    assert contract["frontend"]["writes_canonical"] is False
    assert "ADMIN_WRITE_FORMULA" in contract["events"]["forbidden"]
    md_profiles = json.loads((ROOT / "cko_core" / "layer_md_profiles.json").read_text(encoding="utf-8"))
    reg_profiles = json.loads((ROOT / "cko_core" / "layer_reg_profiles.json").read_text(encoding="utf-8"))
    assert md_profiles["population"] == 44
    assert reg_profiles["population"] == 44


def test_admin_page_projects_layers_and_contract():
    write_registries()
    contract = json.loads((ADMIN_DIR / "contract.json").read_text(encoding="utf-8"))
    html = generate_admin(
        [{"slug": "gotejamento", "kind": "calculator", "status": "review", "overview": {"name": "Gotejamento"}}],
        {"status": "HOLD"},
        layer_records(),
        contract,
        css_href="assets/app.css",
        home_href="index.html",
        inline_css=False,
    )
    assert "Layer Registry (44)" in html
    assert "LAYER-010-MD" in html
    assert "LAYER-010-REG" in html
    assert "SHARED_GITHUB_CONTRACTS" in html
    assert "PRIV-NO-SENSITIVE-CAPTURE" in html
    assert 'id="admin-contract"' in html


def test_build_writes_admin_and_keeps_release_hold():
    written = build()
    names = {path.name for path in written}
    assert "admin.html" in names
    fetch_admin = (ROOT / "render" / "fetch" / "admin.html").read_text(encoding="utf-8")
    inline_admin = (ROOT / "render" / "inline" / "admin.html").read_text(encoding="utf-8")
    assert "CKO-MD" in fetch_admin
    assert "Clinical Calculators" in fetch_admin
    assert "Admin" in (ROOT / "render" / "fetch" / "index.html").read_text(encoding="utf-8")
    fetch_json = (ROOT / "render" / "fetch" / "admin" / "layer_registry.json").read_text(encoding="utf-8")
    assert json.loads(fetch_json)["population"] == 44
    assert (ROOT / "render" / "inline" / "admin" / "contract.json").exists()
    parity = check_parity()
    assert parity["status"] == "PASS"
    completeness = evaluate_catalog()
    release = evaluate_release(completeness, parity)
    assert release["status"] == "HOLD"
