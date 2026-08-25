"""ISO 8000 CKO profile bound to PGDADOS. Not certification."""

import json

from engine.iso8000 import (
    DATA_QUALITY_DIMENSIONS,
    compose_binding,
    compose_field_dictionary,
    evaluate_profile,
)
from engine.paths import ROOT


def test_compose_dictionary_binds_every_field_to_pgdados():
    payload = compose_field_dictionary()
    assert payload["certified"] is False
    assert payload["iso_implemented"] is False
    assert payload["population"] == len(payload["fields"])
    assert payload["population"] >= 27
    keys = [item["business_key"] for item in payload["fields"]]
    assert len(keys) == len(set(keys))
    assert "FLD-ISO8000-IDENTITY-BK" in keys
    assert "FLD-PGDADOS-PLANO" in keys
    for field in payload["fields"]:
        assert field["pgdados_ref"] == "MD-PGDADOS-001"
        assert field["iso_clause_text"] == "CLAUSE_TEXT_UNAVAILABLE"
        assert field["pgdados_clause_text"] == "NOT_COPIED_AS_PRODUCT_RULE"
        assert field["iso_test_id"].startswith("ISO8000-CKO-")


def test_binding_does_not_replace_iso_clause():
    fields = compose_field_dictionary()["fields"]
    binding = compose_binding(fields)
    assert binding["business_key"] == "MD-ISO8000-PGDADOS-BIND-001"
    assert [item["name"] for item in binding["data_quality_dimensions"]] == list(DATA_QUALITY_DIMENSIONS)
    assert len(binding["instruments"]) == 3
    assert all(item["replaces_iso_clause"] is False for item in binding["links"])
    assert "ISO 8000 certified" not in json.dumps(binding)


def test_evaluate_profile_writes_binding_without_cert_claim():
    result = evaluate_profile()
    assert result["certified"] is False
    assert result["iso_implemented"] is False
    assert result["status"] in {"PASS_PROFILE_ONLY", "HOLD"}
    assert result["clause_text"] == "CLAUSE_TEXT_UNAVAILABLE"
    ids = {item["id"]: item["status"] for item in result["tests"]}
    assert ids["ISO8000-CKO-NO-CERT-CLAIM"] == "PASS"
    assert ids["ISO8000-CKO-PGDADOS-BINDING"] == "PASS"
    assert ids["ISO8000-CKO-PGDADOS-QUALITY-DIMS"] == "PASS"
    profile = json.loads((ROOT / "cko_md" / "iso8000_profile.json").read_text(encoding="utf-8"))
    assert profile["iso_implemented"] is False
    assert "ISO 8000 certified" not in json.dumps(profile)
