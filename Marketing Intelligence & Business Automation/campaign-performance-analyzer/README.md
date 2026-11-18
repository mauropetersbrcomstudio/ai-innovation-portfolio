# Campaign Performance Analyzer

**Status: DEMO**

A local Python tool and browser dashboard that read campaign-level CSV data, validate basic count relationships, calculate transparent performance metrics, and produce campaign-level and aggregate reports.

## Metrics

- **CTR:** clicks ÷ impressions
- **Conversion rate:** conversions ÷ clicks
- **CPC:** spend ÷ clicks
- **CPA:** spend ÷ conversions
- **ROAS:** attributed revenue ÷ spend

If a denominator is zero, the corresponding metric is `null`. Aggregate rates are calculated from aggregate totals, not by averaging campaign-level rates.

## Interactive dashboard

Open `dashboard.html` in a modern browser and select a CSV. The dashboard processes the file locally; it does not upload data. It supports campaign search, channel filtering, a filtered JSON report, and (when a valid `date` column exists) date-range filtering with a comparison against the immediately preceding interval of equal length.

## CSV contract

Required headers: `campaign, channel, spend, impressions, clicks, conversions, revenue`.

Optional date header: `date`, with every non-empty data row using a valid ISO calendar date in `YYYY-MM-DD` format. If the date column is absent, legacy CSV files remain supported and period comparison controls are hidden. If the date column is present, invalid or missing row dates are sent to exceptions and excluded from performance calculations.

The comparison uses inclusive date boundaries. For a selected interval of N calendar days, the previous period is the N calendar days immediately before the selected start. Empty previous periods are shown as zero records; percentage change is unavailable when the previous metric is zero or undefined. This is a descriptive comparison, not a causal explanation.

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

The sample dataset is synthetic. Checks are structural, not proof of attribution correctness. The tool does not connect to advertising platforms, verify spend or revenue, infer causation, or recommend budget allocation. ROAS is not profit or ROI.
