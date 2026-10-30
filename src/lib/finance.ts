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
const moneyFormatter = new Intl.NumberFormat("tr-TR", { style: "currency", currency: "TRY", minimumFractionDigits: 2, maximumFractionDigits: 2 });
export function formatMoney(kurus:number){
 if(!Number.isSafeInteger(kurus))throw new RangeError("Geçersiz finansal tutar.");
 const value=BigInt(kurus),negative=value<0n,absolute=negative?-value:value,whole=absolute/100n;
 // Format the whole lira as BigInt; replace only the fraction to preserve every kuruş.
 const formattedWhole=negative?(whole===0n?-0:-whole):whole;
 return moneyFormatter.formatToParts(formattedWhole).map(part=>part.type==="fraction"?String(absolute%100n).padStart(2,"0"):part.value).join("");
}

export type Receipt = { amountKurus: number; reversal?: { amountKurus: number } | null };
function addKurus(a: number, b: number) {
 const result = a + b;
 if (!Number.isSafeInteger(result) || result < 0) throw new RangeError("Geçersiz finansal toplam.");
 return result;
}
export function paymentTotals(payments: Receipt[]) {
 let grossKurus = 0, reversedKurus = 0;
 for (const payment of payments) {
  if (!Number.isSafeInteger(payment.amountKurus) || payment.amountKurus <= 0) throw new RangeError("Geçersiz tahsilat.");
  if (payment.reversal && payment.reversal.amountKurus !== payment.amountKurus) throw new RangeError("Yalnız tam ters kayıt desteklenir.");
  grossKurus = addKurus(grossKurus, payment.amountKurus);
  reversedKurus = addKurus(reversedKurus, payment.reversal?.amountKurus ?? 0);
 }
 return { grossKurus, reversedKurus, netKurus: grossKurus - reversedKurus };
}
export function chargeBalance(charge: { amountKurus: number; payments: Receipt[] }) {
 const totals = paymentTotals(charge.payments);
 return { ...totals, remainingKurus: outstanding({ amountKurus: charge.amountKurus, paidKurus: totals.netKurus, dueDate: "" }) };
}
export function financialSummary(charges: { amountKurus: number; payments: Receipt[] }[]) {
 return charges.reduce((totals, charge) => {
  const balance = chargeBalance(charge);
  return { chargedKurus: addKurus(totals.chargedKurus, charge.amountKurus), grossKurus: addKurus(totals.grossKurus, balance.grossKurus), reversedKurus: addKurus(totals.reversedKurus, balance.reversedKurus), netKurus: addKurus(totals.netKurus, balance.netKurus), remainingKurus: addKurus(totals.remainingKurus, balance.remainingKurus) };
 }, { chargedKurus: 0, grossKurus: 0, reversedKurus: 0, netKurus: 0, remainingKurus: 0 });
}
