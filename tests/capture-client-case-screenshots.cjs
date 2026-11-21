"use strict";

const { chromium } = require(process.env.PLAYWRIGHT_MODULE_PATH || "playwright");
const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");

const root = path.resolve(__dirname, "..");
const cases = [
  { folder: "formare-educacao-profissional", name: "FORMARE", layout: "education", shell: "school-shell" },
  { folder: "casa-viva-varejo", name: "CASA VIVA", layout: "retail", shell: "store-shell" },
  { folder: "aurora-hoteis-hotelaria", name: "AURORA HOTÉIS", layout: "hospitality", shell: "hotel-shell" },
  { folder: "tecnoflex-industria", name: "TECNOFLEX", layout: "manufacturing", shell: "factory-shell" },
];

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: process.env.CHROME_PATH || undefined });
  try {
    for (const item of cases) {
      const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
      const page = await context.newPage();
      page.on("dialog", dialog => dialog.accept("Revisão sintética"));
      const url = `http://127.0.0.1:8770/Client%20Case%20Studies/${item.folder}/index.html`;
      await page.goto(url, { waitUntil: "networkidle" });
      assert.equal(await page.locator("#client-name").textContent(), item.name);
      assert.equal(await page.locator(`body.layout-${item.layout} .${item.shell}`).count(), 1);
      assert.equal(await page.locator("#scenario-nav button:visible").count(), 0);
      for (const example of ["0", "1"]) {
        await page.locator(`[data-example="${example}"]`).click();
        await page.locator('#intake button[type="submit"]').click();
      }
      assert.equal(await page.locator("#total").textContent(), "2");
      assert.equal(await page.locator("#urgent").textContent(), "1");
      await page.evaluate(() => document.fonts.ready);
      const imagePath = path.join(root, "Client Case Studies", item.folder, "dashboard.png");
      fs.mkdirSync(path.dirname(imagePath), { recursive: true });
      await page.screenshot({ path: imagePath, fullPage: true, animations: "disabled" });
      await page.locator('[data-decision="Aprovado na simulação"]').first().click();
      assert.equal(await page.locator("#decided").textContent(), "1");
      await page.reload({ waitUntil: "networkidle" });
      assert.equal(await page.locator("#decided").textContent(), "1");
      await page.setViewportSize({ width: 375, height: 812 });
      const [scrollWidth, clientWidth] = await page.evaluate(() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]);
      assert.ok(scrollWidth <= clientWidth + 1, `${item.name}: mobile overflow ${scrollWidth}/${clientWidth}`);
      console.log(`Captured ${item.name}: ${path.relative(root, imagePath)}`);
      await context.close();
    }
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
