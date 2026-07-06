"""Orquestra pipeline + workflow para itens pendentes."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "content_agents"))
sys.path.insert(0, str(ROOT / "scripts" / "apgar_agents"))

from content.field_registry import pending_items  # noqa: E402
from content.workflow_store import attach_pipeline_result, create_workflow, load_workflow, set_status  # noqa: E402

FIELD_BY_ARTIFACT = {
    "FLA": "CONTENT.FLA.deck_structure",
    "SIM": "CONTENT.SIM.exam_structure",
    "MMP": "CONTENT.MMP.root_and_branches",
    "PRT": "CONTENT.PRT.checklist_steps",
    "PKT": "CONTENT.PKT.sections",
    "FAQ": "CONTENT.FAQ.questions",
}


def _run_field(field_id: str, *, api_key: str | None, model: str | None, use_llm: bool) -> dict:
    # content_agents antes de apgar_agents — evita import do graph errado
    ca = str(ROOT / "scripts" / "content_agents")
    aa = str(ROOT / "scripts" / "apgar_agents")
    if ca in sys.path:
        sys.path.remove(ca)
    if aa in sys.path:
        sys.path.remove(aa)
    sys.path.insert(0, aa)
    sys.path.insert(0, ca)
    import graph as content_graph  # noqa: E402

    return content_graph.run_field(field_id, api_key=api_key, model=model, use_llm=use_llm)


def run_pending_item(
    pending_id: str,
    *,
    api_key: str | None = None,
    model: str | None = None,
    use_llm: bool = True,
) -> dict:
    item = None
    for row in pending_items().get("items", []):
        if row.get("pending_id") == pending_id:
            item = row
            break
    if not item:
        raise KeyError(f"pending_id não encontrado: {pending_id}")

    artifact_type = item.get("artifact_type", "")
    field_id = FIELD_BY_ARTIFACT.get(artifact_type)
    if not field_id:
        raise ValueError(f"Tipo sem field_id: {artifact_type}")

    wf = create_workflow(
        pending_id=pending_id,
        entity_code=item.get("entity_code", ""),
        artifact_type=artifact_type,
        field_id=field_id,
    )
    wf["status"] = "running"

    try:
        result = _run_field(field_id, api_key=api_key, model=model, use_llm=use_llm)
        wf = attach_pipeline_result(wf, result)
        wf["pending_item"] = {
            "title_pt": item.get("title_pt"),
            "concept_code": item.get("concept_code"),
            "canonical_url": item.get("canonical_url"),
        }
        return wf
    except Exception as exc:
        set_status(wf["workflow_id"], "failed", note=str(exc))
        raise


def run_bulk(
    *,
    artifact_type: str | None = None,
    limit: int = 5,
    api_key: str | None = None,
    model: str | None = None,
    use_llm: bool = True,
) -> dict:
    items = pending_items().get("items", [])
    if artifact_type:
        items = [i for i in items if i.get("artifact_type") == artifact_type.upper()]
    items = [i for i in items if i.get("status") in ("pending", "draft")][:limit]

    results = []
    errors = []
    for item in items:
        try:
            results.append(
                run_pending_item(
                    item["pending_id"],
                    api_key=api_key,
                    model=model,
                    use_llm=use_llm,
                )
            )
        except Exception as exc:
            errors.append({"pending_id": item.get("pending_id"), "error": str(exc)})

    return {
        "ok": len(errors) == 0,
        "processed": len(results),
        "errors": errors,
        "workflows": [w["workflow_id"] for w in results],
        "results": results,
    }


def approve_workflow(workflow_id: str) -> dict:
    from content.apply_proposal import apply_workflow  # noqa: E402

    wf = load_workflow(workflow_id)
    if wf.get("status") not in ("awaiting_approval", "approved"):
        raise ValueError(f"Workflow não pode ser aprovado: status={wf.get('status')}")

    pending_id = wf.get("pending_id")
    already_applied = False
    if pending_id:
        for row in pending_items().get("items", []):
            if row.get("pending_id") == pending_id and row.get("status") == "applied":
                already_applied = True
                break

    if already_applied:
        wf = set_status(workflow_id, "applied", note="Item já gravado — workflow duplicado fechado")
        return {"workflow": wf, "apply": {"skipped": True, "reason": "already_applied"}}

    apply_result = apply_workflow(wf)
    wf = set_status(workflow_id, "applied", note="Dados gravados nos datasets")
    return {"workflow": wf, "apply": apply_result}


def reject_workflow(workflow_id: str, *, reason: str = "") -> dict:
    return set_status(workflow_id, "rejected", note=reason or "Rejeitado pelo revisor")


def retry_workflow(
    workflow_id: str,
    *,
    api_key: str | None = None,
    model: str | None = None,
    use_llm: bool = True,
    auto_approve: bool = False,
) -> dict:
    """Reexecuta pipeline para workflow failed/draft/awaiting_approval."""
    wf = load_workflow(workflow_id)
    status = wf.get("status")
    if status not in ("failed", "draft", "awaiting_approval", "rejected"):
        return {"workflow_id": workflow_id, "status": status, "skipped": True, "reason": "nothing_to_retry"}

    pending_id = wf.get("pending_id")
    if not pending_id:
        raise ValueError(f"Workflow sem pending_id: {workflow_id}")

    result = run_pending_item(pending_id, api_key=api_key, model=model, use_llm=use_llm)
    if auto_approve and result.get("status") == "awaiting_approval":
        return approve_workflow(result["workflow_id"])
    return result


def retry_failed_workflows(
    *,
    limit: int = 20,
    api_key: str | None = None,
    model: str | None = None,
    use_llm: bool = True,
    auto_approve: bool = True,
) -> dict:
    from content.workflow_store import list_workflows  # noqa: E402

    targets = []
    for status in ("failed", "draft", "awaiting_approval"):
        targets.extend(list_workflows(status=status, limit=limit))
    targets = targets[:limit]

    results = []
    errors = []
    for wf in targets:
        wf_id = wf.get("workflow_id")
        try:
            results.append(
                retry_workflow(
                    wf_id,
                    api_key=api_key,
                    model=model,
                    use_llm=use_llm,
                    auto_approve=auto_approve,
                )
            )
        except Exception as exc:
            errors.append({"workflow_id": wf_id, "error": str(exc)})

    return {
        "ok": len(errors) == 0,
        "retried": len(results),
        "errors": errors,
        "results": results,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Retry workflows content-pending")
    parser.add_argument("--retry-failed", action="store_true")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--no-approve", action="store_true")
    args = parser.parse_args()

    if args.retry_failed:
        rep = retry_failed_workflows(
            limit=args.limit,
            use_llm=not args.no_llm,
            auto_approve=not args.no_approve,
        )
        print(f"Retried: {rep['retried']} | errors: {len(rep['errors'])}")
    else:
        parser.print_help()
