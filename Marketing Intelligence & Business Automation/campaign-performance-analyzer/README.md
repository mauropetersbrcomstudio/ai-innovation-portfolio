# Campaign Performance Analyzer

**Status: DEMO**

A local Python tool and browser dashboard that read campaign-level CSV data, validate basic count relationships, calculate transparent performance metrics, and produce campaign-level and aggregate reports.

## Metrics

- **CTR:** clicks ÷ impressions
- **Conversion rate:** conversions ÷ clicks
- **CPC:** spend ÷ clicks
- **CPA:** spend ÷ conversions
- **ROAS:** attributed revenue ÷ spend

If a denominator is zero, the corresponding metric is written as `null` rather than an invented zero rate. Aggregate rates are calculated from aggregate totals, not by averaging campaign-level rates.

## Interactive dashboard

Open `dashboard.html` in a modern browser, choose a CSV file, and inspect the campaign summary, ROAS comparison, channel aggregation, and detailed metrics. The dashboard processes the selected file locally in the browser; it does not upload the data. Download `sample_campaigns.csv` to try the included synthetic records.

After loading a CSV, use the campaign-name search and channel selector to filter the valid campaign rows and exception list. All displayed KPIs, charts, and tables reflect the current selection. The **Export filtered report** action downloads a JSON report containing the active filters, selected valid campaigns, selected exceptions, metric definitions, aggregate summary, export timestamp, and limitations. Exception rows are excluded from performance totals.

The browser dashboard is an independent front-end demonstration; the Python CLI remains available for repeatable file-based reporting.

## CSV contract

Required headers: `campaign, channel, spend, impressions, clicks, conversions, revenue`. The current schema has no date field; period filters and period-over-period comparisons are therefore not available.

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
