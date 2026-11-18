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

## Interactive dashboard

Open `dashboard.html` in a modern browser, choose a CSV file, and inspect the campaign summary, ROAS comparison, and detailed metrics. The dashboard processes the selected file locally in the browser; it does not upload the data. Download `sample_campaigns.csv` to try the included synthetic records.

The browser dashboard applies the same metric definitions and basic row checks described below. It is an independent front-end demonstration; the Python CLI remains available for repeatable file-based reporting.

## Run

Requires Python 3.10 or newer; no third-party dependencies.

```bash
python analyzer.py --input sample_campaigns.csv --output-dir output
python -m unittest discover -s tests -v
node --test tests/dashboard-logic.test.js
```

## Outputs

- `campaign_metrics.csv` — validated campaign rows and calculated metrics.
- `exceptions.csv` — rows that need correction or review.
- `summary.json` — aggregate totals and derived metrics.

## Data integrity and limitations

The included dataset is synthetic. This tool checks that numeric values are non-negative, clicks do not exceed impressions, and conversions do not exceed clicks. These are basic structural checks, not proof of attribution correctness or data quality. It does not connect to advertising platforms, verify spend or revenue, infer causation, recommend budget allocation, or claim campaign effectiveness. ROAS is a ratio based on the supplied revenue field and is not profit or ROI.
