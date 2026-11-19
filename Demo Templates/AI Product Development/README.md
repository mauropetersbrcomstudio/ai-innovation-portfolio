# AI Product Development

This section covers the work involved in turning an AI-related business opportunity into a product: understanding the user and the problem, shaping the experience, testing assumptions, and developing a prototype.

## SME Workflow Opportunity Mapper

The [SME Workflow Opportunity Mapper](./sme-workflow-opportunity-mapper/) is an executable decision-support demo. It uses a transparent, user-supplied rubric to compare workflow opportunities and identify candidates for further discovery. It does not calculate ROI, validate ratings, or approve automation.

## Operations Review Workspace

The [Operations Review Workspace](./operations-review-workspace/) is a local web DEMO connected to the Resumable Intake Operations Hub. It displays a synthetic review queue, records decisions through the existing SQLite-backed decision store, and shows decision/event history.

Run it locally with `python server.py` from the project directory. It uses only the Python standard library and binds to loopback. Reviewer identity is not authenticated; no external actions are performed.

## Verification and presentation

The Operations Review Workspace has a documented presentation path in the [Selected Demo Guide](../../DEMO-GUIDE.md). Its cross-project Chromium checks cover a recorded synthetic decision, persistence after reload, and a 375-pixel mobile layout. Automated checks do not replace human review on the intended presentation device, and they do not establish authentication or production readiness.


## Operations Intake & Human Review Template

The [Operations Intake & Human Review Template](./operations-intake-review/) is a reusable assembly of intake pipelines, durable workflow state, review decisions, and a local workspace. It uses synthetic data and has no authentication or external actions.

**Status: DEMO** — see the project README for exact run instructions, tests, data provenance, and limitations.


## Healthcare Reception Assistant

The [Healthcare Reception Assistant](./healthcare-reception-assistant/) is a local, browser-based product prototype for administrative reception workflows. It demonstrates synthetic appointment preferences, a browser-local human-review queue, and escalation for clinical, urgent, ambiguous, or unsupported requests.

**Status: DEMO** — it has no live messaging, calendar, patient-record, or other external-system integrations. See the project README for run instructions and boundaries.
