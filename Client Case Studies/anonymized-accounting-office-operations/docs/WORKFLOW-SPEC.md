# Workflow Specification — Monthly Close

## 1. Scope

The first demonstration covers a monthly close workflow for Simples Nacional and Lucro Presumido scenarios. Lucro Real and broader operational services are outside the first MVP unless a later scope decision expands them.

## 2. Workflow states

- CREATED
- AWAITING_DOCUMENTS
- DOCUMENTS_RECEIVED
- VALIDATING
- PROCESSING
- RECONCILIATION
- EXCEPTIONS_REVIEW
- AWAITING_APPROVAL
- APPROVED_FOR_DEMO_CLOSE
- BLOCKED
- CLOSED_FOR_DEMO
- FAILED

A state transition must include actor/service, timestamp, reason, and correlation ID.

## 3. Intake requirements

Each imported file must be associated with:
- Non-identifying workspace reference.
- Competence (YYYY-MM).
- Document family/type, when known.
- Original filename and file hash.
- Import timestamp.
- Parser status and validation status.

Do not assume that a file is complete or valid merely because it was received.

## 4. Completeness checks

Checklists must be versioned by tax regime, competence, and applicable service scope. The prototype should distinguish:
- Required and received.
- Required and missing.
- Received but unreadable.
- Received but period-mismatched.
- Optional or not applicable.
- Awaiting client clarification (simulated status only).

No checklist item may be marked satisfied without a supporting file reference or an explicit authorized reviewer override.

## 5. Deterministic processing

- XML: validate parseability and extract only fields supported by the verified schema/sample.
- OFX/CSV: normalize date, amount, description, account reference, and debit/credit direction while preserving original values.
- PDF: extract text only where reliable; OCR output must carry confidence and page references.
- Payroll: process only supplied and verified export layouts; do not infer missing events or employee values.
- Accounting records: normalize only known export layouts and preserve source identifiers.

All monetary values must use decimal-safe arithmetic. Never use binary floating-point for financial calculations.

## 6. Reconciliation

A reconciliation match must record:
- Source record IDs.
- Matching criteria and rule version.
- Amount difference.
- Date difference.
- Match confidence/category.
- Human review status.

Potential matches are suggestions, not confirmed accounting classifications. Unmatched and ambiguous records remain exceptions.

## 7. Cross-workstream audit

The cross-audit compares records only when a valid relationship and comparable period/amount basis are established. It must not treat every difference as an error. Timing, classification, accrual, and legitimate scope differences must be represented as distinct explanations requiring evidence.

## 8. Exception card

Each card should show:
- Exception ID and severity.
- Competence and non-identifying workspace reference.
- Short title and neutral description.
- Affected workflow steps.
- Source evidence references (file, page, row, XML path).
- Deterministic rule and version, where applicable.
- Agent-generated explanation clearly marked as assistance.
- Suggested next action.
- Required reviewer role.
- Status, owner, decision, and rationale.

Related exceptions may be grouped in one review card, but separate root causes and evidence must remain independently visible.

## 9. Approval gates

Human review is mandatory for:
- Tax calculation or interpretation that is not a fully approved deterministic rule.
- Payroll termination calculations and legally sensitive cases.
- Tax regime selection and tax planning.
- Government filing, transmission, payment, or response to an official notice.
- Material unresolved discrepancies.
- Overrides of required document checks.

The prototype only records simulated approval. It does not submit, transmit, pay, or change records in external systems.

## 10. Close readiness

A competence may be marked ready for simulated close only when:
- Required document checklist is satisfied or has a documented authorized exception.
- All required parsers and checks have completed.
- No critical blocker remains open.
- Required approvals are recorded.
- Audit events are complete for material actions.

The status is a prototype workflow result, not certification of tax compliance or approval to file.
