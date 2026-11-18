import test from "node:test";
import assert from "node:assert/strict";
import { monthlyData } from "./data.js";
import { filterPeriod, summarize } from "./metrics.js";

test("summarizes revenue, orders, AOV, and conversion", () => {
  const result = summarize([
    { revenue: 200, orders: 4, visits: 100 },
    { revenue: 300, orders: 6, visits: 100 }
  ]);
  assert.equal(result.revenue, 500);
  assert.equal(result.orders, 10);
  assert.equal(result.averageOrderValue, 50);
  assert.equal(result.conversionRate, 5);
});

test("returns zero rates for empty input", () => {
  assert.deepEqual(summarize([]), {
    revenue: 0, orders: 0, visits: 0, averageOrderValue: 0, conversionRate: 0
  });
});

test("filters quarterly records without mutating source data", () => {
  const q1 = filterPeriod(monthlyData, "q1");
  assert.equal(q1.length, 3);
  assert.equal(monthlyData.length, 6);
  assert.ok(q1.every(row => row.quarter === "q1"));
});

test("all period returns a copy of all records", () => {
  const all = filterPeriod(monthlyData, "all");
  assert.equal(all.length, 6);
  assert.notEqual(all, monthlyData);
});
