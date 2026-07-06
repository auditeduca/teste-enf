"""LangGraph + DeepSeek: tradução APGAR para 30 idiomas."""
from __future__ import annotations

import json
import operator
import sys
from pathlib import Path
from typing import Annotated, TypedDict

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "apgar_agents"))

from apgar.i18n_catalog import LOCALE_MAP, all_locales, build_locale_entry  # noqa: E402
from llm import chat_json, get_api_key, load_prompt, resolve_model  # noqa: E402

try:
    from langgraph.graph import END, START, StateGraph
except ImportError:
    StateGraph = None  # type: ignore

I18N_PATH = ROOT / "datasets" / "master-data" / "apgar" / "i18n.json"
BATCH_SIZE = 5


class TranslationState(TypedDict):
    api_key: str
    model: str
    use_llm: bool
    refresh_tier: str
    source_locale: dict
    target_locale_codes: list[str]
    batch_index: int
    locales: list[dict]
    search_result: dict
    review: dict
    validation: dict
    trace: Annotated[list[str], operator.add]
    error: str


def _load_existing() -> list[dict]:
    if not I18N_PATH.exists():
        return []
    return json.loads(I18N_PATH.read_text(encoding="utf-8")).get("locales", [])


def _source_pt() -> dict:
    for lc in all_locales():
        if lc["locale_code"] == "pt-BR":
            return lc
    return build_locale_entry("pt-BR")


def search_node(state: TranslationState) -> dict:
    existing = _load_existing()
    present = {lc["locale_code"] for lc in existing}
    missing = [lc for lc in LOCALE_MAP if lc not in present]
    refresh_tier = state.get("refresh_tier") or "machine_from_en"
    to_refresh = [
        lc["locale_code"]
        for lc in existing
        if lc.get("translation_tier") == refresh_tier
    ]
    targets = missing or to_refresh or list(LOCALE_MAP.keys())
    return {
        "search_result": {
            "missing": missing,
            "to_refresh": to_refresh,
            "target_count": len(targets),
        },
        "target_locale_codes": targets,
        "batch_index": 0,
        "locales": existing if existing else [],
        "trace": ["search:translation"],
    }


def _deterministic_batch(codes: list[str]) -> list[dict]:
    return [build_locale_entry(code) for code in codes]


def _llm_batch(state: TranslationState, codes: list[str]) -> list[dict]:
    system = load_prompt("translate.md")
    source = state.get("source_locale") or _source_pt()
    user = json.dumps(
        {
            "source_locale": source,
            "target_locale_codes": codes,
            "locale_language_map": {c: LOCALE_MAP[c] for c in codes},
            "required_component_keys": list(source.get("components", {}).keys()),
            "interpretation_band_count": 3,
        },
        ensure_ascii=False,
        indent=2,
    )
    result = chat_json(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user + "\n\nResponda ONLY JSON: {\"locales\": [ ... ]}"},
        ],
        api_key=state["api_key"],
        model=state["model"],
        max_tokens=8192,
    )
    if isinstance(result, dict) and "locales" in result:
        return result["locales"]
    if isinstance(result, list):
        return result
    raise ValueError("Resposta LLM sem array locales")


def generate_batch_node(state: TranslationState) -> dict:
    codes = state["target_locale_codes"]
    idx = state["batch_index"]
    batch = codes[idx * BATCH_SIZE : (idx + 1) * BATCH_SIZE]
    if not batch:
        return {}

    if state.get("use_llm") and state.get("api_key"):
        try:
            new_entries = _llm_batch(state, batch)
            for entry in new_entries:
                entry["review_status"] = "llm_generated"
                entry["translation_tier"] = "deepseek_curated"
            mode = "deepseek_langgraph"
        except Exception as exc:
            new_entries = _deterministic_batch(batch)
            for entry in new_entries:
                entry["llm_error"] = str(exc)
            mode = "deterministic_fallback"
    else:
        new_entries = _deterministic_batch(batch)
        mode = "deterministic"

    by_code = {lc["locale_code"]: lc for lc in (state.get("locales") or [])}
    for entry in new_entries:
        if entry.get("locale_code"):
            by_code[entry["locale_code"]] = entry

    return {
        "locales": list(by_code.values()),
        "batch_index": idx + 1,
        "trace": [f"generate:batch_{idx + 1}:{mode}"],
    }


def _should_continue(state: TranslationState) -> str:
    codes = state["target_locale_codes"]
    if state["batch_index"] * BATCH_SIZE < len(codes):
        return "generate"
    return "merge"


def merge_node(state: TranslationState) -> dict:
    by_code = {lc["locale_code"]: lc for lc in _load_existing()}
    for lc in state.get("locales") or []:
        if lc.get("locale_code"):
            by_code[lc["locale_code"]] = lc
    for code in LOCALE_MAP:
        if code not in by_code:
            by_code[code] = build_locale_entry(code)
    merged = [by_code[k] for k in LOCALE_MAP]
    return {"locales": merged, "trace": ["merge:locales"]}


def review_node(state: TranslationState) -> dict:
    locales = state.get("locales") or []
    issues = [
        lc["locale_code"]
        for lc in locales
        if not lc.get("name") or len((lc.get("components") or {})) < 5
    ]
    review = {
        "decision": "approve" if not issues and len(locales) >= 30 else "revise",
        "issues": issues,
        "locale_count": len(locales),
        "mode": "deterministic",
    }

    if state.get("use_llm") and state.get("api_key") and locales:
        try:
            sample = locales[:3]
            system = load_prompt("review.md")
            user = json.dumps(
                {
                    "task": "review_apgar_translations",
                    "sample_locales": sample,
                    "total_count": len(locales),
                    "issues": issues,
                },
                ensure_ascii=False,
            )
            llm_review = chat_json(
                [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                api_key=state["api_key"],
                model=state["model"],
                temperature=0.1,
            )
            if isinstance(llm_review, dict):
                review = {**review, **llm_review, "mode": "deepseek_langgraph"}
        except Exception as exc:
            review["llm_error"] = str(exc)

    return {"review": review, "trace": [f"review:{review.get('decision', '?')}"]}


def validate_node(state: TranslationState) -> dict:
    locales = state.get("locales") or []
    ok = len(locales) >= 30 and all(
        lc.get("name") and lc.get("description") and len((lc.get("components") or {})) == 5
        for lc in locales
    )
    return {
        "validation": {"ok": ok, "count": len(locales), "expected": 30},
        "trace": [f"validate:{'pass' if ok else 'fail'}"],
    }


def build_translation_graph():
    if StateGraph is None:
        raise ImportError("langgraph não instalado — pip install -r requirements-nkp.txt")

    g = StateGraph(TranslationState)
    g.add_node("search", search_node)
    g.add_node("generate", generate_batch_node)
    g.add_node("merge", merge_node)
    g.add_node("review", review_node)
    g.add_node("validate", validate_node)

    g.add_edge(START, "search")
    g.add_edge("search", "generate")
    g.add_conditional_edges("generate", _should_continue, {"generate": "generate", "merge": "merge"})
    g.add_edge("merge", "review")
    g.add_edge("review", "validate")
    g.add_edge("validate", END)
    return g.compile()


def run_translation_graph(
    *,
    api_key: str | None = None,
    model: str | None = None,
    use_llm: bool = True,
    refresh_tier: str = "machine_from_en",
    write: bool = False,
) -> dict:
    key = get_api_key(api_key) if use_llm else None
    llm_active = bool(use_llm and key)

    initial: TranslationState = {
        "api_key": key or "",
        "model": resolve_model(model),
        "use_llm": llm_active,
        "refresh_tier": refresh_tier,
        "source_locale": _source_pt(),
        "target_locale_codes": [],
        "batch_index": 0,
        "locales": [],
        "search_result": {},
        "review": {},
        "validation": {},
        "trace": [],
        "error": "",
    }

    final = build_translation_graph().invoke(initial)
    locales = final.get("locales") or []

    if write and final.get("validation", {}).get("ok"):
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        payload = {
            "schema_version": "2026.2.2-apgar-pilot",
            "concept_code": "APGAR",
            "entity_code": "APGAR_SCL_001",
            "generated_at": now,
            "source_locale": "pt-BR",
            "target_language_count": len(locales),
            "agent_pipeline": "translation_graph_deepseek",
            "llm_enabled": llm_active,
            "model": resolve_model(model),
            "locales": locales,
        }
        I18N_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return {
        "search": final.get("search_result"),
        "locales": locales,
        "review": final.get("review"),
        "validate": final.get("validation"),
        "trace": final.get("trace"),
        "llm_enabled": llm_active,
        "model": resolve_model(model),
        "ok": bool(final.get("validation", {}).get("ok")),
    }
