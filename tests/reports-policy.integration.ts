import { test } from 'node:test';
import assert from 'node:assert/strict';
import { PrismaClient } from '@prisma/client';
import { management } from '../src/lib/management';
const url=process.env.TEST_DATABASE_URL;
if(!url||!['localhost','127.0.0.1'].includes(new URL(url).hostname)||new URL(url).pathname!='/siteyonetim_test')throw new Error('Dedicated local TEST_DATABASE_URL required');
const db=new PrismaClient({datasourceUrl:url});
test('S03-B politika yetkileri, audit, bakiye, yarışlar, rapor filtreleri ve rollback',async()=>{
 try {
 const user=await db.user.create({data:{name:'Sentetik',email:crypto.randomUUID()+'@example.invalid',emailVerifiedAt:new Date()}});const api=management(db,async()=>({userId:user.id}));const org=await api.createOrganization('Rapor test','COMPANY');const site=await api.createSite(org.id,'Rapor apartmanı');assert.equal(site.partialPaymentsAllowed,true);
 const block=await api.createBlock(site.id,'A');const unit=await api.createUnit(site.id,block.id,'1');await api.createUnit(site.id,block.id,'Aidatsız');
 const charge=await api.createCharge(site.id,unit.id,'2026-01',200000,new Date('2026-01-01'));const receipt=await api.collect(site.id,charge.id,75000,'first');
 await api.setPartialPaymentsAllowed(site.id,false);const policy=await db.paymentPolicyChange.findFirstOrThrow({where:{siteId:site.id}});assert.equal(policy.oldValue,true);assert.equal(policy.newValue,false);assert.equal(policy.actorId,user.id);assert.equal(await db.auditLog.count({where:{entityId:policy.id,action:'PAYMENT_POLICY_CHANGE'}}),1);
 assert.deepEqual(await api.collect(site.id,charge.id,75000,'first'),receipt);await assert.rejects(api.collect(site.id,charge.id,74000,'first'),/IDEMPOTENCY_CONFLICT/);
 await assert.rejects(api.collect(site.id,charge.id,50000,'short'),/PARTIAL_PAYMENTS_DISABLED/);await assert.rejects(api.collect(site.id,charge.id,200000,'over'),/OVERPAYMENT/);
 const results=await Promise.allSettled([api.collect(site.id,charge.id,125000,'full1'),api.collect(site.id,charge.id,125000,'full2')]);assert.equal(results.filter(r=>r.status==='fulfilled').length,1);
 const reversal=await api.reversePayment(site.id,receipt.id,'ENTRY_ERROR',crypto.randomUUID());let report=await api.debtReport({organizationId:org.id});assert.equal(report.summary.netKurus,125000);assert.equal(report.summary.remainingKurus,75000);assert.equal(report.rows[0].status,'PARTIAL');assert.equal(report.rows[0].overdue,true);
 const outsider=await db.user.create({data:{name:'Other',email:crypto.randomUUID()+'@example.invalid',emailVerifiedAt:new Date()}});await assert.rejects(management(db,async()=>({userId:outsider.id})).debtReport({organizationId:org.id}),/FORBIDDEN/);
 const otherOrg=await api.createOrganization('Diğer','COMPANY');const other=await api.createSite(otherOrg.id,'Diğer');await assert.rejects(api.debtReport({organizationId:org.id,siteId:other.id}),/FORBIDDEN/);await assert.rejects(api.debtReport({organizationId:org.id,period:'2026-13'}));
 const memberWhere={organizationId_userId:{organizationId:org.id,userId:user.id}};
 for(const role of ['MANAGER','RESIDENT'] as const){await db.organizationMembership.update({where:memberWhere,data:{role}});await assert.rejects(api.setPartialPaymentsAllowed(site.id,true),/FORBIDDEN/);if(role==='RESIDENT'){await assert.rejects(api.debtReport({organizationId:org.id}),/FORBIDDEN/);await assert.rejects(api.collect(site.id,charge.id,75000,'resident'),/FORBIDDEN/);}}
 await db.organizationMembership.update({where:memberWhere,data:{role:'ADMIN'}});
 const legacy=await db.site.create({data:{name:'Legacy',memberships:{create:{userId:user.id,role:'ADMIN'}}}});await assert.rejects(api.setPartialPaymentsAllowed(legacy.id,false),/ORGANIZATION_REQUIRED/);
 // A fully reversed receipt restores all of a 2000 TL charge.
 const reversedCharge=await api.createCharge(site.id,unit.id,'2026-02',200000,new Date('2026-01-01'));await api.setPartialPaymentsAllowed(site.id,true);const rp=await api.collect(site.id,reversedCharge.id,75000,'reverse-me');await api.reversePayment(site.id,rp.id,'ENTRY_ERROR',crypto.randomUUID());report=await api.debtReport({organizationId:org.id,period:'2026-02'});assert.equal(report.summary.netKurus,0);assert.equal(report.summary.remainingKurus,200000);
 // Race has two legal serial outcomes: receipt succeeds before closure, or is rejected after it.
 const raceCharge=await api.createCharge(site.id,unit.id,'2026-03',10000,new Date('2026-01-01'));const race=await Promise.allSettled([api.setPartialPaymentsAllowed(site.id,false),api.collect(site.id,raceCharge.id,1000,'race')]);assert.equal(race[0].status,'fulfilled');if(race[1].status==='rejected')assert.match(String(race[1].reason),/PARTIAL_PAYMENTS_DISABLED/);assert.equal((await db.site.findUniqueOrThrow({where:{id:site.id}})).partialPaymentsAllowed,false);
 // 28 matching charges cross a page boundary. Same unit counts once; no-charge units never count.
 for(let i=1;i<=26;i++){const u=await api.createUnit(site.id,block.id,'P'+i);await api.createCharge(site.id,u.id,'2025-12',100,new Date('2025-12-01'));}
 const p1=await api.debtReport({organizationId:org.id,page:1});const p2=await api.debtReport({organizationId:org.id,page:2});assert.equal(p1.rows.length,25);assert.equal(p2.rows.length,4);assert.deepEqual(p1.summary,p2.summary);assert.equal(new Set([...p1.rows,...p2.rows].map(r=>r.id)).size,29);assert.equal(p1.summary.debtorUnits,27);
 const overdue=await api.debtReport({organizationId:org.id,overdueOnly:true});assert.equal(overdue.totalCount,29);const unpaid=await api.debtReport({organizationId:org.id,status:'UNPAID'});assert.ok(unpaid.rows.every(r=>r.status==='UNPAID'));
 // Audit failure must roll back policy history + setting, or receipt + audit.
 await db.$executeRawUnsafe(`CREATE FUNCTION s03b_fail() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW."siteId" = '${site.id}' AND NEW.action IN ('PAYMENT_POLICY_CHANGE','PAYMENT_COLLECT') THEN RAISE EXCEPTION 'synthetic failure'; END IF; RETURN NEW; END $$`);await db.$executeRawUnsafe('CREATE TRIGGER s03b_fail BEFORE INSERT ON "AuditLog" FOR EACH ROW EXECUTE FUNCTION s03b_fail()');
 const auditBefore=await db.auditLog.count({where:{siteId:site.id}}),historyBefore=await db.paymentPolicyChange.count({where:{siteId:site.id}}),paymentsBefore=await db.payment.count({where:{siteId:site.id}});
 try{await assert.rejects(api.setPartialPaymentsAllowed(site.id,true));assert.equal((await db.site.findUniqueOrThrow({where:{id:site.id}})).partialPaymentsAllowed,false);assert.equal(await db.paymentPolicyChange.count({where:{siteId:site.id}}),historyBefore);await assert.rejects(api.collect(site.id,charge.id,75000,'rollback'));assert.equal(await db.payment.count({where:{siteId:site.id}}),paymentsBefore);assert.equal(await db.auditLog.count({where:{siteId:site.id}}),auditBefore);}finally{await db.$executeRawUnsafe('DROP TRIGGER s03b_fail ON "AuditLog"');await db.$executeRawUnsafe('DROP FUNCTION s03b_fail()');}
 assert.deepEqual(await db.payment.findUniqueOrThrow({where:{id:receipt.id}}),receipt);assert.deepEqual(await db.paymentReversal.findUniqueOrThrow({where:{id:reversal.id}}),reversal);assert.deepEqual(await db.charge.findUniqueOrThrow({where:{id:charge.id}}),charge);await assert.rejects(db.paymentPolicyChange.update({where:{id:policy.id},data:{newValue:true}}),/append only/);
 await assert.rejects(api.collect(site.id,reversedCharge.id,75000,'stale-full','CASH',true),/BALANCE_CHANGED/);
 const fullReceipt=await api.collect(site.id,charge.id,75000,'finish','CASH',true);assert.deepEqual(await api.collect(site.id,charge.id,75000,'finish','CASH',true),fullReceipt);await assert.rejects(api.collect(site.id,charge.id,75000,'finish','CASH',false),/IDEMPOTENCY_CONFLICT/);const paid=await api.debtReport({organizationId:org.id,status:'PAID'});assert.equal(paid.totalCount,1);assert.equal(paid.rows[0].overdue,false);
 }finally{await db.$disconnect();}
});
