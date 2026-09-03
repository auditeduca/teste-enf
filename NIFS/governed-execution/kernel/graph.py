"""Semantic graph constraints.

JSON Schema cannot see that a structurally valid calculator using temperature
as input is semantically invalid for BMI.
"""

from __future__ import annotations

from typing import Any


class GraphViolation(ValueError):
    def __init__(self, message: str, constraint_id: str | None = None) -> None:
        super().__init__(message)
        self.constraint_id = constraint_id
        self.message = message


def validate_graph(ontology: dict[str, Any], constraints: dict[str, Any]) -> None:
    statements = {(triple["subject"], triple["predicate"], triple["object"]) for triple in ontology.get("triples", [])}
    subject = ontology.get("subject")
    rdf_type = ontology.get("type")

    for constraint in constraints.get("constraints", []):
        cid = constraint.get("id")
        if constraint.get("target_class") and rdf_type != constraint["target_class"]:
            raise GraphViolation(
                f"Ontology type {rdf_type} does not match {constraint['target_class']}",
                cid,
            )
        for prop in constraint.get("properties", []):
            path = prop["path"]
            matches = [triple for triple in statements if triple[0] == subject and triple[1] == path]
            min_count = prop.get("minCount")
            if min_count is not None and len(matches) < min_count:
                raise GraphViolation(
                    f"{subject} {path} count {len(matches)} < minCount {min_count}",
                    cid,
                )
            required = set(prop.get("required_objects", []))
            present = {triple[2] for triple in matches}
            missing = required - present
            if missing:
                raise GraphViolation(
                    f"{subject} missing {path} objects: {sorted(missing)}",
                    cid,
                )
        forbidden = constraint.get("forbidden_input_objects", [])
        inputs = {triple[2] for triple in statements if triple[0] == subject and triple[1] == "cko:hasInput"}
        illegal = inputs.intersection(forbidden)
        if illegal:
            raise GraphViolation(
                f"{subject} has forbidden inputs: {sorted(illegal)}",
                cid,
            )
