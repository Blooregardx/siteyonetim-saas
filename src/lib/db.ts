import { PrismaClient } from "@prisma/client";
import { panelProbeEnabled,panelQuery } from "./panel-probe";
const globalDb = globalThis as unknown as { db?: PrismaClient };
function createDb(){
 const client=new PrismaClient({log:panelProbeEnabled()?[{emit:'event',level:'query'}]:[]});
 client.$on('query',event=>panelQuery(event.query,event.duration));
 return client;
}
export const db = globalDb.db ?? createDb();
if (process.env.NODE_ENV !== "production") globalDb.db = db;
