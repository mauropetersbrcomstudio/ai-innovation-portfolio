# AI Product Development

This section covers the work involved in turning an AI-related business opportunity into a product: understanding the user and the problem, shaping the experience, testing assumptions, and developing a prototype.

## SME Workflow Opportunity Mapper

The [SME Workflow Opportunity Mapper](./sme-workflow-opportunity-mapper/) is an executable decision-support demo. It uses a transparent, user-supplied rubric to compare workflow opportunities and identify candidates for further discovery.

It does not calculate ROI, validate ratings, or approve automation. Its scores and thresholds are illustrative and require human review.

## Operations Review Workspace

The [Operations Review Workspace](./operations-review-workspace/) defines a product-level experience for the Resumable Intake Operations Hub: product brief, reviewer journeys, data model, and interface contract. These artifacts specify the intended connected experience; they do not claim that a UI, API, authentication, or external integration already exists.

## Operations Review Workspace

The [Operations Review Workspace](./operations-review-workspace/) is a functional local web demo connected to the Resumable Intake Operations Hub. It displays a synthetic review queue, records decisions through the existing SQLite-backed decision store, and shows decision/event history. It runs on loopback only and does not authenticate reviewers or trigger external actions.
