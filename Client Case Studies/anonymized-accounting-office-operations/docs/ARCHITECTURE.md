# Architecture — Local Prototype with Production Evolution Path

## 1. Architecture principles

- Local-first execution for the current demonstration.
- No external platform connections in the prototype.
- Deterministic core for arithmetic, reconciliation, period checks, and policy rules.
- LLM/agent use limited to bounded interpretation, document triage assistance, summarization, and preparation of reviewer-facing explanations.
- Human approval for material accounting, fiscal, payroll, and legal decisions.
- Explicit contracts between orchestration, agents, parsers, rules, persistence, and UI.
- Replaceable adapters so future production connectors do not require rewriting the workflow core.
- Evidence provenance for every extracted value and generated exception.

## 2. Logical components

### Local UI
Competence dashboard, document intake, exception queue, evidence viewer, approval simulation, and audit timeline.

### Workflow orchestrator
Maintains workflow state, schedules bounded agent tasks, enforces dependencies, handles retries, and prevents duplicate processing.

### Specialized agents
- Intake Agent: classify incoming items and associate them with a workspace and competence.
- Document Intelligence Agent: extract candidate fields and identify document type.
- Completeness Agent: compare received documents against a versioned checklist.
- Bank Statement Agent: normalize supported OFX/CSV records; PDF support is gated by verified extraction quality.
- Fiscal Review Agent: run approved deterministic checks over XML fields and configured rule tables.
- Payroll Review Agent: validate payroll input completeness and compare approved totals/entries where source evidence permits.
- Reconciliation Agent: match normalized bank movements with accounting/financial records and expose unmatched items.
- Cross-Workstream Audit Agent: compare relevant fiscal, payroll, and accounting totals and references.
- Exception Agent: group related findings, preserve separate root causes, and prepare reviewer summaries.
- Governance Agent: enforce role/approval boundaries and produce audit events.

Agents are logical responsibilities. They may be implemented as deterministic services first; an agent label does not imply an LLM is required.

### Deterministic services
File fingerprinting, parsers, normalization, arithmetic, rule evaluation, reconciliation, duplicate detection, and workflow gates.

### Local persistence
A local database for workflow state, normalized records, rule versions, exceptions, decisions, and audit events. Raw files remain in a controlled local file store with references and hashes.

### Future integration boundary
Future connectors may be added for accounting ERP, document capture, task management, messaging, and banking sources. The current prototype must use local imports and fixtures only. No connector is active.

## 3. Data flow

Local import → file inventory and hashing → parsing and normalization → completeness and deterministic checks → reconciliation → cross-workstream audit → exception grouping → human review → revalidation → simulated close readiness.

## 4. Data model (conceptual)

- Workspace: non-public internal client reference and configuration.
- Competence: period, regime, workflow status.
- SourceFile: local path reference, hash, media type, size, import time, parser status.
- ExtractedRecord: normalized value, source file reference, page/row/XML path, extraction confidence.
- Rule: stable identifier, version, effective period, source/provenance, severity, executable condition.
- CheckRun: input references, rule versions, outcome, timestamp.
- Exception: category, severity, evidence references, status, owner, suggested next action.
- ReviewDecision: reviewer role, decision, rationale, timestamp, affected exception/check IDs.
- AuditEvent: actor/service, action, object, timestamp, correlation ID, before/after references.

## 5. Production evolution path

The prototype should isolate:
- Local file import behind a DocumentSource interface.
- Local persistence behind repositories.
- Deterministic rules behind a RuleEngine interface.
- Human review behind an ApprovalPolicy interface.
- Local identity assumptions behind an AuthorizationProvider interface.

A future deployment can replace these boundaries with approved production adapters, database services, identity controls, and external connectors. This is a design path, not a claim that production integration exists.

## 6. Failure handling

- Unknown format: quarantine and request manual classification.
- Parse error: retain original file, record error, do not create trusted financial values.
- Low-confidence extraction: require review.
- Duplicate file: detect by hash and avoid duplicate processing.
- Conflicting values: preserve both source references and create an exception.
- Rule missing or expired: stop the affected check and escalate.
- Agent timeout/failure: retry only idempotent tasks; record attempts and final status.
- Critical exception: block simulated close readiness until an authorized human decision is recorded.
