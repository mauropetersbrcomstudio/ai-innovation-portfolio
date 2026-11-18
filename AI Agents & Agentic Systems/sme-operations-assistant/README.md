# SME Operations Assistant

<sub>**Status: DEMO** · Deterministic baseline · No external integrations</sub>

A small, executable demonstration of a bounded operations assistant for a fictional SME. It classifies an incoming request, checks a strict action allowlist, and returns a traceable proposal. Actions are simulated only.

## What it demonstrates

- Request classification for billing, order-status, and support triage intents.
- Explicit allowlist validation.
- Escalation when intent is ambiguous or unsupported.
- Rejection of actions outside the allowlist.
- Structured output with an execution trace.
- No external side effects.

## Run

Requires Python 3.10 or newer. No third-party packages are required.

```bash
python agent.py
```

Run the unit tests from this directory:

```bash
python -m unittest discover -s tests -v
```

## Example

```python
from agent import handle_request

result = handle_request("Can you check my invoice?")
print(result.to_dict())
```

The result is a proposal, not a completed business action.

## Safety and limitations

- The classifier is keyword-based, not an LLM.
- Multiple detected intents are treated as ambiguous and escalated.
- The action catalogue is intentionally small and hard-coded.
- No customer records, credentials, APIs, or real company data are used.
- This demo does not claim a client engagement, deployment, endorsement, or measured business outcome.

## Next increments

1. Add schema validation and multilingual test coverage.
2. Add configurable synthetic business data.
3. Add a human-review interface.
4. Add adapter interfaces behind explicit permission boundaries.
5. Add integration and security tests before any external connection.
