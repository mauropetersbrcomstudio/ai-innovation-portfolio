# AI Product Development

This section covers the work involved in turning an AI-related business opportunity into a product: understanding the user and the problem, shaping the experience, testing assumptions, and developing a prototype.

## SME Workflow Opportunity Mapper

The [SME Workflow Opportunity Mapper](./sme-workflow-opportunity-mapper/) is an executable decision-support demo. It uses a transparent, user-supplied rubric to compare workflow opportunities and identify candidates for further discovery. It does not calculate ROI, validate ratings, or approve automation.

## Operations Review Workspace

The [Operations Review Workspace](./operations-review-workspace/) is a local web DEMO connected to the Resumable Intake Operations Hub. It displays a synthetic review queue, records decisions through the existing SQLite-backed decision store, and shows decision/event history.

Run it locally with `python server.py` from the project directory. It uses only the Python standard library and binds to loopback. Reviewer identity is not authenticated; no external actions are performed.
