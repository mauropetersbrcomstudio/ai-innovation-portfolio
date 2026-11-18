# AI Skills & Tooling

This section brings together reusable skills, utilities, and supporting tools for building and operating AI workflows. The emphasis is on components that can be understood, tested, and reused rather than one-off demonstrations.

## Brief-to-Task Skill

The [Brief-to-Task Skill](./brief-to-task/) is an executable, deterministic utility. It converts a structured business brief into a task plan in JSON and Markdown, preserves supplied requirements, separates assumptions, and flags missing information as open questions.

It runs locally with Python and sample data. It does not estimate effort, invent owners or dates, infer dependencies, or connect to project-management platforms.

## CSV Data Quality Profiler

The [CSV Data Quality Profiler](./csv-data-quality/) is a reusable local Python preflight utility. It reports structural CSV issues, blank records and cells, exact duplicate rows, and optional duplicate keys. It does not modify source files or apply business-specific validation rules.

**Status: DEMO** — standard-library Python utility with unit tests and a sample CSV.
