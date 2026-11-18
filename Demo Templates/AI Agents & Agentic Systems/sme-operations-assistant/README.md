# SME Operations Assistant

**Status: DEMO**

A small Python demonstration of an AI-agent pattern for everyday SME operations. It takes a short request, identifies whether it relates to billing, an order, or customer support, checks the proposed action against an allowlist, and returns a result that can be reviewed.

The demo is deliberately limited: it uses keyword matching rather than a language model, and it simulates actions instead of connecting to live business systems.

## What you can try

- Ask about an invoice or payment.
- Ask for an order or delivery update.
- Raise a support issue.
- Submit an unclear request and see it escalated for human review.
- Request an action that is not allowed and see it rejected.

Every result includes a trace of the checks performed. A successful classification produces a proposal, not a completed business action.

## Run it

Requires Python 3.10 or newer. No third-party packages are needed.

From this directory, run:

```bash
python agent.py
```

To run the tests:

```bash
python -m unittest discover -s tests -v
```

## Use it from Python

```python
from agent import handle_request

result = handle_request("Can you check my invoice?")
print(result.to_dict())
```

## Boundaries

The action catalogue is small and hard-coded. Requests that are unclear or match more than one intent are escalated. No customer records, credentials, APIs, or live company data are used, and the program does not send messages or modify business records.

This is a technical demonstration, not a deployed client solution. A real implementation would need suitable business-system integrations, identity and access controls, human-review paths, and further testing before handling operational requests.
