"""LangGraph code review pipeline with DeepSeek API."""

from typing import Any


def __getattr__(name: str) -> Any:
    if name == "run_review_graph":
        from review.graph import run_review_graph

        return run_review_graph
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["run_review_graph"]
