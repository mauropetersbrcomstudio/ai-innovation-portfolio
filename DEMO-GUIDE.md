# Selected Demo Guide

This guide covers three existing demonstrations selected for an initial portfolio presentation. All sample records are synthetic. These are local demonstrations, not production deployments.

## 1. Operations Review Workspace

**What to show:** a local intake review queue, item details, a recorded human-review decision, and persisted decision/event history.

**Requirements:** Python 3.10+; standard library only.

**Start:**

```bash
cd "Demo Templates/AI Product Development/operations-review-workspace"
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
cd "Demo Templates/Marketing Intelligence & Business Automation/campaign-performance-analyzer"
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
cd "Demo Templates/Marketing Intelligence & Business Automation/campaign-launch-qa"
python launch_qa.py --input sample_campaigns.csv --output-dir output
```

**Presentation sequence:**
1. Run the synthetic sample.
2. Inspect `approved_campaigns.csv` and generated tracking URLs.
3. Inspect `exceptions.csv` and the reasons for rejected rows.
4. Show `summary.json` and explain `ready`, `review`, or `blocked`.
5. For a controlled exception demonstration, copy the sample CSV and change one field in the copy; keep the original unchanged.

**Automated check:** the internal validation materials describe the unit tests and sample CSV command, which check that the approved, exception, and summary files are non-empty.

**Boundaries:** the tool does not publish or activate campaigns, verify destination ownership, consent, legal compliance, analytics configuration, live URL availability, or actual tracking collection. A `ready` result means only that implemented checks passed; it is not launch authorization.

## Cross-project browser verification

Cross-project browser checks for the Operations Review Workspace and Campaign Performance Analyzer are maintained with the private internal validation materials. Each demo's README documents its local test commands. The workspace check records a synthetic decision and verifies that it persists after a page reload.

The Campaign Launch QA demonstration is a command-line tool; its automated checks are maintained with the private internal validation materials.

The browser test also includes 375-pixel responsive smoke checks for both interactive demos. It verifies the Operations Review Workspace's stacked panels and the Campaign Performance Analyzer's KPI/filter layout without page-level horizontal overflow. Print-media emulation checks that the executive report remains visible while the dashboard masthead and print control are hidden. These checks are targeted and do not replace a human-led visual review on the intended presentation device.

A CI browser check is not a substitute for a person launching the demos on their own machine and reviewing the visual presentation. Do not claim that manual local review has occurred unless it is separately recorded.

## Verification status

Historical automated evidence for the current responsive baseline is available in these GitHub Actions runs:
- [Portfolio Demo Browser Tests](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44242143780) — passed; persisted workspace decision, 375-pixel mobile layouts for both apps, Campaign Performance Analyzer import/filter/report, and print-media behavior.
- [Portfolio Quality Gate](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44242143819) — passed; 36 project READMEs, eight category indexes, root index coverage, and 224 Python tests across 35 suites.
- [Campaign Performance Analyzer Tests](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44242143783) — passed; Python tests, browser-logic tests, and sample CLI output checks.
- [Marketing Analytics Pipeline Tests](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44242144371) — passed.
- [Operations Review Workspace Tests](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44241490459) — passed; six integration tests.

- Operations Review Workspace: Python integration tests and the cross-project browser flow.
- Campaign Performance Analyzer: Python tests, browser-logic tests, sample CLI execution, and the cross-project browser flow.
- Campaign Launch QA & UTM Builder: Python tests and sample CLI execution.

Use the linked GitHub Actions runs for the actual pass/fail result. Workflow configuration and test source code alone do not establish a successful run.

