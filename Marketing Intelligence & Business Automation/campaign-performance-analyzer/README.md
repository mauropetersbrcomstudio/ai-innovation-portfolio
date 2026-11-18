# Campaign Performance Analyzer

**Status: DEMO**

A local Python tool that reads campaign-level CSV data, validates basic count relationships, calculates transparent performance metrics, and writes campaign-level and aggregate reports.

## Metrics

- **CTR:** clicks ÷ impressions
- **Conversion rate:** conversions ÷ clicks
- **CPC:** spend ÷ clicks
- **CPA:** spend ÷ conversions
- **ROAS:** attributed revenue ÷ spend

If a denominator is zero, the corresponding metric is written as `null` rather than an invented zero rate. Aggregate rates are calculated from aggregate totals, not by averaging campaign-level rates.

## Run

Requires Python 3.10 or newer; no third-party dependencies.

```bash
python analyzer.py --input sample_campaigns.csv --output-dir output
python -m unittest discover -s tests -v
```

## Outputs

- `campaign_metrics.csv` — validated campaign rows and calculated metrics.
- `exceptions.csv` — rows that need correction or review.
- `summary.json` — aggregate totals and derived metrics.

## Data integrity and limitations

The included dataset is synthetic. This tool checks that numeric values are non-negative, clicks do not exceed impressions, and conversions do not exceed clicks. These are basic structural checks, not proof of attribution correctness or data quality. It does not connect to advertising platforms, verify spend or revenue, infer causation, recommend budget allocation, or claim campaign effectiveness. ROAS is a ratio based on the supplied revenue field and is not profit or ROI.
