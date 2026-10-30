import { z } from 'zod';
export const dashboardPage=z.coerce.number().int().min(1).max(1000000).default(1);
export const unitFilters=z.object({page:dashboardPage,q:z.string().trim().max(100).default(''),block:z.string().max(200).default(''),floor:z.preprocess(v=>v===''?undefined:v,z.coerce.number().int().min(-20).max(200).optional()),type:z.enum(['','RESIDENTIAL','COMMERCIAL','STORAGE','OTHER']).default(''),status:z.enum(['','UNKNOWN','OCCUPIED','VACANT']).default('')}).strict();
export const chargeFilters=z.object({page:dashboardPage,period:z.union([z.literal(''),z.string().regex(/^\d{4}-(0[1-9]|1[0-2])$/)]).default(''),block:z.string().max(200).default(''),unit:z.string().max(200).default(''),status:z.enum(['ALL','UNPAID','PARTIAL','PAID']).default('ALL'),debt:z.enum(['','true']).default('')}).strict();
export const simpleFilters=z.object({page:dashboardPage,q:z.string().trim().max(100).default('')}).strict();
export const PAGE_SIZE=25;

export function validateDashboardParams(raw:unknown,allowed:readonly string[]){const params=z.record(z.string(),z.string()).parse(raw);if(Object.keys(params).some(key=>!allowed.includes(key)))throw new Error('INVALID_FILTER');return params;}
