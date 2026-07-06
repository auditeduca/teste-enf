"""LangGraph workflow: scan → classify → batch review (DeepSeek) → report."""
from __future__ import annotations

import operator
from pathlib import Path
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph

from review.cancel import is_cancelled
from review.config import MAX_BATCH_CHARS, MAX_PATHS_DEFAULT
from review.deepseek_client import chat_complete
from review.file_scanner import ScanResult, batch_entries, scan_paths
from review.progress import set_progress

SYSTEM_PROMPT = """Você é revisor sênior do repositório CALENF-NKD (Nursing OS).
Analise apenas os trechos fornecidos. Foque em:
- bugs e regressões prováveis
- violações de convenção do repo (envelope NKOS, content_paths.py)
- segurança (secrets, LGPD)
- performance óbvia

Responda em português, bullets curtos por arquivo. Se não houver problema, diga "OK".

Correções automáticas: após a revisão, o pipeline pode aplicar patches nos arquivos
revisados (scripts/, platform/src/, docs/) e registrar cada alteração em
datasets/metadata/code_review_changes.jsonl."""


class ReviewState(TypedDict):
    root: str
    target_paths: list[str]
    api_key: str
    model: str
    focus: str
    scan: ScanResult | None
    batches: list[list[dict]]
    batch_index: int
    findings: Annotated[list[str], operator.add]
    skipped_summary: list[dict]
    report: str
    error: str


def _scan_node(state: ReviewState) -> dict:
    set_progress(phase="scan")
    root = Path(state["root"])
    targets = state.get("target_paths") or list(MAX_PATHS_DEFAULT)
    scan = scan_paths(root, targets)
    skipped_summary = [
        {"path": e.rel, "reason": e.reason, "size": e.size}
        for e in scan.skipped
    ]
    batches_raw = batch_entries(scan.entries, MAX_BATCH_CHARS)
    batches = [
        [{"rel": e.rel, "content": e.content} for e in batch]
        for batch in batches_raw
    ]
    return {
        "scan": scan,
        "batches": batches,
        "batch_index": 0,
        "skipped_summary": skipped_summary,
        "findings": [],
    }


def _cancelled_payload(state: ReviewState) -> dict:
    total = len(state.get("batches") or [])
    return {
        "error": "Revisão cancelada pelo usuário.",
        "batch_index": total,
    }


def _review_batch_node(state: ReviewState) -> dict:
    if is_cancelled():
        return _cancelled_payload(state)

    idx = state["batch_index"]
    batches = state["batches"]
    if idx >= len(batches):
        return {}

    set_progress(phase="review", batch_index=idx + 1, batch_total=len(batches))
    batch = batches[idx]
    blocks = []
    for item in batch:
        blocks.append(f"### `{item['rel']}`\n```\n{item['content']}\n```")
    user_body = "\n\n".join(blocks)
    focus = (state.get("focus") or "").strip()
    if focus:
        user_body = f"Foco adicional: {focus}\n\n{user_body}"

    try:
        content = chat_complete(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_body},
            ],
            api_key=state["api_key"],
            model=state.get("model") or "deepseek-v4-flash",
        )
    except Exception as exc:
        return {"error": str(exc), "batch_index": idx + 1}

    label = f"Lote {idx + 1}/{len(batches)} ({len(batch)} arquivo(s))"
    if is_cancelled():
        return {
            **_cancelled_payload(state),
            "findings": [f"## {label}\n\n{content}\n\n*(Cancelado após este lote.)*"],
        }

    return {
        "findings": [f"## {label}\n\n{content}"],
        "batch_index": idx + 1,
    }


def _should_continue(state: ReviewState) -> str:
    if state.get("error"):
        return "aggregate"
    if state["batch_index"] < len(state.get("batches") or []):
        return "review"
    return "aggregate"


def _aggregate_node(state: ReviewState) -> dict:
    scan = state.get("scan")
    skipped = state.get("skipped_summary") or []
    findings = state.get("findings") or []
    err = state.get("error") or ""

    lines = ["# Relatório de revisão (LangGraph + DeepSeek)", ""]

    if scan:
        lines.append(f"- **Revisados:** {len(scan.entries)} arquivo(s)")
        lines.append(f"- **Ignorados:** {len(skipped)} (grandes, node_modules, nodes, datasets…)")
        lines.append("")

    if skipped:
        lines.append("## Arquivos ignorados (amostra)")
        for row in skipped[:40]:
            lines.append(f"- `{row['path']}` — {row['reason']}")
        if len(skipped) > 40:
            lines.append(f"- … e mais {len(skipped) - 40}")
        lines.append("")

    if err:
        lines.append(f"## Erro\n\n{err}\n")
        if "cancelada" in err.lower():
            lines.insert(2, "- **Status:** cancelada pelo usuário")

    if findings:
        lines.append("## Achados")
        lines.extend(findings)
    elif not err:
        lines.append("## Achados\n\nNenhum lote revisado (fila vazia ou tudo ignorado).")

    return {"report": "\n".join(lines)}


def build_review_graph():
    graph = StateGraph(ReviewState)
    graph.add_node("scan", _scan_node)
    graph.add_node("review", _review_batch_node)
    graph.add_node("aggregate", _aggregate_node)

    graph.add_edge(START, "scan")
    graph.add_edge("scan", "review")
    graph.add_conditional_edges("review", _should_continue, {"review": "review", "aggregate": "aggregate"})
    graph.add_edge("aggregate", END)
    return graph.compile()


def run_review_graph(
    *,
    root: Path | str,
    target_paths: list[str] | None = None,
    api_key: str,
    model: str = "deepseek-v4-flash",
    focus: str = "",
) -> dict:
    """Execute full review; returns report dict for API/CLI."""
    app = build_review_graph()
    initial: ReviewState = {
        "root": str(Path(root).resolve()),
        "target_paths": target_paths or list(MAX_PATHS_DEFAULT),
        "api_key": api_key,
        "model": model,
        "focus": focus,
        "scan": None,
        "batches": [],
        "batch_index": 0,
        "findings": [],
        "skipped_summary": [],
        "report": "",
        "error": "",
    }
    final = app.invoke(initial)
    scan = final.get("scan")
    return {
        "report": final.get("report") or "",
        "error": final.get("error") or "",
        "reviewed_count": len(scan.entries) if scan else 0,
        "skipped_count": len(final.get("skipped_summary") or []),
        "batch_count": len(final.get("batches") or []),
        "skipped_sample": (final.get("skipped_summary") or [])[:20],
    }
