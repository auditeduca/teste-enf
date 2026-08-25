"""Congress API federal catalog gate. Enacted LCP allowed; PLP blocked; DEC-n regulatory; revoked usable for tools."""

import json

from engine.congress import classify_tipo
from engine.paths import ROOT


def test_force_of_law_gate_blocks_plp_and_allows_enacted_lcp_and_lei():
    lei = classify_tipo(sigla="LEI-n", nome="Lei Numerada", source="senado_tipos_norma")
    assert lei["decision"] == "ALLOW"
    assert lei["force_of_law"] is True
    assert lei["force_of_regulation"] is False

    lcp = classify_tipo(sigla="LCP", nome="Lei Complementar", source="senado_tipos_norma")
    assert lcp["decision"] == "ALLOW"
    assert lcp["force_of_law"] is True

    plp = classify_tipo(sigla="PLP", nome="Projeto de Lei Complementar", source="camara_proposicao")
    assert plp["decision"] == "BLOCK"
    assert plp["force_of_law"] is False

    projeto = classify_tipo(sigla=None, nome="Projeto de Lei Complementar", source="senado_tipos_norma")
    assert projeto["decision"] == "BLOCK"

    req = classify_tipo(sigla="REQ", nome="Requerimento", source="camara_siglaTipo")
    assert req["decision"] == "BLOCK"

    consulta = classify_tipo(sigla="CON", nome="Consulta", source="camara_siglaTipo")
    assert consulta["decision"] == "BLOCK"

    cf = classify_tipo(sigla="CON-v", nome="Constituição Federal Vigente", source="senado_tipos_norma")
    assert cf["decision"] == "ALLOW"


def test_regulatory_decree_numbered_allowed_unsigned_blocked():
    dec = classify_tipo(sigla="DEC", nome="Decreto", source="senado_tipos_norma")
    assert dec["decision"] == "ALLOW"
    assert dec["force_of_law"] is False
    assert dec["force_of_regulation"] is True
    assert dec["legal_effect"] == "REGULATORY"

    dec_n = classify_tipo(sigla="DEC-n", nome="Decreto Numerado", source="senado_tipos_norma")
    assert dec_n["decision"] == "ALLOW"
    assert dec_n["force_of_law"] is False
    assert dec_n["force_of_regulation"] is True

    dec_sn = classify_tipo(sigla="DEC-sn", nome="Decreto não Numerado", source="senado_tipos_norma")
    assert dec_sn["decision"] == "BLOCK"
    assert dec_sn["force_of_regulation"] is False

    dec_cl = classify_tipo(sigla="DEC-cl", nome="Decreto com Letra", source="senado_tipos_norma")
    assert dec_cl["decision"] == "BLOCK"

    pdc = classify_tipo(sigla="PDC", nome="Projeto de Decreto Legislativo", source="camara_siglaTipo")
    assert pdc["decision"] == "BLOCK"


def test_extract_offline_writes_legislation_md_reg_without_inventing_uuid():
    from engine.agents import run_extraction
    from engine.generate import build

    run = run_extraction(network=False)
    step_ids = [step["agent_id"] for step in run["steps"]]
    assert "AG-PROBE-CONGRESS-API" in step_ids
    assert "AG-FETCH-FEDERAL-LEGISLATION" in step_ids
    leg_step = next(step for step in run["steps"] if step["agent_id"] == "AG-FETCH-FEDERAL-LEGISLATION")
    assert leg_step.get("promotes_to_md") is False
    assert leg_step.get("publication") == "HOLD"

    md = json.loads((ROOT / "cko_md" / "legislation_instrument_registry.json").read_text(encoding="utf-8"))
    reg = json.loads((ROOT / "cko_reg" / "legislation_qualification.json").read_text(encoding="utf-8"))
    assert md["uuid"] is None
    assert md["publication"] if "publication" in md else True
    assert all(item.get("uuid") is None for item in md.get("instruments") or [])
    assert all(item.get("clause_text") == "NOT_COPIED_AS_PRODUCT_RULE" for item in md.get("instruments") or [])
    assert all(item.get("md_ref") and item.get("reg_ref") for item in reg.get("qualifications") or [])
    assert "PLP" in (reg.get("block_siglas") or [])
    assert "LCP" in (reg.get("allow_siglas") or [])
    assert "DEC-n" in (reg.get("allow_siglas") or [])
    assert "DEC-sn" not in (reg.get("allow_siglas") or [])
    keys = {item.get("business_key") for item in md.get("instruments") or []}
    assert "INS-DEC-7508-2011" in keys
    dec = next(item for item in md["instruments"] if item["business_key"] == "INS-DEC-7508-2011")
    assert dec.get("force_of_law") is False
    assert dec.get("force_of_regulation") is True
    assert dec.get("issuer") == "Presidência da República"
    assert "LEG.BR." not in (dec.get("business_key") or "")
    for item in md.get("instruments") or []:
        if item.get("revoked"):
            assert item.get("business_key")
            links = json.loads((ROOT / "cko_md" / "legislation_tool_links.json").read_text(encoding="utf-8"))
            revoked_links = [lnk for lnk in links.get("links") or [] if lnk.get("instrument_ref") == item["business_key"]]
            assert all(lnk.get("current_applicability") is False for lnk in revoked_links)

    ops = json.loads((ROOT / "cko_md" / "operating_method.json").read_text(encoding="utf-8"))
    assert ops["uuid"] is None
    assert ops["method"].startswith("RECOVER")
    assert ops["publication"] == "HOLD"

    build()
    admin_api = (ROOT / "render" / "fetch" / "admin" / "apis.html").read_text(encoding="utf-8")
    assert "força de lei" in admin_api.lower() or "PLP" in admin_api
    assert "Nenhuma alteração de RLS" in admin_api
    assert "adsbygoogle" not in admin_api
    biblioteca = (ROOT / "render" / "fetch" / "biblioteca.html").read_text(encoding="utf-8")
    assert "INS-DEC-7508-2011" in biblioteca
    assert "7.508" in biblioteca
    assert "adsbygoogle" not in biblioteca
