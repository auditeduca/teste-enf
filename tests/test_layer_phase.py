"""MD+REG envelopes for all 44 layers are phased from evidence. Not a completeness claim."""

import json

from engine.generate import build
from engine.layer_phase import compose_layer_md_reg_phase, evaluate_layer_md_reg
from engine.paths import ROOT, TOOLS_DIR


def test_all_44_envelopes_complete_none_assured():
    result = evaluate_layer_md_reg()
    assert result["agent_id"] == "AG-LAYER-PHASE"
    assert result["envelope_complete"] == 44
    assert result["assured"] is False
    assert result["publication"] == "HOLD"
    assert result["promotes_to_md"] is False
    catalog = json.loads((ROOT / "cko_md" / "layer_md_reg_phase.json").read_text(encoding="utf-8"))
    assert catalog["business_key"] == "MD-LAYER-PHASE-001"
    assert catalog["population"] == 44
    assert catalog["counts"]["envelope_complete"] == 44
    assert catalog["counts"]["assured"] == 0
    assert catalog["braden_in_data_tools"] is False
    assert catalog["layer_records_remain_m0"] is True
    codes = [item["layer_code"] for item in catalog["layers"]]
    assert codes[0] == "L10"
    assert codes[-1] == "L440"
    assert len(set(codes)) == 44
    for row in catalog["layers"]:
        assert row["envelope_complete"] is True
        assert row["md"]["assured"] is False
        assert row["reg"]["assured"] is False
        assert row["reg"]["clause_text"] == "CLAUSE_TEXT_UNAVAILABLE"
        assert row["publication"] == "HOLD"
        assert row["uuid"] is None
    phases = {item["id"] for item in catalog["phases"]}
    assert phases == {"P0", "P1", "P2", "P3", "P4", "P5"}
    phased = [code for item in catalog["phases"] for code in item["layers"]]
    assert sorted(phased) == sorted(codes)
    assert len(phased) == 44
    registry = json.loads((ROOT / "cko_core" / "layer_registry.json").read_text(encoding="utf-8"))
    assert all(item.get("populated") is False for item in registry["layers"])
    assert all(item.get("maturity") == "M0_REGISTERED" for item in registry["layers"])
    by_code = {item["layer_code"]: item for item in catalog["layers"]}
    assert by_code["L10"]["phase"] == "P0"
    assert by_code["L30"]["md"]["implemented"] is True
    assert by_code["L40"]["do_not"].startswith("Copiar braden")
    assert by_code["L120"]["owner_unblock"] == "UNBLOCK-NNN-LICENSE"
    assert by_code["L70"]["md"]["population"] == "COMPARE_ONLY"
    assert by_code["L70"]["owner_unblock"] == "UNBLOCK-ANVISA-API-CREDENTIALS"
    assert not (TOOLS_DIR / "insulina.json").exists()
    assert by_code["L310"]["md"]["identities"][0] == "who.en+local.pt-BR"
    assert by_code["L430"]["reg"]["population"] == "HOLD"
    assert not (TOOLS_DIR / "braden.json").exists()
    md = json.loads((ROOT / "cko_core" / "layer_md_profiles.json").read_text(encoding="utf-8"))
    reg = json.loads((ROOT / "cko_core" / "layer_reg_profiles.json").read_text(encoding="utf-8"))
    assert md["population"] == 44
    assert reg["population"] == 44
    assert all(item.get("envelope_complete") is True for item in md["profiles"])
    assert all(item.get("clause_text") == "CLAUSE_TEXT_UNAVAILABLE" for item in reg["profiles"])
    assert all(item.get("assured") is False for item in md["profiles"])
    assert compose_layer_md_reg_phase()["assured"] is False


def test_admin_layers_surfaces_phases_without_complete_claim():
    evaluate_layer_md_reg()
    build()
    html = (ROOT / "render" / "fetch" / "admin" / "layers.html").read_text(encoding="utf-8")
    assert "MD + REG faseados" in html
    assert "P0" in html
    assert "L310" in html
    assert "who.en+local.pt-BR" in html or "i18n" in html.lower() or "HOLD" in html
    assert "envelope completo nas 44 ≠ população completa" in html.lower() or "Envelope completo nas 44" in html
    assert "ISO 8000 certified" not in html
    assert "certified=true" not in html.lower()
    blob = json.loads((ROOT / "render" / "fetch" / "admin" / "layer_md_reg_phase.json").read_text(encoding="utf-8"))
    assert blob["counts"]["envelope_complete"] == 44
    assert blob["publication"] == "HOLD"
