# Marketing Analytics Pipeline

**Status: DEMO**

A local, deterministic pipeline that composes two existing portfolio components:

1. **CSV Data Quality Profiler** — inspects CSV structure, blank rows/cells, duplicate records/keys, and malformed rows without changing the source.
2. **Campaign Performance Analyzer** — validates campaign-specific numeric relationships and calculates CTR, conversion rate, CPC, CPA, and ROAS.

## Run

Requires Python 3.10+; Python standard library only.

From this directory:

```bash
python pipeline.py --input ../campaign-performance-analyzer/sample_campaigns.csv --output-dir output
python -m unittest discover -s tests -v
```

The default policy stops when the preflight status is `review` or `invalid`. After inspecting the source and quality report, a reviewer may explicitly allow a review-level file:

```bash
python pipeline.py --input ../campaign-performance-analyzer/sample_campaigns.csv --output-dir output --allow-review
```

## Outputs

- `quality_report.json` — structural preflight report.
- `campaign_metrics.csv` — valid campaign rows and calculated metrics.
- `exceptions.csv` — campaign-specific rows excluded by the analyzer.
- `summary.json` — aggregate totals and derived metrics.

## Safety and limitations

The source CSV is never modified. The preflight is conservative: `review` blocks by default, and `--allow-review` is an explicit operator override, not an approval system. The analyzer may exclude malformed campaign rows and report them as exceptions. The included campaign sample is synthetic. This pipeline does not connect to ad platforms, verify attribution, infer causation, recommend budget changes, or establish production-grade governance.
