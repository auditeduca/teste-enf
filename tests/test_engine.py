import json
from pathlib import Path

import pytest

from engine.score import compute, format_result, interpret, safe_eval
from engine.validate import load_tool, validate_tool, validate_tools_dir
from engine.generate import generate_tool_page, build
from engine.paths import TOOLS_DIR, ROOT
from validators.clinical_completeness import evaluate_catalog, evaluate_object
from validators.dual_render import check_parity
from validators.release_gate import evaluate_release


def _tool(slug: str):
    return load_tool(TOOLS_DIR / f"{slug}.json")


def test_gotejamento_macro_8h():
    tool = _tool("gotejamento")
    total = compute(tool, {"volume": 500, "tempo": 8, "unidade": 60, "fator": 20})
    assert round(total, 2) == 20.83
    assert format_result(tool, total) == "21"
    band = interpret(tool, round(total))
    assert band is not None


def test_gotejamento_micro_1h_equals_ml_per_hour():
    tool = _tool("gotejamento")
    total = compute(tool, {"volume": 100, "tempo": 1, "unidade": 60, "fator": 60})
    assert round(total) == 100


def test_meows_all_zero_is_low():
    tool = _tool("meows")
    total = compute(tool)
    assert total == 0
    assert interpret(tool, total)["riskLevel"] == "low"


def test_meows_alert_example():
    tool = _tool("meows")
    total = compute(tool, {
        "temperatura": "t2h",
        "pas": "s2h",
        "pad": "d0",
        "fc": "fc1h",
        "fr": "fr0",
        "satO2": "sat0",
        "dor": "dor1",
        "consciencia": "c0",
    })
    assert total == 6
    assert interpret(tool, total)["riskLevel"] == "critical"


def test_safe_eval_rejects_names():
    with pytest.raises(ValueError):
        safe_eval("__import__('os').system('id')")


def test_all_tools_match_schema():
    assert validate_tools_dir() == {}


def test_invalid_tool_is_reported():
    errors = validate_tool({"slug": "x"})
    assert errors


def test_catalog_has_five_pilots():
    slugs = {path.stem for path in TOOLS_DIR.glob("*.json")}
    assert slugs == {"gotejamento", "meows", "cinco-ts-pcr", "simulado-tecnico", "dimensionamento"}


def test_dimensionamento_is_hold_without_formula():
    tool = _tool("dimensionamento")
    assert tool["status"] == "hold"
    assert "calculator" not in tool
    with pytest.raises(ValueError):
        compute(tool)


def test_sae_hold_blocks_promotion():
    result = evaluate_object(_tool("gotejamento"))
    assert result["status"] == "HOLD"
    assert result["promotionAllowed"] is False


def test_guide_completeness_not_applicable():
    result = evaluate_object(_tool("cinco-ts-pcr"))
    assert result["status"] == "NOT_APPLICABLE"


def test_generated_gotejamento_html_has_contract():
    html = generate_tool_page(
        _tool("gotejamento"),
        css_href="../assets/app.css",
        script_href="../assets/calc-engine.js",
        home_href="../index.html",
        inline_css=False,
    )
    assert 'id="tool-config"' in html
    assert "Ir para o conteúdo" in html
    assert "cdn" not in html.lower()
    config = html.split('id="tool-config">', 1)[1].split("</script>", 1)[0]
    parsed = json.loads(config)
    assert parsed["slug"] == "gotejamento"


def test_build_writes_dual_render():
    written = build()
    names = {path.name for path in written}
    assert "index.html" in names
    assert "gotejamento.html" in names
    assert "meows.html" in names
    fetch_index = (ROOT / "render" / "fetch" / "index.html").read_text(encoding="utf-8")
    inline_index = (ROOT / "render" / "inline" / "index.html").read_text(encoding="utf-8")
    assert "Gotejamento" in fetch_index
    assert "MEOWS" in fetch_index
    assert "<style>" in inline_index
    assert 'rel="stylesheet"' in fetch_index
    assert "cdn.jsdelivr" not in fetch_index.lower()
    assert "googleapis" not in fetch_index.lower()
    parity = check_parity()
    assert parity["status"] == "PASS"
    completeness = evaluate_catalog()
    release = evaluate_release(completeness, parity)
    assert release["status"] == "HOLD"
