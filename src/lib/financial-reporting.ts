import { Prisma,PrismaClient } from '@prisma/client';
import { z } from 'zod';
import type { SessionVerifier } from './management';
import { actor,organizationAccess } from './security';
import { reportInput,reportBusinessDate,reportBalance,reportTotals,safeInteger,paymentStatuses } from './reports';
import { movementInput,movementSummary,signedKurus } from './income-expense-validation';
import { debtBase,movementBase,movementTotals,shiftMonth,DebtRow,MovementRow } from './report-queries';
import { csvLine } from './csv';
import { cursorCsv,CsvArtifact } from './csv-artifact';
import { reversalReasons } from './reversals';
export const comparisonInput=movementInput.extend({months:z.union([z.literal(3),z.literal(6),z.literal(12)]).default(6)});
export const DEBT_HEADERS=['Apartman','Blok','Daire numarası','Aidat dönemi','Tahakkuk tutarı','Brüt tahsilat','Ters kayıt tutarı','Net tahsilat','Kalan borç','Son ödeme tarihi','Ödeme durumu','Vade durumu'];
export const MOVEMENT_HEADERS=['İşlem tarihi','Apartman','İşlem kaynağı/türü','Kategori','Açıklama','Tutar','Ödeme yöntemi','Ters kayıt durumu','Gerekçe'];
type MovementTotals={dues:bigint;income:bigint;expense:bigint;count:bigint;incomeCount:bigint;expenseCount:bigint};
type DebtTotals={count:bigint;summaryAmount:bigint;summaryGross:bigint;summaryReversed:bigint;debtors:bigint;paid:bigint;partial:bigint;overdue:bigint};
const date=(d:Date)=>d.toISOString().slice(0,10);
const movementRow=(r:MovementRow)=>({id:r.id,sourceId:r.sourceId,siteId:r.siteId,site:r.site,type:r.type,category:r.category,description:r.description,day:date(r.day),amount:signedKurus(r.amount),method:r.method,reversal:r.reversal,reversed:r.reversed,reason:r.reason});
const debtRow=(r:DebtRow,today:string)=>({id:r.id,siteId:r.siteId,site:r.site,unitId:r.unitId,period:r.period,amountKurus:r.amountKurus,dueDate:date(r.dueDate),block:r.block,number:r.number,...reportBalance(r.amountKurus,r.gross,r.reversed,date(r.dueDate),today)});
function debtCsv(row:DebtRow,today:string){const r=debtRow(row,today);return csvLine([{text:r.site},{text:r.block},{text:r.number},{text:r.period},...([r.amountKurus,r.grossKurus,r.reversedKurus,r.netKurus,r.remainingKurus].map(money=>({money}))),{text:r.dueDate},{text:paymentStatuses[r.status]},{text:r.overdue?'Vadesi geçmiş':r.remainingKurus===0?'Borç yok':'Vadesi geçmedi'}]);}
function movementCsv(row:MovementRow){return csvLine([{text:date(row.day)},{text:row.site},{text:row.type==='DUES'?'Aidat tahsilatı':row.type==='INCOME'?'Diğer gelir':'Gider'},{text:row.category},{text:row.description},{money:signedKurus(row.amount)},{text:row.method==='CASH'?'Nakit':'Havale/EFT'},{text:row.reversal?'Ters kayıt (karşı hareket)':row.reversed?'Ters kaydedilmiş orijinal':'Orijinal kayıt'},{text:row.reason?(row.type==='DUES'?(reversalReasons as Record<string,string>)[row.reason]??'Aidat düzeltmesi':row.reason):''}]);}
export function financialReporting(db:PrismaClient,verify:SessionVerifier){
 async function authorize(tx:Prisma.TransactionClient,input:{organizationId:string;siteId?:string;categoryId?:string}){
  const user=await actor(tx,verify);await organizationAccess(tx,user.id,input.organizationId);
  if(input.siteId&&!await tx.site.findFirst({where:{id:input.siteId,organizationId:input.organizationId}}))throw new Error('FORBIDDEN');
  if(input.categoryId&&!await tx.financialCategory.findFirst({where:{id:input.categoryId,organizationId:input.organizationId,...(input.siteId?{siteId:input.siteId}:{})}}))throw new Error('FORBIDDEN');
 }
 async function exportFile<T>(kind:'debt'|'movement',input:{organizationId:string;siteId?:string;categoryId?:string},query:Prisma.Sql,headers:string[],encode:(r:T)=>string,finish:()=>void=()=>{}){
  let artifact:CsvArtifact|undefined;
  try{await db.$transaction(async tx=>{await authorize(tx,input);artifact=await cursorCsv<T>(tx,kind,query,headers,encode,finish);},{timeout:180000,maxWait:10000});return artifact!;}catch(error){await artifact?.dispose();throw error;}
 }
 async function movement(tx:Prisma.TransactionClient,input:z.output<typeof movementInput>){const result=await tx.$queryRaw<(MovementRow&MovementTotals)[]>(Prisma.sql`${movementBase(input)}, totals AS (${movementTotals}) SELECT t.*,p.* FROM totals t LEFT JOIN LATERAL (SELECT * FROM filtered ORDER BY day DESC,id LIMIT 25 OFFSET ${(input.page-1)*25}) p ON true`);
   const t=result[0];return {rows:result.filter(r=>r.id!==null).map(movementRow),summary:{...movementSummary(t.dues,t.income,t.expense),incomeCount:signedKurus(t.incomeCount),expenseCount:signedKurus(t.expenseCount)},totalCount:signedKurus(t.count),page:input.page};
 }
 async function compare(tx:Prisma.TransactionClient,input:z.output<typeof comparisonInput>){const start=shiftMonth(input.month,-input.months);
   const grouped=await tx.$queryRaw<{month:string;dues:bigint;income:bigint;expense:bigint}[]>(Prisma.sql`${movementBase(input,start)}, monthly AS (SELECT to_char(day,'YYYY-MM') AS month,coalesce(sum(amount) FILTER(WHERE type='DUES'),0)::bigint AS dues,coalesce(sum(amount) FILTER(WHERE type='INCOME'),0)::bigint AS income,coalesce(sum(amount) FILTER(WHERE type='EXPENSE'),0)::bigint AS expense FROM filtered GROUP BY to_char(day,'YYYY-MM')) SELECT * FROM monthly`);
   const map=new Map(grouped.map(r=>[r.month,r]));const totals=(month:string)=>{const r=map.get(month);return movementSummary(r?.dues??0n,r?.income??0n,r?.expense??0n);};
   return Array.from({length:input.months},(_,i)=>{const month=shiftMonth(input.month,i-input.months+1);const sum=totals(month);return {month,...sum,changeKurus:signedKurus(BigInt(sum.netKurus)-BigInt(totals(shiftMonth(month,-1)).netKurus))};});
 }
 return {
  async debtReport(raw:z.input<typeof reportInput>){const input=reportInput.parse(raw);return db.$transaction(async tx=>{
   await authorize(tx,input);const today=reportBusinessDate();const base=debtBase(input,today);
   const result=await tx.$queryRaw<(DebtRow&DebtTotals)[]>(Prisma.sql`${base}, totals AS (SELECT count(*)::bigint AS count,coalesce(sum("amountKurus"),0)::bigint AS "summaryAmount",coalesce(sum(gross),0)::bigint AS "summaryGross",coalesce(sum(reversed),0)::bigint AS "summaryReversed",count(DISTINCT ("siteId","unitId")) FILTER(WHERE remaining>0)::bigint AS debtors,count(*) FILTER(WHERE remaining=0)::bigint AS paid,count(*) FILTER(WHERE remaining>0 AND gross>reversed)::bigint AS partial,coalesce(sum(remaining) FILTER(WHERE remaining>0 AND "dueDate"<${today}::date),0)::bigint AS overdue FROM filtered)
   SELECT t.*,p.* FROM totals t LEFT JOIN LATERAL (SELECT * FROM filtered ORDER BY period DESC,"siteId",block,number,id LIMIT 25 OFFSET ${(input.page-1)*25}) p ON true`);
   const t=result[0];return {rows:result.filter(r=>r.id!==null).map(r=>debtRow(r,today)),summary:{...reportTotals(t.summaryAmount,t.summaryGross,t.summaryReversed),debtorUnits:safeInteger(t.debtors),paidCount:safeInteger(t.paid),partialCount:safeInteger(t.partial),overdueKurus:safeInteger(t.overdue)},totalCount:safeInteger(t.count),page:input.page,pageSize:25,today};
  },{timeout:30000});},
  async movementReport(raw:z.input<typeof movementInput>){const input=movementInput.parse(raw);return db.$transaction(async tx=>{await authorize(tx,input);return movement(tx,input);},{timeout:30000});},
  async monthlyComparison(raw:z.input<typeof comparisonInput>){const input=comparisonInput.parse(raw);return db.$transaction(async tx=>{await authorize(tx,input);return compare(tx,input);},{timeout:30000});},
  async movementOverview(raw:z.input<typeof comparisonInput>){const input=comparisonInput.parse(raw);return db.$transaction(async tx=>{await authorize(tx,input);return {report:await movement(tx,input),comparison:await compare(tx,input)};},{timeout:30000});},
  async exportDebtCsv(raw:z.input<typeof reportInput>){const input=reportInput.parse(raw),today=reportBusinessDate();let amount=0n,gross=0n,reversed=0n;return exportFile<DebtRow>('debt',input,Prisma.sql`${debtBase(input,today)} SELECT *,count(*) OVER()::bigint AS "exportCount" FROM filtered ORDER BY id`,DEBT_HEADERS,r=>{amount+=BigInt(r.amountKurus);gross+=r.gross;reversed+=r.reversed;return debtCsv(r,today);},()=>{reportTotals(amount,gross,reversed);});},
  async exportMovementCsv(raw:z.input<typeof movementInput>){const input=movementInput.parse(raw);let dues=0n,income=0n,expense=0n;return exportFile<MovementRow>('movement',input,Prisma.sql`${movementBase(input)} SELECT *,count(*) OVER()::bigint AS "exportCount" FROM filtered ORDER BY id`,MOVEMENT_HEADERS,r=>{if(r.type==='DUES')dues+=r.amount;else if(r.type==='INCOME')income+=r.amount;else expense+=r.amount;return movementCsv(r);},()=>{movementSummary(dues,income,expense);});},
 };
}
