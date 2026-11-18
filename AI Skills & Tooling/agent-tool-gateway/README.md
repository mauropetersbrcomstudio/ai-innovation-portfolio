# Agent Tool Gateway — Allowlisting & Permission Controls

**Status: DEMO**

A small Python component that mediates calls from an agent or workflow to application-registered tool handlers. It applies an explicit allowlist, role policy, argument contract, optional human approval, per-session call limits, and an in-memory audit trail.

## Capabilities

- Register named tools with an object input contract.
- Reject unregistered tool names.
- Enforce configured role allowlists.
- Validate required fields, primitive types, unknown fields, string lengths, enums, and numeric bounds.
- Require an explicit approval marker for selected tools.
- Limit calls per tool per session.
- Record successful calls and denials in an in-memory audit log.
- Return generic handler errors without exposing exception details.

## Run tests

Requires Python 3.10+ and uses only the standard library.

```bash
python -m unittest discover -s tests -v
```

## Integration pattern

The host application registers a handler function for each approved capability. The gateway does not discover functions, import tools dynamically, execute shell commands, or create network connections. The host application remains responsible for authenticating the user, deriving the trusted role, collecting human approval, implementing the handler safely, and persisting audit events when durable records are required.

See [test_gateway.py](./tests/test_gateway.py) for a simulated ticket-creation handler.

## Security boundaries and limitations

- The role and approved-tool list in `Session` are supplied by the caller. They are not authentication or proof of human approval; production hosts must populate them from trusted identity and approval systems.
- The audit log is in memory only and is lost when the process exits.
- The input contract supports a deliberately small subset of schema checks; it is not a full JSON Schema validator.
- Handler side effects are outside this component's control. The gateway cannot roll back a handler that partially executes before failing.
- No real ticket is created by the included example. No CRM, email, browser, shell, or external API integration is included.
- This is a reference component, not a complete security sandbox or production authorization service.
