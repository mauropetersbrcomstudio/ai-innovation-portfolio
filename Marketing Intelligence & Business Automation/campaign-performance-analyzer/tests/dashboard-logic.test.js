import test from "node:test";
import assert from "node:assert/strict";
import { analyzeRows, parseCsv, summarizeByChannel } from "../dashboard-logic.js";

test("parses quoted commas and escaped quotes", () => {
  const rows = parseCsv('campaign,channel,spend,impressions,clicks,conversions,revenue\n"Spring, launch",Search,10,100,5,1,20\n');
  assert.equal(rows[0].campaign, "Spring, launch");
  assert.equal(analyzeRows(rows).valid.length, 1);
});

test("rejects missing required headers", () => {
  assert.throws(() => parseCsv("campaign,channel\nA,Search"), /Missing required columns/);
});

test("calculates metrics from uploaded records", () => {
  const rows = parseCsv("campaign,channel,spend,impressions,clicks,conversions,revenue\nA,Search,100,1000,100,10,400\nB,Social,100,9000,90,9,300\n");
  const result = analyzeRows(rows);
  assert.equal(result.valid.length, 2);
  assert.equal(result.summary.spend, 200);
  assert.equal(result.summary.roas, 3.5);
  assert.equal(result.summary.ctr, 190 / 10000);
});

test("routes structurally invalid rows to exceptions", () => {
  const rows = parseCsv("campaign,channel,spend,impressions,clicks,conversions,revenue\nBad,Search,-1,100,10,2,20\nImpossible,Social,1,10,11,1,2\n");
  const result = analyzeRows(rows);
  assert.equal(result.valid.length, 0);
  assert.equal(result.exceptions.length, 2);
});

test("zero denominators remain null", () => {
  const rows = parseCsv("campaign,channel,spend,impressions,clicks,conversions,revenue\nZero,Other,0,0,0,0,0\n");
  const result = analyzeRows(rows);
  for (const key of ["ctr", "conversion_rate", "cpc", "cpa", "roas"]) {
    assert.equal(result.valid[0][key], null);
    assert.equal(result.summary[key], null);
  }
});

test("unclosed quoted fields are rejected", () => {
  assert.throws(() => parseCsv('campaign,channel,spend,impressions,clicks,conversions,revenue\n"Open,Search,1,2,1,1,2'), /unclosed quoted field/);
});

test("summarizes channel ratios from channel totals", () => {
  const source = [
    "campaign,channel,spend,impressions,clicks,conversions,revenue",
    "A,Search,100,1000,100,10,200",
    "B,Search,300,9000,90,9,600",
    "C,Social,100,1000,100,10,500"
  ].join(String.fromCharCode(10));
  const rows = parseCsv(source);
  const result = analyzeRows(rows);
  const channels = summarizeByChannel(result.valid);
  const search = channels.find(item => item.channel === "Search");
  assert.equal(search.campaign_count, 2);
  assert.equal(search.spend, 400);
  assert.equal(search.conversions, 19);
  assert.equal(search.roas, 2);
  assert.equal(search.cpa, 400 / 19);
});
