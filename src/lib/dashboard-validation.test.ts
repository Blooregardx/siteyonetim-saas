import { test } from 'node:test';
import assert from 'node:assert/strict';
import { dashboardPage,unitFilters,chargeFilters,validateDashboardParams } from './dashboard-validation';
import { pageUrl } from '../components/dashboard-navigation';
test('dashboard filters reject malformed pages, dates and enums; retain zero floor',()=>{
 for(const page of [0,-1,1.5,1000001,'bad'])assert.throws(()=>dashboardPage.parse(page));
 assert.equal(unitFilters.parse({floor:'0'}).floor,0);assert.equal(unitFilters.parse({floor:''}).floor,undefined);
 assert.throws(()=>unitFilters.parse({type:'INVALID'}));assert.throws(()=>unitFilters.parse({status:'INVALID'}));assert.throws(()=>unitFilters.parse({floor:'x'}));assert.throws(()=>unitFilters.parse({q:'x'.repeat(101)}));
 assert.throws(()=>chargeFilters.parse({period:'2026-13'}));assert.throws(()=>chargeFilters.parse({status:'PAID OR true'}));assert.throws(()=>chargeFilters.parse({debt:'false'}));
 assert.equal(chargeFilters.parse({}).page,1);assert.throws(()=>unitFilters.parse({cursor:'foreign'}));assert.throws(()=>validateDashboardParams({site:['a','b']},['site']));assert.throws(()=>validateDashboardParams({cursor:'x'},['site']));
});
test('paging URLs retain scope and filters and encode user text',()=>{const u=new URL(pageUrl('/panel',{org:'org',site:'site',q:'A & B',period:'2026-01'},{unitsPage:'2'}),'http://localhost');assert.equal(u.searchParams.get('q'),'A & B');assert.equal(u.searchParams.get('site'),'site');assert.equal(u.searchParams.get('period'),'2026-01');assert.equal(u.searchParams.get('unitsPage'),'2');});
