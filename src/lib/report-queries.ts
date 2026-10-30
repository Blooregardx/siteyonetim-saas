import { Prisma } from '@prisma/client';
import { z } from 'zod';
import { reportInput } from './reports';
import { movementInput } from './income-expense-validation';
export type DebtFilter=z.output<typeof reportInput>;
export type MovementFilter=z.output<typeof movementInput>;
export function shiftMonth(month:string,offset:number){const [y,m]=month.split('-').map(Number);const ordinal=y*12+m-1+offset;return `${String(Math.floor(ordinal/12)).padStart(4,'0')}-${String(ordinal%12+1).padStart(2,'0')}`;}
export function debtBase(input:DebtFilter,today:string){return Prisma.sql`WITH balances AS (
 SELECT c.id,c."siteId",c."unitId",c.period,c."amountKurus",c."dueDate",s.name AS site,b.name AS block,u.number,
 coalesce(sum(p."amountKurus"),0)::bigint AS gross,coalesce(sum(r."amountKurus"),0)::bigint AS reversed
 FROM "Charge" c JOIN "Site" s ON s.id=c."siteId" JOIN "Unit" u ON u.id=c."unitId" AND u."siteId"=c."siteId"
 JOIN "Block" b ON b.id=u."blockId" AND b."siteId"=c."siteId"
 LEFT JOIN "Payment" p ON p."chargeId"=c.id AND p."siteId"=c."siteId" LEFT JOIN "PaymentReversal" r ON r."paymentId"=p.id AND r."siteId"=p."siteId"
 WHERE s."organizationId"=${input.organizationId}
 ${input.siteId?Prisma.sql`AND c."siteId"=${input.siteId}`:Prisma.empty}
 ${input.period?Prisma.sql`AND c.period=${input.period}`:Prisma.empty}
 GROUP BY c.id,s.name,b.name,u.number
 ), filtered AS MATERIALIZED (SELECT *,"amountKurus"-gross+reversed AS remaining FROM balances
 WHERE (${input.status}='ALL' OR (${input.status}='UNPAID' AND gross=reversed) OR (${input.status}='PARTIAL' AND gross-reversed>0 AND gross-reversed<"amountKurus") OR (${input.status}='PAID' AND gross-reversed="amountKurus"))
 AND (${!input.debtOnly} OR "amountKurus"-gross+reversed>0)
 AND (${!input.overdueOnly} OR ("amountKurus"-gross+reversed>0 AND "dueDate"<${today}::date)))`;}
export function movementBase(input:MovementFilter,start=input.month,end=shiftMonth(input.month,1)){
 const scope=(site:Prisma.Sql,method:Prisma.Sql,day:Prisma.Sql)=>Prisma.sql`AND ${day}>=${start+'-01'}::date AND ${day}<${end+'-01'}::date ${input.siteId?Prisma.sql`AND ${site}=${input.siteId}`:Prisma.empty} ${input.method!=='ALL'?Prisma.sql`AND ${method}=${input.method}`:Prisma.empty}`;
 const manual=(day:Prisma.Sql)=>Prisma.sql`${scope(Prisma.sql`e."siteId"`,Prisma.sql`e.method`,day)} ${input.type!=='ALL'?Prisma.sql`AND e.type::text=${input.type}`:Prisma.empty} ${input.categoryId?Prisma.sql`AND e."categoryId"=${input.categoryId}`:Prisma.empty}`;
 const paidDay=Prisma.sql`(p."paidAt" AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Istanbul')::date`;
 const reverseDay=Prisma.sql`(r."createdAt" AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Istanbul')::date`;
 return Prisma.sql`WITH filtered AS MATERIALIZED (
 SELECT 'P:'||p.id AS id,p.id AS "sourceId",p."siteId",s.name AS site,'DUES' AS type,NULL::text AS "categoryId",'Aidat tahsilatı' AS category,'Aidat tahsilatı' AS description,${paidDay} AS day,p."amountKurus"::bigint AS amount,p.method,false AS reversal,(r.id IS NOT NULL) AS reversed,NULL::text AS reason
 FROM "Payment" p JOIN "Site" s ON s.id=p."siteId" LEFT JOIN "PaymentReversal" r ON r."paymentId"=p.id WHERE s."organizationId"=${input.organizationId} AND ${!input.categoryId&&(input.type==='ALL'||input.type==='DUES')} ${scope(Prisma.sql`p."siteId"`,Prisma.sql`p.method`,paidDay)}
 UNION ALL
 SELECT 'PR:'||r.id,p.id,p."siteId",s.name,'DUES',NULL::text,'Aidat tahsilatı','Aidat tahsilatı ters kaydı',${reverseDay},-r."amountKurus"::bigint,p.method,true,true,r."reasonCode"::text
 FROM "PaymentReversal" r JOIN "Payment" p ON p.id=r."paymentId" AND p."siteId"=r."siteId" JOIN "Site" s ON s.id=p."siteId" WHERE s."organizationId"=${input.organizationId} AND ${!input.categoryId&&(input.type==='ALL'||input.type==='DUES')} ${scope(Prisma.sql`p."siteId"`,Prisma.sql`p.method`,reverseDay)}
 UNION ALL
 SELECT 'E:'||e.id,e.id,e."siteId",s.name,e.type::text,c.id,c.name,e.description,e."businessDate",e."amountKurus"::bigint,e.method,false,(r.id IS NOT NULL),NULL::text
 FROM "FinancialEntry" e JOIN "Site" s ON s.id=e."siteId" JOIN "FinancialCategory" c ON c.id=e."categoryId" LEFT JOIN "FinancialEntryReversal" r ON r."entryId"=e.id WHERE e."organizationId"=${input.organizationId} AND ${input.type!=='DUES'} ${manual(Prisma.sql`e."businessDate"`)}
 UNION ALL
 SELECT 'ER:'||r.id,e.id,e."siteId",s.name,e.type::text,c.id,c.name,e.description,${reverseDay},-r."amountKurus"::bigint,e.method,true,true,r.reason
 FROM "FinancialEntryReversal" r JOIN "FinancialEntry" e ON e.id=r."entryId" JOIN "Site" s ON s.id=e."siteId" JOIN "FinancialCategory" c ON c.id=e."categoryId" WHERE e."organizationId"=${input.organizationId} AND ${input.type!=='DUES'} ${manual(reverseDay)})`;
}
export type DebtRow={id:string;siteId:string;site:string;unitId:string;period:string;amountKurus:number;dueDate:Date;block:string;number:string;gross:bigint;reversed:bigint};
export type MovementRow={id:string;sourceId:string;siteId:string;site:string;type:string;category:string;description:string;day:Date;amount:bigint;method:string;reversal:boolean;reversed:boolean;reason:string|null};
export const movementTotals=Prisma.sql`SELECT coalesce(sum(amount) FILTER(WHERE type='DUES'),0)::bigint AS dues,coalesce(sum(amount) FILTER(WHERE type='INCOME'),0)::bigint AS income,coalesce(sum(amount) FILTER(WHERE type='EXPENSE'),0)::bigint AS expense,count(*)::bigint AS count,count(*) FILTER(WHERE type='INCOME' AND NOT reversal)::bigint AS "incomeCount",count(*) FILTER(WHERE type='EXPENSE' AND NOT reversal)::bigint AS "expenseCount" FROM filtered`;
