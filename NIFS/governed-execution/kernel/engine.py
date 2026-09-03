"""Deterministic calculation engine.

LLM is never a calculation engine. Only a closed arithmetic AST is executed.
"""

from __future__ import annotations

import ast
import operator
from typing import Any

ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
ALLOWED_UNARY = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


class DeterministicEngineError(ValueError):
    pass


def evaluate_formula(expression: str, inputs: dict[str, Any]) -> float:
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise DeterministicEngineError(f"Invalid formula syntax: {expression}") from exc
    value = _eval_node(tree.body, inputs)
    if not isinstance(value, (int, float)):
        raise DeterministicEngineError("Formula did not evaluate to a number")
    if isinstance(value, bool) or value != value or value in (float("inf"), float("-inf")):
        raise DeterministicEngineError("Non-finite calculation result")
    return float(value)


def _eval_node(node: ast.AST, names: dict[str, Any]) -> float:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return float(node.value)
        raise DeterministicEngineError("Only numeric literals are allowed")
    if isinstance(node, ast.Name):
        if node.id not in names:
            raise DeterministicEngineError(f"Unknown identifier: {node.id}")
        value = names[node.id]
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise DeterministicEngineError(f"Identifier {node.id} is not numeric")
        return float(value)
    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_BINOPS:
        left = _eval_node(node.left, names)
        right = _eval_node(node.right, names)
        if isinstance(node.op, ast.Div) and right == 0:
            raise DeterministicEngineError("Division by zero")
        return float(ALLOWED_BINOPS[type(node.op)](left, right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_UNARY:
        return float(ALLOWED_UNARY[type(node.op)](_eval_node(node.operand, names)))
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, names)
    raise DeterministicEngineError(f"Disallowed expression node: {type(node).__name__}")
