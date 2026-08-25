"""Deterministic scoring for tool JSON (sum and arithmetic expression)."""

from __future__ import annotations

import ast
import operator
import re
from typing import Any, Mapping

_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
_UNARYOPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _as_number(value: Any) -> float:
    if value is None or value == "":
        return 0.0
    return float(value)


def score_of(inp: Mapping[str, Any], value: Any) -> float:
    """Return the numeric score of one input given a raw value."""
    if inp.get("type") == "select":
        for opt in inp.get("options") or []:
            if str(opt.get("value")) == str(value):
                if "score" in opt:
                    return _as_number(opt.get("score", 0))
                return _as_number(opt.get("value"))
        return 0.0
    return _as_number(value)


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARYOPS:
        return _UNARYOPS[type(node.op)](_eval_node(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        if isinstance(node.op, ast.Div) and right == 0:
            raise ZeroDivisionError("division by zero in formula")
        return float(_BINOPS[type(node.op)](left, right))
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    raise ValueError(f"unsupported expression node: {type(node).__name__}")


def safe_eval(expr: str) -> float:
    compact = expr.strip()
    if not compact or not re.fullmatch(r"[0-9+\-*/().\s]+", compact):
        raise ValueError(f"unsafe or empty expression: {expr!r}")
    tree = ast.parse(compact, mode="eval")
    return _eval_node(tree)


def compute(tool: Mapping[str, Any], values: Mapping[str, Any] | None = None) -> float:
    """Compute the tool result from input values (defaults used when omitted)."""
    calculator = tool.get("calculator") or {}
    inputs = calculator.get("inputs") or []
    formula = calculator.get("formula") or {}
    ftype = formula.get("type")
    if ftype in (None, "none"):
        raise ValueError(f"tool {tool.get('slug')!r} has no numeric formula")

    state: dict[str, Any] = {}
    for inp in inputs:
        key = inp["id"]
        if values and key in values:
            state[key] = values[key]
        else:
            state[key] = inp.get("defaultValue", 0)

    if ftype == "sum":
        return sum(score_of(inp, state.get(inp["id"])) for inp in inputs)
    if ftype == "expression":
        expr = formula.get("expression") or ""
        for inp in inputs:
            expr = re.sub(rf"\b{re.escape(inp['id'])}\b", str(score_of(inp, state.get(inp["id"]))), expr)
        return safe_eval(expr)
    raise ValueError(f"unsupported formula type: {ftype!r}")


def interpret(tool: Mapping[str, Any], total: float) -> dict[str, Any] | None:
    ranges = (tool.get("interpretation") or {}).get("ranges") or []
    for item in ranges:
        if _as_number(item.get("min")) <= total <= _as_number(item.get("max")):
            return dict(item)
    return None


def format_result(tool: Mapping[str, Any], total: float) -> str:
    decimals = int(((tool.get("calculator") or {}).get("formula") or {}).get("decimals") or 0)
    if decimals > 0:
        return f"{total:.{decimals}f}"
    return str(int(round(total)))
