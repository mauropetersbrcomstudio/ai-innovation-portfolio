# AI Skills & Tooling

This section brings together reusable skills, utilities, and supporting tools for building and operating AI workflows. The emphasis is on components that can be understood, tested, and reused rather than one-off demonstrations.

## Brief-to-Task Skill

The [Brief-to-Task Skill](./brief-to-task/) is an executable, deterministic utility. It converts a structured business brief into a task plan in JSON and Markdown, preserves supplied requirements, separates assumptions, and flags missing information as open questions.

It runs locally with Python and sample data. It does not estimate effort, invent owners or dates, infer dependencies, or connect to project-management platforms.

## CSV Data Quality Profiler

The [CSV Data Quality Profiler](./csv-data-quality/) is a reusable local Python preflight utility. It reports structural CSV issues, blank records and cells, exact duplicate rows, and optional duplicate keys. It does not modify source files or apply business-specific validation rules.

**Status: DEMO** — standard-library Python utility with unit tests and a sample CSV.

## Document Intelligence — Plain-Text Extraction

The [Document Intelligence skill](./document-intelligence/) extracts headings, simple key/value pairs, contact details, ISO dates, currency-like mentions, and basic document statistics from UTF-8 text and Markdown files. It preserves line references and does not modify source files.

**Status: DEMO** — deterministic pattern-based extraction; no OCR, semantic interpretation, or external services.

## JSON Contract Validator

The [JSON Contract Validator](./json-contract-validator/) checks JSON data against a documented schema subset, including types, required fields, additional properties, nested arrays, enums, and basic length/range constraints. It is designed for local input/output contract checks in reusable tools and agent workflows.

**Status: DEMO** — Python standard-library implementation; not a full JSON Schema engine.

## Config-Driven CSV Data Normalization

The [CSV Data Normalization skill](./data-normalization/) applies explicit, field-level CSV transformations: trimming, column renaming, case conversion, null-marker handling, and date parsing using configured formats. It writes a separate output file and a change report; it does not infer mappings or modify the source.

**Status: DEMO** — local Python utility with unit tests; CSV only.

## Knowledge Retrieval — Role-Filtered Lexical Search

The [Knowledge Retrieval skill](./knowledge-retrieval/) searches an explicitly supplied JSON knowledge base, filters sources by configured role values, ranks lexical matches, and returns traceable excerpts or an escalation status when no source qualifies.

**Status: DEMO** — local Python utility; role values are request inputs, not authenticated identity or a security boundary.

## Agent Tool Gateway — Allowlisting & Permission Controls

The [Agent Tool Gateway](./agent-tool-gateway/) mediates calls to explicitly registered handlers. It applies tool allowlisting, caller-supplied role checks, argument validation, optional approval markers, per-session invocation limits, and an in-memory audit trail that excludes handler output. Registered input schemas are copied on registration, and host-facing contract lookups return defensive copies so external mutation cannot silently alter dispatch validation.

**Status: DEMO** — dispatch control only. Its session role and approval markers are not trusted identity or approval evidence. A host should call Agent Security & Governance first, then dispatch only after an allowed policy decision. The host remains responsible for identity, approval verification, durable audit storage, and safe handler side effects.

## Agent Execution & Orchestration

The [Agent Orchestration framework](./agent-orchestration/) runs declared steps sequentially, supports bounded retries, pauses for host-mediated approval, records lifecycle events, and allows cancellation.

**Status: DEMO** — in-memory sequential runner; no durable queue, parallel execution, or production approval/authentication.

## Multi-Agent Coordination — Bounded Handoffs

The [Agent Coordination utility](./agent-coordination/) routes structured payloads among explicitly registered handlers, enforcing permitted handoffs, per-agent invocation limits, and a global handoff budget.

**Status: DEMO** — sequential in-process coordination; no autonomous agent loop, message broker, or persistent memory.

## Agent Evaluation — Scenario Assertions

The [Agent Evaluation skill](./agent-evaluation/) checks structured agent outputs against explicit expectations for status, output fields, trace participants, and lifecycle events. It produces a machine-readable PASS/FAIL report.

**Status: DEMO** — deterministic scenario assertions; no model grading or automatic test generation.

## Agent State Store — SQLite Persistence

The [Agent State Store](./agent-state-store/) persists workflow JSON state in SQLite, uses optimistic version checks to reject stale writes, and stores ordered workflow events.

**Status: DEMO** — local persistence only; no encryption, distributed locking, or automated backups.

## Agent Observability — Structured JSONL Events

The [Agent Observability utility](./agent-observability/) writes structured local JSONL events and recursively redacts values under recognized sensitive field names. Its matcher handles common case and separator variants, but does not inspect arbitrary free-text values.

**Status: DEMO** — local logs only; key-name redaction is a limited safeguard, not a data-loss-prevention or tamper-proof audit system.

## Agent Recovery — Compensating Actions

The [Agent Recovery utility](./agent-recovery/) runs bounded sequential steps and attempts declared compensations in reverse order after failure, reporting complete or partial rollback outcomes.

**Status: DEMO** — compensations are application handlers, not guaranteed transactional rollback.

## Agent Policy Validator — Governance Configuration Checks

The [Agent Policy Validator](./agent-policy-validator/) checks agent risk labels, explicit tool allowlists, approval gates, and execution bounds in a small declarative policy format.

**Status: DEMO** — configuration validation only; runtime authorization and identity verification remain external responsibilities.

## Agent Security & Governance — Deny-by-Default Authorization

The [Agent Security & Governance engine](./agent-security-governance/) evaluates explicit agent, role, tool, and risk grants. It separates authorization from human approval and fails closed when approval evidence cannot be verified. Its validated policy is held as an internal snapshot; callers receive defensive copies. It is the policy decision component to call before dispatch through the Agent Tool Gateway.

**Status: DEMO** — the host must supply a trusted authenticated principal and an authoritative approval verifier. The module itself provides neither identity authentication nor cryptographic approval verification; its audit events are in-memory.

## Recommended governed dispatch path

The following sequence describes how the existing DEMOs fit together; it is an integration pattern, not a production security guarantee:

1. The trusted application host authenticates the user and constructs the principal passed to the policy engine.
2. Agent Security & Governance evaluates the requested agent, role, tool, and risk. A deny or error stops the flow.
3. If the policy requires human approval, the host calls an authoritative approval verifier and passes only its verified result into the governed host adapter.
4. The host adapter checks policy/gateway configuration alignment and dispatches through the Agent Tool Gateway only after an allowed policy decision.
5. Agent Observability may record a structured event, but its key-name redaction is limited and its local log is not tamper-evident.

**Trust boundary:** caller-supplied role labels, session markers, and approval IDs are not proof of identity or approval. The host remains responsible for authentication, approval verification, safe handler effects, durable audit storage, and operational controls. These components remain **DEMOs**, not production authorization infrastructure.


## Client Case Publication Gate

The [Client Case Publication Gate](./client-case-publication-gate/) is a deterministic pre-publication checklist for evidence references, attribution permissions, data review, and claim-authorization declarations. It never authorizes publication.

**Status: DEMO** — see the project README for exact run instructions, tests, data provenance, and limitations.
