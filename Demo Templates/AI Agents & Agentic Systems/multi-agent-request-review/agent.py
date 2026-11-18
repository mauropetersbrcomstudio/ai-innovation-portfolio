"""Synthetic multi-agent request review using the reusable bounded coordinator."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "AI Skills & Tooling" / "agent-coordination"))

from coordinator import AgentCoordinator, AgentSpec  # noqa: E402


def run_review(request: dict[str, Any]) -> dict[str, Any]:
    def intake(payload: dict[str, Any]) -> dict[str, Any]:
        text = payload.get("request")
        if not isinstance(text, str) or not text.strip():
            return {"status": "ESCALATE", "reason": "MISSING_REQUEST_TEXT"}
        return {
            "status": "HANDOFF",
            "next_agent": "policy_review",
            "payload": {"request": text.strip(), "category": payload.get("category", "general")},
        }

    def policy_review(payload: dict[str, Any]) -> dict[str, Any]:
        category = payload.get("category")
        if category not in {"access", "procurement", "support"}:
            return {"status": "ESCALATE", "reason": "CATEGORY_REQUIRES_HUMAN_REVIEW",
                    "request": payload["request"]}
        return {"status": "COMPLETED", "decision": "ROUTE_TO_HUMAN_QUEUE",
                "queue": category, "request": payload["request"],
                "notice": "Routing recommendation only; no external system was changed."}

    agents = {
        "intake": (AgentSpec("intake", ("policy_review",)), intake),
        "policy_review": (AgentSpec("policy_review", ()), policy_review),
    }
    return AgentCoordinator(agents, max_handoffs=1).run("intake", request)


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Run a synthetic multi-agent request review.")
    parser.add_argument("--request", required=True)
    parser.add_argument("--category", default="general")
    args = parser.parse_args()
    print(json.dumps(run_review({"request": args.request, "category": args.category}),
                     indent=2, ensure_ascii=False))
