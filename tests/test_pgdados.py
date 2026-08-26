"""PGDADOS official catalog, quality dimensions, COREN/COFEN without invented REST."""

import json

from engine.agents import run_extraction
from engine.generate import build
from engine.paths import ROOT


def test_pgdados_catalog_and_coren_has_no_rest_api():
    run_extraction(network=False)
    build()
    agencies = json.loads((ROOT / "cko_md" / "agency_registry.json").read_text(encoding="utf-8"))
    by_key = {item["business_key"]: item for item in agencies["agencies"]}
    assert by_key["AGY-COREN-SP"]["rest_api"] == "NOT_OBSERVED"
    assert by_key["AGY-COFEN"]["rest_api"] == "NOT_OBSERVED"
    assert "AGY-SGD" in by_key
    assert "AGY-MGI" in by_key
    assert all(item.get("uuid") is None for item in agencies["agencies"])

    pgd = json.loads((ROOT / "cko_md" / "pgdados_program.json").read_text(encoding="utf-8"))
    assert pgd["uuid"] is None
    assert pgd["publication"] == "HOLD"
    assert pgd["clause_text"] == "NOT_COPIED_AS_PRODUCT_RULE"
    parts = {item.get("part"): item for item in pgd.get("guia_parts") or []}
    assert 1 in parts and 2 in parts
    assert parts[3]["status"] == "EVIDENCE_PENDING"
    assert parts[3].get("url") is None
    vols = {item.get("volume"): item for item in pgd.get("cartilhas") or []}
    assert 1 in vols and 2 in vols and 3 in vols
    assert vols[1].get("url", "").endswith(".pdf")
    assert "gov.br" in (vols[1].get("url") or "")
    assert vols[4]["status"] == "EVIDENCE_PENDING"
    assert vols[5]["status"] == "EVIDENCE_PENDING"
    blob = json.dumps(pgd)
    assert "mwpt.com.br" not in blob
    assert "abnt-nbr" not in blob.lower()
    dims = pgd.get("quality_dimensions") or []
    assert len(dims) == 7
    assert all(item.get("clause_text") == "NOT_COPIED_AS_PRODUCT_RULE" for item in dims)
    dq = pgd.get("data_quality_dimensions") or []
    assert [item["name"] for item in dq] == [
        "integridade",
        "padronização",
        "precisão",
        "acurácia",
        "atualização",
        "acessibilidade",
        "confiabilidade",
    ]
    assert pgd["glossary_url"].endswith("glossario-de-termos-de-dados")
    assert len(pgd.get("implementation_instruments") or []) == 3
    iso = json.loads((ROOT / "cko_md" / "iso8000_profile.json").read_text(encoding="utf-8"))
    bind = json.loads((ROOT / "cko_md" / "iso8000_pgdados_binding.json").read_text(encoding="utf-8"))
    assert iso["iso_implemented"] is False
    assert iso["certified"] is False
    assert bind["pgdados_ref"] == "MD-PGDADOS-001"
    assert all(item.get("replaces_iso_clause") is False for item in bind["links"])
    mdm = (ROOT / "render" / "fetch" / "admin" / "mdm.html").read_text(encoding="utf-8")
    assert "Vínculo ISO 8000 CKO → PGDADOS" in mdm
    assert "FLD-PGDADOS-QD-INTEGRIDADE" in mdm
    assert "glossario-de-termos-de-dados" in mdm

    html = (ROOT / "render" / "fetch" / "biblioteca.html").read_text(encoding="utf-8")
    assert "PGDADOS" in html
    assert "governancadedados/pgdados" in html
    assert "INS-DEC-10046-2019" in html or "10.046" in html
    assert "adsbygoogle" not in html
    assert "mwpt.com.br" not in html
    admin = (ROOT / "render" / "fetch" / "admin" / "apis.html").read_text(encoding="utf-8")
    assert "sem REST" in admin or "COREN-SP" in admin
    api_reg = json.loads((ROOT / "cko_assurance" / "api_registry.json").read_text(encoding="utf-8"))
    coren = next(item for item in api_reg["apis"] if item["business_key"] == "API-CAND-COREN")
    assert coren["base_url"] is None
    assert coren["rest_api"] == "NOT_OBSERVED"
    cofen = next(item for item in api_reg["apis"] if item["business_key"] == "API-CAND-COFEN")
    assert cofen["base_url"] is None
