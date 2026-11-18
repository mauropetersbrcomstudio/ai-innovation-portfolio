# Selected Demo Guide

This guide covers three existing demonstrations selected for an initial portfolio presentation. All sample records are synthetic. These are local demonstrations, not production deployments.

## 1. Operations Review Workspace

**What to show:** a local intake review queue, item details, a recorded human-review decision, and persisted decision/event history.

**Requirements:** Python 3.10+; standard library only.

**Start:**

```bash
cd "AI Product Development/operations-review-workspace"
python server.py
```

Open `http://127.0.0.1:8765` (or the address printed by the server).

**Presentation sequence:**
1. Show queue totals and filter by lead/invoice or pending/decided.
2. Open a pending item and explain its routing reason and source reference.
3. Enter a clearly synthetic reviewer ID, select an outcome, provide a reason, and record it.
4. Refresh the workspace and show the saved decision and event history.

**Automated check:**

```bash
python -m unittest discover -s tests -v
```

**Boundaries:** loopback-only; reviewer ID is not authenticated; records are synthetic; no CRM, email, accounting, payment, or bank transfer action occurs. Do not expose the server to a LAN or internet.

## 2. Campaign Performance Analyzer

**What to show:** local CSV import, campaign metrics, filters, date comparison (when a valid `date` column exists), trend, and executive report.

**Requirements:** Python 3.10+ for the CLI; a modern browser for the dashboard; Node.js 20+ for browser-logic tests.

**Run the sample analysis:**

```bash
cd "Marketing Intelligence & Business Automation/campaign-performance-analyzer"
python analyzer.py --input sample_campaigns.csv --output-dir output
```

Open `dashboard.html` in a browser and load `sample_campaigns.csv`.

**Presentation sequence:**
1. Show the sample CSV loaded in the browser.
2. Filter by campaign and channel.
3. If the CSV contains valid dates, select a date range and inspect the immediately preceding equal-length period.
4. Show daily evolution and the executive report; use Print / Save as PDF if needed.
5. Show CLI outputs: `campaign_metrics.csv`, `exceptions.csv`, and `summary.json`.

**Automated checks:**

```bash
python -m unittest discover -s tests -v
node --test tests/dashboard-logic.test.js
```

**Boundaries:** browser processing is local and does not upload the selected CSV. Structural checks do not verify attribution; comparisons are descriptive, not causal. ROAS is not profit or ROI. No advertising-platform connection or budget recommendation is provided.

## 3. Campaign Launch QA & UTM Builder

**What to show:** pre-launch campaign metadata validation, generated tracking URLs, exceptions, and readiness summary.

**Requirements:** Python 3.10+; standard library only.

**Run:**

```bash
cd "Marketing Intelligence & Business Automation/campaign-launch-qa"
python launch_qa.py --input sample_campaigns.csv --output-dir output
```

**Presentation sequence:**
1. Run the synthetic sample.
2. Inspect `approved_campaigns.csv` and generated tracking URLs.
3. Inspect `exceptions.csv` and the reasons for rejected rows.
4. Show `summary.json` and explain `ready`, `review`, or `blocked`.
5. For a controlled exception demonstration, copy the sample CSV and change one field in the copy; keep the original unchanged.

**Automated check:**

```bash
python -m unittest discover -s tests -v
```

**Boundaries:** the tool does not publish or activate campaigns, verify destination ownership, consent, legal compliance, analytics configuration, live URL availability, or actual tracking collection. A `ready` result means only that implemented checks passed; it is not launch authorization.

## Verification status

The repository's GitHub Actions workflows have passed for these three projects:
- Operations Review Workspace integration tests.
- Campaign Performance Analyzer Python tests and browser-logic tests.
- Campaign Launch QA & UTM Builder Python tests.

CI evidence confirms the automated checks listed above. It does not establish that a human has launched the applications interactively on a local machine or verified every visual interaction. Record that manual demonstration separately when performed.
