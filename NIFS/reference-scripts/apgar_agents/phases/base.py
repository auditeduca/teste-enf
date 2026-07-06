"""Agente base por micro-fase Master Data APGAR."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class PhaseResult:
    phase_id: str
    name_pt: str
    search: dict = field(default_factory=dict)
    generate: dict = field(default_factory=dict)
    review: dict = field(default_factory=dict)
    validate: dict = field(default_factory=dict)
    ok: bool = False
    trace: list[str] = field(default_factory=list)


@dataclass
class PhaseAgent:
    phase_id: str
    name_pt: str
    search_fn: Callable[[], dict]
    generate_fn: Callable[[dict], dict]
    review_fn: Callable[[dict, dict], dict]
    validate_fn: Callable[[], dict]

    def run(self) -> PhaseResult:
        result = PhaseResult(phase_id=self.phase_id, name_pt=self.name_pt)
        result.search = self.search_fn()
        result.trace.append(f"search:{self.phase_id}")
        result.generate = self.generate_fn(result.search)
        result.trace.append(f"generate:{self.phase_id}")
        result.review = self.review_fn(result.search, result.generate)
        result.trace.append(f"review:{self.phase_id}:{result.review.get('decision', '?')}")
        result.validate = self.validate_fn()
        result.trace.append(f"validate:{self.phase_id}:{'pass' if result.validate.get('ok') else 'fail'}")
        result.ok = bool(result.validate.get("ok")) and result.review.get("decision") != "reject"
        return result
