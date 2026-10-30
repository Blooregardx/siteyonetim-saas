import { Prisma } from '@prisma/client';
import { mkdtemp,open,rm,stat } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { csvLine,EXPORT_BATCH_SIZE,EXPORT_MAX_BYTES,EXPORT_MAX_ROWS } from './csv';
export type CsvArtifact={path:string;size:number;rows:number;dispose:()=>Promise<void>};
/** DECLARE/FETCH preserves one PostgreSQL query snapshot even at READ COMMITTED.
 * Build the complete private file before sending HTTP headers; DB errors never yield partial CSV. */
export async function cursorCsv<T>(tx:Prisma.TransactionClient,kind:'debt'|'movement',query:Prisma.Sql,headers:string[],encode:(row:T)=>string,finish:()=>void=()=>{}):Promise<CsvArtifact>{
 const cursor=Prisma.raw(kind==='debt'?'finance_debt_export':'finance_movement_export');
 await tx.$executeRaw(Prisma.sql`DECLARE ${cursor} NO SCROLL CURSOR FOR ${query}`);
 const first=await tx.$queryRaw<(T&{exportCount:bigint})[]>(Prisma.sql`FETCH FORWARD 1 FROM ${cursor}`);
 const count=first[0]?.exportCount??0n;
 if(count>BigInt(EXPORT_MAX_ROWS))throw new Error('EXPORT_LIMIT');
 const directory=await mkdtemp(join(tmpdir(),'siteyonetim-csv-'));const path=join(directory,'export.csv');
 const dispose=()=>rm(directory,{recursive:true,force:true});
 const file=await open(path,'wx',0o600).catch(async error=>{await dispose();throw error;});let bytes=0,written=0;
 try{
  const write=async(value:string)=>{bytes+=Buffer.byteLength(value);if(bytes>EXPORT_MAX_BYTES)throw new Error('EXPORT_LIMIT');await file.writeFile(value);};
  await write('\uFEFF'+csvLine(headers.map(text=>({text}))));
  let batch:T[]=first;
  while(batch.length){written+=batch.length;if(written>EXPORT_MAX_ROWS)throw new Error('EXPORT_LIMIT');await write(batch.map(encode).join(''));batch=await tx.$queryRaw<T[]>(Prisma.sql`FETCH FORWARD ${Prisma.raw(String(EXPORT_BATCH_SIZE))} FROM ${cursor}`);}
  if(written!==Number(count))throw new Error('EXPORT_INCOMPLETE');
  finish();
  await tx.$executeRaw(Prisma.sql`CLOSE ${cursor}`);
  await file.close();const info=await stat(path);return {path,size:info.size,rows:written,dispose};
 }catch(error){await file.close().catch(()=>{});await dispose();throw error;}
}
