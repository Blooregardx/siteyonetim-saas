import { test } from 'node:test';
import assert from 'node:assert/strict';
import { PrismaClient } from '@prisma/client';
import { management } from '../src/lib/management';
const url=process.env.TEST_DATABASE_URL;
if(!url||!['localhost','127.0.0.1'].includes(new URL(url).hostname)||new URL(url).pathname!='/siteyonetim_test')throw new Error('Dedicated local TEST_DATABASE_URL required');
const db=new PrismaClient({datasourceUrl:url});
test('toplu tahakkuk: izolasyon, 50 daire, önizleme, tekrar, çakışma, concurrency, rollback ve audit',async()=>{
 try {
 const user=await db.user.create({data:{name:'Sentetik',email:crypto.randomUUID()+'@example.invalid',emailVerifiedAt:new Date()}});
 const api=management(db,async()=>({userId:user.id}));const org=await api.createOrganization('Toplu test','COMPANY');const site=await api.createSite(org.id,'Test');const block=await api.createBlock(site.id,'A');
 const units=await Promise.all(Array.from({length:50},(_,i)=>api.createUnit(site.id,block.id,String(i+1))));
 const input={siteId:site.id,unitIds:units.map(u=>u.id),period:'2026-11',amountKurus:12345,dueDate:'2026-11-30'};
 const preview=await api.previewBulkCharges(input);assert.equal(preview.totalKurus,617250);assert.equal(await db.charge.count({where:{siteId:site.id}}),0);
 await assert.rejects(management(db,async()=>null).previewBulkCharges(input),/UNAUTHENTICATED/);
 const outsider=await db.site.create({data:{name:'Other'}});await assert.rejects(api.previewBulkCharges({...input,siteId:outsider.id}),/FORBIDDEN/);
 const foreign=await db.block.create({data:{siteId:outsider.id,name:'X'}});const foreignUnit=await db.unit.create({data:{siteId:outsider.id,blockId:foreign.id,number:'1'}});
 await assert.rejects(api.previewBulkCharges({...input,unitIds:[foreignUnit.id]}),/INVALID_UNITS/);
 await db.organizationMembership.update({where:{organizationId_userId:{organizationId:org.id,userId:user.id}},data:{role:'RESIDENT'}});
 await assert.rejects(api.commitBulkCharges(input,preview.snapshot,crypto.randomUUID()),/FORBIDDEN/);
 await db.organizationMembership.update({where:{organizationId_userId:{organizationId:org.id,userId:user.id}},data:{role:'MANAGER'}});
 const key=crypto.randomUUID();const repeated=await Promise.all([api.commitBulkCharges(input,preview.snapshot,key),api.commitBulkCharges(input,preview.snapshot,key)]);assert.deepEqual(repeated[0],repeated[1]);assert.equal(repeated[0].createdCount,50);
 await assert.rejects(api.commitBulkCharges({...input,amountKurus:1},preview.snapshot,key),/IDEMPOTENCY_CONFLICT/);
 await assert.rejects(api.commitBulkCharges(input,preview.snapshot,crypto.randomUUID()),/BULK_CONFLICT:A/);
 assert.equal(await db.charge.count({where:{siteId:site.id}}),50);assert.equal(await db.auditLog.count({where:{siteId:site.id,action:'CHARGE_CREATE'}}),50);
 const next={...input,period:'2026-12'};const p2=await api.previewBulkCharges(next);
 const concurrent=await Promise.allSettled([api.commitBulkCharges(next,p2.snapshot,crypto.randomUUID()),api.commitBulkCharges(next,p2.snapshot,crypto.randomUUID())]);assert.equal(concurrent.filter(r=>r.status==='fulfilled').length,1);
 const changed={...input,period:'2027-01'};const p3=await api.previewBulkCharges(changed);await api.updateUnit(site.id,units[0].id,{number:'99',floor:1,sectionType:'RESIDENTIAL',usageStatus:'VACANT'});
 await assert.rejects(api.commitBulkCharges(changed,p3.snapshot,crypto.randomUUID()),/STALE_PREVIEW/);
 const p4=await api.previewBulkCharges(changed);await api.createCharge(site.id,units[0].id,changed.period,1,new Date(changed.dueDate));await assert.rejects(api.commitBulkCharges(changed,p4.snapshot,crypto.randomUUID()),/BULK_CONFLICT/);
 // Fail the second audit insert, after a charge and its audit were already written.
 const rollback={...input,period:'2027-02'};const pr=await api.previewBulkCharges(rollback);
 await db.$executeRawUnsafe(`CREATE FUNCTION s03_fail_audit() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW."siteId" = '${site.id}' AND NEW.action = 'CHARGE_CREATE' AND (SELECT count(*) FROM "Charge" WHERE "siteId" = '${site.id}' AND period = '${rollback.period}') >= 2 THEN RAISE EXCEPTION 'synthetic audit failure'; END IF; RETURN NEW; END $$`);
 await db.$executeRawUnsafe('CREATE TRIGGER s03_fail BEFORE INSERT ON "AuditLog" FOR EACH ROW EXECUTE FUNCTION s03_fail_audit()');
 const before=await db.auditLog.count({where:{siteId:site.id}});const rollbackKey=crypto.randomUUID();
 try {await assert.rejects(api.commitBulkCharges(rollback,pr.snapshot,rollbackKey));assert.equal(await db.charge.count({where:{siteId:site.id,period:rollback.period}}),0);assert.equal(await db.auditLog.count({where:{siteId:site.id}}),before);assert.equal(await db.bulkChargeOperation.count({where:{siteId:site.id,idempotencyKey:rollbackKey}}),0);}finally{await db.$executeRawUnsafe('DROP TRIGGER s03_fail ON "AuditLog"');await db.$executeRawUnsafe('DROP FUNCTION s03_fail_audit()');}
 const charge=await db.charge.findFirstOrThrow({where:{siteId:site.id,period:input.period}});const payment=await api.collect(site.id,charge.id,100,'receipt');
 await db.organizationMembership.update({where:{organizationId_userId:{organizationId:org.id,userId:user.id}},data:{role:'ADMIN'}});const reversal=await api.reversePayment(site.id,payment.id,'ENTRY_ERROR',crypto.randomUUID());
 await api.commitBulkCharges(rollback,pr.snapshot,rollbackKey);
 assert.deepEqual(await db.payment.findUniqueOrThrow({where:{id:payment.id}}),payment);assert.deepEqual(await db.paymentReversal.findUniqueOrThrow({where:{id:reversal.id}}),reversal);
 }finally{await db.$disconnect();}
});
