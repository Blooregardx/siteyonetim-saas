import { test } from "node:test";
import assert from "node:assert/strict";
import { PrismaClient } from "@prisma/client";
import { management } from "../src/lib/management";
const url=process.env.TEST_DATABASE_URL;
if(!url||!["localhost","127.0.0.1"].includes(new URL(url).hostname)||new URL(url).pathname!=="/siteyonetim_test")throw new Error("Isolated DB required");
const db=new PrismaClient({datasourceUrl:url});test.after(()=>db.$disconnect());
async function fixture(){const user=await db.user.create({data:{email:`${crypto.randomUUID()}@example.invalid`,name:"S02 Test",emailVerifiedAt:new Date()}});const api=management(db,async()=>({userId:user.id}));const org=await api.createOrganization("S02 Test","COMPANY");const site=await api.createSite(org.id,"Apartman");const block=await api.createBlock(site.id,"A");const unit=await api.createUnit(site.id,block.id,"1");return {user,api,org,site,block,unit};}
const unitData={number:"12",floor:3,sectionType:"COMMERCIAL",usageStatus:"VACANT"};
test("apartman/blok/daire güncelleme, tenant izolasyonu, finans korunumu ve audit",async()=>{
 const f=await fixture();const other=await fixture();const charge=await f.api.createCharge(f.site.id,f.unit.id,"2026-10",10000,new Date());const payment=await f.api.collect(f.site.id,charge.id,4000,crypto.randomUUID());const reversal=await f.api.reversePayment(f.site.id,payment.id,"ENTRY_ERROR",crypto.randomUUID());
 const before=await db.payment.findUnique({where:{id:payment.id}});const auditBefore=await db.auditLog.findMany({where:{siteId:f.site.id},orderBy:{id:"asc"}});
 await f.api.updateSite(f.site.id,{name:"Yeni Apartman",address:"Sentetik adres",description:"Açıklama"});await f.api.updateBlock(f.site.id,f.block.id,{name:"Yeni A",description:"Blok açıklaması"});await f.api.updateUnit(f.site.id,f.unit.id,unitData);
 assert.equal((await db.unit.findUniqueOrThrow({where:{id:f.unit.id}})).blockId,f.block.id);
 await assert.rejects(other.api.updateUnit(f.site.id,f.unit.id,unitData),/FORBIDDEN/);
 await assert.rejects(other.api.updateUnit(other.site.id,f.unit.id,unitData));
 await assert.rejects(f.api.updateBlock(f.site.id,other.block.id,{name:"Saldırı",description:""}));
 await assert.rejects(f.api.updateUnit(f.site.id,f.unit.id,{...unitData,floor:201}));
 const unit2=await f.api.createUnit(f.site.id,f.block.id,"13");await assert.rejects(f.api.updateUnit(f.site.id,unit2.id,unitData));
 assert.deepEqual(await db.payment.findUnique({where:{id:payment.id}}),before);assert.deepEqual(await db.paymentReversal.findUnique({where:{id:reversal.id}}),reversal);assert.deepEqual(await db.charge.findUnique({where:{id:charge.id}}),charge);
 const logs=await db.auditLog.findMany({where:{siteId:f.site.id},orderBy:{id:"asc"}});assert.ok(auditBefore.every(old=>logs.some(l=>l.id===old.id&&l.action===old.action)));
 for(const action of ["SITE_UPDATE","BLOCK_UPDATE","UNIT_UPDATE"])assert.ok(logs.some(l=>l.action===action&&l.actorId===f.user.id));
});
test("kişi çoklu daire, çoklu malik, çıkış/yeni giriş ve eski Occupancy korunumu",async()=>{
 const f=await fixture();const other=await fixture();const second=await f.api.createUnit(f.site.id,f.block.id,"2");const person=await f.api.createPerson(f.site.id,"Aynı İsim");const separate=await f.api.createPerson(f.site.id,"Aynı İsim");assert.notEqual(person.id,separate.id);
 await f.api.linkPerson(f.site.id,f.unit.id,person.id,"OWNER","2026-01-01");await f.api.linkPerson(f.site.id,second.id,person.id,"OWNER","2026-01-01");await f.api.linkPerson(f.site.id,f.unit.id,separate.id,"OWNER","2026-01-01");
 const directUser=await db.user.create({data:{email:`${crypto.randomUUID()}@example.invalid`,name:"Apartman görevlisi",emailVerifiedAt:new Date()}});
 await db.membership.create({data:{siteId:f.site.id,userId:directUser.id,role:"MANAGER"}});
 const direct=management(db,async()=>({userId:directUser.id}));assert.equal((await direct.propertyDetails(f.site.id)).persons.length,0);
 await assert.rejects(direct.createPerson(f.site.id,"Organizasyon rehberi"),/FORBIDDEN/);
 await assert.rejects(direct.linkPerson(f.site.id,f.unit.id,person.id,"TENANT","2026-01-01"),/FORBIDDEN/);
 const tenancy=await f.api.linkPerson(f.site.id,f.unit.id,person.id,"TENANT","2026-01-01");await assert.rejects(f.api.linkPerson(f.site.id,f.unit.id,person.id,"TENANT","2026-02-01"),/OVERLAPPING_RELATION/);
 await assert.rejects(f.api.endRelation(f.site.id,tenancy.id,"TENANT","2025-12-31"));await f.api.endRelation(f.site.id,tenancy.id,"TENANT","2026-03-31");await assert.rejects(f.api.endRelation(f.site.id,tenancy.id,"TENANT","2026-04-01"));
 const next=await f.api.linkPerson(f.site.id,f.unit.id,person.id,"TENANT","2026-04-01");assert.notEqual(next.id,tenancy.id);assert.equal(await db.occupancy.count({where:{personId:person.id}}),2);
 await assert.rejects(other.api.endRelation(f.site.id,next.id,"TENANT","2026-05-01"),/FORBIDDEN/);await assert.rejects(other.api.linkPerson(other.site.id,other.unit.id,person.id,"OWNER","2026-01-01"));
 await assert.rejects(db.ownership.create({data:{organizationId:other.org.id,siteId:other.site.id,unitId:other.unit.id,personId:person.id,startedAt:new Date()}}));
 const legacy=await db.occupancy.create({data:{siteId:f.site.id,unitId:f.unit.id,name:"Eski kayıt",kind:"TENANT",startedAt:new Date("2025-01-01")}});await f.api.endRelation(f.site.id,legacy.id,"TENANT","2025-12-31");assert.equal((await db.occupancy.findUniqueOrThrow({where:{id:legacy.id}})).personId,null);
 await db.organizationMembership.update({where:{organizationId_userId:{organizationId:f.org.id,userId:f.user.id}},data:{role:"RESIDENT"}});await assert.rejects(f.api.endRelation(f.site.id,next.id,"TENANT","2026-05-01"),/FORBIDDEN/);await assert.rejects(f.api.linkPerson(f.site.id,second.id,person.id,"OWNER","2026-01-01"),/FORBIDDEN/);
});
test("güncelleme audit arızasında rollback",async()=>{
 const f=await fixture();await db.$executeRawUnsafe(`CREATE FUNCTION test_property_audit() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.action = 'UNIT_UPDATE' THEN RAISE EXCEPTION 'property audit failure'; END IF; RETURN NEW; END $$`);await db.$executeRawUnsafe(`CREATE TRIGGER test_property_failure BEFORE INSERT ON "AuditLog" FOR EACH ROW EXECUTE FUNCTION test_property_audit()`);
 try{await assert.rejects(f.api.updateUnit(f.site.id,f.unit.id,unitData),/property audit failure/);assert.deepEqual(await db.unit.findUnique({where:{id:f.unit.id}}),f.unit);}finally{await db.$executeRawUnsafe(`DROP TRIGGER test_property_failure ON "AuditLog"`);await db.$executeRawUnsafe(`DROP FUNCTION test_property_audit()`);}
});
