"""End-to-end CAL-IMC-001 scenario: policy → evidence → twin → audit."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from .agent import GovernedAgent
from .audit import audit_record, drift_report
from .ci import run_ci_gates
from .evidence import EvidenceStore
from .loader import load_object_pack
from .models import Actor, ExecutionRequest
from .runtime import GovernedRuntime
from .twin import DigitalTwin

FIXED_TS = datetime(2026, 9, 2, 22, 15, 0, tzinfo=ZoneInfo("America/Sao_Paulo"))


def run_imc_scenario() -> dict[str, Any]:
    pack = load_object_pack("CAL-IMC-001")
    ci = run_ci_gates(pack)
    store = EvidenceStore(clock=lambda: FIXED_TS)
    runtime = GovernedRuntime(pack, store=store)

    human = Actor(type="HUMAN", id="NURSE-001")
    success = runtime.execute(
        ExecutionRequest(
            calculator_id="CAL-IMC-001",
            version="1.0.0",
            input={"weight_kg": 70, "height_m": 1.75},
            actor=human,
            mission="Calculate BMI",
        )
    )

    denied_zero = runtime.execute(
        ExecutionRequest(
            calculator_id="CAL-IMC-001",
            version="1.0.0",
            input={"weight_kg": 70, "height_m": 0},
            actor=human,
            mission="Calculate BMI with invalid height",
        )
    )

    agent = GovernedAgent(pack, runtime)
    agent_ok = agent.invoke("Calcule o IMC desse paciente.", {"weight_kg": 70, "height_m": 1.75})
    agent_denied = agent.invoke("Calcule o IMC desse paciente.", {"weight_kg": 70, "height_m": 0})
    llm_denied = agent.invoke(
        "Calcule o IMC desse paciente.",
        {"weight_kg": 70, "height_m": 1.75},
        engine="LLM",
    )
    mutation = agent.attempt_mutation("policy")

    twin = DigitalTwin(pack.twin_contract["seed_state"], pack)
    twin_result = twin.derive(runtime, actor=Actor(type="AGENT", id=pack.agent["id"]))

    return {
        "object_id": pack.object_id,
        "constitutional_chain": [
            "POLICY-AS-CODE",
            "SCHEMA",
            "GRAPH CONSTRAINTS",
            "CI GATES",
            "REGISTRY",
            "RUNTIME",
            "EXECUTION",
            "AGENT",
            "DIGITAL TWIN",
            "EVIDENCE",
            "AUDIT",
            "DRIFT / LEARNING",
        ],
        "ci": ci,
        "success": {
            "execution": audit_record(success),
            "evidence": success.evidence,
            "provenance": success.provenance,
        },
        "denied_zero_height": {
            "execution": audit_record(denied_zero),
            "evidence": denied_zero.evidence,
        },
        "agent": {
            "allowed": audit_record(agent_ok),
            "invalid_input": audit_record(agent_denied),
            "llm_arithmetic": audit_record(llm_denied),
            "mutation": {
                "target": "policy",
                "decision": mutation.status,
                "reason": mutation.reason,
                "failed_rule": mutation.failed_rule,
            },
        },
        "twin": {
            "event": twin_result.twin_event,
            "knowledge_graph": twin.knowledge_graph(twin_result),
            "execution": audit_record(twin_result),
        },
        "drift": drift_report(runtime.executions),
        "evidence_log": store.events,
    }
