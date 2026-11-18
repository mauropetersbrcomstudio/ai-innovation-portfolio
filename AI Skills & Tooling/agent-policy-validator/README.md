# Agent Policy Validator — Governance Configuration Checks

**Status: DEMO**

A deterministic validator for declarative agent policy manifests. It checks that agent identities, risk levels, tool allowlists, approval requirements, and execution bounds are explicit and internally consistent.

## Capabilities

- Require a non-empty list of agent definitions.
- Validate unique agent names and recognized risk levels.
- Require explicit tool lists and reject wildcard access.
- Ensure approval-required tools are part of the allowlist.
- Require at least one approval-gated tool for HIGH and CRITICAL risk agents with tools.
- Enforce a configured step limit from 1 to 100.
- Emit warnings for additional controls expected around critical-risk tools.

## Run tests

Requires Python 3.10+ and uses only the standard library.

```bash
python -m unittest discover -s tests -v
```

## Boundaries

- This validates a small custom policy format, not a recognized industry standard.
- It checks configuration consistency only; it does not enforce runtime authorization.
- It does not authenticate identities, validate approvals, inspect handler behavior, or prove that tools are safe.
- Risk labels and approval requirements must be assigned by accountable system owners.
- Production systems require independent security review and runtime enforcement.
