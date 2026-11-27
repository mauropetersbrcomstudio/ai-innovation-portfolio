# Multi-Agent Coordination — Bounded Handoffs

**Status: DEMO**

A deterministic coordinator for passing structured payloads between explicitly registered agent handlers. It enforces declared handoff relationships, per-agent invocation limits, and a global handoff budget.

## Capabilities

- Register named agent handlers with explicit permitted next-agent lists.
- Pass structured payloads through bounded handoffs.
- Enforce per-agent invocation limits and a global handoff limit.
- Stop on completion, human escalation, invalid status, unregistered agent, or handler error.
- Return a trace of agent execution and coordination events.

## Run tests

Requires Python 3.10+ and uses only the standard library.

```bash
python -m unittest discover -s tests -v
```

## Agent result contract

Handlers return a dictionary with one of these statuses:
- `HANDOFF` with `next_agent` and optional `payload`.
- `COMPLETED` when the request is finished.
- `ESCALATE` when a human must review.
Other statuses are treated as invalid and fail the coordination run.

## Boundaries

- Handlers are ordinary functions registered by the host; no LLM, autonomous agent loop, network call, or dynamic tool loading.
- Handoffs are sequential and in-process; no message broker, parallel execution, persistent memory, or crash recovery.
- The coordinator does not authenticate agents or users, enforce data-level permissions, or sanitize sensitive payloads.
- The host remains responsible for identity, policy enforcement, approval, durable audit storage, and safe handler behavior.
