import { chromium } from "playwright";
import assert from "node:assert/strict";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const browser = await chromium.launch({ headless: true });

try {
  const page = await browser.newPage();
  page.setDefaultTimeout(15000);

  // Operations Review Workspace: record a synthetic decision, verify the
  // queue counters, reload the page, and confirm the decision still exists.
  await page.goto("http://127.0.0.1:8765", { waitUntil: "networkidle" });
  await page.locator("#workflow-status").waitFor();
  await page.waitForFunction(() => document.querySelector("#total-count")?.textContent !== "—");

  const initialPending = Number(await page.locator("#pending-count").textContent());
  const initialDecided = Number(await page.locator("#decided-count").textContent());
  assert.ok(initialPending > 0, "the synthetic queue must contain a pending item");

  const selectedReference = (await page.locator("#detail-reference").textContent())?.trim();
  assert.ok(selectedReference, "the workspace must select an item for review");

  await page.locator("#reviewer").fill("e2e-demo-reviewer");
  await page.locator("#outcome").selectOption("REQUESTED_INFORMATION");
  await page.locator("#reason").fill("Automated browser demonstration check");
  await page.locator("#submit").click();
  await page.getByText("Decision persisted.").waitFor();

  const decisionEntry = page
    .locator("#history-list .history-entry")
    .filter({ hasText: "e2e-demo-reviewer" });
  await decisionEntry.waitFor();
  assert.match(await decisionEntry.innerText(), /Automated browser demonstration check/);
  assert.equal(Number(await page.locator("#pending-count").textContent()), initialPending - 1);
  assert.equal(Number(await page.locator("#decided-count").textContent()), initialDecided + 1);

  // A full page reload verifies that the decision is stored, not just held
  // in the browser's current in-memory snapshot.
  await page.reload({ waitUntil: "networkidle" });
  await page.waitForFunction(() => document.querySelector("#total-count")?.textContent !== "—");
  const persistedEntry = page
    .locator("#history-list .history-entry")
    .filter({ hasText: "e2e-demo-reviewer" });
  await persistedEntry.waitFor();
  assert.match(await persistedEntry.innerText(), /Automated browser demonstration check/);
  assert.equal(Number(await page.locator("#pending-count").textContent()), initialPending - 1);
  assert.equal(Number(await page.locator("#decided-count").textContent()), initialDecided + 1);

  // Campaign Performance Analyzer: import the synthetic CSV, filter by
  // channel, and render the executive report in the browser.
  await page.goto("http://127.0.0.1:8766/dashboard.html", { waitUntil: "networkidle" });
  const sample = path.join(
    root,
    "Marketing Intelligence & Business Automation",
    "campaign-performance-analyzer",
    "sample_campaigns.csv"
  );
  await page.locator("#csv-file").setInputFiles(sample);
  await page.waitForFunction(() =>
    document.querySelector("#file-status")?.textContent.includes("processed locally")
  );

  assert.equal(await page.locator("#campaign-count").textContent(), "4 VALID CAMPAIGNS");
  assert.notEqual(await page.locator("#roas").textContent(), "—");
  await page.locator("#channel-filter").selectOption({ label: "Search" });
  assert.equal(await page.locator("#valid-count").textContent(), "1 VALID");
  await page.locator("#generate-report").click();
  await page.locator("#executive-report").waitFor({ state: "visible" });
  assert.ok((await page.locator("#report-content").innerText()).includes("Executive summary"));

  console.log("PASS: Operations Review Workspace browser flow and persisted decision");
  console.log("PASS: Campaign Performance Analyzer browser import, filter, and report flow");
} finally {
  await browser.close();
}
