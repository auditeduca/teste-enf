"""Agente tradução APGAR — LangGraph + DeepSeek (30 idiomas)."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "apgar_agents"))

from apgar.i18n_catalog import all_locales  # noqa: E402
from apgar_agents.llm import get_api_key, resolve_model  # noqa: E402

NOW = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
RUNS = ROOT / "datasets" / "master-data" / "apgar" / "agent_runs"


def run_deterministic_pipeline(write: bool) -> dict:
    from apgar.i18n_catalog import LOCALE_MAP, build_locale_entry  # noqa: E402

    I18N_PATH = ROOT / "datasets" / "master-data" / "apgar" / "i18n.json"
    locales = all_locales()
    ok = len(locales) >= 30
    if write and ok:
        payload = {
            "schema_version": "2026.2.2-apgar-pilot",
            "concept_code": "APGAR",
            "entity_code": "APGAR_SCL_001",
            "generated_at": NOW,
            "source_locale": "pt-BR",
            "target_language_count": len(locales),
            "agent_pipeline": "deterministic",
            "locales": locales,
        }
        I18N_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "search": {"missing_count": 0},
        "locales": locales,
        "review": {"decision": "approve", "mode": "deterministic"},
        "validate": {"ok": ok, "count": len(locales)},
        "llm_enabled": False,
        "ok": ok,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Translation Agent APGAR (LangGraph + DeepSeek)")
    parser.add_argument("--write", action="store_true", help="Grava i18n.json")
    parser.add_argument("--llm", action="store_true", help="Usar DeepSeek via LangGraph")
    parser.add_argument("--no-llm", action="store_true", help="Modo deterministico")
    parser.add_argument("--refresh-tier", default="machine_from_en", help="Retraduzir tier")
    parser.add_argument("--model", default=None)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    use_llm = not args.no_llm and (args.llm or bool(get_api_key(args.api_key)))
    api_key = get_api_key(args.api_key)
    model = resolve_model(args.model)

    if use_llm and api_key:
        from translation_graph import run_translation_graph  # noqa: E402

        out = run_translation_graph(
            api_key=api_key,
            model=model,
            use_llm=True,
            refresh_tier=args.refresh_tier,
            write=args.write,
        )
    else:
        if use_llm and not api_key:
            print("AVISO: DEEPSEEK_API_KEY ausente — modo deterministico.")
        out = run_deterministic_pipeline(args.write)

    print("=== APGAR Translation Agent ===")
    print(f"LLM: {'DeepSeek ' + model if out.get('llm_enabled') else 'deterministico'}")
    print(f"Locales: {out.get('validate', {}).get('count', len(out.get('locales', [])))}/30")
    print(f"Review: {out.get('review', {}).get('decision', '?')}")
    print(f"Validate: {'PASS' if out.get('ok') else 'FAIL'}")
    if out.get("trace"):
        print(f"Trace: {' -> '.join(out['trace'][:8])}{'...' if len(out['trace']) > 8 else ''}")

    if args.json:
        RUNS.mkdir(parents=True, exist_ok=True)
        path = RUNS / f"translation_{NOW.replace(':', '').replace('-', '')[:15]}.json"
        path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Salvo: {path.relative_to(ROOT)}")

    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
