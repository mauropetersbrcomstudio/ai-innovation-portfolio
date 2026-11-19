# Validation Plan — Accounting Office Operations Prototype

## 1. Evidence required before claiming a capability

Every claimed capability must be supported by:
- A representative input fixture or authorized local source sample.
- Expected output defined by a reviewed rule or reference result.
- Automated test or documented manual verification.
- Recorded limitations and unsupported layouts.

## 2. Test layers

### Unit
- File hashing and duplicate detection.
- XML field extraction.
- OFX/CSV normalization.
- Decimal-safe monetary calculations.
- Competence and date validation.
- Checklist evaluation.
- Rule evaluation and version selection.
- Reconciliation matching and ambiguity handling.
- Exception grouping without loss of root-cause detail.
- Workflow state transitions and approval gates.

### Integration (local components only)
- Import → parse → normalize → validate.
- Normalize → reconcile → exception.
- Fiscal/Payroll/Accounting records → cross-audit.
- Exception → human decision → revalidation.
- Workflow → dashboard and audit timeline.

### End-to-end
- Complete monthly close with all required inputs.
- Missing document blocks progress.
- Unreadable or malformed document is quarantined.
- Duplicate import is idempotent.
- Ambiguous bank movement becomes an exception.
- Critical discrepancy blocks simulated close.
- Authorized reviewer decision is recorded and triggers revalidation.
- The example of an unexplained bank transfer and a potentially incorrect fiscal document is represented as two separately evidenced exceptions, grouped for review only when a valid relationship is established.

### Security and privacy
- Reject or exclude secrets from fixtures.
- Confirm source files remain outside repository.
- Confirm logs do not expose personal or bank data.
- Confirm public artifacts contain no client-specific identifiers.
- Confirm no network integration or outbound submission is performed by the prototype.

## 3. Metrics

Measure on a reviewed sample:
- Parse success by format/layout.
- Extraction field accuracy.
- Completeness detection precision/recall.
- Reconciliation precision and recall.
- False-positive and false-negative counts per rule.
- Exception evidence completeness.
- Human review time.
- Workflow completion time.

## 4. Release gates

Do not label a feature implemented until:
- Inputs and outputs are documented.
- Expected results are independently reviewed.
- Relevant automated tests pass.
- Failure and ambiguity behavior is tested.
- Privacy boundary is checked.
- The README accurately states limitations.

No performance or business-impact claim may be published before measurement against an agreed baseline.
