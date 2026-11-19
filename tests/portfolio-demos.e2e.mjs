import { chromium } from "playwright";
import assert from "node:assert/strict";
import path from "node:path";
import { fileURLToPath } from "node:url";

async function assertNoHorizontalOverflow(page, label) {
  const dimensions = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    document: document.documentElement.scrollWidth,
    offenders: [...document.querySelectorAll("body *")]
      .map(element => {
        const rect = element.getBoundingClientRect();
        return {
          tag: element.tagName.toLowerCase(),
          id: element.id,
          className: typeof element.className === "string" ? element.className : "",
          left: Math.round(rect.left),
          right: Math.round(rect.right),
          width: Math.round(rect.width),
          scrollWidth: element.scrollWidth,
          clientWidth: element.clientWidth,
          parentClass: element.parentElement?.className || "",
          scrollContainerAncestor: (() => {
            let parent = element.parentElement;
            while (parent && parent !== document.body) {
              const overflow = getComputedStyle(parent).overflowX;
              if (["auto", "scroll", "hidden", "clip"].includes(overflow)) {
                return parent.className || parent.tagName.toLowerCase();
              }
              parent = parent.parentElement;
            }
            return null;
          })()
        };
      })
      .filter(item =>
        (item.right > document.documentElement.clientWidth + 1 || item.left < -1) &&
        !item.scrollContainerAncestor
      )
      .sort((a, b) => b.right - a.right)
      .slice(0, 20)
  }));
  assert.ok(
    dimensions.document <= dimensions.viewport + 1,
    `${label}: horizontal overflow (${dimensions.document}px document / ${dimensions.viewport}px viewport); offenders=${JSON.stringify(dimensions.offenders)}`
  );
}

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const browser = await chromium.launch({ headless: true });

try {
  const page = await browser.newPage();
  page.setDefaultTimeout(15000);

  // Operations Review Workspace: synthetic decision, counters, and persistence.
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

  // Full reload confirms persistence beyond the browser's in-memory state.
  await page.reload({ waitUntil: "networkidle" });
  await page.waitForFunction(() => document.querySelector("#total-count")?.textContent !== "—");
  const persistedEntry = page
    .locator("#history-list .history-entry")
    .filter({ hasText: "e2e-demo-reviewer" });
  await persistedEntry.waitFor();
  assert.match(await persistedEntry.innerText(), /Automated browser demonstration check/);
  assert.equal(Number(await page.locator("#pending-count").textContent()), initialPending - 1);
  assert.equal(Number(await page.locator("#decided-count").textContent()), initialDecided + 1);

  // Mobile layout: panels stack and page-level horizontal overflow is absent.
  await page.setViewportSize({ width: 375, height: 812 });
  await page.reload({ waitUntil: "networkidle" });
  await page.waitForFunction(() => document.querySelector("#total-count")?.textContent !== "—");
  await page.locator("#history-list .history-entry").filter({ hasText: "e2e-demo-reviewer" }).waitFor();
  await assertNoHorizontalOverflow(page, "Operations Review Workspace at 375px");
  const workspaceColumns = await page.locator(".workspace").evaluate(
    element => getComputedStyle(element).gridTemplateColumns.trim().split(/\\s+/).length
  );
  assert.equal(workspaceColumns, 1, "the Operations Review Workspace panels should stack on mobile");
  const workspacePanels = await page.locator(".workspace > .panel").evaluateAll(elements =>
    elements.map(element => {
      const rect = element.getBoundingClientRect();
      return { left: rect.left, right: rect.right };
    })
  );
  assert.equal(workspacePanels.length, 2);
  for (const rect of workspacePanels) {
    assert.ok(rect.left >= 0 && rect.right <= 376, "workspace panel must fit inside the mobile viewport");
  }

  // Campaign Performance Analyzer: local CSV import, filter, and executive report.
  await page.goto("http://127.0.0.1:8766/dashboard.html", { waitUntil: "networkidle" });
  const sample = path.join(
    root,
    "Demo Templates",
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
  assert.ok((await page.locator("#report-meta").textContent()).includes("sample_campaigns.csv"));
  assert.equal(await page.locator("#report-content .report-table-wrap table").count(), 1);
  assert.equal(await page.locator("#report-content .report-table-wrap").evaluate(element => getComputedStyle(element).overflowX), "auto");
  assert.ok(await page.locator("#print-report").isVisible());

  // Mobile dashboard and report smoke checks.
  await page.setViewportSize({ width: 375, height: 812 });
  await assertNoHorizontalOverflow(page, "Campaign Performance Analyzer at 375px");
  const kpiColumns = await page.locator(".kpis").evaluate(
    element => getComputedStyle(element).gridTemplateColumns.trim().split(/\\s+/).length
  );
  assert.equal(kpiColumns, 2, "campaign KPIs should use a two-column mobile layout");
  const channelFilterWidth = await page.locator("#channel-filter").evaluate(
    element => element.getBoundingClientRect().width
  );
  assert.ok(channelFilterWidth > 0 && channelFilterWidth <= 375, "channel filter must fit the mobile viewport");
  assert.equal(
    await page.evaluate(() => document.body.innerText.includes("\\n")),
    false,
    "dashboard must not render a literal backslash-n sequence"
  );

  await page.emulateMedia({ media: "print" });
  assert.equal(
    await page.locator(".masthead").evaluate(element => getComputedStyle(element).display),
    "none",
    "the dashboard chrome should be hidden in print mode"
  );
  assert.equal(
    await page.locator("#executive-report").evaluate(element => getComputedStyle(element).display),
    "block",
    "the executive report should remain visible in print mode"
  );
  assert.equal(
    await page.locator("#print-report").evaluate(element => getComputedStyle(element).display),
    "none",
    "the print control should not appear in the printed report"
  );
  await page.emulateMedia({ media: "screen" });

  console.log("PASS: Operations Review Workspace browser flow, persisted decision, and 375px mobile layout");
  console.log("PASS: Campaign Performance Analyzer import, filter, executive report, 375px mobile layout, and print media");
} finally {
  await browser.close();
}
