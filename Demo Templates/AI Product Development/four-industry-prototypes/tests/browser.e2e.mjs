import { chromium } from "playwright";
import assert from "node:assert/strict";

const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage();
  page.setDefaultTimeout(10000);
  page.on("dialog", dialog => dialog.accept("Revisão humana sintética"));
  const clients = { education: "FORMARE", retail: "CASA VIVA", hospitality: "AURORA HOTÉIS", manufacturing: "TECNOFLEX" };
  for (const sector of Object.keys(clients)) {
    await page.goto(`http://127.0.0.1:8768/?sector=${sector}&presentation=1`, { waitUntil: "networkidle" });
    assert.equal(await page.locator("#client-name").textContent(), clients[sector]);
    assert.equal(await page.locator("#scenario-nav button:visible").count(), 0);
    await page.locator('[data-example="1"]').click();
    await page.locator('#intake button[type="submit"]').click();
    assert.equal(await page.locator("#total").textContent(), "1");
    assert.equal(await page.locator("#pending").textContent(), "1");
    assert.equal(await page.locator("#urgent").textContent(), "1");
    assert.ok(await page.locator(".item ul li").count() > 0);
    await page.locator('[data-decision="Aprovado na simulação"]').click();
    assert.equal(await page.locator("#decided").textContent(), "1");
    await page.reload({ waitUntil: "networkidle" });
    assert.equal(await page.locator("#decided").textContent(), "1");
    assert.match(await page.locator("#history").innerText(), /Aprovado na simulação/);
  }
  await page.setViewportSize({ width: 375, height: 812 });
  await page.reload({ waitUntil: "networkidle" });
  const widths = await page.evaluate(() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]);
  assert.ok(widths[0] <= widths[1] + 1, `mobile horizontal overflow: ${widths}`);
  assert.equal((await page.request.get("http://127.0.0.1:8768/brand-sheet.jpg")).status(), 200);
  console.log("PASS: four sector workflows, local decisions, persistence, and 375px layout");
} finally {
  await browser.close();
}
