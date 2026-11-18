#!/usr/bin/env python3
"""Validate JSON data against a documented, deliberately limited schema subset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _matches_type(value: Any, expected: str) -> bool:
    checks = {
        "object": lambda item: isinstance(item, dict),
        "array": lambda item: isinstance(item, list),
        "string": lambda item: isinstance(item, str),
        "number": lambda item: isinstance(item, (int, float)) and not isinstance(item, bool),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "boolean": lambda item: isinstance(item, bool),
        "null": lambda item: item is None,
    }
    return expected in checks and checks[expected](value)


def _validate(value: Any, schema: dict[str, Any], path: str, errors: list[dict[str, str]]) -> None:
    expected = schema.get("type")
    if expected is not None:
        if not isinstance(expected, str) or not _matches_type(value, expected):
            errors.append({"path": path, "code": "type_mismatch", "message": f"Expected type {expected}."})
            return

    if "enum" in schema and value not in schema["enum"]:
        errors.append({"path": path, "code": "enum_mismatch", "message": "Value is not one of the allowed options."})

    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append({"path": path, "code": "min_length", "message": f"String is shorter than {schema['minLength']}."})
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append({"path": path, "code": "max_length", "message": f"String is longer than {schema['maxLength']}."})

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append({"path": path, "code": "minimum", "message": f"Number is below {schema['minimum']}."})
        if "maximum" in schema and value > schema["maximum"]:
            errors.append({"path": path, "code": "maximum", "message": f"Number is above {schema['maximum']}."})

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append({"path": f"{path}.{key}", "code": "required", "message": "Required property is missing."})
        for key, child in value.items():
            if key not in properties:
                if schema.get("additionalProperties") is False:
                    errors.append({"path": f"{path}.{key}", "code": "additional_property", "message": "Property is not allowed."})
                continue
            _validate(child, properties[key], f"{path}.{key}", errors)

    if isinstance(value, list) and "items" in schema:
        for index, item in enumerate(value):
            _validate(item, schema["items"], f"{path}[{index}]", errors)


def validate_json(data: Any, schema: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(schema, dict):
        raise TypeError("schema must be a JSON object")
    if "type" not in schema:
        raise ValueError("schema must declare a root type")
    errors: list[dict[str, str]] = []
    _validate(data, schema, "$", errors)
    return {
        "valid": not errors,
        "error_count": len(errors),
        "errors": errors,
        "schema_scope": "documented local subset; not a full JSON Schema implementation",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a JSON file against a supported schema subset.")
    parser.add_argument("data", help="Path to JSON data")
    parser.add_argument("schema", help="Path to JSON schema subset")
    parser.add_argument("--output", help="Optional JSON report path")
    args = parser.parse_args()

    try:
        data = json.loads(Path(args.data).read_text(encoding="utf-8"))
        schema = json.loads(Path(args.schema).read_text(encoding="utf-8"))
        report = validate_json(data, schema)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        parser.error(str(exc))

    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
