# Agent Runtime Control Plane

**Status: DEMO**

A local control-plane reference for registering agents, managing lifecycle, enforcing explicit tool permissions and invocation limits, tracking health, opening human escalations, and producing a read-only audit projection.

## Run

Requires Python 3.10+ and uses only the standard library.

```bash
python -m unittest discover -s tests -v
```

## Capabilities

- Register agents with a role, explicit tool allowlist, approval-required tools, and invocation cap.
- Manage lifecycle transitions: REGISTERED → ACTIVE/RETIRED; ACTIVE → PAUSED/RETIRED; PAUSED → ACTIVE/RETIRED.
- Deny invocations unless the agent is active, healthy, authorized for the tool, within its invocation cap, and approved when required.
- Optionally enforce the Agent Security & Governance policy engine inside `invoke()` through an injected `authorization_check`; denials are recorded before any handler executes.
- In secured mode, each invocation must supply a host-authenticated principal, risk level, and matching approval evidence when policy requires it. Missing identity or failed authorization is denied by default.
- Record health reports; an UNHEALTHY report opens a persisted human escalation.
- Open and resolve human escalations exactly once through the exposed API.
- Produce a read-only per-agent audit report from the event table.

## Important boundaries

- The registry, escalation queue, and event log share one local SQLite database. The audit projection is read-only by API convention, not an independently secured or tamper-proof audit system.
- Without `authorization_check`, the runtime retains its legacy demo approval mechanism (`approved_tools`) and does not provide RBAC. Enable secured mode by injecting `SecurityPolicyEngine.authorize` from `AI Skills & Tooling/agent-security-governance`.
- In secured mode, the host must authenticate identities and construct trusted `Principal` objects. The policy engine's `authenticated` flag is a host assertion, not proof of identity. The host must also supply an authoritative approval verifier; this repository does not include an identity provider or cryptographic approval service.
- Handlers are registered in the host process. This is not a remote agent runtime, scheduler, sandbox, or distributed control plane.
- Health is based on explicit host-reported status; there is no automatic heartbeat monitor or timeout detector.
- Invocation limits are lifetime counters per registered agent, not rate limits or token/cost budgets.
- No LLM inference, external business integration, encryption, backup automation, tamper-evident audit storage, or production deployment is included.
