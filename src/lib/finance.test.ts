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

test("net tahsilat, ters kayıt ve güvenli tam sayı toplamları", async () => {
 const { paymentTotals, chargeBalance, financialSummary } = await import("./finance");
 const payments=[{amountKurus:4000,reversal:{amountKurus:4000}},{amountKurus:6000}];
 assert.deepEqual(paymentTotals(payments),{grossKurus:10000,reversedKurus:4000,netKurus:6000});
 assert.equal(chargeBalance({amountKurus:10000,payments}).remainingKurus,4000);
 assert.equal(financialSummary([{amountKurus:10000,payments}]).netKurus,6000);
 assert.throws(()=>paymentTotals([{amountKurus:4000,reversal:{amountKurus:1}}]));
 assert.throws(()=>paymentTotals([{amountKurus:Number.MAX_SAFE_INTEGER},{amountKurus:1}]));
 assert.throws(()=>chargeBalance({amountKurus:100,payments:[{amountKurus:101}]}));
});
