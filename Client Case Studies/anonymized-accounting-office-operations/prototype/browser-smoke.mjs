import { chromium } from "playwright";
import assert from "node:assert/strict";

const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const nonReadRequests = [];
  page.on("request", request => {
    if (!["GET", "HEAD"].includes(request.method())) nonReadRequests.push(request.method());
  });
  await page.goto("http://127.0.0.1:8767", { waitUntil: "networkidle" });
  assert.equal(await page.title(), "Accounting Intelligence | Operations Control Center");

  await page.locator("#files").setInputFiles({
    name: "synthetic.csv", mimeType: "text/csv",
    buffer: Buffer.from(["date,amount,description","2026-10-01,125.50,Service fee",""].join(String.fromCharCode(10)))
  });
  await page.waitForFunction(() => document.querySelector("#mRecords")?.textContent === "1");
  assert.match(await page.locator("#recordRows").innerText(), /125.50/);

  await page.locator("#files").setInputFiles({
    name: "synthetic.ofx", mimeType: "application/x-ofx",
    buffer: Buffer.from(["<OFX>","<BANKTRANLIST>","<STMTTRN>","<DTPOSTED>20261001120000","<TRNAMT>-42.10","<NAME>Bank fee","</STMTTRN>","</BANKTRANLIST>","</OFX>"].join(String.fromCharCode(10)))
  });
  await page.waitForFunction(() => document.querySelector("#mRecords")?.textContent === "2");
  assert.match(await page.locator("#recordRows").innerText(), /-42.10/);

  await page.locator("#files").setInputFiles({
    name: "valid.xml", mimeType: "application/xml",
    buffer: Buffer.from("<root><item>synthetic</item></root>")
  });
  await page.waitForFunction(() => document.querySelector("#mFiles")?.textContent === "3");
  assert.match(await page.locator("#fileRows").innerText(), /XML BEM FORMADO/);

  await page.locator("#files").setInputFiles({
    name: "unsafe.xml", mimeType: "application/xml",
    buffer: Buffer.from('<!DOCTYPE root [<!ENTITY x SYSTEM "file:///etc/passwd">]><root>&x;</root>')
  });
  await page.waitForFunction(() => document.querySelector("#mFiles")?.textContent === "4");
  assert.match(await page.locator("#fileRows").innerText(), /ERRO DE LEITURA/);

  await page.locator("#files").setInputFiles({
    name: "unsupported.pdf", mimeType: "application/pdf", buffer: Buffer.from("not read")
  });
  await page.waitForFunction(() => document.querySelector("#mFiles")?.textContent === "5");
  assert.match(await page.locator("#fileRows").innerText(), /NÃO SUPORTADO/);

  await page.locator("#files").setInputFiles({
    name: "oversized.csv", mimeType: "text/csv", buffer: Buffer.alloc(10 * 1024 * 1024 + 1)
  });
  await page.waitForFunction(() => document.querySelector("#mFiles")?.textContent === "6");
  assert.match(await page.locator("#fileRows").innerText(), /REJEITADO · LIMITE 10 MB/);

  await page.setViewportSize({ width: 375, height: 812 });
  const dims = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    page: document.documentElement.scrollWidth
  }));
  assert.ok(dims.page <= dims.viewport + 1, `Mobile page overflow: ${JSON.stringify(dims)}`);

  await page.locator("#clear").click();
  assert.equal(await page.locator("#mFiles").textContent(), "0");
  assert.equal(await page.locator("#mRecords").textContent(), "0");
  assert.deepEqual(nonReadRequests, [], "source files must not be uploaded or posted");
  console.log("PASS: CSV/OFX normalization, XML validation and DTD rejection, unsupported/oversized files, session clearing, mobile layout, and no-upload boundary");
} finally {
  await browser.close();
}
