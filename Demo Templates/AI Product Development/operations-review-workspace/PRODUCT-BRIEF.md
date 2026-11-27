# Product Brief — Operations Review Workspace

## Problem

The Resumable Intake Operations Hub can prepare a consolidated queue of lead exceptions and invoice review items and persist human decisions. Its current interaction is command-line oriented. A product-level workspace needs to make that review process inspectable and presentable without obscuring the deterministic workflow or its safety boundaries.

## Primary user

An operations reviewer working from a completed intake batch. The reviewer is expected to have been authenticated and authorized by a host application; the current demo does not provide that authentication.

## User need

"I need to see which intake records require attention, understand the reason for each exception, record a clear decision with a reason, and review what has already been decided."

## Value proposition

A single review surface for lead and invoice intake exceptions, backed by the existing durable workflow state and decision record.

## Product workflow

1. Intake batch completes.
2. Workspace loads the workflow summary and review queue.
3. Reviewer opens an item and inspects its source, reference, reason, and details.
4. Reviewer records one supported outcome and a reason.
5. Workspace refreshes the queue state and displays the persisted decision and audit event.

## Functional requirements

- Identify a workflow by its workflow ID.
- Show workflow status and completed steps.
- Display queue items with stable item IDs.
- Distinguish lead-intake and invoice-intake items.
- Prevent a second decision for the same workflow/item pair.
- Validate supported outcome and non-empty reviewer ID and reason.
- Display reviewer ID, outcome, reason, and timestamp from persisted records.
- Surface errors without silently discarding user input.

## Non-functional requirements

- Reuse the existing SQLite state and decision store.
- Keep business logic in the existing workflow modules.
- Use a clear, responsive interface with accessible labels and keyboard operation.
- Keep all demo data synthetic.
- Bind any local demo server to loopback only unless a later, separately reviewed deployment design authorizes otherwise.

## Success criteria for a connected demo

- A reviewer can inspect every queue item from a completed sample workflow.
- A valid decision is persisted and remains visible after a page reload.
- Duplicate decisions are rejected by the underlying store.
- Unknown workflow and item IDs, incomplete workflows, invalid outcomes, and empty required fields are rejected.
- The interface clearly states that reviewer identity is not authenticated in the demo.
- No external side effect is triggered by any review outcome.

## Explicit limitations

The current backend's reviewer ID is a caller-supplied assertion. It is not proof of identity. Decision records are append-only through the exposed API, not tamper-proof against direct database modification. Accepting an invoice for the next stage does not authorize payment.
