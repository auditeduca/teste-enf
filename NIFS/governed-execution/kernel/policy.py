"""Policy-as-code evaluator.

Policy is not documentation. Policy is executable code.
"""

from __future__ import annotations

import ast
import operator
from typing import Any

from .models import Decision, ExecutionRequest

COMPARE_OPS = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}


class PolicyError(ValueError):
    pass


def evaluate_policy(policy: dict[str, Any], request: ExecutionRequest, formula: str) -> Decision:
    if policy.get("status") != "ACTIVE":
        return Decision.deny("POLICY_INACTIVE", failed_rule=policy.get("id"), status=policy.get("status"))

    applies = policy.get("applies_to", {})
    if applies.get("object_type") and applies.get("object_type") != "CALCULATOR":
        return Decision.deny("POLICY_OBJECT_TYPE_MISMATCH", failed_rule=policy.get("id"))
    if applies.get("object_id") and applies.get("object_id") != request.calculator_id:
        return Decision.deny("POLICY_OBJECT_MISMATCH", failed_rule=policy.get("id"))

    for rule in policy.get("rules", []):
        decision = _evaluate_rule(rule, request, formula)
        if not decision.allowed:
            return decision
    return Decision.allow(policy_id=policy.get("id"), policy_version=policy.get("version"))


def _evaluate_rule(rule: dict[str, Any], request: ExecutionRequest, formula: str) -> Decision:
    rule_id = rule.get("id", "UNKNOWN")
    rule_type = rule.get("type")
    condition = rule.get("condition") or {}
    requirement = rule.get("requirement") or {}

    if rule_type == "obligation" and "field" in condition and condition.get("required"):
        field = condition["field"]
        if field not in request.input or request.input[field] is None:
            return Decision.deny("MISSING_REQUIRED_FIELD", failed_rule=rule_id, field=field)

    if rule_type == "prohibition" and "expression" in condition:
        if _eval_bool(condition["expression"], request.input):
            return Decision.deny(
                "POLICY_PROHIBITION",
                failed_rule=rule_id,
                expression=condition["expression"],
            )

    if rule_type == "prohibition" and condition.get("calculation_engine"):
        forbidden = condition["calculation_engine"]
        if request.engine == forbidden or request.engine == "LLM":
            return Decision.deny("LLM_ARITHMETIC_FORBIDDEN", failed_rule=rule_id, engine=request.engine)

    if rule_type == "obligation" and requirement.get("formula"):
        expected = _normalize_expr(requirement["formula"])
        actual = _normalize_expr(formula)
        if expected != actual:
            return Decision.deny(
                "FORMULA_MISMATCH",
                failed_rule=rule_id,
                expected=requirement["formula"],
                actual=formula,
            )

    if rule_type == "obligation" and requirement.get("evidence_event"):
        return Decision.allow()

    if rule_type == "obligation" and requirement.get("fields"):
        return Decision.allow()

    return Decision.allow()


def _normalize_expr(expression: str) -> str:
    return "".join(expression.split())


def _eval_bool(expression: str, names: dict[str, Any]) -> bool:
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise PolicyError(f"Invalid policy expression: {expression}") from exc
    return bool(_eval_node(tree.body, names))


def _eval_node(node: ast.AST, names: dict[str, Any]) -> Any:
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, names)
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        if node.id not in names:
            return None
        return names[node.id]
    if isinstance(node, ast.Compare):
        left = _eval_node(node.left, names)
        for op, comparator in zip(node.ops, node.comparators):
            if type(op) not in COMPARE_OPS:
                raise PolicyError(f"Disallowed comparison: {type(op).__name__}")
            right = _eval_node(comparator, names)
            if left is None or right is None:
                return False
            if not COMPARE_OPS[type(op)](left, right):
                return False
            left = right
        return True
    if isinstance(node, ast.BoolOp):
        values = [_eval_node(v, names) for v in node.values]
        if isinstance(node.op, ast.And):
            return all(values)
        if isinstance(node.op, ast.Or):
            return any(values)
    raise PolicyError(f"Disallowed policy node: {type(node).__name__}")
