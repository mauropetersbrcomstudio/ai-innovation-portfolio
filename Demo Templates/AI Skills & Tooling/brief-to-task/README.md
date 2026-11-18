# Brief-to-Task Skill

**Status: DEMO**

A deterministic utility that converts a structured business brief (JSON) into a reviewable task plan (JSON and Markdown). It is designed to preserve supplied information, keep user-provided assumptions separate, and surface missing details as open questions instead of silently inventing them.

## What it does

- Validates a small, documented brief schema.
- Preserves the supplied objective, context, constraints, stakeholders, deadline, deliverables, and success criteria.
- Creates one traceable task entry per supplied deliverable.
- Marks acceptance criteria as unresolved when none were provided.
- Lists missing objective, deliverables, success criteria, and deadline as open questions.
- Produces both machine-readable and human-readable outputs.

## Run

Requires Python 3.10 or newer. No third-party packages are required.

```bash
python skill.py --input sample_brief.json --output-dir output
python -m unittest discover -s tests -v
```

## Input schema

Required: `title`.

Optional fields:
- `objective`, `context`, `deadline`: strings.
- `deliverables`, `constraints`, `stakeholders`, `success_criteria`, `assumptions`: a string or an array of strings.

See `sample_brief.json` for a complete example.

## Outputs

- `task_plan.json` — structured task plan, confirmed requirements, assumptions, open questions, and guardrails.
- `task_plan.md` — readable review document.

## Scope and limitations

This is a deterministic demonstration, not an autonomous project manager or an LLM-based skill. It does not estimate effort, invent owners or dates, infer dependencies, prioritize tasks, contact stakeholders, or integrate with project-management platforms. Task sequencing and more detailed work breakdown require human review. The sample brief is fictional.
