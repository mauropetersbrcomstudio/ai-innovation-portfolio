"""Bounded multi-agent handoff coordinator with explicit agent registry."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class AgentSpec:
    name: str
    allowed_next: tuple[str, ...]
    max_invocations: int = 1


class AgentCoordinator:
    def __init__(self, agents: dict[str, tuple[AgentSpec, Callable[[dict[str, Any]], dict[str, Any]]]],
                 *, max_handoffs: int = 5):
        if max_handoffs < 0:
            raise ValueError("max_handoffs cannot be negative")
        self.agents = agents
        self.max_handoffs = max_handoffs
        self.events: list[dict[str, Any]] = []

    def run(self, start_agent: str, request: dict[str, Any]) -> dict[str, Any]:
        counts: dict[str, int] = {}
        trace: list[dict[str, Any]] = []
        current = start_agent
        payload = dict(request)
        handoffs = 0

        while True:
            registered = self.agents.get(current)
            if registered is None:
                return self._finish("BLOCKED", "AGENT_NOT_REGISTERED", trace, payload)
            spec, handler = registered
            used = counts.get(current, 0)
            if used >= spec.max_invocations:
                return self._finish("BLOCKED", "AGENT_INVOCATION_LIMIT", trace, payload)
            counts[current] = used + 1
            self.events.append({"event": "AGENT_STARTED", "agent": current, "invocation": counts[current]})
            try:
                result = handler(dict(payload))
            except Exception:
                trace.append({"agent": current, "status": "ERROR"})
                return self._finish("FAILED", "AGENT_HANDLER_ERROR", trace, payload)
            if not isinstance(result, dict) or "status" not in result:
                trace.append({"agent": current, "status": "INVALID_RESULT"})
                return self._finish("FAILED", "INVALID_AGENT_RESULT", trace, payload)

            trace.append({"agent": current, "status": result["status"]})
            self.events.append({"event": "AGENT_FINISHED", "agent": current, "status": result["status"]})
            if result["status"] in {"COMPLETED", "ESCALATE"}:
                return self._finish(result["status"], result.get("reason", "AGENT_TERMINAL_RESULT"), trace, result)
            if result["status"] != "HANDOFF":
                return self._finish("FAILED", "UNSUPPORTED_AGENT_STATUS", trace, result)

            next_agent = result.get("next_agent")
            if not isinstance(next_agent, str) or next_agent not in spec.allowed_next:
                return self._finish("BLOCKED", "HANDOFF_NOT_ALLOWED", trace, result)
            if handoffs >= self.max_handoffs:
                return self._finish("BLOCKED", "HANDOFF_LIMIT_REACHED", trace, result)
            if next_agent not in self.agents:
                return self._finish("BLOCKED", "TARGET_AGENT_NOT_REGISTERED", trace, result)
            handoffs += 1
            self.events.append({"event": "AGENT_HANDOFF", "from": current, "to": next_agent, "handoff": handoffs})
            payload = dict(result.get("payload", {}))
            current = next_agent

    def _finish(self, status: str, reason: str, trace: list[dict[str, Any]], output: dict[str, Any]) -> dict[str, Any]:
        result = {"status": status, "reason": reason, "trace": trace, "output": output,
                  "events": list(self.events)}
        self.events.append({"event": "COORDINATION_FINISHED", "status": status, "reason": reason})
        return result
