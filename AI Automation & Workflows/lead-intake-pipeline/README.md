# Lead Intake Pipeline

**Status: DEMO**

A local Python example of a first-pass lead intake process for a small sales team. It reads a CSV file, checks and standardizes the records, flags duplicate email addresses, applies a simple qualification score, and separates leads into follow-up groups.

The workflow uses the Python standard library; no external services or third-party packages are required.

## What it does

1. Checks that required fields are present and that email addresses have a basic valid shape.
2. Standardizes names, email addresses, company names, and source labels.
3. Flags later rows that repeat an email address and leaves those duplicates out of lead routing.
4. Calculates a score using the rules below.
5. Assigns each valid record to `priority`, `standard`, or `review`.
6. Writes the processed records, exceptions, and a summary to the output directory.

## Run it

Requires Python 3.10 or newer. From this directory, run:

```bash
python pipeline.py --input sample_leads.csv --output-dir output
```

To run the tests:

```bash
python -m unittest discover -s tests -v
```

## How the score is calculated

- **+30** when a company is supplied.
- **+25** when a business email is supplied. Common free-mail domains do not qualify for these points.
- **+25** when the requested service is supplied.
- **+20** when the lead source is supplied.

The resulting score determines the route:

- **70–100:** priority
- **40–69:** standard
- **0–39:** review

These weights are example rules chosen to make the workflow easy to inspect. They are not based on measured conversion data and should not be treated as a prediction of sales potential.

## Files produced

- `processed_leads.csv` — records that passed validation and were routed.
- `exceptions.csv` — rows that need attention, including invalid and duplicate records.
- `summary.json` — a summary of the run.

## Data and limitations

The included CSV contains sample data. Use synthetic or appropriately authorized information when trying the workflow. This demo does not connect to a CRM, send messages, or update external systems. Its email check looks at format only; it does not confirm that a mailbox exists.
