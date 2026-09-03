"""End-to-end tests for the CAL-IMC-001 governed execution example."""

from __future__ import annotations

import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kernel.agent import GovernedAgent
from kernel.ci import run_ci_gates
from kernel.engine import DeterministicEngineError, evaluate_formula
from kernel.graph import GraphViolation, validate_graph
from kernel.loader import load_object_pack
from kernel.models import Actor, ExecutionRequest
from kernel.runtime import GovernedRuntime
from kernel.schema import SchemaViolation, validate_schema
from kernel.scenario import run_imc_scenario


class BmiEngineTests(unittest.TestCase):
    def test_golden_formula(self) -> None:
        result = evaluate_formula("weight_kg / (height_m * height_m)", {"weight_kg": 70, "height_m": 1.75})
        self.assertEqual(result, 22.857142857142858)

    def test_zero_height_is_invalid(self) -> None:
        with self.assertRaises(DeterministicEngineError):
            evaluate_formula("weight_kg / (height_m * height_m)", {"weight_kg": 70, "height_m": 0})

    def test_negative_weight_evaluates_but_runtime_rejects(self) -> None:
        value = evaluate_formula("weight_kg / (height_m * height_m)", {"weight_kg": -70, "height_m": 1.75})
        self.assertLess(value, 0)

    def test_llm_ast_call_is_rejected(self) -> None:
        with self.assertRaises(DeterministicEngineError):
            evaluate_formula("__import__('os').system('echo pwned')", {})


class SchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = load_object_pack().input_schema

    def test_negative_weight_is_schema_violation(self) -> None:
        with self.assertRaises(SchemaViolation):
            validate_schema({"weight_kg": -5, "height_m": 1.75}, self.schema)

    def test_zero_height_is_schema_violation(self) -> None:
        with self.assertRaises(SchemaViolation):
            validate_schema({"weight_kg": 70, "height_m": 0}, self.schema)

    def test_additional_property_is_schema_violation(self) -> None:
        with self.assertRaises(SchemaViolation):
            validate_schema({"weight_kg": 70, "height_m": 1.75, "temperature": 37}, self.schema)


class GraphTests(unittest.TestCase):
    def test_temperature_input_is_graph_violation(self) -> None:
        pack = load_object_pack()
        ontology = deepcopy(pack.ontology)
        ontology["triples"] = [
            triple
            for triple in ontology["triples"]
            if not (triple["predicate"] == "cko:hasInput" and triple["object"] == "cko:BodyWeight")
        ]
        ontology["triples"].append(
            {
                "subject": "cko:CAL-IMC-001",
                "predicate": "cko:hasInput",
                "object": "cko:BodyTemperature",
            }
        )
        with self.assertRaises(GraphViolation):
            validate_graph(ontology, pack.graph_constraints)


class RuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.pack = load_object_pack()
        self.runtime = GovernedRuntime(self.pack)
        self.actor = Actor(type="HUMAN", id="NURSE-001")

    def test_successful_execution_emits_evidence_and_provenance(self) -> None:
        result = self.runtime.execute(
            ExecutionRequest(
                calculator_id="CAL-IMC-001",
                version="1.0.0",
                input={"weight_kg": 70, "height_m": 1.75},
                actor=self.actor,
                mission="Calculate BMI",
            )
        )
        self.assertTrue(result.executed)
        self.assertEqual(result.result["bmi"], 22.857142857142858)
        self.assertEqual(result.result["presented"], 22.9)
        self.assertEqual(result.evidence["event_type"], "CALCULATION_EXECUTED")
        self.assertTrue(result.evidence["input_hash"].startswith("sha256:"))
        self.assertTrue(result.evidence["output_hash"].startswith("sha256:"))
        self.assertEqual(result.evidence["evidence_contract"], "SATISFIED")
        self.assertEqual(result.provenance["chain"][0]["kind"], "Policy")
        self.assertEqual(result.validation["schema"], "PASS")
        self.assertEqual(result.runtime_assertions["deterministic_engine"], "PASS")

    def test_zero_height_is_denied_with_evidence(self) -> None:
        result = self.runtime.execute(
            ExecutionRequest(
                calculator_id="CAL-IMC-001",
                version="1.0.0",
                input={"weight_kg": 70, "height_m": 0},
                actor=self.actor,
            )
        )
        self.assertEqual(result.status, "DENIED")
        self.assertEqual(result.decision.reason, "INVALID_INPUT")
        self.assertEqual(result.evidence["event_type"], "EXECUTION_DENIED")
        self.assertIsNone(result.result)

    def test_llm_engine_is_denied(self) -> None:
        result = self.runtime.execute(
            ExecutionRequest(
                calculator_id="CAL-IMC-001",
                version="1.0.0",
                input={"weight_kg": 70, "height_m": 1.75},
                actor=self.actor,
                engine="LLM",
            )
        )
        self.assertEqual(result.status, "DENIED")
        self.assertEqual(result.decision.reason, "LLM_ARITHMETIC_FORBIDDEN")
        self.assertEqual(result.decision.failed_rule, "POL-IMC-006")


class AgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.pack = load_object_pack()
        self.runtime = GovernedRuntime(self.pack)
        self.agent = GovernedAgent(self.pack, self.runtime)

    def test_agent_may_use_but_not_modify_policy(self) -> None:
        allowed = self.agent.invoke("Calcule o IMC.", {"weight_kg": 70, "height_m": 1.75})
        self.assertTrue(allowed.executed)
        self.assertEqual(allowed.request.actor.type, "AGENT")
        mutation = self.agent.attempt_mutation("policy")
        self.assertEqual(mutation.reason, "AGENT_MUTATION_FORBIDDEN")
        self.assertEqual(mutation.failed_rule, "cannot_modify_policy")

    def test_agent_invalid_input_is_denied_with_evidence(self) -> None:
        result = self.agent.invoke("Calcule o IMC.", {"weight_kg": 70, "height_m": 0})
        self.assertEqual(result.status, "DENIED")
        self.assertEqual(result.evidence["event_type"], "EXECUTION_DENIED")
        self.assertEqual(result.evidence["actor"]["id"], "AGENT-NURSE-001")


class CiAndScenarioTests(unittest.TestCase):
    def test_ci_gates_are_deployable_and_closed(self) -> None:
        report = run_ci_gates(load_object_pack())
        self.assertEqual(report["status"], "DEPLOYABLE")
        self.assertEqual(report["closed"]["status"], "CLOSED")
        self.assertEqual(report["closed"]["missing"], [])
        self.assertTrue(all(gate["status"] == "PASS" for gate in report["gates"]))

    def test_full_scenario_covers_chain(self) -> None:
        scenario = run_imc_scenario()
        self.assertEqual(scenario["ci"]["status"], "DEPLOYABLE")
        self.assertEqual(scenario["success"]["execution"]["result"]["bmi"], 22.857142857142858)
        self.assertEqual(scenario["denied_zero_height"]["evidence"]["event_type"], "EXECUTION_DENIED")
        self.assertEqual(scenario["agent"]["mutation"]["reason"], "AGENT_MUTATION_FORBIDDEN")
        self.assertEqual(scenario["agent"]["llm_arithmetic"]["authorization"]["decision"], "DENY")
        self.assertEqual(scenario["twin"]["event"]["derived_observation"]["concept"], "body_mass_index")
        self.assertEqual(scenario["twin"]["event"]["derived_observation"]["value"], 22.857142857142858)
        self.assertEqual(scenario["twin"]["event"]["derivation"]["kind"], "DERIVED_OBSERVATION")
        predicates = {edge["predicate"] for edge in scenario["twin"]["knowledge_graph"]["edges"]}
        self.assertIn("derives", predicates)
        self.assertIn("supported_by", predicates)
        nanda = next(
            item
            for item in load_object_pack().licensing["entries"]
            if item["source_id"] == "NANDA-I"
        )
        self.assertEqual(nanda["status"], "REQUIRES_LICENSE")
        self.assertGreaterEqual(len(scenario["evidence_log"]), 5)
        self.assertIsNotNone(scenario["drift"]["signal"])


if __name__ == "__main__":
    unittest.main()
