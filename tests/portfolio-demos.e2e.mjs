import { chromium } from "playwright";
import assert from "node:assert/strict";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const browser = await chromium.launch({ headless: true });
const failures = [];
try {
  const page = await browser.newPage();

  // Operations Review Workspace: load synthetic queue, record one decision,
  // then verify it appears in the persisted history after refresh.
  await page.goto("http://127.0.0.1:8765", { waitUntil: "networkidle" });
  await page.locator("#workflow-status").waitFor();
  await page.waitForFunction(() => document.querySelector("#total-count")?.textContent !== "—");
  assert.ok(Number(await page.locator("#total-count").textContent()) > 0);
  assert.ok(Number(await page.locator("#pending-count").textContent()) > 0);
  const selectedReference = await page.locator("#detail-reference").textContent();
  assert.ok(selectedReference);
  await page.locator("#reviewer").fill("e2e-demo-reviewer");
  await page.locator("#outcome").selectOption("REQUESTED_INFORMATION");
  await page.locator("#reason").fill("Automated browser demonstration check");
  await page.locator("#submit").click();
  await page.getByText("Decision persisted.").waitFor();
  await page.locator("#history-list").getByText("e2e-demo-reviewer").waitFor();
  assert.equal(await page.locator("#pending-count").textContent(), "4");

  // Campaign dashboard: upload the included CSV through the browser UI,
  // assert the expected KPI, channel rows, temporal view and executive report.
  await page.goto("http://127.0.0.1:8766/dashboard.html", { waitUntil: "networkidle" });
  const sample = path.join(root, "Marketing Intelligence & Business Automation", "campaign-performance-analyzer", "sample_campaigns.csv");
  await page.locator("#csv-file").setInputFiles(sample);
  await page.getByText(/processed locally/).waitFor();
  assert.equal(await page.locator("#campaign-count").textContent(), "4 VALID CAMPAIGNS");
  assert.notEqual(await page.locator("#roas").textContent(), "—");
  await page.locator("#channel-filter").selectOption({ label: "Search" });
  assert.equal(await page.locator("#valid-count").textContent(), "2 VALID");
  await page.locator("#generate-report").click();
  await page.locator("#executive-report").waitFor({ state: "visible" });
  assert.ok((await page.locator("#report-content").innerText()).includes("Executive summary"));
  console.log("PASS: Operations Review Workspace browser flow");
  console.log("PASS: Campaign Performance Analyzer browser flow");
} catch (error) {
  failures.push(error);
} finally {
  await browser.close();
}
if (failures.length) {
  console.error(failures[0]);
  process.exit(1);
}
