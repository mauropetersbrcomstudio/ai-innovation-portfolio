# Product Brief — Accounting Office Operations Workspace

## 1. Product intent

Build a demonstrable local-first prototype for a multi-agent accounting-office workflow. The product should help staff identify missing inputs, process structured financial documents, reconcile records, detect cross-department discrepancies, and route exceptions to the appropriate human reviewer.

The prototype is also the architectural foundation for a possible future operational deployment. Design decisions should preserve clear seams for later integrations, identity management, multi-user operation, and controlled production data access.

## 2. Users and roles

- Operations assistant: imports and organizes documents; resolves basic intake requests.
- Fiscal analyst: reviews fiscal document checks and tax-related exceptions.
- Payroll analyst: reviews payroll inputs and payroll-to-accounting differences.
- Accounting analyst: reviews ledger, bank reconciliation, and close status.
- Coordinator: reviews prioritized exceptions and approves actions within delegated authority.
- Partner/director: handles high-risk decisions and matters reserved to executive or technical leadership.
- System administrator: manages local environment and prototype configuration.

These are prototype roles, not production identity controls.

## 3. Primary user outcome

A reviewer can open a monthly competence, understand its completion status, inspect the evidence behind each check, resolve or assign exceptions, and see a complete event history before simulated close approval.

## 4. MVP workflow

1. Create or select a client workspace using a non-identifying demo reference.
2. Select competence and applicable tax regime.
3. Import local source files.
4. Inventory files and extract supported metadata.
5. Check required document completeness.
6. Parse supported document formats.
7. Run deterministic validations and reconciliations.
8. Group related exceptions without merging unrelated causes.
9. Route exceptions according to severity and role.
10. Record human decision and rationale.
11. Re-run affected checks and produce a close-readiness summary.

## 5. MVP priorities

P0:
- Local document intake and file inventory.
- Competence/client-reference association.
- Completeness checks.
- XML and OFX/CSV parsing after fixture validation.
- Deterministic reconciliation primitives.
- Exception register with evidence references.
- Human review and audit trail.

P1:
- PDF text extraction and OCR for scanned files.
- Cross-workstream checks for fiscal, payroll, and accounting.
- Dashboard and exportable review report.
- Rule configuration with versioning.

P2:
- Future production integration adapters, authentication, multi-user controls, monitoring, and deployment hardening. These are design targets only and are not part of the current no-integration demonstration.

## 6. Explicit non-goals for the prototype

- Connecting to external platforms or APIs.
- Accessing production ERP databases or servers.
- Transmitting tax declarations or government filings.
- Making payments or issuing binding tax/payroll instructions.
- Replacing professional accounting, tax, labor, or legal judgment.
- Claiming savings, accuracy, throughput, or business outcomes before measured tests.

## 7. Success measures

Capture baseline and prototype measurements separately:
- Time to inventory and classify a document batch.
- Completeness detection precision and recall against a reviewed sample.
- Parsing success rate by file type and layout.
- Reconciliation match rate and unresolved exception rate.
- False-positive and false-negative counts for each deterministic rule.
- Time from import to coordinator-ready exception summary.
- Percentage of decisions with complete evidence and reviewer rationale.

Targets must be agreed after baseline measurement. Do not infer achieved improvements from the desired outcomes.
