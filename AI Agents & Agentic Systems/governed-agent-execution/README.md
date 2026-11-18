# Governed Agent Execution

**Status: DEMO**

A deterministic integration showing how a trusted application host can connect the portfolio's policy decision engine, allowlisted tool gateway, and bounded execution components.

The project includes:
- Agent Policy Validator — checks the documented policy-manifest format before execution.
- Agent Security & Governance — makes a deny-by-default authorization decision and delegates approval verification to an injected verifier.
- Governed Tool Host Adapter — derives the gateway session role and approval marker only after an allowed policy decision, binds an in-memory session to one subject and role, and blocks same-instance approval-ID replay.
- Agent Tool Gateway — checks registered tools, role allowlists, argument contracts, approval markers, and per-session invocation limits.
- Agent Execution & Orchestration — runs the existing bounded workflow example and records execution events.

## Run

Requires Python 3.10+ and uses only the standard library.

From this directory:

```bash
python -m unittest discover -s tests -v
```

Run the existing orchestration example:

```bash
python -c "from governed_execution import run_governed_execution; print(run_governed_execution('Review support request', approved=True))"
```

Run the trusted-host adapter with synthetic fixtures:

```bash
python -c "from host_adapter import run_demo; print(run_demo(approval_present=True))"
```

Omit `approval_present=True` to see the fail-closed path when approval is missing.

## Governed dispatch sequence

1. The application host authenticates the user and constructs a `Principal`. Do not build this object from untrusted request fields.
2. The host supplies the principal, agent, tool, risk, and any approval evidence to `GovernedToolHost`.
3. `SecurityPolicyEngine` checks the principal and policy grant. If approval is required, its injected verifier must accept the scoped evidence.
4. The adapter checks that the policy and gateway agree on whether approval is required, resolves a role permitted by both, and creates or reuses a session bound to the same subject and role.
5. Only after authorization does the adapter add the gateway approval marker and call the registered handler.
6. The policy engine and gateway keep active contracts isolated from caller-owned mutation; host inspection methods return defensive snapshots.
7. Authorization, host, and gateway audit records retain decision and outcome metadata, not handler output or request arguments.

The adapter also rejects reuse of a consumed approval ID within the same host instance and preserves the gateway's per-session invocation counter across calls made through that instance.

## Demonstrated controls

- Unauthenticated or unauthorized principals are denied before gateway dispatch.
- Missing, incorrectly scoped, or unverified approval evidence fails closed.
- Policy and gateway approval requirements must match.
- A principal must have a role permitted by both policy and the gateway.
- A session ID cannot be rebound to another subject or role.
- A verified approval ID is consumed after handler entry, including a handler error.
- Per-session tool invocation limits persist across adapter calls in the same process.
- Handler output is returned to the caller but excluded from the host, policy, and gateway audit records.
- Invalid arguments are rejected before the handler runs and do not consume the approval ID or invocation quota.

## Verification evidence

- [Governed Agent Execution Tests — run 44264628146](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44264628146): 18 tests passed, including the new host-adapter regression suite.
- [Portfolio Quality Gate — run 44264628058](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44264628058): portfolio documentation validation passed for 36 project READMEs and eight category indexes; 244 Python tests passed across 35 test suites.

The first CI attempt exposed a missing `ToolSpec` import in the demo runner. It was corrected in commit [c376b19](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/commit/c376b19c16224f35a8abd0fdb0eb66657ecf8fb5); the final runs above passed. The failed initial runs remain visible in Actions history.

## Boundaries and limitations

- This is a deterministic integration DEMO, not an LLM-powered agent or production security service.
- The adapter does not authenticate identities. The host must construct `Principal` only after its own authentication step and protect that trust boundary.
- The adapter does not authenticate approvers. The injected approval verifier must consult an authoritative approval source and validate approver authority, scope, expiry, and revocation.
- The included verifier and identities are synthetic test fixtures, not cryptographic approval.
- Session bindings, invocation counts, consumed approval IDs, and audit events are in memory. They reset when the process restarts and are not shared across processes.
- The in-memory session and approval registries are synchronous demonstration code, not concurrency-safe or durable replay protection.
- Handler side effects are not transactional and cannot be rolled back by this adapter.
- Audit records are not encrypted, tamper-evident, or durably stored. Use opaque subject and session identifiers; do not use names, emails, credentials, or customer data.
- No external system is contacted, and no live ticket or review task is created.

The existing `run_governed_execution` example remains available for the original policy-validator/gateway/orchestrator walkthrough. The new `host_adapter.py` path demonstrates the separate Security & Governance contract before gateway dispatch.
