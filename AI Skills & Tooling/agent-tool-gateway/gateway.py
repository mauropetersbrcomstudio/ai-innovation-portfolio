"""Small allowlisted tool gateway with explicit contracts and audit events."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, Any]
    allowed_roles: tuple[str, ...]
    requires_approval: bool = False
    max_calls_per_session: int = 1


@dataclass
class Session:
    session_id: str
    role: str
    approved_tools: tuple[str, ...] = ()
    call_counts: dict[str, int] | None = None

    def __post_init__(self) -> None:
        if self.call_counts is None:
            self.call_counts = {}


def _matches_type(value: Any, expected: str) -> bool:
    checks = {
        "object": lambda v: isinstance(v, dict),
        "array": lambda v: isinstance(v, list),
        "string": lambda v: isinstance(v, str),
        "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
        "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
        "boolean": lambda v: isinstance(v, bool),
    }
    if expected not in checks:
        raise ValueError(f"Unsupported schema type: {expected}")
    return checks[expected](value)


def validate_arguments(arguments: Any, schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(arguments, dict):
        return ["Arguments must be an object"]
    if schema.get("type") != "object":
        return ["Tool schema root must declare type 'object'"]

    properties = schema.get("properties", {})
    required = schema.get("required", [])
    if not isinstance(properties, dict) or not isinstance(required, list):
        return ["Tool schema properties/required are invalid"]

    for field in required:
        if field not in arguments:
            errors.append(f"Missing required field: {field}")
    if schema.get("additionalProperties") is False:
        for field in arguments:
            if field not in properties:
                errors.append(f"Unexpected field: {field}")

    for field, value in arguments.items():
        rule = properties.get(field)
        if rule is None:
            continue
        expected = rule.get("type")
        if expected and not _matches_type(value, expected):
            errors.append(f"Field '{field}' must be {expected}")
            continue
        if isinstance(value, str):
            if "minLength" in rule and len(value) < rule["minLength"]:
                errors.append(f"Field '{field}' is shorter than minLength")
            if "maxLength" in rule and len(value) > rule["maxLength"]:
                errors.append(f"Field '{field}' exceeds maxLength")
            if "enum" in rule and value not in rule["enum"]:
                errors.append(f"Field '{field}' is not an allowed value")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if "minimum" in rule and value < rule["minimum"]:
                errors.append(f"Field '{field}' is below minimum")
            if "maximum" in rule and value > rule["maximum"]:
                errors.append(f"Field '{field}' exceeds maximum")
    return errors


class ToolGateway:
    """Dispatches only handlers explicitly registered by the application."""

    def __init__(self) -> None:
        self._specs: dict[str, ToolSpec] = {}
        self._handlers: dict[str, Callable[[dict[str, Any]], Any]] = {}
        self.audit_log: list[dict[str, Any]] = []

    def register(self, spec: ToolSpec, handler: Callable[[dict[str, Any]], Any]) -> None:
        if not spec.name or spec.name in self._specs:
            raise ValueError("Tool name must be non-empty and unique")
        if spec.max_calls_per_session < 1:
            raise ValueError("max_calls_per_session must be positive")
        if not callable(handler):
            raise ValueError("Handler must be callable")
        # Validate the schema shape before making the tool available.
        if spec.input_schema.get("type") != "object":
            raise ValueError("Tool input schema must be an object")
        self._specs[spec.name] = spec
        self._handlers[spec.name] = handler

    def get_tool_spec(self, tool_name: str) -> ToolSpec | None:
        """Return a registered tool contract for host-side policy alignment.

        The returned specification is intended for inspection. Callers should not
        mutate its nested input-schema dictionary.
        """
        return self._specs.get(tool_name)

    def invoke(self, tool_name: str, arguments: Any, session: Session) -> dict[str, Any]:
        event = {
            "session_id": session.session_id,
            "tool": tool_name,
            "role": session.role,
        }

        def deny(reason: str, errors: list[str] | None = None) -> dict[str, Any]:
            result = {"status": "DENIED", "reason": reason}
            if errors:
                result["validation_errors"] = errors
            self.audit_log.append({**event, **result})
            return result

        spec = self._specs.get(tool_name)
        if spec is None:
            return deny("TOOL_NOT_ALLOWLISTED")
        if spec.allowed_roles and session.role not in spec.allowed_roles:
            return deny("ROLE_NOT_ALLOWED")
        errors = validate_arguments(arguments, spec.input_schema)
        if errors:
            return deny("INVALID_ARGUMENTS", errors)
        if spec.requires_approval and tool_name not in session.approved_tools:
            return deny("HUMAN_APPROVAL_REQUIRED")
        count = session.call_counts.get(tool_name, 0)
        if count >= spec.max_calls_per_session:
            return deny("SESSION_CALL_LIMIT_REACHED")

        # Count an invocation attempt before entering application code. A handler may
        # perform a side effect and then raise, so counting only successful returns
        # would allow the same session to repeat a partially completed operation.
        session.call_counts[tool_name] = count + 1

        try:
            output = self._handlers[tool_name](dict(arguments))
        except Exception:
            result = {"status": "ERROR", "reason": "HANDLER_FAILED"}
            self.audit_log.append({**event, **result})
            return result

        result = {"status": "EXECUTED", "tool": tool_name, "output": output}
        # Keep potentially sensitive handler output out of the audit trail. The
        # caller receives the output; the audit event records only the outcome.
        self.audit_log.append({**event, "status": "EXECUTED"})
        return result
