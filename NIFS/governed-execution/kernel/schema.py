"""Minimal JSON Schema validator for governed calculator inputs."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any


class SchemaViolation(ValueError):
    def __init__(self, message: str, path: str = "$") -> None:
        super().__init__(message)
        self.path = path
        self.message = message


def validate_schema(instance: Any, schema: dict[str, Any], path: str = "$") -> None:
    expected_type = schema.get("type")
    if expected_type == "object":
        if not isinstance(instance, dict):
            raise SchemaViolation(f"{path} must be an object", path)
        required = schema.get("required", [])
        for field in required:
            if field not in instance:
                raise SchemaViolation(f"{path}.{field} is required", f"{path}.{field}")
        if schema.get("additionalProperties") is False:
            allowed = set(schema.get("properties", {}))
            extra = set(instance) - allowed
            if extra:
                raise SchemaViolation(
                    f"{path} has additional properties: {sorted(extra)}",
                    path,
                )
        for key, subschema in schema.get("properties", {}).items():
            if key in instance:
                validate_schema(instance[key], subschema, f"{path}.{key}")
        return
    if expected_type == "number":
        if isinstance(instance, bool) or not isinstance(instance, (int, float)):
            raise SchemaViolation(f"{path} must be a number", path)
        number = Decimal(str(instance))
        if "exclusiveMinimum" in schema and number <= Decimal(str(schema["exclusiveMinimum"])):
            raise SchemaViolation(
                f"{path} must be > {schema['exclusiveMinimum']}",
                path,
            )
        if "minimum" in schema and number < Decimal(str(schema["minimum"])):
            raise SchemaViolation(f"{path} must be >= {schema['minimum']}", path)
        if "maximum" in schema and number > Decimal(str(schema["maximum"])):
            raise SchemaViolation(f"{path} must be <= {schema['maximum']}", path)
        if "exclusiveMaximum" in schema and number >= Decimal(str(schema["exclusiveMaximum"])):
            raise SchemaViolation(
                f"{path} must be < {schema['exclusiveMaximum']}",
                path,
            )
        if "multipleOf" in schema and not _is_multiple_of(number, Decimal(str(schema["multipleOf"]))):
            raise SchemaViolation(
                f"{path} must be a multiple of {schema['multipleOf']}",
                path,
            )
        return
    if expected_type == "string":
        if not isinstance(instance, str):
            raise SchemaViolation(f"{path} must be a string", path)
        return
    if expected_type == "boolean":
        if not isinstance(instance, bool):
            raise SchemaViolation(f"{path} must be a boolean", path)
        return
    if expected_type == "array":
        if not isinstance(instance, list):
            raise SchemaViolation(f"{path} must be an array", path)
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(instance):
                validate_schema(item, item_schema, f"{path}[{index}]")


def _is_multiple_of(value: Decimal, multiple: Decimal) -> bool:
    if multiple == 0:
        return False
    try:
        quotient = value / multiple
    except InvalidOperation:
        return False
    return quotient == quotient.to_integral_value()
