# Agent Security & Governance

**Status: DEMO**

A reusable, deterministic policy engine for agent-tool authorization. It applies deny-by-default rules across the host-supplied principal, agent, role, tool, and risk level. Human approval is a separate control: approval evidence must match the requested subject, agent, tool, and risk, then pass an injected verifier.

## Run tests

Requires Python 3.10+ and uses only the standard library.

```bash
python -m unittest discover -s tests -v
```

## Controls

- Normalize and retain the validated policy as an internal snapshot at engine construction.
- Expose policy as a defensive copy; mutating the source mapping or a returned snapshot does not change active authorization rules.
- Explicit agent-to-role and agent-to-tool grants; wildcard grants are rejected.
- Risk allowlists for each tool, with malformed and non-string risk values rejected.
- Authentication-required gate for every authorization decision.
- Separate approval-required flag for high-impact operations.
- Approval evidence is scoped to subject, agent, tool, and risk.
- Fail-closed behavior when an approval verifier is absent, rejects evidence, or raises an error.
- Structured in-memory audit events for both allowed and denied decisions.

## Integration contract

The host application must authenticate the human or service identity and construct the `Principal` only from that trusted authentication result. The host must also provide an `approval_verifier` that validates approval evidence against its authoritative approval system. Call `authorize()` before passing a tool request to the runtime control plane or executing a handler.

The [Agent Tool Gateway](../agent-tool-gateway/) provides a separate dispatch-time allowlist and input contract. Its caller-supplied role and approval markers do not replace this policy decision. A host integration should authorize first and dispatch only when `Decision.allowed` is true.

## Verification evidence

- [Agent Security Governance Tests — run 44272797055](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44272797055): 13 tests passed, including source-policy and defensive-snapshot mutation checks.
- [Portfolio Quality Gate — run 44272829717](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44272829717): catalogue validation passed; 249 Python tests passed across 35 suites.

## Security boundaries

- The `authenticated` field is a host assertion, not proof of identity. A caller able to construct arbitrary principals can forge it. This module is not an identity provider, authentication middleware, or network security boundary.
- The injected approval verifier defines the trust in human approval. This demo includes no signature, key management, approval database, or cryptographic verification.
- Audit events are held in process memory and are mutable by the process. They are not durable, tamper-evident, or independently secured.
- Policy is loaded as an in-memory Python mapping and normalized into an internal snapshot; the public policy property returns a defensive copy. There is no policy distribution, version signing, or live reload.
- The module returns authorization decisions; it does not itself execute tools or enforce a network boundary. The caller must deny execution unless `allowed` is true.
- This is a reference demo, not production-ready security infrastructure.

## Example policy

```python
policy = {
    "agents": {
        "support-agent": {
            "roles": ["support_operator"],
            "tools": {
                "search_kb": {
                    "risks": ["LOW", "MEDIUM"],
                    "approval_required": False
                }
            }
        }
    }
}
```
