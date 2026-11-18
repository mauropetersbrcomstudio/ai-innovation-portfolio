# SME Procurement Request Triage Agent

**Status: DEMO**

A local Python demonstration of a bounded agent workflow for handling internal purchase requests. It checks required fields, detects duplicate request IDs, applies a transparent policy file, and routes requests to the appropriate human review path.

The implementation is deterministic and rule-based. It does not use a language model, approve purchases, create purchase orders, contact suppliers, or connect to procurement or finance systems.

## Run the demonstration

Requires Python 3.10 or newer. No third-party packages are needed.

From this directory:

\`\`\`bash
python procurement_agent.py
\`\`\`

The program reads \`sample_requests.json\` and \`policy.json\`, then writes \`output/triage_report.json\`.

To provide different inputs:

\`\`\`bash
python procurement_agent.py --input my_requests.json --policy my_policy.json --output output/my_report.json
\`\`\`

Run the tests:

\`\`\`bash
python -m unittest discover -s tests -v
\`\`\`

## What it demonstrates

- Checks required request fields and rejects invalid values.
- Detects duplicate request IDs within the same input batch.
- Confirms the request currency matches the policy currency; it does not convert currencies.
- Checks the request category against the policy allowlist.
- Routes requests using the configured manager and finance review limits.
- Sends urgent requests to priority review.
- Requires supplier due diligence when a supplier is marked unverified.
- Produces a trace explaining the checks and the resulting review route.

## Review routes

| Condition | Route |
|---|---|
| Amount at or below the manager limit | Manager review |
| Amount above the manager limit and at or below the finance limit | Finance review |
| Amount above the finance limit | Executive review |
| Urgent request | Priority review |
| Unverified supplier | Supplier due diligence |
| Duplicate request ID | Human review |
| Missing required information | Requester follow-up |
| Invalid currency, amount, category, or field type | Human review |

The sample policy uses BRL and illustrative thresholds of 1,500 and 5,000. These are demonstration values, not a recommended purchasing policy. Replace them with thresholds and categories formally approved by the organization before adapting the example.

## Data and safety boundaries

- All included requests and supplier names are synthetic.
- Every route is a recommendation for human review; no request is approved automatically.
- No purchase order is created and no payment or supplier communication occurs.
- No external service, API, database, or live business system is accessed.
- The output is a decision-support record, not a financial, legal, or procurement approval.

A real implementation would require approved procurement policies, identity and access controls, supplier verification procedures, audit retention rules, integration security, and acceptance testing with the responsible business owners.

---

This is an independently developed portfolio demonstration, not a completed client engagement or a production procurement system.
