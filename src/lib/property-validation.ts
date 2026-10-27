import { z } from "zod";
export const unitTypes = { RESIDENTIAL:"Konut", COMMERCIAL:"İş yeri", STORAGE:"Depo", OTHER:"Diğer" } as const;
export const usageStatuses = { UNKNOWN:"Belirtilmedi", OCCUPIED:"Kullanımda", VACANT:"Boş" } as const;
const name=z.string().trim().min(1).max(200);
export const siteInput=z.object({name,address:z.string().trim().max(500),description:z.string().trim().max(2000)});
export const blockInput=z.object({name:z.string().trim().min(1).max(100),description:z.string().trim().max(2000)});
export const unitInput=z.object({number:z.string().trim().min(1).max(30),floor:z.number().int().min(-20).max(200).nullable(),sectionType:z.enum(["RESIDENTIAL","COMMERCIAL","STORAGE","OTHER"]),usageStatus:z.enum(["UNKNOWN","OCCUPIED","VACANT"])});
export const personInput=name;
export const dateInput=z.string().date().transform(v=>new Date(`${v}T00:00:00.000Z`));
