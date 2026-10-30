import { z } from 'zod';
import { createHash } from 'node:crypto';
export const bulkInput = z.object({
 siteId:z.string().min(1), unitIds:z.array(z.string().min(1)).min(1).max(5000).refine(v=>new Set(v).size===v.length),
 period:z.string().regex(/^\d{4}-(0[1-9]|1[0-2])$/), amountKurus:z.number().int().positive().max(2147483647),
 dueDate:z.string().date(),
}).transform(v=>({...v,unitIds:[...v.unitIds].sort()}));
export type BulkInput = z.input<typeof bulkInput>;
export const fingerprint = (value:unknown) => createHash('sha256').update(JSON.stringify(value)).digest('hex');
export function bulkTotal(amount:number,count:number) {
 const total=amount*count;
 if(!Number.isSafeInteger(total)||total<0)throw new Error('INVALID_TOTAL');
 return total;
}
