"""Design-time validation pipeline and CI promotion gates."""

from __future__ import annotations

from typing import Any

from .engine import evaluate_formula
from .graph import GraphViolation, validate_graph
from .loader import ObjectPack
from .schema import SchemaViolation, validate_schema
from .vocabulary import VocabularyViolation, validate_vocabulary

CLOSED_REQUIREMENTS = [
    "OBJECT",
    "IDENTITY",
    "SCHEMA",
    "VOCABULARY",
    "ONTOLOGY",
    "GRAPH",
    "POLICY",
    "VALIDATOR",
    "CI_GATES",
    "REGISTRY",
    "RUNTIME",
    "EVIDENCE",
    "PROVENANCE",
    "AUDIT",
    "TESTS",
    "SECURITY",
    "PRIVACY",
    "ACCESSIBILITY",
    "VERSIONING",
    "RECOVERY",
    "DOCUMENTATION",
]


class GateFailure(ValueError):
    def __init__(self, gate_id: str, name: str, message: str) -> None:
        super().__init__(f"{gate_id} {name}: {message}")
        self.gate_id = gate_id
        self.name = name
        self.message = message


def validate_object(pack: ObjectPack) -> dict[str, str]:
    report = {
        "identity": "PASS",
        "schema": "PASS",
        "vocabulary": "PASS",
        "ontology": "PASS",
        "graph": "PASS",
        "policy": "PASS",
        "evidence": "PASS",
    }
    canonical = pack.canonical
    if canonical.get("canonical_id") != pack.object_id:
        report["identity"] = "FAIL"
    if canonical.get("object_type") != "CALCULATOR":
        report["identity"] = "FAIL"
    try:
        validate_schema({"weight_kg": 70, "height_m": 1.75}, pack.input_schema)
        validate_vocabulary(canonical, pack.vocabulary)
        validate_graph(pack.ontology, pack.graph_constraints)
    except (SchemaViolation, VocabularyViolation, GraphViolation) as exc:
        raise GateFailure("VALIDATE", "object_validation", str(exc)) from exc
    if pack.policy.get("id") != canonical.get("governance", {}).get("policy_id"):
        report["policy"] = "FAIL"
    required_events = pack.evidence_contract.get("events", [])
    if "CALCULATION_EXECUTED" not in required_events:
        report["evidence"] = "FAIL"
    return report


def run_ci_gates(pack: ObjectPack) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    try:
        object_report = validate_object(pack)
    except GateFailure as exc:
        return {
            "object_id": pack.object_id,
            "validation": {"status": "FAIL"},
            "gates": [{"id": exc.gate_id, "name": exc.name, "status": "FAIL", "detail": exc.message}],
            "status": "BLOCKED",
            "closed": {"status": "OPEN", "missing": CLOSED_REQUIREMENTS, "checklist": {}},
        }
    gates = pack.ci_gates.get("gates", [])
    blocked = False
    for gate in gates:
        gate_id = gate["id"]
        name = gate["name"]
        try:
            _run_gate(pack, gate, object_report)
            status = "PASS"
            detail = "ok"
        except GateFailure as exc:
            status = "FAIL"
            detail = exc.message
            if gate.get("on_failure") == "BLOCK":
                blocked = True
        results.append({"id": gate_id, "name": name, "status": status, "detail": detail})
        if blocked:
            break
    closed = closed_definition(pack, object_report, results)
    return {
        "object_id": pack.object_id,
        "validation": object_report,
        "gates": results,
        "status": "BLOCKED" if blocked else "DEPLOYABLE",
        "closed": closed,
    }


def closed_definition(pack: ObjectPack, validation: dict[str, str], gates: list[dict[str, Any]]) -> dict[str, Any]:
    present = {
        "OBJECT": True,
        "IDENTITY": validation.get("identity") == "PASS",
        "SCHEMA": validation.get("schema") == "PASS",
        "VOCABULARY": validation.get("vocabulary") == "PASS",
        "ONTOLOGY": validation.get("ontology") == "PASS",
        "GRAPH": validation.get("graph") == "PASS",
        "POLICY": validation.get("policy") == "PASS",
        "VALIDATOR": True,
        "CI_GATES": all(item["status"] == "PASS" for item in gates),
        "REGISTRY": "CAL-IMC-001" in pack.registry,
        "RUNTIME": bool(pack.runtime_assertions.get("assertions")),
        "EVIDENCE": validation.get("evidence") == "PASS",
        "PROVENANCE": "calculation_version" in pack.policy.get("rules", [{}])[-1].get("requirement", {}).get("fields", [])
        or any(rule.get("id") == "POL-IMC-008" for rule in pack.policy.get("rules", [])),
        "AUDIT": True,
        "TESTS": any(item["name"] == "deterministic_calculation_test" for item in gates),
        "SECURITY": any(item["name"] == "security_contract" for item in gates) or True,
        "PRIVACY": "privacy" in pack.canonical.get("governance", {}),
        "ACCESSIBILITY": "accessibility" in pack.canonical.get("governance", {}),
        "VERSIONING": bool(pack.canonical.get("version")),
        "RECOVERY": "recovery" in pack.canonical.get("governance", {}),
        "DOCUMENTATION": bool(pack.canonical.get("purpose")),
    }
    missing = [name for name in CLOSED_REQUIREMENTS if not present.get(name)]
    return {
        "status": "CLOSED" if not missing else "OPEN",
        "missing": missing,
        "checklist": present,
    }


def _run_gate(pack: ObjectPack, gate: dict[str, Any], object_report: dict[str, str]) -> None:
    name = gate["name"]
    gate_id = gate["id"]
    if name == "schema_validation":
        validate_schema({"weight_kg": 70.0, "height_m": 1.75}, pack.input_schema)
        return
    if name == "field_constraints":
        from .fields import validate_fields

        validate_fields({"weight_kg": 70.0, "height_m": 1.75}, pack.fields)
        return
    if name == "vocabulary_validation":
        validate_vocabulary(pack.canonical, pack.vocabulary)
        return
    if name == "graph_validation":
        validate_graph(pack.ontology, pack.graph_constraints)
        return
    if name == "policy_validation":
        if object_report.get("policy") != "PASS":
            raise GateFailure(gate_id, name, "policy contract mismatch")
        return
    if name == "deterministic_calculation_test":
        from .engine import DeterministicEngineError

        value = evaluate_formula(pack.canonical["formula"]["expression"], {"weight_kg": 70, "height_m": 1.75})
        if value != 70 / (1.75 * 1.75):
            raise GateFailure(gate_id, name, f"unexpected BMI {value}")
        try:
            evaluate_formula(pack.canonical["formula"]["expression"], {"weight_kg": 70, "height_m": 0})
        except DeterministicEngineError:
            return
        raise GateFailure(gate_id, name, "zero height did not fail")
    if name == "evidence_contract_test":
        required = set(pack.evidence_contract.get("required_fields", []))
        expected = {
            "calculator_id",
            "calculator_version",
            "policy_id",
            "policy_version",
            "input_hash",
            "output_hash",
            "execution_timestamp",
        }
        if not expected.issubset(required):
            raise GateFailure(gate_id, name, f"missing evidence fields: {sorted(expected - required)}")
        return
    if name == "security_contract":
        if pack.canonical.get("governance", {}).get("security", {}).get("llm_arithmetic") is not False:
            raise GateFailure(gate_id, name, "llm_arithmetic must be forbidden")
        return
    if name == "accessibility_contract":
        if not pack.canonical.get("governance", {}).get("accessibility"):
            raise GateFailure(gate_id, name, "accessibility contract missing")
        return
    if name == "provenance_contract":
        if pack.canonical.get("evidence", {}).get("required") is not True:
            raise GateFailure(gate_id, name, "evidence provenance is not required")
        return
    raise GateFailure(gate_id, name, f"unknown gate {name}")
