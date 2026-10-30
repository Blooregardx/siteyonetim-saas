import { test } from 'node:test';
import assert from 'node:assert/strict';
import { reportBusinessDate,reportBalance,reportInput,reportTotals,safeInteger } from './reports';
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

test('İstanbul 00.30 ve 02.59 sınırları, vade günü ve ertesi gün',()=>{
 for(const instant of ['2026-10-30T21:30:00Z','2026-10-30T23:59:00Z']){
  const today=reportBusinessDate(new Date(instant));assert.equal(today,'2026-10-31');
  assert.equal(reportBalance(10000,0,0,'2026-10-31',today).overdue,false);
  assert.equal(reportBalance(10000,0,0,'2026-10-30',today).overdue,true);
 }
 assert.equal(reportBusinessDate(new Date('2026-10-30T20:59:59Z')),'2026-10-30');
 assert.equal(reportBusinessDate(new Date('2026-10-30T21:00:00Z')),'2026-10-31');
 assert.equal(reportBusinessDate(new Date('2026-12-31T21:30:00Z')),'2027-01-01');
});
test('iş günü farklı sistem saat dilimlerinden bağımsızdır',()=>{
 const previous=process.env.TZ;
 try {for(const zone of ['UTC','America/Los_Angeles','Asia/Tokyo','Europe/Istanbul']){
  process.env.TZ=zone;
  for(const instant of ['2026-10-30T21:30:00Z','2026-10-30T23:59:00Z'])assert.equal(reportBusinessDate(new Date(instant)),'2026-10-31');
 }}finally{if(previous===undefined)delete process.env.TZ;else process.env.TZ=previous;}
});
