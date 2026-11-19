# Accounting Office Operations Workspace (Anonymized)

**Status: PROTOTYPE**

A local-first, multi-agent prototype for demonstrating a monthly accounting close workflow across fiscal, payroll, and accounting workstreams. The public artifact is anonymized and intentionally excludes client identity, source documents, personal data, tax identifiers, commercial records, credentials, and client-specific operational metrics.

The prototype is designed as the first product increment of a solution that may later be deployed operationally. Its current demonstration mode is independent and local; external platforms are not connected.

## Product objective

Demonstrate how an accounting office can move from fragmented document intake and departmental handoffs to a controlled monthly-close workflow with deterministic checks, explainable exceptions, human approvals, and an auditable event history.

## Initial scope

- Monthly close for Simples Nacional and Lucro Presumido scenarios.
- Local import and inventory of source documents.
- Document completeness and period checks.
- Parsing adapters for XML, OFX, CSV, and PDF, enabled incrementally as formats are verified against supplied samples.
- Rule-based reconciliation and cross-workstream checks.
- Exception grouping with evidence and recommended next actions.
- Human review and approval simulation.
- Local dashboard for workflow status, blockers, and audit events.

## Architecture boundary

The prototype has no live integrations. Domínio, Acessórias, Sieg, Digisac, WhatsApp, Google Workspace, banking platforms, government portals, and external APIs are not connected. Future integration seams will be represented by replaceable adapters and documented contracts, not active connections.

## Safety and accounting controls

- No autonomous tax calculation or legal/tax interpretation by an LLM.
- Financial arithmetic and deterministic validations must be implemented in testable code with explicit rules and provenance.
- Low-confidence extraction is flagged for human review; it is never silently accepted.
- Critical discrepancies block the simulated release step.
- Tax filings, payments, payroll termination approvals, tax regime decisions, and legal responses remain human decisions.
- Every material transformation and review decision must produce an attributable audit event.

## Local execution

Requires Python 3. From the project directory:

```bash
cd prototype
python server.py
```

Open `http://127.0.0.1:8767` on the same computer. The initial shell supports session-only file selection and metadata inventory. It does not upload or persist file contents and does not yet parse or reconcile source documents. Do not run this project against production systems or place source client files in this public repository.

## Data and publication boundary

Use only authorized source files in a controlled local working directory. Keep all raw client documents, extracted personal data, tax identifiers, bank details, payroll information, credentials, and customer-specific records outside Git. Public screenshots and documentation must be anonymized and must not expose client identity or confidential baselines.

## Current maturity and limitations

This is a **PROTOTYPE**. No production integration, filing, payment, or deployment is implemented or claimed. Parsing coverage, business rules, reconciliation behavior, and performance must be verified against the client's supplied sample files before being described as working capabilities.

See:
- [Product brief](./docs/PRODUCT-BRIEF.md)
- [Architecture](./docs/ARCHITECTURE.md)
- [Workflow specification](./docs/WORKFLOW-SPEC.md)
- [Security and privacy](./docs/SECURITY-PRIVACY.md)
- [Validation plan](./docs/VALIDATION-PLAN.md)
