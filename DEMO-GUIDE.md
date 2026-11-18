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

The cross-project Chromium check also records a synthetic review decision, reloads the page, and verifies that the decision remains in the history.

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

The cross-project Chromium check imports the included CSV, verifies the expected campaign count, applies the Search channel filter, and renders the executive report.

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

**Automated check:** the dedicated GitHub Actions workflow runs the unit tests and executes the sample CSV command, checking that the approved, exception, and summary files are non-empty.

**Boundaries:** the tool does not publish or activate campaigns, verify destination ownership, consent, legal compliance, analytics configuration, live URL availability, or actual tracking collection. A `ready` result means only that implemented checks passed; it is not launch authorization.

## Cross-project browser verification

The [Portfolio Demo Browser Tests workflow](./.github/workflows/portfolio-demo-browser-tests.yml) runs the Operations Review Workspace and Campaign Performance Analyzer in headless Chromium. It starts both services on loopback, uses the included synthetic records, and checks the principal browser paths. The workspace check includes a full page reload to verify that a recorded decision persists in its isolated SQLite database.

The test source is [`tests/portfolio-demos.e2e.mjs`](./tests/portfolio-demos.e2e.mjs). The Campaign Launch QA demonstration is checked separately by its own workflow because it is a command-line tool rather than a browser application.

A CI browser check is not a substitute for a person launching the demos on their own machine and reviewing the visual presentation. Do not claim that manual local review has occurred unless it is separately recorded.

## Verification status

The repository has dedicated automated workflows for all three demonstrations:
The latest recorded checks for this presentation path are:
- [Portfolio Demo Browser Tests](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44235238035) — passed; both browser flows completed, including persisted review history and executive report rendering.
- [Portfolio Quality Gate](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44235238079) — passed; 36 project READMEs validated and 224 Python tests passed across 34 suites.
- [Campaign Performance Analyzer Tests](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44235237936) — passed; six Python tests and the sample CLI output checks passed.

- Operations Review Workspace: Python integration tests and the cross-project browser flow.
- Campaign Performance Analyzer: Python tests, browser-logic tests, sample CLI execution, and the cross-project browser flow.
- Campaign Launch QA & UTM Builder: Python tests and sample CLI execution.

Use the linked GitHub Actions runs for the actual pass/fail result. Workflow configuration and test source code alone do not establish a successful run.

