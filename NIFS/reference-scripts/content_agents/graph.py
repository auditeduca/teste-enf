"""LangGraph + DeepSeek: Search → Generate → Review → Validate (conteúdo pendente)."""
from __future__ import annotations

import json
import operator
import sys
from pathlib import Path
from typing import Annotated, TypedDict

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "content_agents"))
sys.path.insert(0, str(ROOT / "scripts" / "apgar_agents"))

from apgar_agents.llm import chat_json, get_api_key, load_prompt as _load_apgar_prompt, resolve_model  # noqa: E402
from content.field_registry import canonical, field_docs, pending_items  # noqa: E402
from config import PROMPTS_DIR  # noqa: E402
from validators import validate_field  # noqa: E402

try:
    from langgraph.graph import END, START, StateGraph
except ImportError:
    StateGraph = None  # type: ignore


def load_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    if path.exists():
        return path.read_text(encoding="utf-8")
    return _load_apgar_prompt(name)


class FieldPipelineState(TypedDict):
    field_id: str
    field_doc: dict
    api_key: str
    model: str
    use_llm: bool
    search_result: dict
    proposal: dict
    review: dict
    validation: dict
    trace: Annotated[list[str], operator.add]
    error: str


def _content_type(field_id: str) -> str:
    parts = field_id.split(".")
    return parts[1] if len(parts) > 1 else "registry"


def _pending_for_type(type_code: str) -> list[dict]:
    if type_code == "registry":
        return pending_items().get("items", [])[:5]
    return [i for i in pending_items().get("items", []) if i.get("artifact_type") == type_code][:5]


def _deterministic_search(fd: dict, field_id: str) -> dict:
    ctype = _content_type(field_id)
    canon = canonical()
    return {
        "field_id": field_id,
        "content_type": ctype,
        "expected_value": fd.get("expected_value"),
        "pending_items": _pending_for_type(ctype if ctype != "registry" else "FLA"),
        "artifact_rules": canon.get("artifact_types", {}).get(ctype, {}),
        "dataset_paths": fd.get("dataset_paths") or [],
        "confidence": 0.85,
        "mode": "deterministic",
    }


def search_node(state: FieldPipelineState) -> dict:
    fd = state["field_doc"]
    field_id = state["field_id"]
    result = _deterministic_search(fd, field_id)

    if state.get("use_llm") and state.get("api_key"):
        try:
            system = load_prompt("search.md")
            user = json.dumps(
                {
                    "field_documentation": fd,
                    "deterministic_search": result,
                    "pending_sample": _pending_for_type(_content_type(field_id)),
                },
                ensure_ascii=False,
                indent=2,
            )
            llm_result = chat_json(
                [{"role": "system", "content": system}, {"role": "user", "content": user}],
                api_key=state["api_key"],
                model=state["model"],
            )
            if isinstance(llm_result, dict):
                result = {**result, **llm_result, "mode": "deepseek_langgraph"}
        except Exception as exc:
            result["llm_error"] = str(exc)

    return {"search_result": result, "trace": [f"search:{field_id}"]}


def _deterministic_proposal(fd: dict, field_id: str) -> dict:
    ctype = _content_type(field_id)
    return {
        "field_id": field_id,
        "artifact_type": ctype,
        "proposed_value": fd.get("expected_value"),
        "target_dataset": (fd.get("dataset_paths") or ["pending_items.json"])[0],
        "rationale_pt": fd.get("why_selected", ""),
        "evidence_grade": "A" if ctype in ("FLA", "PRT", "PKT", "SIM") else "B",
        "mode": "deterministic",
    }


def generate_node(state: FieldPipelineState) -> dict:
    fd = state["field_doc"]
    field_id = state["field_id"]
    proposal = _deterministic_proposal(fd, field_id)

    if state.get("use_llm") and state.get("api_key"):
        try:
            system = load_prompt("generate.md")
            user = json.dumps(
                {
                    "field_id": field_id,
                    "search_result": state.get("search_result") or {},
                    "expected_value": fd.get("expected_value"),
                },
                ensure_ascii=False,
                indent=2,
            )
            llm_proposal = chat_json(
                [{"role": "system", "content": system}, {"role": "user", "content": user}],
                api_key=state["api_key"],
                model=state["model"],
            )
            if isinstance(llm_proposal, dict):
                proposal = {**proposal, **llm_proposal, "mode": "deepseek_langgraph"}
        except Exception as exc:
            proposal["llm_error"] = str(exc)

    return {"proposal": proposal, "trace": [f"generate:{field_id}"]}


def _deterministic_review(fd: dict, field_id: str, proposal: dict) -> dict:
    completion = fd.get("completion_pct", 0)
    decision = "approve" if completion >= 100 else "revise"
    return {
        "field_id": field_id,
        "decision": decision,
        "notes_pt": f"Completion {completion}% — master-data em progresso",
        "evidence_ok": proposal.get("evidence_grade") in ("A", "B"),
        "mode": "deterministic",
    }


def review_node(state: FieldPipelineState) -> dict:
    fd = state["field_doc"]
    field_id = state["field_id"]
    proposal = state.get("proposal") or {}
    review = _deterministic_review(fd, field_id, proposal)

    if state.get("use_llm") and state.get("api_key"):
        try:
            system = load_prompt("review.md")
            user = json.dumps(
                {"field_id": field_id, "proposal": proposal, "expected": fd.get("expected_value")},
                ensure_ascii=False,
                indent=2,
            )
            llm_review = chat_json(
                [{"role": "system", "content": system}, {"role": "user", "content": user}],
                api_key=state["api_key"],
                model=state["model"],
                temperature=0.1,
            )
            if isinstance(llm_review, dict):
                review = {**review, **llm_review, "mode": "deepseek_langgraph"}
        except Exception as exc:
            review["llm_error"] = str(exc)

    return {"review": review, "trace": [f"review:{field_id}:{review.get('decision', '?')}"]}


def validate_node(state: FieldPipelineState) -> dict:
    vf = validate_field(state["field_id"])
    validation = {
        "field_id": state["field_id"],
        "validation_passed": vf["ok"],
        "findings": vf["findings"],
        "ready_for_ci": vf["ok"],
        "mode": "deterministic",
    }
    return {
        "validation": validation,
        "trace": [f"validate:{state['field_id']}:{'pass' if vf['ok'] else 'fail'}"],
    }


def build_graph():
    if StateGraph is None:
        raise ImportError("langgraph não instalado — pip install -r requirements-nkp.txt")
    g = StateGraph(FieldPipelineState)
    g.add_node("search", search_node)
    g.add_node("generate", generate_node)
    g.add_node("review", review_node)
    g.add_node("validate", validate_node)
    g.add_edge(START, "search")
    g.add_edge("search", "generate")
    g.add_edge("generate", "review")
    g.add_edge("review", "validate")
    g.add_edge("validate", END)
    return g.compile()


def run_field(
    field_id: str,
    *,
    api_key: str | None = None,
    model: str | None = None,
    use_llm: bool = True,
) -> dict:
    fields = {f["field_id"]: f for f in field_docs()["fields"]}
    if field_id not in fields:
        raise KeyError(f"Campo desconhecido: {field_id}")

    key = get_api_key(api_key) if use_llm else None
    llm_active = bool(use_llm and key)
    graph = build_graph()
    initial: FieldPipelineState = {
        "field_id": field_id,
        "field_doc": fields[field_id],
        "api_key": key or "",
        "model": resolve_model(model),
        "use_llm": llm_active,
        "search_result": {},
        "proposal": {},
        "review": {},
        "validation": {},
        "trace": [],
        "error": "",
    }
    result = graph.invoke(initial)
    result["llm_enabled"] = llm_active
    result["model"] = resolve_model(model)

    from agent_common.sanitize import sanitize_agent_result  # noqa: E402

    return sanitize_agent_result(result)


def run_all_agent_fields(*, api_key: str | None = None, model: str | None = None, use_llm: bool = True) -> list[dict]:
    results = []
    for fd in field_docs()["fields"]:
        if "search" in (fd.get("agent_roles") or []):
            results.append(run_field(fd["field_id"], api_key=api_key, model=model, use_llm=use_llm))
    return results
