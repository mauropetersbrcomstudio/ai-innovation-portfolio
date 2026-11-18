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
