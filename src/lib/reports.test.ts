import { test } from 'node:test';
import assert from 'node:assert/strict';
import { reportBalance,reportInput,reportTotals,safeInteger } from './reports';
test('ödenmedi/kısmi/tam ve bağımsız vade hesabı',()=>{
 assert.equal(reportBalance(200000,0,0,'2026-10-01','2026-10-30').status,'UNPAID');
 const partial=reportBalance(200000,75000,0,'2026-10-01','2026-10-30');assert.equal(partial.status,'PARTIAL');assert.equal(partial.overdue,true);assert.equal(partial.remainingKurus,125000);
 assert.equal(reportBalance(200000,200000,0,'2026-10-01','2026-10-30').status,'PAID');assert.equal(reportBalance(200000,200000,0,'2026-10-01','2026-10-30').overdue,false);
 assert.equal(reportBalance(200000,0,0,'2026-10-30','2026-10-30').overdue,false);
});
test('750 TL tam ters kaydı, doğru net toplam ve taşma reddi',()=>{
 const balance=reportBalance(200000,75000,75000,'2026-10-01','2026-10-30');assert.equal(balance.netKurus,0);assert.equal(balance.remainingKurus,200000);assert.equal(balance.status,'UNPAID');
 assert.deepEqual(reportTotals(200000n,75000n,75000n),{chargedKurus:200000,grossKurus:75000,reversedKurus:75000,netKurus:0,remainingKurus:200000});assert.throws(()=>safeInteger(9007199254740992n));
});
test('geçersiz rapor filtreleri reddedilir',()=>{for(const patch of [{period:'2026-13'},{page:0},{page:1.5},{status:'UNKNOWN'},{debtOnly:'true'}])assert.equal(reportInput.safeParse({organizationId:'org',...patch}).success,false);});
