"""Agent capability gate.

The model may propose. The architecture decides whether a tool may run.
Agents can USE a calculator. They cannot ALTER policy, schema, or runtime.
"""

from __future__ import annotations

from typing import Any

from .loader import ObjectPack
from .models import Actor, Decision, ExecutionRequest, ExecutionResult
from .runtime import GovernedRuntime


class AgentAuthorizationError(PermissionError):
    pass


class GovernedAgent:
    def __init__(self, pack: ObjectPack, runtime: GovernedRuntime) -> None:
        self.pack = pack
        self.runtime = runtime
        self.spec = pack.agent

    def invoke(self, mission: str, inputs: dict[str, Any], *, engine: str = "DETERMINISTIC_CALC_ENGINE") -> ExecutionResult:
        actor = Actor(type="AGENT", id=self.spec["id"])
        authorization = self.authorize("CAP-CALCULATE-BMI", "CAL-IMC-001")
        if not authorization.allowed:
            request = ExecutionRequest(
                calculator_id="CAL-IMC-001",
                version=self.pack.canonical["version"],
                input=inputs,
                actor=actor,
                engine=engine,
                mission=mission,
            )
            denied = ExecutionResult(status="DENIED", request=request, decision=authorization)
            return self.runtime._finalize(request, denied, event_type="EXECUTION_DENIED")
        request = ExecutionRequest(
            calculator_id="CAL-IMC-001",
            version=self.pack.canonical["version"],
            input=inputs,
            actor=actor,
            engine=engine,
            mission=mission,
        )
        return self.runtime.execute(request)

    def authorize(self, capability_id: str, tool_id: str) -> Decision:
        capabilities = {item["id"]: item for item in self.spec.get("capabilities", [])}
        capability = capabilities.get(capability_id)
        if capability is None:
            return Decision.deny("UNKNOWN_CAPABILITY", failed_rule=self.spec.get("policy", {}).get("id"))
        if tool_id not in capability.get("allowed_tools", []):
            return Decision.deny("TOOL_NOT_ALLOWED", failed_rule=capability_id, tool=tool_id)
        return Decision.allow(capability=capability_id, autonomy=capability.get("autonomy", {}).get("level"))

    def attempt_mutation(self, target: str) -> Decision:
        restrictions = set(self.spec.get("capabilities", [{}])[0].get("restrictions", []))
        blocked = {
            "calculator": "cannot_modify_calculator",
            "policy": "cannot_modify_policy",
            "runtime": "cannot_override_runtime",
            "validation": "cannot_bypass_validation",
        }
        rule = blocked.get(target)
        if rule and rule in restrictions:
            return Decision.deny("AGENT_MUTATION_FORBIDDEN", failed_rule=rule, target=target)
        return Decision.deny("AGENT_MUTATION_FORBIDDEN", failed_rule="implicit_deny", target=target)
