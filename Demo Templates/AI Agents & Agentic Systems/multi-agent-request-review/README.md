# Multi-Agent Request Review

**Status: DEMO**

A small deterministic multi-agent demonstration built on the reusable Agent Coordination utility. An intake agent validates the request and hands it to a policy-review agent. The review agent routes only three explicitly supported categories; all other categories are escalated.

## Run

Requires Python 3.10+ and uses only the standard library. From this directory:

```bash
python agent.py --request "Need access to the reporting workspace" --category access
python agent.py --request "Need a legal interpretation" --category legal
```

## Architecture

- **Intake agent:** checks that request text is present and forwards a structured payload.
- **Policy review agent:** accepts only `access`, `procurement`, or `support`; other categories require human review.
- **Coordinator:** enforces the registered handoff path and a one-handoff budget.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Boundaries

- Deterministic rules only; no LLM inference or autonomous planning.
- Routing is illustrative and does not represent a real company policy.
- No ticket, procurement request, or access permission is created or changed.
- No external integrations, durable memory, or authentication.
