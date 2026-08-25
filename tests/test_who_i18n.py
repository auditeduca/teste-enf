"""WHO/OMS modulates international i18n envelopes. Not a translation engine."""

import json

from engine.generate import build
from engine.iso8000 import compose_field_dictionary, evaluate_profile
from engine.paths import ROOT
from engine.who_i18n import WHO_OFFICIAL_SELECTOR, compose_who_i18n, evaluate_who_i18n, who_official_codes


def test_who_official_selector_excludes_runtime_pt_br():
    codes = who_official_codes()
    assert codes == {"en", "ar", "zh", "fr", "ru", "es"}
    assert "pt" not in codes
    assert "pt-BR" not in codes
    assert [item["bcp47"] for item in WHO_OFFICIAL_SELECTOR] == ["en", "ar", "zh", "fr", "ru", "es"]


def test_who_fields_bind_pgdados_interoperability_without_iso_clause():
    keys = {item["business_key"] for item in compose_field_dictionary()["fields"]}
    for key in (
        "FLD-I18N-BCP47",
        "FLD-I18N-WHO-OFFICIAL",
        "FLD-I18N-TRANSLATION-OBJECT",
        "FLD-I18N-GHO-INDICATOR",
        "FLD-I18N-ICD-CODE",
        "FLD-I18N-ICNP-CANDIDATE",
        "FLD-I18N-WHO-REGION",
    ):
        assert key in keys
    who_fields = [item for item in compose_field_dictionary()["fields"] if item["business_key"].startswith("FLD-I18N-")]
    assert len(who_fields) == 7
    for field in who_fields:
        assert field["iso_test_id"] == "ISO8000-CKO-WHO-I18N"
        assert field["pgdados_term"] == "Interoperabilidade"
        assert field["iso_clause_text"] == "CLAUSE_TEXT_UNAVAILABLE"
        assert field["certified"] is False


def test_who_i18n_holds_translation_and_forbids_dumps():
    result = evaluate_who_i18n()
    assert result["agent_id"] == "AG-WHO-I18N"
    assert result["status"] == "HOLD"
    assert result["translation_gate"] == "HOLD"
    assert result["wired_to_frontend"] is False
    assert result["promotes_to_md"] is False
    payload = json.loads((ROOT / "cko_md" / "who_i18n_modulation.json").read_text(encoding="utf-8"))
    assert payload["business_key"] == "MD-WHO-I18N-001"
    assert payload["icd_icnp_gho_dump"] == "FORBIDDEN"
    assert payload["drive_intersection"] == ["ar", "en", "es", "fr", "ru", "zh"]
    assert "pt" in payload["drive_only"]
    assert payload["runtime_not_in_who_selector"] is True
    i18n = json.loads((ROOT / "cko_reg" / "i18n_profile.json").read_text(encoding="utf-8"))
    assert i18n["translation_gate"] == "HOLD"
    assert i18n["wired_to_frontend"] is False
    assert i18n["who_ref"] == "MD-WHO-I18N-001"
    assert i18n["display_language_runtime"] == "pt-BR"
    blob = json.dumps(payload)
    assert "ICD-11 License" in blob or "texto não copiado" in blob
    assert "Não inferir pt → pt-BR" in payload["rules"]


def test_iso_profile_includes_who_i18n_test():
    result = evaluate_profile()
    ids = {item["id"]: item["status"] for item in result["tests"]}
    assert ids["ISO8000-CKO-WHO-I18N"] == "PASS"
    assert result["certified"] is False


def test_admin_locales_surfaces_who_overlay_without_wiring_chrome():
    evaluate_who_i18n()
    build()
    locales = (ROOT / "render" / "fetch" / "admin" / "locales.html").read_text(encoding="utf-8")
    assert "Modulação WHO/OMS" in locales
    assert "who.int" in locales
    assert "en, ar, zh, fr, ru, es" in locales or "en, ar, zh, fr, ru, es".replace(" ", "") in locales.replace(" ", "")
    assert "HOLD" in locales
    home = (ROOT / "render" / "fetch" / "index.html").read_text(encoding="utf-8")
    assert 'data-i18n-gate="HOLD"' in home
    assert 'data-who-official="en,ar,zh,fr,ru,es"' in home
    assert "pt-BR · i18n HOLD" in home
    mdm = (ROOT / "render" / "fetch" / "admin" / "mdm.html").read_text(encoding="utf-8")
    assert "FLD-I18N-WHO-OFFICIAL" in mdm
    assert "Interoperabilidade" in mdm
    modulation = json.loads((ROOT / "render" / "fetch" / "admin" / "who_i18n_modulation.json").read_text(encoding="utf-8"))
    assert modulation["wired_to_frontend"] is False
    assert compose_who_i18n()["publication"] == "HOLD"
