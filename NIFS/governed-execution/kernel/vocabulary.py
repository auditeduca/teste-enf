"""Controlled vocabulary resolution for calculator fields."""

from __future__ import annotations

from typing import Any


class VocabularyViolation(ValueError):
    pass


def validate_vocabulary(canonical: dict[str, Any], vocabulary: dict[str, Any]) -> None:
    terms = vocabulary.get("terms", vocabulary)
    required_ids = [item["id"] for item in canonical.get("inputs", [])]
    required_ids.extend(item["id"] for item in canonical.get("outputs", []))
    for field_id in required_ids:
        if field_id not in terms:
            raise VocabularyViolation(f"Field {field_id} is missing from vocabulary")
        term = terms[field_id]
        if "canonical_term" not in term or "unit" not in term:
            raise VocabularyViolation(f"Vocabulary term {field_id} is incomplete")


def resolve_term(vocabulary: dict[str, Any], field_id: str) -> dict[str, Any]:
    terms = vocabulary.get("terms", vocabulary)
    if field_id not in terms:
        raise VocabularyViolation(f"Unknown term: {field_id}")
    return terms[field_id]
