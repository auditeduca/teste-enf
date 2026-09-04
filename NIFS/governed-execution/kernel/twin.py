"""Digital Twin as governed operational state, not a calculator."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .loader import ObjectPack
from .models import Actor, ExecutionRequest, ExecutionResult
from .runtime import GovernedRuntime
from .vocabulary import resolve_term


class DigitalTwin:
    def __init__(self, spec: dict[str, Any], pack: ObjectPack) -> None:
        self.spec = deepcopy(spec)
        self.pack = pack
        self.events: list[dict[str, Any]] = []

    @property
    def twin_id(self) -> str:
        return self.spec["twin_id"]

    def measurement(self, canonical_term: str) -> dict[str, Any]:
        measurements = self.spec["context"]["measurements"]
        for key, payload in measurements.items():
            if key == canonical_term or payload.get("concept") == canonical_term:
                return payload
        raise KeyError(canonical_term)

    def calculator_input(self) -> dict[str, Any]:
        mapping = self.pack.twin_contract["input_binding"]
        out: dict[str, Any] = {}
        for field_id, term in mapping.items():
            out[field_id] = self.measurement(term)["value"]
        return out

    def derive(self, runtime: GovernedRuntime, actor: Actor | None = None) -> ExecutionResult:
        actor = actor or Actor(type="HUMAN", id="TWIN-RUNTIME")
        request = ExecutionRequest(
            calculator_id=self.pack.canonical["canonical_id"],
            version=self.pack.canonical["version"],
            input=self.calculator_input(),
            actor=actor,
            mission=f"Derive observation for {self.twin_id}",
            twin_id=self.twin_id,
        )
        result = runtime.execute(request)
        if result.executed:
            bmi_term = resolve_term(self.pack.vocabulary, "bmi")
            event = {
                "event_type": "OBSERVATION_DERIVED",
                "twin_id": self.twin_id,
                "derived_observation": {
                    "concept": bmi_term["canonical_term"],
                    "value": result.result["bmi"],
                    "unit": result.result["unit"],
                },
                "derivation": {
                    "calculator": self.pack.canonical["canonical_id"],
                    "version": self.pack.canonical["version"],
                    "evidence_id": result.evidence["event_id"],
                    "kind": "DERIVED_OBSERVATION",
                },
            }
            self.events.append(event)
            result.twin_event = event
            self.spec.setdefault("context", {}).setdefault("derived", {})["body_mass_index"] = event["derived_observation"]
        return result

    def knowledge_graph(self, result: ExecutionResult) -> dict[str, Any]:
        return {
            "nodes": [
                {"id": self.twin_id, "type": "DigitalTwin"},
                {"id": "obs:body_weight", "type": "Observation", "value": self.measurement("body_weight")},
                {"id": "obs:body_height", "type": "Observation", "value": self.measurement("body_height")},
                {"id": self.pack.canonical["canonical_id"], "type": "ClinicalCalculator", "version": self.pack.canonical["version"]},
                {
                    "id": "obs:body_mass_index",
                    "type": "DerivedObservation",
                    "value": None if result.result is None else result.result["bmi"],
                },
                {"id": (result.evidence or {}).get("event_id"), "type": "Evidence"},
            ],
            "edges": [
                {"from": self.twin_id, "predicate": "hasObservation", "to": "obs:body_weight"},
                {"from": self.twin_id, "predicate": "hasObservation", "to": "obs:body_height"},
                {"from": "obs:body_weight", "predicate": "inputOf", "to": self.pack.canonical["canonical_id"]},
                {"from": "obs:body_height", "predicate": "inputOf", "to": self.pack.canonical["canonical_id"]},
                {"from": self.pack.canonical["canonical_id"], "predicate": "derives", "to": "obs:body_mass_index"},
                {"from": "obs:body_mass_index", "predicate": "supported_by", "to": (result.evidence or {}).get("event_id")},
            ],
        }
