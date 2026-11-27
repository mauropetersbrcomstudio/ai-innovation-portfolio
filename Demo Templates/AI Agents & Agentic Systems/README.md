# AI Agents & Agentic Systems

This section explores agents that interpret a request, decide what to do next, and operate within clearly defined boundaries. The demonstrations focus on practical controls: explicit action permissions, human review, traceable decisions, and safe handling of uncertain inputs.

## SME Operations Assistant

The [SME Operations Assistant](./sme-operations-assistant/) classifies a small set of business requests, checks proposed actions against an allowlist, and returns a traceable proposal. Actions are simulated; the demo does not connect to business systems or change records.

**Status: DEMO** — deterministic keyword classification, not an LLM-powered agent.

## SME Procurement Request Triage Agent

The [SME Procurement Request Triage Agent](./sme-procurement-request-triage/) validates synthetic purchase requests against a local policy file and routes them to manager, finance, executive, priority, or supplier review. It detects duplicate request IDs and records a decision trace.

**Status: DEMO** — deterministic policy-based routing. It never approves a purchase or creates a purchase order.

Both projects run locally and use no live company data or external integrations. Their READMEs describe setup, tests, assumptions, and limitations.

## Bounded Support Workflow Agent

The [Bounded Support Workflow Agent](./bounded-support-workflow-agent/) composes the portfolio's orchestration and tool-gateway components. It validates a synthetic support request, pauses for host-mediated approval, checks role and argument policy, and records workflow/tool events.

**Status: DEMO** — the ticket action is simulated; role and approval inputs are not production identity controls.

## Multi-Agent Request Review

The [Multi-Agent Request Review demo](./multi-agent-request-review/) demonstrates a bounded handoff from intake to policy review, with explicit category routing and human escalation for unsupported requests.

**Status: DEMO** — deterministic routing only; no external systems or autonomous planning.

## Agent Platform Reference Integration

The [Agent Platform Reference](./agent-platform-reference/) connects the portfolio's sequential orchestrator, SQLite state store, and structured JSONL observability utility in one runnable local workflow.

**Status: DEMO** — local deterministic integration; no external business system, LLM, or production security controls.

## Governed Agent Execution

The [Governed Agent Execution demo](./governed-agent-execution/) now includes a trusted-host adapter that connects the deny-by-default Agent Security & Governance engine to the allowlisted Agent Tool Gateway. The adapter accepts a host-authenticated principal, delegates approval verification to an injected verifier, checks policy/gateway configuration alignment, binds sessions to a subject and role, and prevents same-instance approval-ID replay before dispatching a simulated handler.

**Status: DEMO** — the adapter does not authenticate users or approvers. Its identity and approval verifier fixtures are synthetic; session, quota, replay, and audit state are in memory. The policy engine and gateway isolate their active authorization and dispatch contracts from later mutation of caller-owned mappings; host inspection methods return defensive snapshots.

## Durable Workflow Runner

The [Durable Workflow Runner](./durable-workflow-runner/) checkpoints each sequential step in SQLite, records events in SQLite and JSONL, skips completed steps on resume, and rejects a changed plan or context.

**Status: DEMO** — handlers with side effects must enforce the supplied idempotency key; the runner cannot guarantee exactly-once external execution.

## Agent Runtime Control Plane

The [Agent Runtime Control Plane](./agent-runtime-control-plane/) provides a local SQLite-backed registry, lifecycle transitions, explicit tool allowlists, approval gates, invocation caps, host-reported health, persisted human escalations, and a read-only audit projection.

**Status: DEMO** — caller-supplied identity and approval values; local database only; no independent tamper-proof audit or automatic heartbeat monitor.


## SME Internal Knowledge Assistant

The [SME Internal Knowledge Assistant](./sme-internal-knowledge-assistant/) is a deterministic local knowledge-retrieval demo with role-filtered source excerpts, citations, and human escalation. Role values are not authenticated identity; it does not use an LLM.

**Status: DEMO** — see the project README for exact run instructions, tests, data provenance, and limitations.
