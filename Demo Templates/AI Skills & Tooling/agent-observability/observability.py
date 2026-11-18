"""Structured JSONL event logging with recursive sensitive-key redaction."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SENSITIVE_KEY_TOKENS = frozenset({
    "password", "passwd", "passphrase", "secret", "token",
    "authorization", "credential", "credentials", "cookie", "jwt", "auth",
    "apikey", "privatekey", "clientsecret", "accesskey", "sessiontoken", "sessionid",
})
SENSITIVE_KEY_SEQUENCES = frozenset({
    "api_key", "private_key", "client_secret", "access_key",
    "session_token", "session_id",
})


def _is_sensitive_key(key: Any) -> bool:
    """Match known sensitive field names without matching unrelated substrings."""
    text = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", str(key))
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").casefold()
    parts = normalized.split("_") if normalized else []

    if any(part in SENSITIVE_KEY_TOKENS for part in parts):
        return True

    return any(
        "_".join(parts[index:index + 2]) in SENSITIVE_KEY_SEQUENCES
        for index in range(len(parts) - 1)
    )


def redact(value: Any, *, replacement: str = "[REDACTED]") -> Any:
    if isinstance(value, dict):
        cleaned = {}
        for key, item in value.items():
            if _is_sensitive_key(key):
                cleaned[key] = replacement
            else:
                cleaned[key] = redact(item, replacement=replacement)
        return cleaned
    if isinstance(value, list):
        return [redact(item, replacement=replacement) for item in value]
    if isinstance(value, tuple):
        return [redact(item, replacement=replacement) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise ValueError(f"Unsupported log value type: {type(value).__name__}")


class JsonlEventLogger:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def emit(self, event_type: str, *, level: str = "INFO", workflow_id: str | None = None,
             agent: str | None = None, details: dict[str, Any] | None = None) -> dict[str, Any]:
        if not isinstance(event_type, str) or not event_type.strip():
            raise ValueError("event_type must be a non-empty string")
        if not isinstance(level, str):
            raise ValueError("level must be a string")
        normalized_level = level.upper()
        if normalized_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError("Unsupported log level")
        if details is not None and not isinstance(details, dict):
            raise ValueError("details must be an object")
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "event_type": event_type,
            "level": normalized_level,
            "workflow_id": workflow_id,
            "agent": agent,
            "details": redact(details or {}),
        }
        line = json.dumps(event, ensure_ascii=False, sort_keys=True)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
        return event

    def read_events(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        events = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    item = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSONL record at line {line_number}") from exc
                if not isinstance(item, dict):
                    raise ValueError(f"JSONL record at line {line_number} must be an object")
                events.append(item)
        return events
