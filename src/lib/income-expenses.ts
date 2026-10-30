import { Prisma, PrismaClient } from '@prisma/client';
import { z } from 'zod';
import type { SessionVerifier } from './management';
import { actor,audit,organizationAccess } from './security';
import { fingerprint } from './bulk-charges';
import { categoryInput,categoryKey,defaultCategories,entryInput,movementInput,movementSummary,signedKurus } from './income-expense-validation';
export function incomeExpenses(db:PrismaClient,verify:SessionVerifier){
 async function scope(tx:Prisma.TransactionClient,siteId:string,admin=false){
  const user=await actor(tx,verify);const site=await tx.site.findUnique({where:{id:siteId}});
  if(!site?.organizationId)throw new Error('FORBIDDEN');
  await organizationAccess(tx,user.id,site.organizationId,admin);
  await tx.$queryRaw`SELECT id FROM "Site" WHERE id=${siteId} FOR UPDATE`;
  return {actorId:user.id,organizationId:site.organizationId,siteId};
 }
 async function addCategory(tx:Prisma.TransactionClient,s:Awaited<ReturnType<typeof scope>>,raw:z.input<typeof categoryInput>,defaults=false){
  const input=categoryInput.parse(raw);const nameKey=categoryKey(input.name);
  const previous=await tx.financialCategory.findUnique({where:{siteId_type_nameKey:{siteId:s.siteId,type:input.type,nameKey}}});
  if(previous){if(defaults)return previous;throw new Error('CATEGORY_EXISTS');}
  const category=await tx.financialCategory.create({data:{organizationId:s.organizationId,siteId:s.siteId,...input,nameKey}});
  await audit(tx,s.actorId,'FINANCIAL_CATEGORY_CREATE',category.id,s.organizationId,s.siteId);return category;
 }
 return {
  async categories(siteId:string){return db.$transaction(async tx=>{await scope(tx,siteId);return tx.financialCategory.findMany({where:{siteId},orderBy:[{type:'asc'},{name:'asc'}]});});},
  async createCategory(siteId:string,input:z.input<typeof categoryInput>){return db.$transaction(async tx=>addCategory(tx,await scope(tx,siteId),input));},
  async defaultCategories(siteId:string){return db.$transaction(async tx=>{const s=await scope(tx,siteId);for(const type of ['INCOME','EXPENSE'] as const)for(const name of defaultCategories[type])await addCategory(tx,s,{type,name},true);});},
  async deactivateCategory(siteId:string,id:string){return db.$transaction(async tx=>{const s=await scope(tx,siteId);const c=await tx.financialCategory.findFirstOrThrow({where:{id,siteId,organizationId:s.organizationId}});if(!c.active)return c;const result=await tx.financialCategory.update({where:{id},data:{active:false}});await audit(tx,s.actorId,'FINANCIAL_CATEGORY_DEACTIVATE',id,s.organizationId,siteId);return result;});},
  async createEntry(siteId:string,raw:z.input<typeof entryInput>){
   const input=entryInput.parse(raw);const requestHash=fingerprint(input);
   return db.$transaction(async tx=>{const s=await scope(tx,siteId);
    const previous=await tx.financialEntry.findUnique({where:{siteId_idempotencyKey:{siteId,idempotencyKey:input.idempotencyKey}}});
    if(previous){if(previous.requestHash!==requestHash)throw new Error('IDEMPOTENCY_CONFLICT');return previous;}
    const category=await tx.financialCategory.findFirst({where:{id:input.categoryId,organizationId:s.organizationId,siteId,type:input.type,active:true}});if(!category)throw new Error('INVALID_CATEGORY');
    const entry=await tx.financialEntry.create({data:{...input,...s,businessDate:new Date(input.businessDate+'T00:00:00Z'),requestHash}});
    await audit(tx,s.actorId,'FINANCIAL_ENTRY_CREATE',entry.id,s.organizationId,siteId);return entry;
   });
  },
  async reverseEntry(siteId:string,entryId:string,reason:string,idempotencyKey:string){
   reason=z.string().trim().min(3).max(1000).parse(reason);z.string().uuid().parse(idempotencyKey);
   return db.$transaction(async tx=>{const s=await scope(tx,siteId,true);
    await tx.$queryRaw`SELECT id FROM "FinancialEntry" WHERE id=${entryId} AND "siteId"=${siteId} FOR UPDATE`;
    const entry=await tx.financialEntry.findFirstOrThrow({where:{id:entryId,siteId,organizationId:s.organizationId}});
    const previous=await tx.financialEntryReversal.findUnique({where:{siteId_idempotencyKey:{siteId,idempotencyKey}}});
    if(previous){if(previous.entryId!==entryId||previous.reason!==reason)throw new Error('IDEMPOTENCY_CONFLICT');return previous;}
    if(await tx.financialEntryReversal.findUnique({where:{entryId}}))throw new Error('ALREADY_REVERSED');
    const reversal=await tx.financialEntryReversal.create({data:{...s,entryId,amountKurus:entry.amountKurus,reason,idempotencyKey}});
    await audit(tx,s.actorId,'FINANCIAL_ENTRY_REVERSE',reversal.id,s.organizationId,siteId);return reversal;
   });
  },
  async movementReport(raw:z.input<typeof movementInput>){
   const input=movementInput.parse(raw);
   return db.$transaction(async tx=>{
    const user=await actor(tx,verify);await organizationAccess(tx,user.id,input.organizationId);
    if(input.siteId&&!await tx.site.findFirst({where:{id:input.siteId,organizationId:input.organizationId}}))throw new Error('FORBIDDEN');
    if(input.categoryId&&!await tx.financialCategory.findFirst({where:{id:input.categoryId,organizationId:input.organizationId,...(input.siteId?{siteId:input.siteId}:{})}}))throw new Error('FORBIDDEN');
    const day=Prisma.sql`(p."paidAt" AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Istanbul')::date`;
    const base=Prisma.sql`WITH events AS (
     SELECT 'P:'||p.id AS id,p.id AS "sourceId",p."siteId",s.name AS site,'DUES' AS type,NULL::text AS "categoryId",'Aidat tahsilatı' AS category,'Aidat tahsilatı' AS description,${day} AS day,p."amountKurus"::bigint AS amount,p.method,false AS reversal,(r.id IS NOT NULL) AS reversed,NULL::text AS reason
     FROM "Payment" p JOIN "Site" s ON s.id=p."siteId" LEFT JOIN "PaymentReversal" r ON r."paymentId"=p.id WHERE s."organizationId"=${input.organizationId}
     UNION ALL
     SELECT 'PR:'||r.id,p.id,p."siteId",s.name,'DUES',NULL::text,'Aidat tahsilatı','Aidat tahsilatı ters kaydı',(r."createdAt" AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Istanbul')::date,-r."amountKurus"::bigint,p.method,true,true,r."reasonCode"::text
     FROM "PaymentReversal" r JOIN "Payment" p ON p.id=r."paymentId" AND p."siteId"=r."siteId" JOIN "Site" s ON s.id=p."siteId" WHERE s."organizationId"=${input.organizationId}
     UNION ALL
     SELECT 'E:'||e.id,e.id,e."siteId",s.name,e.type::text,c.id,c.name,e.description,e."businessDate",e."amountKurus"::bigint,e.method,false,(r.id IS NOT NULL),NULL::text
     FROM "FinancialEntry" e JOIN "Site" s ON s.id=e."siteId" JOIN "FinancialCategory" c ON c.id=e."categoryId" LEFT JOIN "FinancialEntryReversal" r ON r."entryId"=e.id WHERE e."organizationId"=${input.organizationId}
     UNION ALL
     SELECT 'ER:'||r.id,e.id,e."siteId",s.name,e.type::text,c.id,c.name,e.description,(r."createdAt" AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Istanbul')::date,-r."amountKurus"::bigint,e.method,true,true,r.reason
     FROM "FinancialEntryReversal" r JOIN "FinancialEntry" e ON e.id=r."entryId" JOIN "Site" s ON s.id=e."siteId" JOIN "FinancialCategory" c ON c.id=e."categoryId" WHERE e."organizationId"=${input.organizationId}
    ), filtered AS (SELECT * FROM events WHERE day>=${input.month+'-01'}::date AND day<(${input.month+'-01'}::date+interval '1 month')
     ${input.siteId?Prisma.sql`AND "siteId"=${input.siteId}`:Prisma.empty}
     ${input.type!=='ALL'?Prisma.sql`AND type=${input.type}`:Prisma.empty}
     ${input.categoryId?Prisma.sql`AND "categoryId"=${input.categoryId}`:Prisma.empty}
     ${input.method!=='ALL'?Prisma.sql`AND method=${input.method}`:Prisma.empty})`;
    const totals=await tx.$queryRaw<{dues:bigint;income:bigint;expense:bigint;count:bigint;incomeCount:bigint;expenseCount:bigint}[]>(Prisma.sql`${base} SELECT coalesce(sum(amount) FILTER(WHERE type='DUES'),0)::bigint AS dues,coalesce(sum(amount) FILTER(WHERE type='INCOME'),0)::bigint AS income,coalesce(sum(amount) FILTER(WHERE type='EXPENSE'),0)::bigint AS expense,count(*)::bigint AS count,count(*) FILTER(WHERE type='INCOME' AND NOT reversal)::bigint AS "incomeCount",count(*) FILTER(WHERE type='EXPENSE' AND NOT reversal)::bigint AS "expenseCount" FROM filtered`);
    const rows=await tx.$queryRaw<{id:string;sourceId:string;siteId:string;site:string;type:string;category:string;description:string;day:Date;amount:bigint;method:string;reversal:boolean;reversed:boolean;reason:string|null}[]>(Prisma.sql`${base} SELECT * FROM filtered ORDER BY day DESC,id LIMIT 25 OFFSET ${(input.page-1)*25}`);
    const t=totals[0];return {rows:rows.map(r=>({...r,day:r.day.toISOString().slice(0,10),amount:signedKurus(r.amount)})),summary:{...movementSummary(t.dues,t.income,t.expense),incomeCount:signedKurus(t.incomeCount),expenseCount:signedKurus(t.expenseCount)},totalCount:signedKurus(t.count),page:input.page};
   },{timeout:15000});
  },
 };
}
