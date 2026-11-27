# Data Model and Interface Contract — Operations Review Workspace

This contract describes the minimum information the future interface needs from the existing Intake Operations Hub. It is a design contract, not an implemented HTTP API.

## Workflow summary

| Field | Type | Meaning |
|---|---|---|
| `workflow_id` | string | Stable workflow identifier |
| `status` | string | Workflow execution status |
| `completed_steps` | string array | Steps persisted as completed |
| `review_items` | object array | Items from the prepared human-review queue |

## Review item

| Field | Type | Meaning |
|---|---|---|
| `item_id` | string | Stable ID, e.g. `lead_intake:2` |
| `source` | string | `lead_intake` or `invoice_intake` |
| `reference` | string | Lead email, invoice ID, or row fallback |
| `reason` | string | Primary routing reason or status |
| `row` | integer | Source row reference |
| `details` | object or array | Additional source-specific review details, when present |

## Decision record

| Field | Type | Meaning |
|---|---|---|
| `decision_id` | integer | Database-generated decision identifier |
| `workflow_id` | string | Parent workflow |
| `item_id` | string | Queue item being reviewed |
| `reviewer_id` | string | Host-supplied reviewer identifier |
| `outcome` | enum | One of the three supported outcomes |
| `reason` | string | Required explanation |
| `created_at` | ISO 8601 string | UTC timestamp |

Supported outcomes:
- `ACCEPTED_FOR_NEXT_STAGE`
- `REJECTED`
- `REQUESTED_INFORMATION`

## Required operations for a future adapter

1. Read a workflow summary and its prepared review queue.
2. Read persisted decisions for a workflow.
3. Submit a decision for a workflow/item pair.
4. Return a clear conflict when a decision already exists.
5. Return explicit not-found, invalid-state, validation, and storage errors.

## Decision submission invariants

- The workflow must exist and be `COMPLETED`.
- The item ID must occur exactly once in that workflow's review queue.
- Reviewer ID and reason must be non-empty strings.
- Outcome must be one of the supported values.
- A unique constraint must prevent more than one decision per workflow/item.
- The decision row and `HUMAN_REVIEW_DECISION_RECORDED` event must commit atomically.

## Security requirements before real use

- Authenticate the reviewer using a trusted identity provider.
- Derive the reviewer principal server-side; do not trust a browser-supplied identity string.
- Enforce reviewer permissions server-side.
- Protect local or remote service endpoints against unauthorized access and cross-origin abuse.
- Define retention, backup, access logging, and tamper-evidence requirements.
- Review privacy and data minimization before using real lead or invoice records.

## Integration rule

The interface must call the existing workflow and decision modules through a narrow adapter. It must not write directly to SQLite tables or reimplement decision validation.
