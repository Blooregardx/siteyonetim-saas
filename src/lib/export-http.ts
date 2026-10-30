import { createReadStream } from 'node:fs';
import { Readable } from 'node:stream';
import { db } from './db';
import { verifySession } from './session';
import { management } from './management';
import { reportInput } from './reports';
import { movementInput } from './income-expense-validation';
import { ZodError } from 'zod';
export function exportParams(url:string,kind:'debt'|'movement'){
 const params=new URL(url).searchParams;
 const allowed=kind==='debt'?['org','site','period','status','debt','overdue']:['org','site','month','type','category','method'];
 for(const key of params.keys())if(!allowed.includes(key)||params.getAll(key).length!==1)throw new Error('INVALID_FILTER');
 const get=(key:string)=>params.get(key)??undefined;
 if(kind==='debt'){
  if(![undefined,'true'].includes(get('debt'))||![undefined,'true'].includes(get('overdue')))throw new Error('INVALID_FILTER');
  return reportInput.parse({organizationId:get('org'),siteId:get('site')||undefined,period:get('period')||undefined,status:get('status'),debtOnly:get('debt')==='true',overdueOnly:get('overdue')==='true'});
 }
 return movementInput.parse({organizationId:get('org'),siteId:get('site')||undefined,month:get('month'),type:get('type'),categoryId:get('category')||undefined,method:get('method')});
}
export async function csvDownload(request:Request,kind:'debt'|'movement'){
 try{
  // Validation + management verification both run on this download request.
  const api=management(db,verifySession);
  const params=exportParams(request.url,kind);
  const artifact=kind==='debt'?await api.exportDebtCsv(reportInput.parse(params)):await api.exportMovementCsv(movementInput.parse(params));
  try{
   if(request.signal.aborted){await artifact.dispose();return new Response('İndirme iptal edildi.',{status:499,headers:{'Cache-Control':'private, no-store'}});}
   const file=createReadStream(artifact.path);const abort=()=>{file.destroy();};request.signal.addEventListener('abort',abort,{once:true});file.once('close',()=>{request.signal.removeEventListener('abort',abort);void artifact.dispose().catch(()=>{});});
   return new Response(Readable.toWeb(file) as ReadableStream<Uint8Array>,{headers:{'Content-Type':'text/csv; charset=utf-8','Content-Disposition':`attachment; filename="${kind==='debt'?'borc-tahsilat':'gelir-gider'}.csv"`,'Content-Length':String(artifact.size),'X-Export-Rows':String(artifact.rows),'Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff'}});
  }catch(error){await artifact.dispose();throw error;}
 }catch(error){
  const code=error instanceof Error?error.message:'';
  const limit=code==='EXPORT_LIMIT';const denied=['UNAUTHENTICATED','FORBIDDEN','EMAIL_UNVERIFIED'].includes(code);
  const invalid=error instanceof ZodError||code==='INVALID_FILTER';
  return new Response(limit?'Dışa aktarma sınırı aşıldı (en fazla 50.000 kayıt veya 128 MB). Filtreleri daraltın.':denied?'Bu indirme için yetkiniz veya doğrulanmış oturumunuz yok.':invalid?'Filtreler geçersiz. Rapor ekranından yeniden deneyin.':'CSV hazırlanamadı. Lütfen yeniden deneyin.',{status:limit?413:denied?(code==='UNAUTHENTICATED'?401:403):invalid?400:500,headers:{'Content-Type':'text/plain; charset=utf-8','Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff'}});
 }
}
