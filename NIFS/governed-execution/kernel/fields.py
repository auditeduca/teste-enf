"""Universal field constraints shared by schema, API, runtime, and tests."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from .schema import SchemaViolation


def validate_fields(instance: dict[str, Any], fields: dict[str, Any]) -> None:
    catalog = fields.get("fields", fields)
    for name, spec in catalog.items():
        if spec.get("required") and name not in instance:
            raise SchemaViolation(f"$.{name} is required", f"$.{name}")
        if name not in instance:
            continue
        value = instance[name]
        if spec.get("nullable") is False and value is None:
            raise SchemaViolation(f"$.{name} is not nullable", f"$.{name}")
        if spec.get("datatype") in {"DECIMAL", "NUMBER"}:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise SchemaViolation(f"$.{name} must be decimal", f"$.{name}")
            number = Decimal(str(value))
            if "min_exclusive" in spec and number <= Decimal(str(spec["min_exclusive"])):
                raise SchemaViolation(
                    f"$.{name} must be > {spec['min_exclusive']}",
                    f"$.{name}",
                )
            scale = spec.get("scale")
            if scale is not None:
                exponent = number.as_tuple().exponent
                actual_scale = -exponent if isinstance(exponent, int) and exponent < 0 else 0
                if actual_scale > int(scale):
                    raise SchemaViolation(
                        f"$.{name} exceeds scale {scale}",
                        f"$.{name}",
                    )
