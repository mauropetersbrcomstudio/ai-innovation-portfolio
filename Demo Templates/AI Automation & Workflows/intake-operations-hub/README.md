# Resumable Intake Operations Hub

**Status: DEMO**

A deterministic integration demonstration composing the existing Lead Intake Pipeline and Invoice Intake & Exception Routing workflow with the portfolio's SQLite durable runner, structured event logging, and durable human-review decision capture.

## What it demonstrates

1. Reuses existing lead and invoice validation/routing logic.
2. Persists per-step workflow checkpoints in SQLite and structured events in SQLite/JSONL.
3. Prepares a consolidated human-review queue with stable item identifiers.
4. Records one human decision per review item, including reviewer identifier, outcome, reason, and timestamp, in SQLite.
5. Writes a corresponding `HUMAN_REVIEW_DECISION_RECORDED` workflow event in the same database transaction as the decision.
6. Rejects unknown review items, invalid outcomes, empty reasons, and duplicate decisions.

## Run intake

Requires Python 3.10+ and the standard library only. Prepare two JSON files, each containing an array.

    python workflow_hub.py --leads leads.json --invoices invoices.json --workflow-id intake-batch-001

Optional flags: --database, --events, and --approval-threshold.

## Record a human decision

The `reviewer-id` must be supplied by an authenticated host application. The CLI does not authenticate users or verify reviewer identity.

    python review_cli.py --workflow-id intake-batch-001 --item-id lead_intake:2 --reviewer-id reviewer-123 --outcome REQUESTED_INFORMATION --reason "Confirm company details"

Allowed outcomes:
- `ACCEPTED_FOR_NEXT_STAGE`
- `REJECTED`
- `REQUESTED_INFORMATION`

A decision is a review record only. Accepting an invoice for the next stage does not authorize payment, create an accounting entry, or approve a bank transfer.

## Tests

    python -m unittest discover -s tests -v

## Trust and operational boundaries

- Reviewer identity is a host assertion; this demo has no identity provider, login, session validation, role authorization, or cryptographic proof.
- Decision rows are append-only through the exposed API and duplicate decisions are blocked, but a database administrator or process with direct write access can alter the SQLite file. This is not tamper-proof audit storage.
- No multi-reviewer quorum, decision reversal, signatures, notifications, or external system actions are implemented.
- Workflow inputs are stored in SQLite. Use synthetic or explicitly authorized data only.
- No CRM, accounting, email, payment, or external API integration is performed.
- This remains a deterministic DEMO, not production workflow infrastructure.
