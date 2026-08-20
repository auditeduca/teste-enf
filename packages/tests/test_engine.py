from pathlib import Path
import json
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages"))

from nis_engine.score import compute, format_result, interpret, safe_eval  # noqa: E402
from nis_engine.validate import load_tool, validate_tool, validate_tools_dir  # noqa: E402
from nis_engine.generate import generate_tool_page, build  # noqa: E402
from nis_engine.paths import TOOLS_DIR  # noqa: E402


def _apgar():
    return load_tool(TOOLS_DIR / "apgar.json")


def _imc():
    return load_tool(TOOLS_DIR / "imc.json")


def test_apgar_all_max_is_10():
    tool = _apgar()
    total = compute(tool, {"fc": 2, "respiracao": 2, "tono": 2, "irritabilidade": 2, "cor": 2})
    assert total == 10
    band = interpret(tool, total)
    assert band is not None
    assert band["riskLevel"] == "none"


def test_apgar_critical_example():
    tool = _apgar()
    total = compute(tool, {"fc": 1, "respiracao": 0, "tono": 0, "irritabilidade": 0, "cor": 1})
    assert total == 2
    band = interpret(tool, total)
    assert band["riskLevel"] == "critical"


def test_apgar_defaults_are_vigorous():
    tool = _apgar()
    assert compute(tool) == 10


def test_imc_eutrophy():
    tool = _imc()
    total = compute(tool, {"peso": 65, "altura": 1.7})
    assert round(total, 1) == 22.5
    assert interpret(tool, total)["label"] == "Eutrofia"
    assert format_result(tool, total) == "22.5"


def test_imc_rejects_zero_height():
    tool = _imc()
    with pytest.raises(ZeroDivisionError):
        compute(tool, {"peso": 70, "altura": 0})


def test_safe_eval_rejects_names():
    with pytest.raises(ValueError):
        safe_eval("__import__('os').system('id')")


def test_all_tools_match_schema():
    failures = validate_tools_dir()
    assert failures == {}


def test_invalid_tool_is_reported():
    errors = validate_tool({"slug": "x"})
    assert errors


def test_generated_apgar_html_has_contract():
    html = generate_tool_page(_apgar())
    assert 'id="tool-config"' in html
    assert 'data-calc-input="fc"' in html
    assert "Índice de Apgar" in html
    config = html.split('id="tool-config">', 1)[1].split("</script>", 1)[0]
    parsed = json.loads(config)
    assert parsed["slug"] == "apgar"


def test_build_writes_pages(tmp_path):
    web = tmp_path / "web"
    (web / "tools").mkdir(parents=True)
    written = build(tools_dir=TOOLS_DIR, web_dir=web)
    slugs = {path.name for path in written}
    assert "index.html" in slugs
    assert "apgar.html" in slugs
    assert "imc.html" in slugs
    index = (web / "index.html").read_text(encoding="utf-8")
    assert "Índice de Apgar" in index
    assert "Índice de Massa Corporal" in index
