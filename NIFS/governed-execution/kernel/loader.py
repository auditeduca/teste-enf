"""Load a governed object pack from disk."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ObjectPackError(FileNotFoundError):
    pass


@dataclass(frozen=True)
class ObjectPack:
    object_id: str
    root: Path
    canonical: dict[str, Any]
    input_schema: dict[str, Any]
    fields: dict[str, Any]
    vocabulary: dict[str, Any]
    ontology: dict[str, Any]
    graph_constraints: dict[str, Any]
    policy: dict[str, Any]
    ci_gates: dict[str, Any]
    registry: dict[str, Any]
    runtime_assertions: dict[str, Any]
    agent: dict[str, Any]
    evidence_contract: dict[str, Any]
    twin_contract: dict[str, Any]
    licensing: dict[str, Any]


def objects_root() -> Path:
    return Path(__file__).resolve().parents[1] / "objects"


def load_object_pack(object_id: str = "CAL-IMC-001") -> ObjectPack:
    root = objects_root() / object_id
    if not root.is_dir():
        raise ObjectPackError(f"Object pack not found: {root}")

    def read(name: str) -> dict[str, Any]:
        path = root / name
        if not path.is_file():
            raise ObjectPackError(f"Missing contract: {path}")
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)

    licensing_path = objects_root() / "knowledge-licensing-registry.json"
    with licensing_path.open(encoding="utf-8") as handle:
        licensing = json.load(handle)

    return ObjectPack(
        object_id=object_id,
        root=root,
        canonical=read("canonical.json"),
        input_schema=read("input.schema.json"),
        fields=read("fields.json"),
        vocabulary=read("vocabulary.json"),
        ontology=read("ontology.json"),
        graph_constraints=read("graph-constraints.json"),
        policy=read("policy.json"),
        ci_gates=read("ci-gates.json"),
        registry=read("registry.json"),
        runtime_assertions=read("runtime-assertions.json"),
        agent=read("agent.json"),
        evidence_contract=read("evidence-contract.json"),
        twin_contract=read("twin-contract.json"),
        licensing=licensing,
    )
