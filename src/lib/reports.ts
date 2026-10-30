import { z } from 'zod';
import { chargeBalance, financialSummary } from './finance';
export const reportInput = z.object({
 organizationId:z.string().min(1),siteId:z.string().min(1).optional(),
 period:z.string().regex(/^\d{4}-(0[1-9]|1[0-2])$/).optional(),
 status:z.enum(['ALL','UNPAID','PARTIAL','PAID']).default('ALL'),
 debtOnly:z.boolean().default(false),overdueOnly:z.boolean().default(false),
 page:z.number().int().min(1).max(1000000).default(1),
});
export type ReportInput=z.input<typeof reportInput>;
export const paymentStatuses={UNPAID:'Ödenmedi',PARTIAL:'Kısmi ödendi',PAID:'Tamamen ödendi'} as const;
export function safeInteger(value:bigint|number){const n=Number(value);if(!Number.isSafeInteger(n)||n<0)throw new Error('INVALID_FINANCIAL_TOTAL');return n;}
// Aggregate receipts are represented as one fully reversed and one live receipt.
// This preserves the same full-reversal arithmetic as the existing finance helpers.
export function aggregateCharge(amount:bigint|number,gross:bigint|number,reversed:bigint|number){
 const amountKurus=safeInteger(amount),g=safeInteger(gross),r=safeInteger(reversed);
 if(r>g)throw new Error('INVALID_FINANCIAL_TOTAL');
 return {amountKurus,payments:[...(r?[{amountKurus:r,reversal:{amountKurus:r}}]:[]),...(g-r?[{amountKurus:g-r}]:[])]};
}
export function reportBalance(amount:bigint|number,gross:bigint|number,reversed:bigint|number,dueDate:string,today:string){
 const balance=chargeBalance(aggregateCharge(amount,gross,reversed));
 return {...balance,status:balance.remainingKurus===0?'PAID' as const:balance.netKurus===0?'UNPAID' as const:'PARTIAL' as const,overdue:balance.remainingKurus>0&&dueDate<today};
}
export function reportTotals(amount:bigint,gross:bigint,reversed:bigint){return financialSummary([aggregateCharge(amount,gross,reversed)]);}
