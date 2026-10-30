import { test } from "node:test";
import { readdirSync } from "node:fs";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import assert from "node:assert/strict";
import { PrismaClient } from "@prisma/client";
import { management } from "../src/lib/management";
import { financialSummary, chargeBalance } from "../src/lib/finance";
const url=process.env.TEST_DATABASE_URL;
if(!url||!["localhost","127.0.0.1"].includes(new URL(url).hostname)||new URL(url).pathname!=="/siteyonetim_test") throw new Error("Isolated DB required");
const db=new PrismaClient({datasourceUrl:url});
test.after(async()=>db.$disconnect());
async function fixture() {
 const user=await db.user.create({data:{name:"Sentetik Finans",email:`${crypto.randomUUID()}@example.invalid`,emailVerifiedAt:new Date()}});
 const api=management(db,async()=>({userId:user.id}));const org=await api.createOrganization("Finans Testi","COMPANY");
 const site=await api.createSite(org.id,"Test Apartmanı");const block=await api.createBlock(site.id,"A");const unit=await api.createUnit(site.id,block.id,"1");
 const charge=await api.createCharge(site.id,unit.id,"2026-10",10000,new Date());const payment=await api.collect(site.id,charge.id,4000,crypto.randomUUID());
 return {user,api,org,site,charge,payment};
}
test("1 — doğrulanmış organizasyon ADMIN zorunluluğu ve sahte kimlik",async()=>{
 const f=await fixture();
 await assert.rejects(management(db,async()=>null).reversePayment(f.site.id,f.payment.id,"ENTRY_ERROR",crypto.randomUUID()),/UNAUTHENTICATED/);
 await assert.rejects(management(db,async()=>({userId:"forged-admin"})).reversePayment(f.site.id,f.payment.id,"ENTRY_ERROR",crypto.randomUUID()),/FORBIDDEN/);
 await db.user.update({where:{id:f.user.id},data:{emailVerifiedAt:null}});
 await assert.rejects(f.api.reversePayment(f.site.id,f.payment.id,"ENTRY_ERROR",crypto.randomUUID()),/EMAIL_UNVERIFIED/);
 await db.user.update({where:{id:f.user.id},data:{emailVerifiedAt:new Date()}});
 for(const role of ["MANAGER","RESIDENT"] as const) {
  await db.organizationMembership.update({where:{organizationId_userId:{organizationId:f.org.id,userId:f.user.id}},data:{role}});
  await db.membership.upsert({where:{siteId_userId:{siteId:f.site.id,userId:f.user.id}},create:{siteId:f.site.id,userId:f.user.id,role:"ADMIN"},update:{}});
  await assert.rejects(f.api.reversePayment(f.site.id,f.payment.id,"ENTRY_ERROR",crypto.randomUUID()),/FORBIDDEN/);
 }
 const other=await fixture();await assert.rejects(other.api.reversePayment(f.site.id,f.payment.id,"ENTRY_ERROR",crypto.randomUUID()),/FORBIDDEN/);
 await assert.rejects(f.api.reversePayment(f.site.id,f.payment.id,"ENTRY_ERROR","invalid"));
});
test("2 — başka apartman referansı, tutar, enum ve UUID DB kısıtları",async()=>{
 const f=await fixture();const secondSite=await f.api.createSite(f.org.id,"İkinci Apartman");
 await assert.rejects(f.api.reversePayment(secondSite.id,f.payment.id,"ENTRY_ERROR",crypto.randomUUID()),/PAYMENT_NOT_FOUND/);
 const data={siteId:f.site.id,paymentId:f.payment.id,amountKurus:4000,reasonCode:"ENTRY_ERROR" as const,actorId:f.user.id,idempotencyKey:crypto.randomUUID()};
 await assert.rejects(db.paymentReversal.create({data:{...data,siteId:secondSite.id}}));
 await assert.rejects(db.paymentReversal.create({data:{...data,amountKurus:3999}}));
 await assert.rejects(db.paymentReversal.create({data:{...data,amountKurus:0}}));
 await assert.rejects(db.paymentReversal.create({data:{...data,idempotencyKey:"bad"}}));
 await assert.rejects(db.$executeRaw`INSERT INTO "PaymentReversal" (id,"siteId","paymentId","amountKurus","reasonCode","actorId","idempotencyKey") VALUES ('invalid-enum',${f.site.id},${f.payment.id},4000,'INVALID',${f.user.id},${crypto.randomUUID()})`);
 const reversal=await f.api.reversePayment(f.site.id,f.payment.id,"ENTRY_ERROR",crypto.randomUUID());
 await assert.rejects(db.paymentReversal.create({data:{...data,idempotencyKey:crypto.randomUUID()}}));
 await assert.rejects(db.paymentReversal.update({where:{id:reversal.id},data:{reasonCode:"WRONG_AMOUNT"}}),/append only/);
 await assert.rejects(db.paymentReversal.delete({where:{id:reversal.id}}),/append only/);
});
test("3 — kısmi tahsilatın tam tersi, orijinal kayıt ve dashboard/daire bakiyesi",async()=>{
 const f=await fixture();const original=await db.payment.findUniqueOrThrow({where:{id:f.payment.id}});
 const reversal=await f.api.reversePayment(f.site.id,f.payment.id,"WRONG_AMOUNT",crypto.randomUUID());
 assert.equal(reversal.amountKurus,4000);assert.equal(reversal.actorId,f.user.id);
 assert.deepEqual(await db.payment.findUniqueOrThrow({where:{id:f.payment.id}}),original);
 const site=await f.api.dashboard(f.site.id);assert.deepEqual(financialSummary(site.charges),{chargedKurus:10000,grossKurus:4000,reversedKurus:4000,netKurus:0,remainingKurus:10000});
 assert.equal(chargeBalance(site.charges[0]).remainingKurus,10000);
 await f.api.collect(f.site.id,f.charge.id,10000,crypto.randomUUID());
 assert.equal(financialSummary((await f.api.dashboard(f.site.id)).charges).remainingKurus,0);
 await assert.rejects(f.api.collect(f.site.id,f.charge.id,1,crypto.randomUUID()),/OVERPAYMENT/);
});
test("4 — seri/paralel idempotent tekrar, içerik çatışması, tek audit",async()=>{
 const f=await fixture();const key=crypto.randomUUID();
 const [a,b]=await Promise.all([f.api.reversePayment(f.site.id,f.payment.id,"ENTRY_ERROR",key),f.api.reversePayment(f.site.id,f.payment.id,"ENTRY_ERROR",key)]);
 assert.equal(a.id,b.id);assert.equal((await f.api.reversePayment(f.site.id,f.payment.id,"ENTRY_ERROR",key)).id,a.id);
 await assert.rejects(f.api.reversePayment(f.site.id,f.payment.id,"WRONG_AMOUNT",key),/IDEMPOTENCY_CONFLICT/);
 const next=await f.api.collect(f.site.id,f.charge.id,1000,crypto.randomUUID());
 await assert.rejects(f.api.reversePayment(f.site.id,next.id,"ENTRY_ERROR",key),/IDEMPOTENCY_CONFLICT/);
 const logs=await db.auditLog.findMany({where:{entityId:a.id,action:"PAYMENT_REVERSE"}});assert.equal(logs.length,1);assert.equal(logs[0].actorId,f.user.id);assert.equal(logs[0].organizationId,f.org.id);assert.equal(logs[0].siteId,f.site.id);
});
test("5 — farklı anahtarlarla paralel ters kayıtta tek başarı",async()=>{
 const f=await fixture();const results=await Promise.allSettled([f.api.reversePayment(f.site.id,f.payment.id,"ENTRY_ERROR",crypto.randomUUID()),f.api.reversePayment(f.site.id,f.payment.id,"ENTRY_ERROR",crypto.randomUUID())]);
 assert.equal(results.filter(r=>r.status==="fulfilled").length,1);assert.match(String((results.find(r=>r.status==="rejected") as PromiseRejectedResult).reason),/ALREADY_REVERSED/);
 assert.equal(await db.paymentReversal.count({where:{paymentId:f.payment.id}}),1);
});
test("6 — aynı borçta tahsilat/ters kayıt yarışı ve fazla ödeme reddi",async()=>{
 const f=await fixture();
 const results=await Promise.allSettled([f.api.collect(f.site.id,f.charge.id,10000,crypto.randomUUID()),f.api.reversePayment(f.site.id,f.payment.id,"ENTRY_ERROR",crypto.randomUUID())]);
 assert.equal(results[1].status,"fulfilled");
 if(results[0].status==="rejected") {assert.match(String(results[0].reason),/OVERPAYMENT/);await f.api.collect(f.site.id,f.charge.id,10000,crypto.randomUUID());}
 assert.equal(financialSummary((await f.api.dashboard(f.site.id)).charges).netKurus,10000);
 assert.equal(financialSummary((await f.api.dashboard(f.site.id)).charges).remainingKurus,0);
});
test("7 — audit arızasında reversal rollback ve immutable Payment/Audit",async()=>{
 const f=await fixture();const key=crypto.randomUUID();
 await db.$executeRawUnsafe(`CREATE FUNCTION test_reversal_audit_failure() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.action = 'PAYMENT_REVERSE' THEN RAISE EXCEPTION 'reversal audit failure'; END IF; RETURN NEW; END $$`);
 await db.$executeRawUnsafe(`CREATE TRIGGER test_reversal_failure BEFORE INSERT ON "AuditLog" FOR EACH ROW EXECUTE FUNCTION test_reversal_audit_failure()`);
 try {await assert.rejects(f.api.reversePayment(f.site.id,f.payment.id,"ENTRY_ERROR",key),/reversal audit failure/);assert.equal(await db.paymentReversal.count({where:{paymentId:f.payment.id}}),0);}
 finally {await db.$executeRawUnsafe(`DROP TRIGGER test_reversal_failure ON "AuditLog"`);await db.$executeRawUnsafe(`DROP FUNCTION test_reversal_audit_failure()`);}
 await f.api.reversePayment(f.site.id,f.payment.id,"ENTRY_ERROR",key);
 await assert.rejects(db.payment.update({where:{id:f.payment.id},data:{amountKurus:4000}}),/append only/);
 await assert.rejects(db.payment.delete({where:{id:f.payment.id}}),/append only/);
 await assert.rejects(db.auditLog.updateMany({where:{siteId:f.site.id},data:{action:"TAMPER"}}),/append only/);
 await assert.rejects(db.auditLog.deleteMany({where:{siteId:f.site.id}}),/append only/);
});
test("8 — ayrı LOGIN runtime/migration rolleriyle gerçek izin kısıtları",async()=>{
 const f=await fixture();const suffix=crypto.randomUUID().replaceAll("-","");const runtime=`sy_runtime_${suffix}`;const migration=`sy_migration_${suffix}`;const secret=crypto.randomUUID().replaceAll("-","");
 // Identifiers and password consist solely of generated ASCII identifiers/hex; no external interpolation.
 await db.$executeRawUnsafe(`CREATE ROLE "${runtime}" LOGIN PASSWORD '${secret}' NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION`);
 await db.$executeRawUnsafe(`CREATE ROLE "${migration}" LOGIN PASSWORD '${secret}' NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION`);
 const connect=(role:string)=>{const u=new URL(url!);u.username=role;u.password=secret;return new PrismaClient({datasourceUrl:u.toString()});};
 const app=connect(runtime);const ddl=connect(migration);
 const migrationSchema=`sy_schema_${suffix}`;
 try {
  await db.$executeRawUnsafe(`GRANT USAGE ON SCHEMA public TO "${runtime}"`);
  await db.$executeRawUnsafe(`GRANT USAGE, CREATE ON SCHEMA public TO "${migration}"`);
  await db.$executeRawUnsafe(`GRANT CREATE ON DATABASE siteyonetim_test TO "${migration}"`);
  await db.$executeRawUnsafe(`GRANT SELECT ON "User","Organization","OrganizationMembership","Site","Membership","Charge","Payment","PaymentReversal" TO "${runtime}"`);
  await db.$executeRawUnsafe(`GRANT INSERT ON "Payment","PaymentReversal","AuditLog" TO "${runtime}"`);
  await db.$executeRawUnsafe(`GRANT SELECT (id) ON "AuditLog" TO "${runtime}"`);
  // PostgreSQL row locks require UPDATE privilege: only id is granted; immutable triggers still reject writes.
  await db.$executeRawUnsafe(`GRANT UPDATE (id) ON "User","Organization","Charge","Payment" TO "${runtime}"`);
  await db.$executeRawUnsafe(`CREATE SCHEMA "${migrationSchema}" AUTHORIZATION "${migration}"`);
  const migrationUrl=new URL(url!);migrationUrl.username=migration;migrationUrl.password=secret;migrationUrl.searchParams.set("schema",migrationSchema);
  await promisify(execFile)(process.execPath,["node_modules/prisma/build/index.js","migrate","deploy"],{env:{...process.env,DATABASE_URL:migrationUrl.toString()},timeout:30000});
  const isolatedMigration=new PrismaClient({datasourceUrl:migrationUrl.toString()});
  try { const applied=await isolatedMigration.$queryRawUnsafe<{count:bigint}[]>(`SELECT count(*) FROM "${migrationSchema}"."_prisma_migrations" WHERE finished_at IS NOT NULL`);assert.equal(Number(applied[0].count),readdirSync("prisma/migrations",{withFileTypes:true}).filter(e=>e.isDirectory()).length); }
  finally {await isolatedMigration.$disconnect();}
  await ddl.$executeRawUnsafe(`CREATE TABLE "role_probe_${suffix}" (id INTEGER)`);
  await ddl.$executeRawUnsafe(`DROP TABLE "role_probe_${suffix}"`);
  await assert.rejects(app.$executeRawUnsafe(`CREATE TABLE "runtime_probe_${suffix}" (id INTEGER)`));
  const api=management(app,async()=>({userId:f.user.id}));
  const payment=await api.collect(f.site.id,f.charge.id,1000,crypto.randomUUID());
  await api.reversePayment(f.site.id,payment.id,"ENTRY_ERROR",crypto.randomUUID());
  await assert.rejects(app.payment.update({where:{id:payment.id},data:{amountKurus:1000}}));
  await assert.rejects(app.payment.update({where:{id:payment.id},data:{id:payment.id}}),/append only/);
  await assert.rejects(app.payment.delete({where:{id:payment.id}}));
  await assert.rejects(app.paymentReversal.updateMany({data:{reasonCode:"WRONG_AMOUNT"}}));
  await assert.rejects(app.paymentReversal.deleteMany());
  await assert.rejects(app.auditLog.updateMany({data:{action:"TAMPER"}}));await assert.rejects(app.auditLog.deleteMany());
  for(const table of ["Payment","PaymentReversal","AuditLog"]) await assert.rejects(app.$executeRawUnsafe(`TRUNCATE "${table}"`));
  const roles=await db.$queryRaw<{rolsuper:boolean;rolcreaterole:boolean}[]>`SELECT rolsuper,rolcreaterole FROM pg_roles WHERE rolname=${runtime}`;assert.equal(roles[0].rolsuper,false);assert.equal(roles[0].rolcreaterole,false);
 } finally {
  await app.$disconnect();await ddl.$disconnect();
  await db.$executeRawUnsafe(`DROP SCHEMA IF EXISTS "${migrationSchema}" CASCADE`);
  await db.$executeRawUnsafe(`DROP OWNED BY "${runtime}"`);await db.$executeRawUnsafe(`DROP OWNED BY "${migration}"`);
  await db.$executeRawUnsafe(`DROP ROLE "${runtime}"`);await db.$executeRawUnsafe(`DROP ROLE "${migration}"`);
 }
});
