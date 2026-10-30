import { test } from 'node:test';
import assert from 'node:assert/strict';
import { csvText,csvMoney,csvLine,EXPORT_BATCH_SIZE,EXPORT_MAX_ROWS } from './csv';
import { formatMoney } from './finance';
import { shiftMonth } from './report-queries';
test('CSV metni: formül, boşluk, kontrol, BOM/zero-width kaçınmaları',()=>{for(const prefix of ['',' ','\t','\r\n','\u0000\u000b','\u200b','\ufeff',' \t\n'])for(const formula of ['=1+1','+SUM(A1)','-1','@A1'])assert.ok(csvText(prefix+formula).startsWith('"\''));assert.equal(csvText('Türkçe; "özel"\nmetin'),'"Türkçe; ""özel""\nmetin"');});
test('sunucu sayısı negatif işareti korunur, kuruş yuvarlanmaz',()=>{assert.equal(csvMoney(-123456),'-1234,56');assert.equal(csvMoney(0),'0,00');assert.equal(csvMoney(Number.MAX_SAFE_INTEGER),'90071992547409,91');assert.throws(()=>csvMoney(Number.MAX_SAFE_INTEGER+1));assert.throws(()=>csvMoney(1.5));assert.equal(csvLine([{text:'-1'},{money:-100}]),'"\'-1";-1,00\r\n');assert.equal(EXPORT_BATCH_SIZE,1000);assert.equal(EXPORT_MAX_ROWS,50000);});
test('takvim ayı kaydırma yıl ve aralık sınırlarında sabittir',()=>{assert.equal(shiftMonth('2026-01',-1),'2025-12');assert.equal(shiftMonth('2026-12',1),'2027-01');assert.equal(shiftMonth('2026-01',-12),'2025-01');});

test('ekran ve CSV güvenli sayı sınırında aynı kuruşu korur',()=>{
 assert.equal(formatMoney(Number.MAX_SAFE_INTEGER),'₺90.071.992.547.409,91');
 assert.equal(formatMoney(-Number.MAX_SAFE_INTEGER),'-₺90.071.992.547.409,91');
 assert.equal(formatMoney(-1),'-₺0,01');assert.equal(formatMoney(1),'₺0,01');assert.equal(formatMoney(0),'₺0,00');
 assert.throws(()=>formatMoney(Number.MAX_SAFE_INTEGER+1));
});
