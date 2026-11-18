# Bounded Support Workflow Agent

**Status: DEMO**

A small reference agent that composes two reusable portfolio components: the Agent Orchestration framework and Agent Tool Gateway. It validates a synthetic support request, pauses before a side-effecting tool, and only proceeds when the host supplies an approval signal and the caller has an allowed role.

## Run

Requires Python 3.10+ and uses only the standard library. Run from this directory:

```bash
python agent.py --subject "Cannot access account"
python agent.py --subject "Cannot access account" --priority urgent --approve
```

The first command pauses at the approval gate. The second simulates host-provided approval and completes a mock ticket action.

## Architecture

1. **Assessment:** validates required subject and priority.
2. **Orchestration:** controls sequence and approval pause.
3. **Tool gateway:** checks allowlist, role, input contract, approval marker, and session call limit.
4. **Audit:** captures the simulated tool decision and workflow lifecycle events.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Boundaries

- The ticket handler is simulated and returns a fixed demo identifier; no real ticket is created.
- `--approve` is a demonstration input, not a secure approval mechanism. A real host must authenticate the approver and supply trusted approval evidence.
- The role is a demo input, not authenticated identity.
- Workflow state and audit events are in memory only.
- No LLM, CRM, email, external API, database, or production support integration.
- This demonstrates composition of the portfolio components, not production readiness or autonomous operation.
