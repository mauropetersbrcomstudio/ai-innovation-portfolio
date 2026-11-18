# Operations Intake & Human Review Template

**Status: REUSABLE DEMO TEMPLATE**

A reusable demonstration assembly for businesses that need a traceable intake and exception-review process across lead and invoice records.

This template reuses the existing intake pipelines, durable workflow runner, SQLite state store, human-review decision capture, and local Operations Review Workspace. It does not fork or duplicate their business logic.

## Included capabilities

1. Validate and route lead intake records.
2. Validate invoice records and route exceptions.
3. Persist workflow checkpoints and structured events.
4. Consolidate exceptions into a human-review queue.
5. Record one review decision per queue item.
6. Inspect the queue, decisions, and event history in a local web interface.

## Run the integrated demonstration

Follow the [Operations Review Workspace instructions](../../AI%20Product%20Development/operations-review-workspace/README.md).

The local demo seeds a synthetic sample workflow and runs on loopback only. Python 3.10+ and the standard library are sufficient.

## Reused components

- [Lead Intake Pipeline](../../AI%20Automation%20%26%20Workflows/lead-intake-pipeline/)
- [Invoice Intake & Exception Routing](../../AI%20Automation%20%26%20Workflows/invoice-intake-exception-routing/)
- [Resumable Intake Operations Hub](../../AI%20Automation%20%26%20Workflows/intake-operations-hub/)
- [Durable Workflow Runner](../../AI%20Agents%20%26%20Agentic%20Systems/durable-workflow-runner/)
- [Agent State Store](../../AI%20Skills%20%26%20Tooling/agent-state-store/)
- [Operations Review Workspace](../../AI%20Product%20Development/operations-review-workspace/)

## Adaptation checklist for a business scenario

- Replace synthetic lead and invoice examples with explicitly authorized sample records.
- Confirm required fields and validation rules with the process owner.
- Confirm invoice thresholds, currencies, and escalation rules with finance.
- Define reviewer roles and identity provider before any real use.
- Review privacy, retention, audit, backup, and access-control requirements.
- Test normal, invalid, duplicate, and boundary-value records.
- Keep payment, CRM updates, email, and other external actions disabled until separately integrated and approved.

## Current boundaries

- The bundled sample records are fictional.
- The current local interface has no login or authenticated reviewer identity.
- Decisions are persisted in SQLite, but the database is not tamper-proof.
- An accepted invoice is not a payment instruction or bank-transfer authorization.
- No CRM, accounting, payment, email, or external API is connected.
- This is a reusable DEMO TEMPLATE, not a production-ready business process.

## Template manifest

See [template-manifest.json](./template-manifest.json) for the component map and current capability boundaries.
