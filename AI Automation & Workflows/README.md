# AI Automation & Workflows

This section focuses on practical ways to make repeatable business processes more consistent: handling incoming information, checking it, applying clear rules, routing work, and dealing with exceptions.

## Lead Intake Pipeline

The [Lead Intake Pipeline](./lead-intake-pipeline/) is an executable example. It takes lead records from a CSV file, checks and standardizes the information, identifies duplicate email addresses, applies a transparent scoring rule, and separates records for priority follow-up, standard follow-up, or review.

It runs locally with Python and sample data. It does not connect to a CRM or contact leads.

## Invoice Intake & Exception Routing

The [Invoice Intake & Exception Routing workflow](./invoice-intake-exception-routing/) validates synthetic invoice records, checks supplier/invoice duplicates, verifies dates and amounts, and routes complete records or exceptions to human review queues.

**Status: DEMO** — deterministic rules only. It does not approve invoices, authorize payments, or connect to accounting systems.

## Resumable Intake Operations Hub

The [Resumable Intake Operations Hub](./intake-operations-hub/) composes both existing intake examples with SQLite checkpoints and structured events, then prepares a consolidated human-review queue and records review decisions with a reviewer identifier, outcome, reason, timestamp, and matching audit event. Reviewer identity remains a host-supplied assertion; no authentication provider or external action is included.


## CRM Lead Qualification & Routing

The [CRM Lead Qualification & Routing](./crm-lead-qualification-routing/) demo provides configurable lead qualification, territory queues, follow-up dates, duplicate checks, and human-review routing. It is a local Python demo, not a live CRM integration.

**Status: DEMO** — see the project README for exact run instructions, tests, data provenance, and limitations.

## SME Customer Support Automation

The [SME Customer Support Automation](./sme-customer-support-automation/) demo provides support request classification, approved-knowledge response drafts, and human escalation. It is rule-based; it does not send messages or connect to live systems.

**Status: DEMO** — see the project README for exact run instructions, tests, data provenance, and limitations.
