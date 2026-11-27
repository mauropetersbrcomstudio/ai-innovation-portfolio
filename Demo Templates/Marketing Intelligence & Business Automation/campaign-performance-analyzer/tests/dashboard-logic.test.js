import test from "node:test";
import assert from "node:assert/strict";
import { analyzeRows, comparePeriods, isIsoDate, parseCsv, summarizeByChannel, summarizeCampaigns } from "../dashboard-logic.js";

test("parses quoted commas and escaped quotes", () => {
  const rows = parseCsv('campaign,channel,spend,impressions,clicks,conversions,revenue\n"Spring, launch",Search,10,100,5,1,20\n');
  assert.equal(rows[0].campaign, "Spring, launch");
  assert.equal(analyzeRows(rows).valid.length, 1);
});
test("rejects missing required headers", () => assert.throws(() => parseCsv("campaign,channel\nA,Search"), /Missing required columns/));
test("calculates metrics from uploaded records", () => {
  const result = analyzeRows(parseCsv("campaign,channel,spend,impressions,clicks,conversions,revenue\nA,Search,100,1000,100,10,400\nB,Social,100,9000,90,9,300\n"));
  assert.equal(result.valid.length, 2); assert.equal(result.summary.spend, 200);
  assert.equal(result.summary.roas, 3.5); assert.equal(result.summary.ctr, 190 / 10000);
});
test("routes structurally invalid rows to exceptions", () => {
  const result = analyzeRows(parseCsv("campaign,channel,spend,impressions,clicks,conversions,revenue\nBad,Search,-1,100,10,2,20\nImpossible,Social,1,10,11,1,2\n"));
  assert.equal(result.valid.length, 0); assert.equal(result.exceptions.length, 2);
});
test("zero denominators remain null", () => {
  const result = analyzeRows(parseCsv("campaign,channel,spend,impressions,clicks,conversions,revenue\nZero,Other,0,0,0,0,0\n"));
  for (const key of ["ctr", "conversion_rate", "cpc", "cpa", "roas"]) { assert.equal(result.valid[0][key], null); assert.equal(result.summary[key], null); }
});
test("unclosed quoted fields are rejected", () => assert.throws(() => parseCsv('campaign,channel,spend,impressions,clicks,conversions,revenue\n"Open,Search,1,2,1,1,2'), /unclosed quoted field/));
test("summarizes channel ratios from channel totals", () => {
  const rows = parseCsv(["campaign,channel,spend,impressions,clicks,conversions,revenue","A,Search,100,1000,100,10,200","B,Search,300,9000,90,9,600","C,Social,100,1000,100,10,500"].join(String.fromCharCode(10)));
  const search = summarizeByChannel(analyzeRows(rows).valid).find(item => item.channel === "Search");
  assert.equal(search.campaign_count, 2); assert.equal(search.spend, 400); assert.equal(search.conversions, 19);
  assert.equal(search.roas, 2); assert.equal(search.cpa, 400 / 19);
});
test("summarizes a filtered subset", () => {
  const rows = parseCsv(["campaign,channel,spend,impressions,clicks,conversions,revenue","A,Search,100,1000,100,10,200","B,Social,300,9000,90,9,600"].join(String.fromCharCode(10)));
  const summary = summarizeCampaigns(analyzeRows(rows).valid.filter(item => item.channel === "Search"));
  assert.equal(summary.campaign_count, 1); assert.equal(summary.spend, 100); assert.equal(summary.roas, 2);
});
test("exceptions retain channel for filtering", () => {
  const result = analyzeRows(parseCsv(["campaign,channel,spend,impressions,clicks,conversions,revenue","Broken,Social,-1,100,10,2,20"].join(String.fromCharCode(10))));
  assert.equal(result.exceptions[0].channel, "Social");
});
test("validates strict ISO dates", () => {
  assert.equal(isIsoDate("2026-11-18"), true);
  assert.equal(isIsoDate("2026-02-30"), false);
  assert.equal(isIsoDate("18/11/2026"), false);
});
test("keeps legacy CSVs without a date column working", () => {
  const result = analyzeRows(parseCsv("campaign,channel,spend,impressions,clicks,conversions,revenue\nLegacy,Search,10,100,5,1,20"));
  assert.equal(result.hasDate, false); assert.equal(result.valid.length, 1);
});
test("rejects invalid dates when date column is supplied", () => {
  const result = analyzeRows(parseCsv("campaign,channel,date,spend,impressions,clicks,conversions,revenue\nBad,Search,2026-02-30,10,100,5,1,20"));
  assert.equal(result.valid.length, 0); assert.match(result.exceptions[0].reason, /YYYY-MM-DD/);
});
test("compares current period with immediately preceding equal-length period", () => {
  const rows = parseCsv([
    "campaign,channel,date,spend,impressions,clicks,conversions,revenue",
    "Old A,Search,2026-11-01,100,1000,100,10,200",
    "Old B,Search,2026-11-02,100,1000,100,10,200",
    "New A,Search,2026-11-03,150,1000,100,15,450",
    "New B,Search,2026-11-04,150,1000,100,15,450"
  ].join(String.fromCharCode(10)));
  const valid = analyzeRows(rows).valid;
  const result = comparePeriods(valid, "2026-11-03", "2026-11-04");
  assert.equal(result.current.summary.spend, 300);
  assert.equal(result.previous.summary.spend, 200);
  assert.equal(result.current.summary.roas, 3);
  assert.equal(result.previous.summary.roas, 2);
  assert.equal(result.previous.start, "2026-11-01");
  assert.equal(result.previous.end, "2026-11-02");
});
test("rejects reversed period boundaries", () => {
  assert.throws(() => comparePeriods([], "2026-11-04", "2026-11-03"), /valid start and end/);
});


test("summarizes temporal evolution by date using aggregate totals", async () => {
  const { summarizeTimeline } = await import("../dashboard-logic.js");
  const rows = parseCsv([
    "campaign,channel,date,spend,impressions,clicks,conversions,revenue",
    "A,Search,2026-11-01,100,1000,100,10,200",
    "B,Social,2026-11-01,50,500,25,5,150",
    "A,Search,2026-11-02,200,2000,100,20,600"
  ].join(String.fromCharCode(10)));
  const timeline = summarizeTimeline(analyzeRows(rows).valid);
  assert.equal(timeline.length, 2);
  assert.equal(timeline[0].spend, 150);
  assert.equal(timeline[0].conversions, 15);
  assert.equal(timeline[0].roas, 350 / 150);
  assert.equal(timeline[1].spend, 200);
});
