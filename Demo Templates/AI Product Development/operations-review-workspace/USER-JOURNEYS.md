# User Journeys — Operations Review Workspace

## Journey 1: Open an intake batch

**Goal:** Inspect a completed workflow.

1. Reviewer enters or selects a workflow ID.
2. Workspace retrieves the workflow state.
3. Workspace shows workflow status, completion information, and review queue counts.
4. If the workflow is unknown or incomplete, the workspace explains that decisions cannot be recorded.

**Expected outcome:** The reviewer sees the persisted queue for the selected completed workflow.

## Journey 2: Review a lead exception

**Goal:** Understand and resolve a lead intake exception.

1. Reviewer filters the queue to lead-intake items.
2. Reviewer opens an item using its stable item ID.
3. Workspace displays the source, reference, row, and routing reason.
4. Reviewer selects one supported outcome and supplies a reason.
5. Workspace submits the decision to the existing decision store.
6. Workspace displays the persisted decision and marks the item as decided.

**Expected outcome:** One durable decision and one matching workflow event exist for the workflow/item pair.

## Journey 3: Review an invoice item

**Goal:** Inspect an invoice routed for human review.

1. Reviewer filters the queue to invoice-intake items.
2. Reviewer inspects the invoice reference, status, and available reasons.
3. Reviewer records a decision with a non-empty reason.
4. Workspace displays the recorded decision.

**Safety boundary:** `ACCEPTED_FOR_NEXT_STAGE` is a review outcome only. It does not initiate payment, accounting, or bank transfer.

## Journey 4: Inspect decision history

**Goal:** Understand what has already been recorded.

1. Reviewer opens the decision history for the workflow.
2. Workspace lists item ID, reviewer identifier, outcome, reason, and timestamp.
3. Workspace links the decision to its workflow event where available.

**Expected outcome:** Review history reflects persisted data, not browser-only state.

## Journey 5: Handle an error

**Goal:** Avoid ambiguous or duplicated decisions.

The workspace must clearly handle:
- Unknown workflow.
- Workflow not completed.
- Unknown or duplicated queue item.
- Unsupported outcome.
- Empty reviewer identifier or reason.
- Duplicate decision for an item that already has a decision.
- Storage or service error.

The interface must not display a successful decision unless the backend confirms persistence.

## Identity boundary

The reviewer identifier shown in the current demo is supplied by the host. The workspace must not describe it as authenticated until a real identity provider and server-side authorization checks are integrated.
