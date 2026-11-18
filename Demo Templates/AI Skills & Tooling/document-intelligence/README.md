# Document Intelligence — Plain-Text Extraction Skill

**Status: DEMO**

A deterministic local utility that extracts traceable structure from UTF-8 plain-text and Markdown files.

## Capabilities

- Counts characters, lines, nonempty lines, and words.
- Extracts Markdown headings with their source line numbers and levels.
- Extracts simple line-based key/value pairs using `:` or `=`.
- Identifies email addresses, HTTP(S) URLs, ISO-formatted dates, and currency-like mentions.
- Produces a JSON report while preserving source line references for headings and key/value pairs.

## Run

Requirements: Python 3.10+; standard library only.

From this directory:

```bash
python document_intelligence.py examples/sample-agreement.md
```

Save a JSON report:

```bash
python document_intelligence.py examples/sample-agreement.md --output report.json
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Design boundaries

This is pattern-based extraction, not an LLM agent or a semantic document-understanding system. It does not read PDF, DOCX, image, or scanned files; perform OCR; summarize; translate; validate legal meaning; verify extracted values; or call external services.

Currency and contact details may be sensitive. Review reports before sharing them. The included example is synthetic and uses reserved example domains.

## Reuse

The utility can serve as a small preflight component for text-based intake and downstream document workflows. A consuming workflow remains responsible for validating business meaning, handling sensitive information, and deciding what requires human review.
