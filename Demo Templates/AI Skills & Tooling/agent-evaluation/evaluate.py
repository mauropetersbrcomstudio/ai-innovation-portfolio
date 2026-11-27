"""Scenario-based evaluator for structured agent outputs and safety invariants."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def evaluate(actual: dict[str, Any], expectations: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    expected_status = expectations.get("status")
    if expected_status is not None:
        check("status", actual.get("status") == expected_status,
              f"expected {expected_status!r}, got {actual.get('status')!r}")

    for field, expected in expectations.get("output_equals", {}).items():
        output = actual.get("output", {})
        check(f"output.{field}", isinstance(output, dict) and output.get(field) == expected,
              f"expected {field}={expected!r}")

    required_agents = expectations.get("required_agents", [])
    trace = actual.get("trace", [])
    seen_agents = [item.get("agent") for item in trace if isinstance(item, dict)]
    for agent in required_agents:
        check(f"agent:{agent}", agent in seen_agents, f"trace agents: {seen_agents}")

    forbidden_agents = expectations.get("forbidden_agents", [])
    for agent in forbidden_agents:
        check(f"forbidden-agent:{agent}", agent not in seen_agents, f"trace agents: {seen_agents}")

    required_events = expectations.get("required_events", [])
    events = actual.get("events", [])
    event_names = [item.get("event") for item in events if isinstance(item, dict)]
    for event in required_events:
        check(f"event:{event}", event in event_names, f"event names: {event_names}")

    forbidden_events = expectations.get("forbidden_events", [])
    for event in forbidden_events:
        check(f"forbidden-event:{event}", event not in event_names, f"event names: {event_names}")

    passed = all(item["passed"] for item in checks)
    return {
        "result": "PASS" if passed else "FAIL",
        "checks_passed": sum(1 for item in checks if item["passed"]),
        "checks_failed": sum(1 for item in checks if not item["passed"]),
        "checks": checks,
    }


def evaluate_files(actual_path: Path, expectations_path: Path) -> dict[str, Any]:
    actual = json.loads(actual_path.read_text(encoding="utf-8"))
    expectations = json.loads(expectations_path.read_text(encoding="utf-8"))
    if not isinstance(actual, dict) or not isinstance(expectations, dict):
        raise ValueError("Actual result and expectations must be JSON objects")
    return evaluate(actual, expectations)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate an agent JSON result against explicit expectations.")
    parser.add_argument("--actual", required=True, type=Path)
    parser.add_argument("--expectations", required=True, type=Path)
    args = parser.parse_args()
    result = evaluate_files(args.actual, args.expectations)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["result"] == "PASS" else 1)
