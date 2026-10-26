/** All monetary values are integer kuruş; never calculate balances with floats. */
export type Charge = { amountKurus: number; paidKurus: number; dueDate: string };
export function outstanding(charge: Charge): number {
  for (const value of [charge.amountKurus, charge.paidKurus]) {
    if (!Number.isSafeInteger(value) || value < 0) throw new RangeError("Tutar negatif olmayan güvenli bir tam sayı olmalı.");
  }
  if (charge.paidKurus > charge.amountKurus) throw new RangeError("Ödeme borç tutarını aşamaz.");
  return charge.amountKurus - charge.paidKurus;
}
export function summarize(charges: Charge[], today: string) {
  return charges.reduce((result, charge) => {
    const remaining = outstanding(charge);
    result.totalKurus += charge.amountKurus;
    result.collectedKurus += charge.paidKurus;
    result.outstandingKurus += remaining;
    if (charge.dueDate < today) result.overdueKurus += remaining;
    return result;
  }, { totalKurus: 0, collectedKurus: 0, outstandingKurus: 0, overdueKurus: 0 });
}
export const formatMoney = (kurus: number) => new Intl.NumberFormat("tr-TR", { style: "currency", currency: "TRY", maximumFractionDigits: 2 }).format(kurus / 100);
