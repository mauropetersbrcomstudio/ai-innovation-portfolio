# AI Agents & Agentic Systems

This section explores agents that interpret a request, decide what to do next, and operate within clearly defined boundaries. The demonstrations focus on practical controls: explicit action permissions, human review, traceable decisions, and safe handling of uncertain inputs.

## SME Operations Assistant

The [SME Operations Assistant](./sme-operations-assistant/) classifies a small set of business requests, checks proposed actions against an allowlist, and returns a traceable proposal. Actions are simulated; the demo does not connect to business systems or change records.

**Status: DEMO** — deterministic keyword classification, not an LLM-powered agent.

## SME Procurement Request Triage Agent

The [SME Procurement Request Triage Agent](./sme-procurement-request-triage/) validates synthetic purchase requests against a local policy file and routes them to manager, finance, executive, priority, or supplier review. It detects duplicate request IDs and records a decision trace.

**Status: DEMO** — deterministic policy-based routing. It never approves a purchase or creates a purchase order.

Both projects run locally and use no live company data or external integrations. Their READMEs describe setup, tests, assumptions, and limitations.
