"""Automatic evidence capture.

Evidence is a byproduct of execution, including denied attempts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable
from zoneinfo import ZoneInfo

from .hashing import sha256_uri
from .models import ExecutionRequest, ExecutionResult

SAO_PAULO = ZoneInfo("America/Sao_Paulo")


@dataclass
class EvidenceStore:
    events: list[dict[str, Any]] = field(default_factory=list)
    clock: Callable[[], datetime] = field(
        default_factory=lambda: (lambda: datetime.now(SAO_PAULO))
    )
    sequence: int = 0

    def capture(
        self,
        event_type: str,
        request: ExecutionRequest,
        result: ExecutionResult,
        pack: dict[str, Any],
    ) -> dict[str, Any]:
        self.sequence += 1
        timestamp = self.clock()
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        event_id = f"EVT-{timestamp.year}-{self.sequence:06d}"
        payload = {
            "event_type": event_type,
            "event_id": event_id,
            "calculator_id": request.calculator_id,
            "calculator_version": request.version,
            "policy_id": pack["policy"]["id"],
            "policy_version": pack["policy"]["version"],
            "schema_id": pack["schema_id"],
            "schema_version": pack["schema_version"],
            "actor": {"type": request.actor.type, "id": request.actor.id},
            "input": request.input,
            "input_hash": sha256_uri(request.input),
            "output": result.result,
            "output_hash": sha256_uri(result.result) if result.result is not None else None,
            "execution_engine": request.engine,
            "execution_timestamp": timestamp.isoformat(),
            "mission": request.mission,
            "validation": result.validation,
            "runtime_assertions": result.runtime_assertions,
            "decision": result.decision.status,
            "reason": result.decision.reason,
            "failed_rule": result.decision.failed_rule,
            "failed_assertion": result.decision.failed_assertion,
            "status": "CAPTURED",
        }
        required = pack["evidence_fields"]
        missing = [name for name in required if payload.get(name) in (None, "", [])]
        if event_type == "CALCULATION_EXECUTED" and missing:
            payload["evidence_contract"] = "INCOMPLETE"
            payload["missing_fields"] = missing
        else:
            payload["evidence_contract"] = "SATISFIED"
        self.events.append(payload)
        return payload


def provenance_chain(result: ExecutionResult) -> dict[str, Any]:
    evidence = result.evidence or {}
    return {
        "id": f"PROV-{evidence.get('event_id', 'UNKNOWN')}",
        "chain": [
            {"kind": "Policy", "id": evidence.get("policy_id"), "version": evidence.get("policy_version")},
            {
                "kind": "CanonicalObject",
                "id": evidence.get("calculator_id"),
                "version": evidence.get("calculator_version"),
            },
            {"kind": "Schema", "id": evidence.get("schema_id"), "version": evidence.get("schema_version")},
            {"kind": "Input", "hash": evidence.get("input_hash")},
            {"kind": "Execution", "id": result.execution_id, "engine": evidence.get("execution_engine")},
            {"kind": "Output", "hash": evidence.get("output_hash"), "value": result.result},
            {"kind": "Evidence", "id": evidence.get("event_id")},
        ],
    }
