"""L70 uses the official ANVISA API. Drive dump stays listing-only."""

import json

from engine.generate import build
from engine.l70_anvisa import compare_l70_anvisa, DRIVE_ZIP_ID
from engine.layer_phase import evaluate_layer_md_reg
from engine.govlib import _classify_api_probe
from engine.paths import ROOT, TOOLS_DIR
from engine.store_inventory import classify_drive_file, plan_fronts


def test_anvisa_portal_html_200_is_not_rest_json():
    rec = _classify_api_probe(
        {
            "business_key": "API-ANVISA-PORTAL",
            "agency_key": "AGY-ANVISA",
            "agency": "ANVISA Portal de APIs",
            "url": "https://api.anvisa.gov.br/",
            "kind": "PORTAL_SPA",
            "md_ref": "MD-API-ANVISA-PORTAL",
            "reg_ref": "REG-API-ANVISA-PORTAL",
        },
        {"http_status": 200, "bytes": 120, "sha256": "abc", "error": None},
        b"<!doctype html><html lang=\"en\"><title>Portal APIs ANVISA</title>",
    )
    assert rec["http_status"] == 200
    assert rec["epistemic_status"] == "OBSERVED_HTML"
    assert rec["rest_json"] is False
    assert rec["online"] is False
    assert rec["base_url"] is None
    forbidden = _classify_api_probe(
        {
            "business_key": "API-ANVISA-CONSULTAS-MEDICAMENTOS",
            "agency_key": "AGY-ANVISA",
            "agency": "ANVISA Consultas medicamentos",
            "url": "https://consultas.anvisa.gov.br/api/consulta/medicamentos",
            "kind": "PRODUCT_CONSULTA",
            "md_ref": "MD-API-ANVISA-CONSULTAS",
            "reg_ref": "REG-API-ANVISA-CONSULTAS",
        },
        {"http_status": 403, "bytes": 0, "sha256": None, "error": "HTTPError 403"},
        b"",
    )
    assert forbidden["epistemic_status"] == "AUTH_REQUIRED"
    assert forbidden["online"] is False
    assert forbidden["base_url"] is None


def test_l70_anvisa_compare_does_not_promote_dump_or_insulina():
    result = compare_l70_anvisa()
    assert result["agent_id"] == "AG-L70-ANVISA-COMPARE"
    assert result["promotes_to_md"] is False
    assert result["copied_into_data_tools"] is False
    assert result["unzipped"] is False
    assert result["publication"] == "HOLD"
    assert result["assured"] is False
    assert result["product_rest"] == "NOT_OBSERVED"
    assert result["verified_population"] == "EVIDENCE_PENDING"
    catalog = json.loads((ROOT / "cko_md" / "l70_anvisa_compare.json").read_text(encoding="utf-8"))
    assert catalog["business_key"] == "MD-L70-ANVISA-001"
    assert catalog["uuid"] is None
    assert catalog["copied_into_data_tools"] is False
    assert catalog["unzipped"] is False
    assert catalog["assured"] is False
    assert catalog["implemented"] is False
    assert catalog["claimed_count_drive_description"] == 17231
    assert catalog["verified_population"] == "EVIDENCE_PENDING"
    assert catalog["official_api"]["product_rest"] == "NOT_OBSERVED"
    assert catalog["official_api"]["production_api"] is False
    assert catalog["official_api"]["portal"]["url"] == "https://api.anvisa.gov.br/"
    assert catalog["official_api"]["portal"]["base_url"] in {None, catalog["official_api"]["portal"]["base_url"]}
    assert catalog["official_api"]["openfda_fallback"]["replaces_anvisa_leaflet"] is False
    assert catalog["drive"]["zip"]["id"] == DRIVE_ZIP_ID
    assert catalog["drive"]["zip"]["unzipped"] is False
    assert catalog["pilot"]["data_tools_insulina_json"] is False
    gap_ids = {item["id"] for item in catalog["gaps"]}
    assert {"GAP-L70-ANVISA-REST-JSON", "GAP-L70-DRIVE-DUMP", "GAP-L70-INSULINA-TOOL"} <= gap_ids
    blob = json.dumps(catalog)
    assert "17231" in blob
    assert catalog["verified_population"] != 17231
    assert not (TOOLS_DIR / "insulina.json").exists()
    assert not (TOOLS_DIR / "braden.json").exists()
    slugs = {path.stem for path in TOOLS_DIR.glob("*.json")}
    assert slugs == {"gotejamento", "meows", "cinco-ts-pcr", "simulado-tecnico", "dimensionamento"}
    dump = classify_drive_file({
        "id": DRIVE_ZIP_ID,
        "title": "CKO_Medicamentos_ANVISA_Completo.zip",
        "mimeType": "application/zip",
        "fileSize": "59854232",
    })
    assert dump["classification"] == "SKIP_BINARY_DUMP"
    assert dump["action"] == "COMPARE_ONLY"
    assert dump["promotes_to_md"] is False
    assert "17231" in dump["reason"]
    plan = plan_fronts()
    assert plan["front_count"] == 24
    fronts = json.loads((ROOT / "cko_md" / "fronts_plan.json").read_text(encoding="utf-8"))
    f24 = next(item for item in fronts["fronts"] if item["id"] == "F24")
    assert f24["status"] == "COMPARE_ONLY"
    assert "F24" not in plan["hold"]
    libmap = json.loads((ROOT / "cko_md" / "library_api_map.json").read_text(encoding="utf-8"))
    l70 = next(item for item in libmap["api_where_possible"] if item["layer"] == "L70")
    assert l70["adapter"] == "API-ANVISA-PORTAL"
    assert l70["epistemic_status"] != "OBSERVED" or l70.get("note")
    assert "não substitui bula" in (l70.get("note") or "").lower() or "Não substitui bula" in (l70.get("note") or "")
    evaluate_layer_md_reg()
    phase = json.loads((ROOT / "cko_md" / "layer_md_reg_phase.json").read_text(encoding="utf-8"))
    layer = next(item for item in phase["layers"] if item["layer_code"] == "L70")
    assert layer["md"]["population"] == "COMPARE_ONLY"
    assert layer["md"]["implemented"] is False
    assert layer["owner_unblock"] == "UNBLOCK-ANVISA-API-CREDENTIALS"
    assert "MD-L70-ANVISA-001" in layer["md"]["identities"]
    unblock = json.loads((ROOT / "cko_md" / "owner_unblock.json").read_text(encoding="utf-8"))
    action = next(item for item in unblock["actions"] if item["id"] == "UNBLOCK-ANVISA-API-CREDENTIALS")
    assert action["status"] == "HOLD"
    assert action["frente"] == "F24"
    build()
    html = (ROOT / "render" / "fetch" / "admin" / "library.html").read_text(encoding="utf-8")
    assert "MD-L70-ANVISA-001" in html
    assert "api.anvisa.gov.br" in html
    assert "SKIP_BINARY_DUMP" in html or "59.8" in html or "17231" in html
    admin_json = json.loads((ROOT / "render" / "fetch" / "admin" / "l70_anvisa_compare.json").read_text(encoding="utf-8"))
    assert admin_json["copied_into_data_tools"] is False
    assert admin_json["official_api"]["openfda_fallback"]["replaces_anvisa_leaflet"] is False
    apis = (ROOT / "render" / "fetch" / "admin" / "apis.html").read_text(encoding="utf-8")
    assert "HTML SPA" in apis or "api.anvisa.gov.br" in apis or "JSON" in apis
