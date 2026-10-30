import { test } from 'node:test';
import assert from 'node:assert/strict';
import { bulkInput,bulkTotal } from './bulk-charges';
const valid={siteId:'site',unitIds:['b','a'],amountKurus:12345,period:'2026-11',dueDate:'2026-11-30'};
test('50 daire kuruş toplamı ve kanonik seçim',()=>{assert.equal(bulkTotal(12345,50),617250);assert.deepEqual(bulkInput.parse(valid).unitIds,['a','b']);});
test('boş, yinelenen seçim, dönem, tarih ve tutar reddi',()=>{for(const patch of [{unitIds:[]},{unitIds:['a','a']},{period:'2026-13'},{amountKurus:0},{amountKurus:1.5},{amountKurus:2147483648},{dueDate:'2026-02-30'}])assert.throws(()=>bulkInput.parse({...valid,...patch}));assert.throws(()=>bulkTotal(Number.MAX_SAFE_INTEGER,50));});
