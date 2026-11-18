# Agent Tool Gateway — Allowlisting & Permission Controls

**Status: DEMO**

A small Python component that mediates calls from an agent or workflow to application-registered tool handlers. It applies an explicit tool allowlist, caller-supplied role checks, argument contracts, an optional approval marker, per-session invocation limits, and an in-memory audit trail.

## Capabilities

- Register named tools with an object input contract.
- Reject unregistered tool names.
- Enforce configured role allowlists.
- Validate required fields, primitive types, unknown fields, string lengths, enums, and numeric bounds.
- Require an explicit approval marker for selected tools.
- Limit invocation attempts per tool and session, including attempts whose handler raises an error.
- Record successful calls and denials without copying handler output into the audit trail.
- Return generic handler errors without exposing exception details.

## Run tests

Requires Python 3.10+ and uses only the standard library.

```bash
python -m unittest discover -s tests -v
```

## Integration pattern

The host application registers a handler function for each approved capability. The gateway does not discover functions, import tools dynamically, execute shell commands, or create network connections.

For a governed host flow, authenticate the principal first, then call [Agent Security & Governance](../agent-security-governance/) to evaluate the principal, agent, tool, risk, and any separately verified approval. Dispatch only when that policy decision is allowed. The gateway's `Session.role` and `approved_tools` values are caller-supplied checks; they are not proof of identity or authoritative human approval. Do not treat the gateway alone as an authentication or authorization boundary.

The host remains responsible for trusted identity, approval collection and verification, safe handler implementation, transaction/idempotency behavior, and durable audit storage.

See [test_gateway.py](./tests/test_gateway.py) for a simulated ticket handler.

## Security boundaries and limitations

- The role and approved-tool list in `Session` are supplied by the caller. They are not authentication or proof of human approval; production hosts must populate them from trusted context.
- Invocation limits count attempts once a handler is entered. The counter belongs to the in-memory `Session` object: creating a new object resets it, so it is not a durable quota or abuse-prevention boundary. A handler may still perform a partial side effect before raising; the gateway cannot roll it back. Real handlers need appropriate transaction or idempotency controls.
- The audit log is in memory only and is lost when the process exits. It records the invocation outcome but deliberately excludes handler output; the returned result still goes to the caller.
- The input contract supports a deliberately small subset of schema checks; it is not a full JSON Schema validator.
- Handler side effects are outside this component's control.
- No real ticket is created by the included example. No CRM, email, browser, shell, or external API integration is included.
- This is a reference component, not a complete security sandbox or production authorization service.
