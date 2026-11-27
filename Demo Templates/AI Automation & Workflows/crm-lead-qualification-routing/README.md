# CRM Lead Qualification & Routing

**Status: DEMO**

A local, configurable Python template for the CRM hand-off stage after lead intake. It applies explicit business-fit and engagement rules, assigns eligible records to a team queue, calculates an illustrative follow-up due date, and sends incomplete or conflicting records to a human-review queue.

This is distinct from the portfolio's Lead Intake Pipeline: that demo focuses on CSV cleanup, duplicate detection, and first-pass scoring. This template focuses on configurable qualification policy, queue ownership, and follow-up handling after intake.

## What it does

- Validates required CRM fields and supported values.
- Detects duplicate lead IDs and normalized email addresses.
- Applies a transparent, configurable point rubric.
- Routes qualified leads by declared territory; routes unqualified leads to nurture and exceptions to human review.
- Calculates a follow-up due date from the configured calendar-day SLA.
- Exports routed records and a separate review queue as CSV.

## Run

Requires Python 3.10+; standard library only.

```bash
python crm_router.py --leads sample_leads.csv --rules routing_rules.json --output-dir output
python -m unittest discover -s tests -v
```

## Policy configuration

Edit `routing_rules.json` to change score weights, qualification threshold, territory-to-team mapping, and follow-up SLA. The included values are illustrative examples, not recommended sales policy. The sample SLA uses calendar days; it does not account for weekends, holidays, or working hours.

## Routing behavior

- **sales_queue** — valid records meeting the configured qualification threshold and having a mapped territory.
- **nurture_queue** — valid records below the threshold.
- **review_queue** — missing or invalid required fields, duplicate IDs/emails, or qualified leads with an unmapped territory.

The score is a deterministic rule total, not a prediction of conversion likelihood, revenue, or customer value. Team assignment is a sample mapping, not an actual CRM owner directory.

## Data and limitations

All included records are synthetic. The demo runs locally and does not connect to a CRM, enrich leads, send communications, create tasks, or enforce a real SLA. It does not authenticate users or provide access control. Review and adapt all rules with the business owner before operational use.
