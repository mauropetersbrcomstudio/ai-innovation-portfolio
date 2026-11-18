# Campaign Launch QA & UTM Builder

**Status: DEMO**

A deterministic local tool that checks campaign launch metadata and builds tracking URLs. It is designed as a pre-launch quality checkpoint, not a campaign publishing system.

## Run

Requires Python 3.10+ and the standard library only.

```bash
python launch_qa.py --input sample_campaigns.csv --output-dir output
python -m unittest discover -s tests -v
```

## CSV contract

Required columns: `campaign_id, campaign_name, destination_url, utm_source, utm_medium, utm_campaign, start_date, end_date, budget`.

Optional columns: `utm_content`, `utm_term`.

The validator checks required values, duplicate campaign IDs, absolute HTTP(S) destinations without embedded credentials, collisions with existing UTM parameters, strict ISO dates, date ordering, and finite non-negative decimal budgets. It preserves supplied UTM values and existing non-UTM query parameters. It does not impose a channel taxonomy or naming convention.

## Outputs

- `approved_campaigns.csv` — rows that passed the defined checks, including generated tracking URLs.
- `exceptions.csv` — rejected rows and reasons.
- `summary.json` — counts and run status (`ready`, `review`, or `blocked`).

The source file is never modified. Duplicate campaign IDs cause every occurrence to be rejected.

## Limitations

This is a DEMO, not a publishing or activation tool. It does not verify destination ownership, consent, legal compliance, analytics-platform configuration, live URL availability, or actual tracking collection. Passing the checks is not approval to launch a campaign. Sample data is synthetic.
