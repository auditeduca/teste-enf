"""Audit reconstruction and learning/drift signals."""

from __future__ import annotations

from typing import Any

from .models import ExecutionResult


def audit_record(result: ExecutionResult) -> dict[str, Any]:
    evidence = result.evidence or {}
    return {
        "execution_id": result.execution_id,
        "mission": result.request.mission,
        "actor": {"type": result.request.actor.type, "id": result.request.actor.id},
        "resource": {
            "type": "CALCULATOR",
            "id": result.request.calculator_id,
            "version": result.request.version,
        },
        "authorization": {
            "policy": evidence.get("policy_id"),
            "decision": result.decision.status,
        },
        "validation": result.validation,
        "runtime": {"assertions": result.runtime_assertions},
        "execution": {
            "engine": result.request.engine,
            "formula": None if result.result is None else result.result.get("formula"),
        },
        "result": result.result,
        "evidence": {
            "event_id": evidence.get("event_id"),
            "status": evidence.get("status"),
        },
        "who": result.request.actor.id,
        "what": result.request.calculator_id,
        "when": evidence.get("execution_timestamp"),
        "which_policy": f"{evidence.get('policy_id')} v{evidence.get('policy_version')}",
        "which_schema": f"{evidence.get('schema_id')} v{evidence.get('schema_version')}",
        "which_input": result.request.input,
        "which_output": result.result,
        "which_engine": result.request.engine,
        "which_gates": result.validation,
    }


def drift_report(results: list[ExecutionResult]) -> dict[str, Any]:
    total = len(results)
    denied = [item for item in results if item.status == "DENIED"]
    executed = [item for item in results if item.status == "EXECUTED"]
    reasons: dict[str, int] = {}
    for item in denied:
        reason = item.decision.reason or "UNKNOWN"
        reasons[reason] = reasons.get(reason, 0) + 1
    denial_rate = (len(denied) / total) if total else 0.0
    signal = None
    if total >= 3 and denial_rate >= 0.5:
        signal = {
            "type": "DRIFT_SIGNAL",
            "metric": "denial_rate",
            "value": denial_rate,
            "recommendation": "POLICY_REVIEW",
        }
    return {
        "total": total,
        "executed": len(executed),
        "denied": len(denied),
        "denial_rate": denial_rate,
        "reasons": reasons,
        "signal": signal,
    }
