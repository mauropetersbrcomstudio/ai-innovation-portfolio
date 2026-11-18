# Lead Intake Pipeline

**Status: DEMO — executable local prototype**

A deterministic lead-intake workflow using only the Python standard library. It validates CSV records, normalizes fields, detects duplicate email addresses, calculates a transparent qualification score, routes valid leads, and writes an exception report.

## Problem
Small teams often receive inconsistent lead records and need a repeatable first-pass process before human follow-up.

## What it does
1. Validates required fields and email shape.
2. Normalizes names, email addresses, company names, and source labels.
3. Detects duplicate email addresses (later duplicate rows are flagged and excluded from routing).
4. Scores leads using explicit, editable rules.
5. Routes leads to `priority`, `standard`, or `review`.
6. Exports processed records and row-level exceptions.

## Run
Requires Python 3.10+; no third-party packages.

```bash
python pipeline.py --input sample_leads.csv --output-dir output
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Scoring rules
- +30 when a company is supplied.
- +25 when a business email is supplied (common free-mail domains do not qualify).
- +25 when the requested service is supplied.
- +20 when the source is supplied.
- Score 70–100: priority; 40–69: standard; 0–39: review.

These are demonstration rules, not empirically calibrated conversion predictions. They should be adapted and validated against a real organization's criteria before operational use.

## Outputs
- `processed_leads.csv`
- `exceptions.csv`
- `summary.json`

## Privacy and limitations
Use synthetic or appropriately authorized data. This local demo does not connect to a CRM, send messages, or make external changes. Email validation is intentionally basic and does not verify mailbox existence.

## Acceptance checks
Unit tests cover normalization, scoring, routing, invalid records, duplicate handling, and generated output files.
