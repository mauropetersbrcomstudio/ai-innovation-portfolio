# CSV Data Quality Profiler

**Status: DEMO**

A reusable, local Python utility that profiles CSV structure and reports common data-quality issues before a downstream workflow processes the file.

## What it checks

- Empty files and blank records.
- Empty or duplicate column headers.
- Rows with a different number of fields than the header.
- Exact duplicate records.
- Empty cells by column.
- Duplicate values across optional key columns.

The tool does not edit, clean, enrich, infer, or overwrite the source data. It produces a JSON report and leaves remediation decisions to a person or a downstream process.

## Requirements

- Python 3.10+
- Python standard library only

## Run

From this directory:

```bash
python csv_data_quality.py examples/sample.csv --key-columns record_id
```

Write the report to a file:

```bash
python csv_data_quality.py examples/sample.csv --key-columns record_id --output report.json
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Report interpretation

- `ok`: no detected structural or review conditions.
- `review`: duplicate records/keys, blank rows, or empty cells were found; inspect before use.
- `invalid`: structural issues or requested key columns are invalid/missing.

Line numbers refer to physical CSV lines, starting with the header on line 1. Rows with a field-count mismatch are reported and excluded from cell and duplicate analysis. Blank rows are counted separately and excluded from the nonblank row count.

## Reuse

This utility can be used as a preflight step before CSV-based intake, analytics, or routing workflows. A consuming project should decide which findings are blocking, which require human review, and how to map its own business-specific rules.

## Limitations

- Duplicate record detection is exact and case-sensitive.
- Duplicate key detection ignores records where any selected key field is blank.
- Duplicate header names are reported, but header names are not automatically renamed.
- The utility does not validate email formats, business semantics, date formats, or numeric ranges.
- It reads UTF-8 CSV files (including UTF-8 BOM) and uses Python's default CSV dialect.
- Large files are processed row by row, but exact duplicate tracking stores observed rows and keys in memory.
- This is a local demonstration, not a production data-governance service.
