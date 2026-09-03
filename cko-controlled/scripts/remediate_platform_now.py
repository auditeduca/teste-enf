#!/usr/bin/env python3
"""Remediate platform-sanable pendencies without mutating Drive or closing B9."""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SITE = REPO / "reference-website"
DRIVE = (
    REPO / "cko-controlled" / "public" / "drive",
    REPO / "cko-controlled" / "control-plane" / "drive-html",
)


def assert_not_drive(path: Path) -> None:
    resolved = path.resolve()
    for root in DRIVE:
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            continue
        raise SystemExit(f"refusing Drive write: {path}")


def inject_tool_config(html_name: str, json_name: str, include_engine: bool = False) -> str:
    """Embed parseable tool-config from data/tools JSON without rewriting the page shell.

    Custom calculators keep their own JS. calc-engine.js is only added when requested
    and the page already follows the data-calc-input contract.
    """
    html_path = SITE / html_name
    json_path = SITE / "data" / "tools" / json_name
    html = html_path.read_text(encoding="utf-8")
    cfg = json.loads(json_path.read_text(encoding="utf-8"))
    payload = json.dumps(cfg, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("<", "\\u003c")
    tag = f'<script type="application/json" id="tool-config">{payload}</script>'
    engine = '<script src="js/calc-engine.js"></script>\n' if include_engine else ""
    if 'id="tool-config"' in html:
        html = re.sub(
            r'<script[^>]*id="tool-config"[^>]*>.*?</script>',
            lambda _m: tag,
            html,
            count=1,
            flags=re.S,
        )
        if include_engine and "js/calc-engine.js" not in html:
            html = html.replace("</body>", engine + "</body>", 1)
    else:
        last = html.rfind("</body>")
        if last < 0:
            raise SystemExit(f"{html_name} missing </body>")
        html = html[:last] + "\n" + tag + "\n" + engine + html[last:]
    assert_not_drive(html_path)
    html_path.write_text(html, encoding="utf-8")
    m = re.search(r'<script[^>]*id="tool-config"[^>]*>(.*?)</script>', html, re.S)
    json.loads(m.group(1).replace("\\u003c", "<"))
    cfg_at = html.rfind('id="tool-config"')
    print_close = html.rfind(r"<\/script>")
    if print_close >= 0 and cfg_at < print_close:
        raise SystemExit(f"{html_name}: tool-config landed inside a print-template script")
    return html_name


def write_i18n_hold(locale: str, source: str | None = None) -> str:
    dest = SITE / "i18n" / f"{locale}.json"
    if dest.exists() and locale != "zh":
        return f"{locale}:exists"
    body = {
        "_meta": {
            "locale": locale,
            "status": "HOLD_TRANSLATION_REQUIRED",
            "review_status": "hold",
            "activate_in_selector": False,
            "release": "HOLD / NOT_RELEASED",
            "note": "Scaffold only. Do not activate in the language selector before human review.",
        }
    }
    if source:
        src = json.loads((SITE / "i18n" / source).read_text(encoding="utf-8"))
        src_meta = src.get("_meta") if isinstance(src, dict) else None
        if isinstance(src, dict):
            body.update({k: v for k, v in src.items() if k != "_meta"})
        body["_meta"]["derived_from"] = source
        if src_meta:
            body["_meta"]["source_meta"] = src_meta
    assert_not_drive(dest)
    dest.write_text(json.dumps(body, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return f"{locale}:hold-written"


def main() -> None:
    done = {
        "asa": inject_tool_config("asa.html", "asa.json", include_engine=False),
        "rescisao": inject_tool_config("calculo-rescisao.html", "calculo-rescisao.json", include_engine=False),
        "i18n_da": write_i18n_hold("da"),
        "i18n_uk": write_i18n_hold("uk"),
        "i18n_zh": write_i18n_hold("zh", source="zh-CN.json"),
        "mutate_drive": False,
        "closes_b9": False,
    }
    print(json.dumps(done, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
