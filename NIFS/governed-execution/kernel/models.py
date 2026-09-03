"""Shared runtime types for governed execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


ActorType = Literal["HUMAN", "AGENT"]
DecisionStatus = Literal["ALLOW", "DENY"]
ExecutionStatus = Literal["EXECUTED", "DENIED"]


@dataclass(frozen=True)
class Actor:
    type: ActorType
    id: str


@dataclass
class Decision:
    allowed: bool
    status: DecisionStatus
    reason: str | None = None
    failed_rule: str | None = None
    failed_assertion: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def allow(cls, **details: Any) -> "Decision":
        return cls(allowed=True, status="ALLOW", details=details)

    @classmethod
    def deny(
        cls,
        reason: str,
        *,
        failed_rule: str | None = None,
        failed_assertion: str | None = None,
        **details: Any,
    ) -> "Decision":
        return cls(
            allowed=False,
            status="DENY",
            reason=reason,
            failed_rule=failed_rule,
            failed_assertion=failed_assertion,
            details=details,
        )


@dataclass
class ExecutionRequest:
    calculator_id: str
    version: str
    input: dict[str, Any]
    actor: Actor
    engine: str = "DETERMINISTIC_CALC_ENGINE"
    mission: str | None = None
    twin_id: str | None = None


@dataclass
class ExecutionResult:
    status: ExecutionStatus
    request: ExecutionRequest
    decision: Decision
    result: dict[str, Any] | None = None
    validation: dict[str, str] = field(default_factory=dict)
    runtime_assertions: dict[str, str] = field(default_factory=dict)
    evidence: dict[str, Any] | None = None
    provenance: dict[str, Any] | None = None
    execution_id: str | None = None
    twin_event: dict[str, Any] | None = None

    @property
    def executed(self) -> bool:
        return self.status == "EXECUTED"
