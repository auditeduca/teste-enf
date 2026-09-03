"""Governed runtime: identity, policy, schema, graph, assertions, then execution."""

from __future__ import annotations

from typing import Any

from .engine import DeterministicEngineError, evaluate_formula
from .evidence import EvidenceStore, provenance_chain
from .fields import validate_fields
from .graph import GraphViolation, validate_graph
from .loader import ObjectPack
from .models import Decision, ExecutionRequest, ExecutionResult
from .policy import evaluate_policy
from .schema import SchemaViolation, validate_schema
from .vocabulary import VocabularyViolation, validate_vocabulary


class GovernedRuntime:
    def __init__(self, pack: ObjectPack, store: EvidenceStore | None = None) -> None:
        self.pack = pack
        self.store = store or EvidenceStore()
        self.executions: list[ExecutionResult] = []
        self._seq = 0

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        result = ExecutionResult(
            status="DENIED",
            request=request,
            decision=Decision.deny("UNINITIALIZED"),
        )
        try:
            result.validation["identity"] = self._check_identity(request)
            result.validation["version"] = self._check_version(request)
            result.validation["vocabulary"] = self._check_vocabulary()
            result.validation["ontology"] = "PASS"
            result.validation["graph"] = self._check_graph()
            result.validation["schema"] = self._check_schema(request)
            result.validation["fields"] = self._check_fields(request)
            policy_decision = evaluate_policy(
                self.pack.policy,
                request,
                self.pack.canonical["formula"]["expression"],
            )
            result.validation["policy"] = "PASS" if policy_decision.allowed else "FAIL"
            if not policy_decision.allowed:
                result.decision = policy_decision
                return self._finalize(request, result, event_type="EXECUTION_DENIED")

            assertions = self._run_assertions(request, result)
            result.runtime_assertions = assertions
            failed = next((name for name, status in assertions.items() if status != "PASS"), None)
            if failed:
                result.decision = Decision.deny(
                    "RUNTIME_ASSERTION_FAILED",
                    failed_assertion=failed,
                )
                return self._finalize(request, result, event_type="EXECUTION_DENIED")

            output = self._calculate(request)
            result.result = output
            result.validation["evidence"] = "PASS"
            result.decision = Decision.allow()
            result.status = "EXECUTED"
            return self._finalize(request, result, event_type="CALCULATION_EXECUTED")
        except SchemaViolation as exc:
            result.validation.setdefault("schema", "FAIL")
            result.decision = Decision.deny("INVALID_INPUT", failed_assertion="RT-004", error=str(exc))
            return self._finalize(request, result, event_type="EXECUTION_DENIED")
        except (GraphViolation, VocabularyViolation, DeterministicEngineError) as exc:
            result.decision = Decision.deny(type(exc).__name__.replace("Violation", "").upper() + "_FAILED", error=str(exc))
            return self._finalize(request, result, event_type="EXECUTION_DENIED")

    def _finalize(self, request: ExecutionRequest, result: ExecutionResult, event_type: str) -> ExecutionResult:
        self._seq += 1
        result.execution_id = f"EXEC-{self._seq:06d}"
        pack_meta = {
            "policy": {"id": self.pack.policy["id"], "version": self.pack.policy["version"]},
            "schema_id": self.pack.canonical.get("schema_id", "SCHEMA-CAL-IMC-001"),
            "schema_version": self.pack.input_schema.get("version", "1.0.0"),
            "evidence_fields": self.pack.evidence_contract.get("required_fields", []),
        }
        result.evidence = self.store.capture(event_type, request, result, pack_meta)
        result.provenance = provenance_chain(result)
        self.executions.append(result)
        return result

    def _check_identity(self, request: ExecutionRequest) -> str:
        if request.calculator_id != self.pack.canonical["canonical_id"]:
            raise SchemaViolation("Unknown calculator identity")
        if self.pack.canonical.get("status") != "ACTIVE":
            raise SchemaViolation("Calculator is not ACTIVE")
        return "PASS"

    def _check_version(self, request: ExecutionRequest) -> str:
        approved = self.pack.registry["CAL-IMC-001"]["version"]
        if request.version != approved or request.version != self.pack.canonical["version"]:
            raise SchemaViolation("Calculator version is not approved in registry")
        return "PASS"

    def _check_vocabulary(self) -> str:
        validate_vocabulary(self.pack.canonical, self.pack.vocabulary)
        return "PASS"

    def _check_graph(self) -> str:
        validate_graph(self.pack.ontology, self.pack.graph_constraints)
        return "PASS"

    def _check_schema(self, request: ExecutionRequest) -> str:
        validate_schema(request.input, self.pack.input_schema)
        return "PASS"

    def _check_fields(self, request: ExecutionRequest) -> str:
        validate_fields(request.input, self.pack.fields)
        return "PASS"

    def _run_assertions(self, request: ExecutionRequest, result: ExecutionResult) -> dict[str, str]:
        registry = self.pack.registry["CAL-IMC-001"]
        checks = {
            "calculator_active": self.pack.canonical.get("status") == "ACTIVE",
            "version_approved": request.version == registry["version"],
            "policy_active": self.pack.policy.get("status") == "ACTIVE",
            "input_valid": result.validation.get("schema") == "PASS",
            "graph_valid": result.validation.get("graph") == "PASS",
            "deterministic_engine": request.engine == "DETERMINISTIC_CALC_ENGINE",
            "evidence_enabled": bool(self.pack.canonical.get("evidence", {}).get("required", True)),
        }
        mapping = {
            "RT-001": "calculator_active",
            "RT-002": "version_approved",
            "RT-003": "policy_active",
            "RT-004": "input_valid",
            "RT-005": "graph_valid",
            "RT-006": "deterministic_engine",
            "RT-007": "evidence_enabled",
        }
        declared = {item["id"]: item.get("name", mapping.get(item["id"], item["id"])) for item in self.pack.runtime_assertions.get("assertions", [])}
        out: dict[str, str] = {}
        for assertion_id, key in mapping.items():
            name = declared.get(assertion_id, key)
            out[name] = "PASS" if checks[key] else "FAIL"
        return out

    def _calculate(self, request: ExecutionRequest) -> dict[str, Any]:
        formula = self.pack.canonical["formula"]["expression"]
        value = evaluate_formula(formula, request.input)
        output = self.pack.canonical["outputs"][0]
        canonical_value = value
        decimals = self.pack.canonical.get("presentation", {}).get("decimals")
        presented = round(value, decimals) if decimals is not None else value
        return {
            output["id"]: canonical_value,
            "unit": output.get("unit", "kg/m2"),
            "presented": presented,
            "formula": formula,
        }
