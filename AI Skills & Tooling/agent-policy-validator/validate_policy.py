"""Validate a declarative agent policy manifest against explicit governance rules."""
from __future__ import annotations

from typing import Any


VALID_RISK = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


def validate_policy(policy: Any) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(policy, dict):
        return {"valid": False, "errors": ["Policy must be a JSON object"], "warnings": []}

    agents = policy.get("agents")
    if not isinstance(agents, list) or not agents:
        return {"valid": False, "errors": ["Policy requires a non-empty agents array"], "warnings": []}

    seen: set[str] = set()
    for index, agent in enumerate(agents):
        prefix = f"agents[{index}]"
        if not isinstance(agent, dict):
            errors.append(f"{prefix} must be an object")
            continue
        name = agent.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{prefix}.name must be a non-empty string")
        elif name in seen:
            errors.append(f"Duplicate agent name: {name}")
        else:
            seen.add(name)

        risk = agent.get("risk")
        if risk not in VALID_RISK:
            errors.append(f"{prefix}.risk must be one of {sorted(VALID_RISK)}")

        tools = agent.get("allowed_tools")
        if not isinstance(tools, list) or any(not isinstance(item, str) or not item.strip() for item in tools):
            errors.append(f"{prefix}.allowed_tools must be an array of non-empty tool names")
            tools = []
        if "*" in tools or "all" in [item.casefold() for item in tools]:
            errors.append(f"{prefix}.allowed_tools cannot grant wildcard access")

        approval_tools = agent.get("approval_required_for", [])
        if not isinstance(approval_tools, list) or any(item not in tools for item in approval_tools):
            errors.append(f"{prefix}.approval_required_for must be a subset of allowed_tools")
            approval_tools = []

        max_steps = agent.get("max_steps")
        if not isinstance(max_steps, int) or isinstance(max_steps, bool) or not 1 <= max_steps <= 100:
            errors.append(f"{prefix}.max_steps must be an integer from 1 to 100")

        if risk in {"HIGH", "CRITICAL"} and tools and not approval_tools:
            errors.append(f"{prefix} high-risk agent must require approval for at least one allowed tool")
        if risk == "CRITICAL" and tools:
            warnings.append(f"{prefix} critical-risk tools require independent human and system-level controls")

    return {"valid": not errors, "errors": errors, "warnings": warnings,
            "agents_checked": len(agents)}


if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Validate an agent governance policy JSON file.")
    parser.add_argument("policy", type=Path)
    args = parser.parse_args()
    policy = json.loads(args.policy.read_text(encoding="utf-8"))
    result = validate_policy(policy)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["valid"] else 1)
