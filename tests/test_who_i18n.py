"""WHO/OMS modulates international i18n envelopes. Not a translation engine."""

import json

from engine.generate import build
from engine.iso8000 import compose_field_dictionary, evaluate_profile
from engine.paths import ROOT
from engine.who_i18n import (
    WHO_OFFICIAL_SELECTOR,
    compose_who_i18n,
    evaluate_who_i18n,
    runtime_who_local_key,
    who_local_key,
    who_official_codes,
)


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
        "FLD-I18N-WHO-LOCAL-KEY",
        "FLD-I18N-LOCAL-VARIANT",
        "FLD-I18N-PAHO-PT",
    ):
        assert key in keys
    who_fields = [item for item in compose_field_dictionary()["fields"] if item["business_key"].startswith("FLD-I18N-")]
    assert len(who_fields) == 10
    for field in who_fields:
        assert field["iso_test_id"] == "ISO8000-CKO-WHO-I18N"
        assert field["pgdados_term"] == "Interoperabilidade"
        assert field["iso_clause_text"] == "CLAUSE_TEXT_UNAVAILABLE"
        assert field["certified"] is False


def test_who_i18n_holds_translation_and_forbids_dumps():
    result = evaluate_who_i18n()
    assert result["agent_id"] == "AG-WHO-I18N"
    assert result["status"] == "HOLD"
    assert result["owner_decision"] == "APPROVED"
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
    assert "Não inferir pt → pt-BR nem pt-PT → pt-BR nem pt-AO → pt-BR." in payload["rules"]
    assert payload["runtime_who_local_key"] == "who.en+local.pt-BR"
    assert payload["runtime_who_src"] == "en"
    assert who_local_key("en", "pt-PT") == "who.en+local.pt-PT"
    assert runtime_who_local_key() == "who.en+local.pt-BR"
    variants = {item["bcp47"]: item for item in payload["lusophone_variants"]}
    assert variants["pt-BR"]["runtime"] is True
    assert variants["pt-PT"]["runtime"] is False
    assert variants["pt-AO"]["wired_to_frontend"] is False
    assert variants["pt-AO"]["rfc4647_sibling_fallback"] is False
    assert variants["pt-AO"]["adopt_cldr_pt_fallback"] is False
    assert "pt-PT" in payload["lusophone_hold"]
    paho = next(item for item in payload["sources"] if item["business_key"] == "SRC-PAHO-PT")
    assert paho["http_status"] == 200
    assert paho["content_language"] == "pt-br"
    who_pt = next(item for item in payload["sources"] if item["business_key"] == "SRC-WHO-PT-HOME")
    assert who_pt["http_status"] == 404
    design = payload["design_zip"]
    assert design["file_id"] == "1QS84_ws1yhCLCbHdPWyQDdbZoqI2Mo6Z"
    assert design["unzipped"] is False
    assert design["classification"] == "SKIP_BINARY_DUMP"
    lang = json.loads((ROOT / "cko_md" / "language_locale_registry.json").read_text(encoding="utf-8"))
    assert lang["runtime_who_local_key"] == "who.en+local.pt-BR"
    assert lang["adopt_cldr_pt_fallback"] is False
    i18n = json.loads((ROOT / "cko_reg" / "i18n_profile.json").read_text(encoding="utf-8"))
    assert i18n["runtime_who_local_key"] == "who.en+local.pt-BR"


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
    assert 'data-owner-i18n="APPROVED"' in home
    assert 'data-who-official="en,ar,zh,fr,ru,es"' in home
    assert 'data-who-local-key="who.en+local.pt-BR"' in home
    assert 'data-local-bcp47="pt-BR"' in home
    assert 'data-pt-variants="HOLD"' in home
    assert "who.en+local.pt-BR · i18n HOLD" in home
    mdm = (ROOT / "render" / "fetch" / "admin" / "mdm.html").read_text(encoding="utf-8")
    assert "FLD-I18N-WHO-OFFICIAL" in mdm
    assert "FLD-I18N-WHO-LOCAL-KEY" in mdm
    assert "FLD-I18N-LOCAL-VARIANT" in mdm
    assert "FLD-I18N-PAHO-PT" in mdm
    assert "Interoperabilidade" in mdm
    locales = (ROOT / "render" / "fetch" / "admin" / "locales.html").read_text(encoding="utf-8")
    assert "Chave WHO + local" in locales
    assert "who.en+local.pt-PT" in locales
    assert "pt-AO" in locales
    modulation = json.loads((ROOT / "render" / "fetch" / "admin" / "who_i18n_modulation.json").read_text(encoding="utf-8"))
    assert modulation["wired_to_frontend"] is False
    assert compose_who_i18n()["publication"] == "HOLD"
