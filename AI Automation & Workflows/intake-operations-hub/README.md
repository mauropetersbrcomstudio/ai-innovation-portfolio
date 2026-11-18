# Resumable Intake Operations Hub

**Status: DEMO**

A deterministic integration demonstration composing the existing Lead Intake Pipeline and Invoice Intake & Exception Routing workflow with the portfolio's SQLite durable runner and structured event logging. It reuses existing business rules instead of duplicating them.

## What it demonstrates

1. Lead validation, normalization, duplicate detection, scoring, and routing through the existing lead implementation.
2. Invoice validation, duplicate detection, threshold checks, and exception routing through the existing invoice implementation.
3. SQLite workflow state and per-step checkpoints.
4. Structured execution events in the SQLite event table and JSONL log.
5. A consolidated human-review queue from lead exceptions and invoice outcomes.
6. Resume of completed workflows without repeating completed steps; changed input/configuration is rejected by the persisted plan fingerprint.

## Run

Requires Python 3.10+ and the standard library only. Prepare two JSON files, each containing an array. Lead objects use the fields documented by the Lead Intake Pipeline; invoice objects use the fields documented by Invoice Intake & Exception Routing.

    python workflow_hub.py --leads leads.json --invoices invoices.json --workflow-id intake-batch-001

Optional flags: --database, --events, and --approval-threshold.

Run tests:

    python -m unittest discover -s tests -v

## Human review boundary

The hub prepares a consolidated queue; it does not approve or reject a lead, approve an invoice, authorize payment, contact a lead or supplier, or write to a CRM/ERP. A queue item is a request for a human decision, not a decision itself. Human decision capture and authenticated reviewer identity are outside this demo's current scope.

## Reliability and security limitations

- The durable runner checkpoints each step and uses a stable idempotency key. Current handlers are deterministic local transformations with no external side effects.
- If handlers later gain external side effects, the destination must enforce the idempotency key to address the documented crash window.
- SQLite and JSONL files are local; no multi-host coordination, encryption, backup automation, or tamper-evident audit service is provided.
- Workflow inputs are included in persisted state. Do not use personal, confidential, or regulated records.
- No CRM, accounting, email, payment, or external API integration is performed.
- This is a reference demo, not a production workflow service or autonomous AI agent.

## Reused components

- Lead Intake Pipeline
- Invoice Intake & Exception Routing
- Durable Workflow Runner
