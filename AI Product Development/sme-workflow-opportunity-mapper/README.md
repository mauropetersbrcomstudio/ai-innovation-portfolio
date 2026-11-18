# SME Workflow Opportunity Mapper

**Status: DEMO**

A deterministic decision-support tool for screening business workflow opportunities with an explicit, user-supplied rubric. It ranks candidate processes for further discovery; it does not decide whether a workflow should be automated.

## Rubric

Each opportunity is rated from 1 to 5 on:
- Frequency
- Time burden
- Standardization
- Data readiness
- User impact
- Risk

The first five ratings are higher-is-more-favorable. Risk is reverse-scored as `6 − risk`. The final score is the mean of those six values.

- **4.00–5.00:** `PRIORITIZE_FOR_DISCOVERY`
- **3.00–3.99:** `INVESTIGATE`
- **1.00–2.99:** `DEFER_OR_REDESIGN`

These thresholds are illustrative. Scores are not empirical predictions, ROI estimates, or implementation approvals.

## Run

Requires Python 3.10 or newer; standard library only.

```bash
python mapper.py --input sample_opportunities.json --output output/opportunity_report.json
python -m unittest discover -s tests -v
```

## Input and output

The input JSON contains an `opportunities` array. Each item requires a name, a problem description, and integer ratings from 1 to 5 for all six rubric dimensions. See `sample_opportunities.json`.

The output JSON contains the method, sorted assessments, scores, screening classifications, and limitations.

## Scope and limitations

This demo structures human judgment; it does not discover processes, validate ratings, calculate financial benefits, inspect systems, evaluate legal or regulatory obligations, or execute automation. Separate security, privacy, compliance, technical, and change-impact assessments are required before implementation. The sample scenarios and ratings are fictional.
