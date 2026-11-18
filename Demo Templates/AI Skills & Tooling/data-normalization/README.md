# Config-Driven CSV Data Normalization

**Status: DEMO**

A small, deterministic Python utility for applying explicitly configured field-level normalization to CSV files.

## Capabilities

- Trim whitespace only on configured fields.
- Map explicitly named input columns to output names.
- Apply configured lower-, upper-, or title-case transformations.
- Convert configured null markers to empty values.
- Parse dates using an explicit list of input formats and write a configured output format.
- Produce a compact JSON report with processed row count and changed-cell counts by output field.

## Run

Requires Python 3.10+ and uses only the standard library.

From this directory:

```bash
python normalize.py --input examples/input.csv --config config.example.json --output output/normalized.csv --report output/report.json
```

The input file is read only. The output CSV and optional report are written to the paths supplied on the command line.

## Configuration

All transformations are opt-in. See [config.example.json](./config.example.json). Unconfigured fields retain their original values. Date parsing fails with an error if no configured format matches; the utility does not guess date order. Column rename collisions and unsupported case rules also fail rather than silently choosing a result.

## Boundaries

- CSV only; no Excel, database, API, or CRM connectors.
- No inferred mappings, fuzzy matching, locale guessing, or automatic type inference.
- No deduplication or structural profiling; use the [CSV Data Quality Profiler](../csv-data-quality/) for preflight checks.
- No source-file modification, external calls, or AI/LLM processing.
- This is a reusable local utility, not a production ETL platform.

## Tests

```bash
python -m unittest discover -s tests -v
```
