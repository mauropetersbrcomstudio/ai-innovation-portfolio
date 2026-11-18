# Governed Agent Execution

**Status: DEMO**

A runnable integration that composes three existing portfolio foundations:

- Agent Policy Validator — rejects invalid policy manifests before workflow execution.
- Agent Tool Gateway — enforces registered tools, role allowlists, argument contracts, approval gates, and per-session call limits.
- Agent Execution & Orchestration — runs the bounded workflow and records execution events.

## Run

Requires Python 3.10+ and uses only the standard library.

From this directory:

```bash
python -m unittest discover -s tests -v
```

Run a simple approved example:

```bash
python -c "from governed_execution import run_governed_execution; print(run_governed_execution('Review support request', approved=True))"
```

## Demonstrated controls

1. Invalid policy is rejected before a workflow or tool can run.
2. Missing approval is denied by the tool gateway.
3. A role outside the tool allowlist is denied.
4. Only an authorized, approved session reaches the simulated tool handler.
5. The orchestrator marks denied execution as failed rather than treating the denial as success.

## Boundaries

- This is a deterministic integration demo, not an LLM-powered agent.
- Policy validation checks a documented manifest subset; it is not a full policy engine.
- The role and approval values are caller-supplied demo inputs, not authenticated identity or cryptographic approval.
- The simulated action is held in process memory and does not contact external systems.
- This example does not claim production security, durable audit storage, or deployment readiness.
