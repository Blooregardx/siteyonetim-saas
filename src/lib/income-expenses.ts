import { financialReporting } from "./financial-reporting";
import { Prisma, PrismaClient } from '@prisma/client';
import { z } from 'zod';
import type { SessionVerifier } from './management';
import { actor,audit,organizationAccess } from './security';
import { fingerprint } from './bulk-charges';
import { categoryInput,categoryKey,defaultCategories,entryInput,movementInput } from './income-expense-validation';
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
  // Preserve the existing direct service API while sharing the reporting implementation.
  async movementReport(raw:z.input<typeof movementInput>){return financialReporting(db,verify).movementReport(raw);},
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
 };
}
