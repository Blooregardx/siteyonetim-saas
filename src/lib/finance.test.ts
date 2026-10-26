import { test } from "node:test";
import assert from "node:assert/strict";
import { outstanding, summarize } from "./finance";
test("kısmi, tam ve gecikmiş ödemeler doğru toplanır", () => {
  assert.deepEqual(summarize([
    { amountKurus: 250000, paidKurus: 100000, dueDate: "2026-10-01" },
    { amountKurus: 250000, paidKurus: 250000, dueDate: "2026-10-01" },
    { amountKurus: 100000, paidKurus: 0, dueDate: "2026-11-01" },
  ], "2026-10-26"), { totalKurus: 600000, collectedKurus: 350000, outstandingKurus: 250000, overdueKurus: 150000 });
});
test("vade günü gecikmiş sayılmaz", () => {
  assert.equal(summarize([{ amountKurus: 100, paidKurus: 0, dueDate: "2026-10-26" }], "2026-10-26").overdueKurus, 0);
});
test("geçersiz, kesirli ve fazla ödemeler reddedilir", () => {
  for (const [amountKurus, paidKurus] of [[-1, 0], [1.5, 0], [100, 101], [100, -1], [Infinity, 0], [NaN, 0], [Number.MAX_SAFE_INTEGER + 1, 0]]) {
    assert.throws(() => outstanding({ amountKurus, paidKurus, dueDate: "2026-10-01" }), RangeError);
  }
});
test("boş liste sıfır bakiye verir", () => assert.equal(summarize([], "2026-10-26").outstandingKurus, 0));
